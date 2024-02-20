from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from os import remove
import requests
import json
import csv


def combine_and_delete_files(file_count):
    combined_filename = "Csv_Data/Combined_Updated_MPN.csv"
    with open(combined_filename, "w", newline="", encoding='utf-8-sig') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["MPN", "Price"])
        for index in range(file_count):
            filename = f"Csv_Data/Updated_MPN_{index}.csv"
            with open(filename, "r", encoding='utf-8-sig') as infile:
                reader = csv.reader(infile)
                next(reader)  # Skip header
                for row in reader:
                    writer.writerow(row)
            remove(filename)


def fetch_price(session, number):
    try:
        response = session.get(f'https://uk.rs-online.com/web/c/?searchTerm={number}',
                               headers={
                                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'})
        soup = BeautifulSoup(response.content, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")
        if script:
            dataJson = json.loads(script.text)
            element = dataJson['props']['pageProps']['articleResult']['data']['article']
            price = element['priceBreaks'][0]['price']
            return "%.2f" % float(price)
        else:
            print(f"Script not found for {number}.")
            return "N/A"
    except Exception as e:
        print(f"Error fetching price for {number}: {e}")
        return "N/A"


def update_prices_segment(numbers, index):
    session = requests.Session()
    output_filename = f"Csv_Data/Updated_MPN_{index}.csv"
    with open(output_filename, "w", newline="", encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["MPN", "Price"])
        for number in numbers:
            price = fetch_price(session, number)
            writer.writerow([number, f'£{price}'])
            print(f'{number} -> {price}')
    session.close()


def read_mpn_list():
    with open("Csv_Data/MPN.csv", "r", encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
        numbers = [row[0].strip("[]'") for row in reader]
    return numbers


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def main():
    numbers = read_mpn_list()
    chunk_size = len(numbers) // 10
    numbers_chunks = list(divide_chunks(numbers, chunk_size))

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(update_prices_segment, chunk, index) for index, chunk in enumerate(numbers_chunks)]
        for future in as_completed(futures):
            print(f"Task completed: {future.result()}")

    combine_and_delete_files(len(numbers_chunks))


if __name__ == "__main__":
    main()

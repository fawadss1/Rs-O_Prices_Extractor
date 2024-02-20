from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import requests
import json
import csv


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
            return price
        else:
            print(f"Script not found for {number}.")
            return "N/A"
    except Exception as e:
        print(f"Error fetching price for {number}: {e}")
        return "N/A"


def update_prices_segment(numbers, index):
    session = requests.Session()
    output_filename = f"data/Updated_MPN_{index}.csv"
    with open(output_filename, "w", newline="", encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["MPN", "Price"])
        for number in numbers:
            price = fetch_price(session, number)
            writer.writerow([number, f'£ {price}'])
            print(f'{number} -> {price}')
    session.close()


def read_mpn_list():
    with open("MPN.csv", "r", encoding='utf-8-sig') as csvfile:
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


if __name__ == "__main__":
    main()

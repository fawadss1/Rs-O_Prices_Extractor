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


def update_prices_real_time():
    with open("MPN.csv", "r", encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
        numbers = [row[0].strip("[]'") for row in reader]

    session = requests.Session()

    with open("Updated_MPN.csv", "w", newline="", encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["MPN", "Price"])

        for number in numbers:
            price = fetch_price(session, number)
            writer.writerow([number, price])
            print(f'{number} -> {price}')

    session.close()


update_prices_real_time()

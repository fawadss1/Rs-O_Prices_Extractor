from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
import csv


def extract_data_from_site(number, driver):
    try:
        acceptButton = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[@id='ensCloseBanner']")))
        acceptButton.click()
    except Exception as e:
        print('No Accept Button Found')

    try:
        feedBackButton = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='uws-button uws-button--link uws-invite__button uws-invite__button-decline']")))
        feedBackButton.click()
    except Exception as e:
        print('No FeedBack Button Found')

    data = 'No Price'
    search_box = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@id='searchBarTextInput']")))
    try:
        search_box.clear()
        search_box.send_keys(number)

        search_button = driver.find_element(By.XPATH, "//button[@aria-label='Search button']")
        search_button.click()
        price = driver.find_elements(By.XPATH, "//p[@data-testid='price-exc-vat']")
        data = [price[1].text.strip()]
    except Exception as e:
        search_box.clear()
        print(f'{number} Have Price')

    return data


def main():
    numbers = []
    with open("MPN.csv", "r", encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            clean_element = row[0].strip("[]'")
            numbers.append(clean_element)

    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://uk.rs-online.com/web")

    with open("Updated_MPN.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["MPN", "Price"])
        for number in numbers:
            data = extract_data_from_site(number, driver)
            writer.writerow([number, data[0]])
            print(f'{number} -> is Done ....')

    driver.quit()


if __name__ == "__main__":
    main()

import csv
import random
from asyncio import sleep

from bs4 import BeautifulSoup
import requests
import json
import lxml


def main():
    headers = {
        'Accept': '*/*',
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }

    # url = 'https://health-diet.ru/table_calorie/'
    #
    # req = requests.get(url, headers=headers)
    # req.encoding = 'utf-8'
    #
    # src = req.text
    #
    # with open('index.html', 'w') as file:
    #     file.write(src)

    with open('index.html') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    # all groups of products
    all_categories = soup.find_all(class_='mzr-tc-group-item-href')

    all_categories_dict = {}

    for category in all_categories:
        all_categories_dict[category.text] = 'https://health-diet.ru' + category.get("href")

    with open('all_categories.json', 'w', encoding="utf-8") as file:
        json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)

    with open('all_categories.json', encoding="utf-8") as file:
        categories = json.load(file)

    iteration_count = len(categories) - 1
    print(f'Iterations:{iteration_count}')

    count = 1
    for item, url in categories.items():

        try:
            req = requests.get(url, headers=headers)
            req.encoding = 'utf-8'

            src = req.text

            with open(f'data/{count}.{item}.html', 'w', encoding="utf-8") as file:
                file.write(src)

            with open(f'data/{count}.{item}.html', encoding="utf-8") as file:
                src = file.read()

            soup = BeautifulSoup(src, 'lxml')


            #proverka na nalichie infi na stranice
            alert_block = soup.find(class_='uk-alert-danger')
            if alert_block is not None:
                continue

            #headings
            headings = soup.find(class_='uk-table mzr-tc-group-table uk-table-hover uk-table-striped uk-table-condensed').find_all('th')
            product = headings[0].text
            call = headings[1].text
            proteins = headings[2].text
            fats = headings[3].text
            carbons = headings[4].text

            with open(f'data/{count}.{item}.csv', 'w', newline='', errors='replace') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(
                    (
                        product,
                        call,
                        proteins,
                        fats,
                        carbons
                    )
                )
            #product_data
            product_data_all = soup.find('tbody').find_all('tr')
            for data in product_data_all:
                product_data = data.find_all('td')

                title = product_data[0].find('a').text
                calories = product_data[1].text
                proteins = product_data[2].text
                fats = product_data[3].text
                carbohydrates = product_data[4].text

                with open(f'data/{count}.{item}.csv', 'a', newline='', errors='replace') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow(
                        (
                            title,
                            calories,
                            proteins,
                            fats,
                            carbohydrates

                        )
                    )

            print(f'iteration # {count} completed...\n'
                  f'iterations to go: {iteration_count - 1}')

            count += 1
            iteration_count -= 1

            if iteration_count == 0:
                print('Programm completed!')
                break

            sleep(random.randrange(2, 4))

        except Warning:
            print(f'This page ({url}) has no data!')


if __name__ == '__main__':
    main()

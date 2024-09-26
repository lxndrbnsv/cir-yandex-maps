import sys
import json
import warnings

import PySimpleGUI as Sg
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType

from modules.queries import ReadQueries
from modules.parse import GetCompanies, GetCompanyData
from modules.write import WriteXLSX
from modules.util import ClearWB, parse_query_string
from modules.proxy import GetProxy, AddProxy
from selenium.webdriver.chrome.service import Service


warnings.filterwarnings("ignore", category=UserWarning)


# sys.stdout = open("log.log", "w+")
# sys.stderr = open("log.log", "w+")

service = Service()
options = webdriver.ChromeOptions()
# options.add_argument("--headless")
browser = webdriver.Chrome(service=service, options=options)


# options = Options()
# options.headless = True
# options.add_experimental_option("excludeSwitches", ["enable-logging"])
# browser = webdriver.Chrome(
#     executable_path="./webdriver/chromedriver", options=options
# )

Sg.theme("TealMono")

layout = [
    [
        Sg.Text("Путь к файлу с адресами:", size=(75, 1)),
        Sg.FileBrowse("Обзор"),
    ],
    [Sg.HSeparator()],
    # [Sg.Output(size=(75, 10), echo_stdout_stderr=False)],
    [
        Sg.Text("Добавить прокси (ip:port):"),
        Sg.InputText(do_not_clear=False),
        Sg.Button("Добавить прокси"),
    ],
    [
        Sg.Button("Запуск"),
        Sg.Checkbox("Использовать прокси"),
        Sg.VSeparator(),
        Sg.Button("Очистить файл результатов"),
        Sg.VSeparator(),
        Sg.Button("Выход"),
    ],
]

window = Sg.Window("Yandex Maps scraper", layout)

if __name__ == "__main__":
    while True:
        event, values = window.read()

        if event == "Очистить файл результатов":
            ClearWB()
            Sg.Popup("Файл результатов очищен!")

        if event == Sg.WIN_CLOSED or event == "Выход":
            break

        if event == "Запуск":
            proxy = values[2]
            print(proxy)

            if proxy is True:
                proxy_ip = GetProxy().proxy_addr
                if proxy_ip is None:
                    Sg.popup(
                        "Отсутсвует файл с прокси либо формат прокси неверный!"
                        "\nПарсер будет запущен без использования прокси."
                    )
                else:
                    proxy = Proxy()
                    proxy.proxy_type = ProxyType.MANUAL
                    proxy.ssl_proxy = proxy_ip

                    capabilities = webdriver.DesiredCapabilities.CHROME
                    proxy.add_to_capabilities(capabilities)
            else:
                proxy = None

            if values["Обзор"] != "":
                print(values["Обзор"])
                queries = ReadQueries(filepath=values["Обзор"]).queries

                for q in queries:
                    print(q)
                    companies = GetCompanies(browser=browser, query=q).results

                    print(f"Собрано {len(companies)} организаций.")
                    print("Обработка данных:")
                    phones = []
                    for company in companies:
                        company_dict = GetCompanyData(
                            browser=browser, company_link=company
                        ).data

                        if company_dict is not None:
                            company_dict["address"] = q
                            company_dict["building_id"] = parse_query_string(q)
                            WriteXLSX(company_dict=company_dict)
                            print("Данные записаны")
                            phones.append(company_dict["phone"])
                        else:
                            print("Отсутствуют контактные данные!")
                    print("--- --- ---")
                Sg.popup("Сбор данных завершён!")
            else:
                Sg.popup("Добавьте файл с адресами!")

        if event == "Добавить прокси":
            proxy = values[1]
            print(values)
            print(proxy)
            if ":" not in proxy:
                Sg.popup("Неправильный формат прокси!")
            else:
                AddProxy(proxy)
                Sg.popup_ok("Прокси добавлен!")

    browser.quit()

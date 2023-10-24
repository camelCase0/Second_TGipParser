import json
import re 
import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import schedule
import time

def write_data_to_sqlite(database_file, table_name, column_names, values):
  """Writes data to a SQLite database.

  Args:
    database_file: The path to the SQLite database file.
    table_name: The name of the table to write the data to.
    column_names: A list of the column names.
    values: A list of the values to write to the database.
  """

  connection = sqlite3.connect(database_file)
  cursor = connection.cursor()

  try:
    cursor.execute("CREATE TABLE IF NOT EXISTS {} ({})".format(
        table_name, ", ".join(column_names)))
  except sqlite3.OperationalError:
    pass

  insert_statement = "INSERT INTO {} ({}) VALUES ({})".format(
      table_name, ", ".join(column_names), ",".join(["?" for _ in column_names]))

  cursor.execute(insert_statement, values)
  connection.commit()
  connection.close()

def is_proxy_working(proxy):
    try:
        response = requests.get("https://www.example.com", proxies={"http": f'http://{proxy}'}, timeout=5)
        if response.status_code == 200:
            print(f"Proxy {proxy} is working fine.")
            return True
        else:
            print(f"Proxy {proxy} returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False
    
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"
YELLOW = "\033[33m"

def parse_ips_from_url(url, proxy_address):
    proxy_dict = {
        # "http":f'http://{proxy_address}',
        "http":f'http://{proxy_address}'
    }
    try:
        response = requests.get(url, proxies=proxy_dict)
        # print(response)

        if response.status_code != 200:
            print(f"{RED}[-]{RESET} Failed to retrieve {url} using proxy: {proxy_address}")
            return 0
            
        print(f"{GREEN}[+]{RESET} Successfully parsed {url} using proxy: {proxy_address}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")  
        # print(response.content)

    soup = BeautifulSoup(response.content, "html.parser")
    arr_find = soup.findAll("div", class_="tgme_widget_message_text js-message_text")
    # print(arr_find)
    
    ip_addresses = []

    pattern = r"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}"
    for input_str in arr_find:
        ip_addresses.extend(re.findall(pattern, input_str.text))

    for id, ip in enumerate(ip_addresses):
        ip_addresses[id] = re.sub(r'[^\d]', ".", ip)

    print(f"Result for {YELLOW}{url}: {ip_addresses}{RESET}")
    return ip_addresses  
        
urls = ["https://t.me/s/psaldriikwjl","https://t.me/s/uwwixgqsfulbhw"]
f = open("proxy.txt", "r")
proxies = f.readlines()

def parse_all_tg():
    # proxy_address = proxies.pop(0)
    # print(f"Proxy ip={proxy_address}")
    # while not is_proxy_working(proxy_address):
    #     proxy_address = proxies.pop(0)
    #     # print(proxy_address)
    # proxies.append(proxy_address)

    for url in urls:
        proxy_address = proxies.pop(0)
        while not is_proxy_working(proxy_address):
            proxy_address = proxies.pop(0)
        proxies.append(proxy_address)

        ip_addresses = parse_ips_from_url(url, proxy_address)

        if ip_addresses !=0:
            serialized_data = json.dumps(ip_addresses)

            database_file = "my_database.db"
            table_name = "telegrams"
            column_names = ["address", "ip", "datetime_parsing"]
            values = [url, serialized_data, datetime.now()]

            write_data_to_sqlite(database_file, table_name, column_names, values)

schedule.every(20).minutes.do(parse_all_tg)
while True:
    schedule.run_pending()
    time.sleep(1)
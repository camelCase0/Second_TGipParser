import json
import re 
import requests
from bs4 import BeautifulSoup
import sqlite3

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
        response = requests.get("https://www.example.com", proxies={"http": f'http://{proxy_address}'}, timeout=5)
        if response.status_code == 200:
            print(f"Proxy {proxy} is working fine.")
            return True
        else:
            print(f"Proxy {proxy} returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False
    
urls = ["https://t.me/s/psaldriikwjl","https://t.me/s/uwwixgqsfulbhw"]

f = open("proxy.txt", "r")
proxies = f.readlines()

for url in urls:
    proxy_address = proxies.pop(0)
    print(proxy_address)
    while not is_proxy_working(proxy_address):
        proxy_address = proxies.pop(0)
        print(proxy_address)

    proxy_dict = {
        # "http":f'http://{proxy_address}',
        "http":f'http://{proxy_address}'
    }
    proxies.append(proxy_address)
    try:
        response = requests.get(url, proxies=proxy_dict)
        print(response)

        if response.status_code != 200:
            print(f"Failed to retrieve {url} using proxy: {proxy_address}")
            continue
            
        print(f"Successfully parsed {url} using proxy: {proxy_address}")
        
        print(response.content)
        soup = BeautifulSoup(response.content, "html.parser")
        arr_find = soup.findAll("div", class_="tgme_widget_message_text js-message_text")
        print(arr_find)
        
        ip_addresses = []

        pattern = r"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}"
        for input_str in arr_find:
            ip_addresses.extend(re.findall(pattern, input_str.text))

        for id, ip in enumerate(ip_addresses):
            ip_addresses[id] = re.sub(r'[^\d]', ".", ip)

        print(ip_addresses)
        serialized_data = json.dumps(ip_addresses)

        database_file = "my_database.db"
        table_name = "telegrams"
        column_names = ["address", "ip"]
        values = [url, serialized_data]
        
        write_data_to_sqlite(database_file, table_name, column_names, values)
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    
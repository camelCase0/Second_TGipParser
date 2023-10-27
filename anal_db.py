import sqlite3
import json
import requests
import time
from shodan import Shodan
from bs4 import BeautifulSoup
from censys.search import CensysHosts



database_file = "server1.db"
table_name = "telegrams"
column_names = ["address", "ip", "datetime_parsing"]

connection = sqlite3.connect(database_file)
cursor = connection.cursor()


cursor.execute("SELECT {} FROM {} GROUP BY {} ORDER BY {}".format(", ".join(column_names), table_name, "ip","datetime_parsing"))

tgs = cursor.fetchall()
connection.close()

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"
YELLOW = "\033[33m"


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

def fetch_url(url):
    # f = open("proxy.txt", "r")
    # proxies = f.readlines()
    # proxy_address = proxies.pop(0)
    # while not is_proxy_working(proxy_address):
    #     proxy_address = proxies.pop(0)
    # # proxies.append(proxy_address)
    
    # proxy_dict = {
    #     # "http":f'http://{proxy_address}',
    #     "http":f'http://{proxy_address}'
    # }
    headers = {
        'accept': 'application/json',
        'Authorization': 'Basic '
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return(response.content)
    else:
        print(f"{RED}[-]Failed to fetch data from the API.{RESET} Status code:", response.status_code)
        return False
    
h = CensysHosts()

with open('res_anal5.json', 'a+') as file:
    for tg in tgs:
        ips = json.loads(tg[1])
        strochka = f"Telegram: {GREEN}{tg[0]}{RESET} | ips:{RED}{ips}{RESET} | first detected:{YELLOW}{tg[2]}{RESET}"
        print(strochka)
        # file.write(strochka)
        
        
        # for ip in ips:
        #     host = h.view(ip)
        #     # print(host)
        #     json.dump(host,file,indent=4)



        #     url = f"https://search.censys.io/api/v2/{ip}"
        #     # url = f"https://otx.alienvault.com/indicator/ip/{ip}"
        #     # url = f"https://www.shodan.io/host/{ip}"
        #     res = fetch_url(url)
        #     print(res)
            # soup = BeautifulSoup(res, 'html.parser')

            # arr_find = soup.findAll("div", class_="language-json hljs")
            # serialized = json.dumps(arr_find)
            # if res:
            #     print(arr_find)
            # file.write(str(host))




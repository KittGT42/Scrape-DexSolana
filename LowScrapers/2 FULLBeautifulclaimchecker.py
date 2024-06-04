import os
import csv
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

cookies = {
    'chakra-ui-color-mode': 'dark',
    '_ga': 'GA1.1.2124747211.1717081062',
    'cf_clearance': 'l_t1xooMmpssfM6WhbW9ZOgjso_Dwia5TJHgS4g53Jo-1717266778-1.0.1.1-nr7PdxFwdVmtDdKKEwFHaDAV1OzUrawAuW7lTulAn1k0tbj7539PXA2DakxZ4ugxKeQgaDve6AP7EcSuScXM_g',
    '_ga_CFY1SSGE2N': 'GS1.1.1717269052.1.0.1717269053.0.0.0',
    '__cf_bm': 'NmC_4dxfp8OsGqrGJNsl.ec_lTEeX0P2TefR5Gp5_LY-1717275807-1.0.1.1-PpvQQDp_6GEcCq3MBiSoFVDuOr3YhyMaPOSSfujs.X6RXeiIxCsw3ASU5aYvJAwe1eTgingSe0jpfMkBiohrhUHgCTmD5aWgOp9JvaL1Blg',
    '_ga_532KFVB4WT': 'GS1.1.1717276067.8.1.1717276253.59.0.0',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ru;q=0.8,uk-UA;q=0.7,uk;q=0.6',
    'cache-control': 'max-age=0',
    # 'cookie': 'chakra-ui-color-mode=dark; _ga=GA1.1.2124747211.1717081062; cf_clearance=l_t1xooMmpssfM6WhbW9ZOgjso_Dwia5TJHgS4g53Jo-1717266778-1.0.1.1-nr7PdxFwdVmtDdKKEwFHaDAV1OzUrawAuW7lTulAn1k0tbj7539PXA2DakxZ4ugxKeQgaDve6AP7EcSuScXM_g; _ga_CFY1SSGE2N=GS1.1.1717269052.1.0.1717269053.0.0.0; __cf_bm=NmC_4dxfp8OsGqrGJNsl.ec_lTEeX0P2TefR5Gp5_LY-1717275807-1.0.1.1-PpvQQDp_6GEcCq3MBiSoFVDuOr3YhyMaPOSSfujs.X6RXeiIxCsw3ASU5aYvJAwe1eTgingSe0jpfMkBiohrhUHgCTmD5aWgOp9JvaL1Blg; _ga_532KFVB4WT=GS1.1.1717276067.8.1.1717276253.59.0.0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version': '"125.0.6422.113"',
    'sec-ch-ua-full-version-list': '"Google Chrome";v="125.0.6422.113", "Chromium";v="125.0.6422.113", "Not.A/Brand";v="24.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"macOS"',
    'sec-ch-ua-platform-version': '"12.7.5"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def search_for_phrase(link):
    if not is_valid_url(link):
        print(f"Invalid URL: {link}")
        return "Invalid URL", None, None
    print(f"Accessing link: {link}")
    try:
        response = requests.get(link, headers=headers, cookies=cookies, timeout=15)  # Increased timeout
        soup = BeautifulSoup(response.text, 'html.parser')  # Changed parser

        # Adjusted finding method to use class
        phrase_element = soup.find("strong", class_="chakra-text custom-0")
        name_element = soup.find("h3")  # Assuming names are consistently in <h3>
        date_element = soup.find("p", text=re.compile(
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{1,2},\s\d{4}\b'))

        phrase_found = "Yes" if phrase_element else "No"
        name_found = name_element.text.strip() if name_element else None
        date_found = date_element.text.strip() if date_element else None

        return phrase_found, name_found, date_found
    except requests.exceptions.RequestException as e:
        print(f"Error accessing page or finding phrase: {str(e)}")
        return "No", None, None


def update_csv(file_path):
    print("Updating CSV with search results...")
    temp_file_path = file_path.replace('.csv', '_temp.csv')
    with open(file_path, 'r', newline='', encoding='utf-8') as infile, open(temp_file_path, 'w', newline='',
                                                                            encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        headers = next(reader, None)
        writer.writerow(headers if headers else ["Url", "Community Takeover Found", "Name", "TakeoverDate"])

        for row in reader:
            if len(row) < 4:
                row.extend([None] * (4 - len(row)))  # Ensure row has at least 4 elements
            result, name, date = search_for_phrase(row[0])
            print(f"Search result for URL '{row[0]}': {result}, Name found: {name}, Date found: {date}")
            row[1], row[2], row[3] = result, name, date
            writer.writerow(row)
    os.replace(temp_file_path, file_path)


def main():
    start_time = time.time()
    print("Script started.")
    file_path = "../data/scraped_links.csv"
    update_csv(file_path)
    elapsed_time = time.time() - start_time
    print("Process complete. Exiting...")
    print(f"Total runtime: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()

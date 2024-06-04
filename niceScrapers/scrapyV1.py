import os
import csv
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from get_cookes import get_cookes

cookies_values = get_cookes()
cookies = cookies_values

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ru;q=0.8,uk-UA;q=0.7,uk;q=0.6',
    'cache-control': 'max-age=0',
    # 'cookie': 'chakra-ui-color-mode=dark; _ga=GA1.1.2124747211.1717081062; cf_clearance=l_t1xooMmpssfM6WhbW9ZOgjso_Dwia5TJHgS4g53Jo-1717266778-1.0.1.1-nr7PdxFwdVmtDdKKEwFHaDAV1OzUrawAuW7lTulAn1k0tbj7539PXA2DakxZ4ugxKeQgaDve6AP7EcSuScXM_g; _ga_CFY1SSGE2N=GS1.1.1717269052.1.0.1717269053.0.0.0; __cf_bm=DDovlNfGdTH2B9djsVMF5TeyzMeJLWjwL0p3RV38fu8-1717289875-1.0.1.1-_l5Ty77geGG4FizlzQNx11LXDSbaJxzCZkQFKZCdPTAIf5BQWDedFsNnhQb7RBLau6xxaTuB_hsToWxAGV1qA9h4zNDlbITR6rjCpjGkp0w; _ga_532KFVB4WT=GS1.1.1717286227.9.1.1717289877.58.0.0',
    'if-modified-since': 'Sun, 02 Jun 2024 00:57:55 GMT',
    'priority': 'u=0, i',
    'referer': 'https://www.upwork.com/',
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
        soup = BeautifulSoup(response.text, 'lxml')  # Changed parser

        block_with_info = soup.find('div', class_='custom-1iorrph')
        if block_with_info:
            phrase_element = block_with_info.find("strong", class_="chakra-text custom-0")
            if phrase_element:
                phrase_element = block_with_info.find("strong", class_="chakra-text custom-0").text.strip()
                name_element = block_with_info.find("h3", class_="chakra-heading custom-y5314g").text.strip()
                date_element = block_with_info.find("span", 'chakra-text custom-2ygcmq').text.strip()
                # if date_element is None:
                #
                return phrase_element, name_element, date_element
            else:
                phrase_found = None
                name_found = None
                date_found = None
                return phrase_found, name_found, date_found

        else:
            phrase_found = None
            name_found = None
            date_found = None

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
    file_path = "../data/scraped_links5.csv"
    update_csv(file_path)
    elapsed_time = time.time() - start_time
    print("Process complete. Exiting...")
    print(f"Total runtime: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()

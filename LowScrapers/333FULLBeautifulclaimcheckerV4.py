import os
import csv
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

cookies = {
    'chakra-ui-color-mode': 'dark',
    'cf_clearance': 'sIIGW_ZYkK4oifjYVM8zM0r2nzbRVP9N2.tIvx2OhRM-1715110823-1.0.1.1-s_qmN7UeoBrZOMgHKCQqF1LOpzvYM1AzxG.hqHiJ.Ype71k8Of7CMfSzzd4IqMF_j19nttTPfAKd5gJRGO3o5w',
    'cf_clearance': 'KYYZFZB04ahKNnuFGMcFVkKG4xYIri1TIu.bRSo5dik-1717269454-1.0.1.1-sJlNaSSv8Hy9KbRda89XFRUcBJqWPKkh6osnhQkzH67plMgoiKkVqR1mNhHn91OVU1OF2ZfI_j1QJURHt_NE0g',
    '__cf_bm': 'PTCzIp4uQG8I8rvkqi1NK5VCwV6hRrptEzPMDkx6RPQ-1717279684-1.0.1.1-ZtRRac7JaPfKLCYFoi6HyjbN8Xjyy5eovEmE4.ZaZbFaCqmrWOchL6FxRkji2he4zkcXmJDYJZ810BZqbSqU2G2YHDBxst1Z4WJL30gm8lo',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.8',
    'cache-control': 'no-cache',
    # 'cookie': 'chakra-ui-color-mode=dark; cf_clearance=sIIGW_ZYkK4oifjYVM8zM0r2nzbRVP9N2.tIvx2OhRM-1715110823-1.0.1.1-s_qmN7UeoBrZOMgHKCQqF1LOpzvYM1AzxG.hqHiJ.Ype71k8Of7CMfSzzd4IqMF_j19nttTPfAKd5gJRGO3o5w; cf_clearance=KYYZFZB04ahKNnuFGMcFVkKG4xYIri1TIu.bRSo5dik-1717269454-1.0.1.1-sJlNaSSv8Hy9KbRda89XFRUcBJqWPKkh6osnhQkzH67plMgoiKkVqR1mNhHn91OVU1OF2ZfI_j1QJURHt_NE0g; __cf_bm=PTCzIp4uQG8I8rvkqi1NK5VCwV6hRrptEzPMDkx6RPQ-1717279684-1.0.1.1-ZtRRac7JaPfKLCYFoi6HyjbN8Xjyy5eovEmE4.ZaZbFaCqmrWOchL6FxRkji2he4zkcXmJDYJZ810BZqbSqU2G2YHDBxst1Z4WJL30gm8lo',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://www.upwork.com/',
    'sec-ch-ua': '"Brave";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"macOS"',
    'sec-ch-ua-platform-version': '"14.4.1"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'sec-gpc': '1',
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

        block_with_info = soup.find('div', class_='custom-1yuu8tw')
        if block_with_info:
            phrase_element = block_with_info.find("strong", class_="chakra-text custom-0")
            if phrase_element:
                phrase_element = block_with_info.find("strong", class_="chakra-text custom-0").text.strip()
                name_element = block_with_info.find("h3", class_="chakra-heading custom-y5314g").text.strip()
                date_element = block_with_info.find("span", 'chakra-text custom-2ygcmq').text.strip()
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
    file_path = "/Users/timoteusbakker/OptionsCrypto/Communitytakeover/scraped_links.csv"
    update_csv(file_path)
    elapsed_time = time.time() - start_time
    print("Process complete. Exiting...")
    print(f"Total runtime: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()

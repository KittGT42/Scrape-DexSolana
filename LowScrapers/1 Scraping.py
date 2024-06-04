import csv
import time

from bs4 import BeautifulSoup
import requests

cookies = {
    'cf_clearance': 'l_t1xooMmpssfM6WhbW9ZOgjso_Dwia5TJHgS4g53Jo-1717266778-1.0.1.1-nr7PdxFwdVmtDdKKEwFHaDAV1OzUrawAuW7lTulAn1k0tbj7539PXA2DakxZ4ugxKeQgaDve6AP7EcSuScXM_g',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}

def find_and_extract_links(url):
    global cookies, headers
    print("Finding and extracting links...")
    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        soup = BeautifulSoup(response.text, 'lxml')
        elements_of_site = soup.find_all('a', class_='ds-dex-table-row ds-dex-table-row-top')
        if not elements_of_site:
            print("No elements found with specified selector.")
            return []
        print(f"Number of elements found: {len(elements_of_site)}")
    except Exception as e:
        print("An error occurred:", e)
        return []

    matching_hrefs = []
    for element in elements_of_site:
        href = element.get('href')
        if href:
            base_url = "https://dexscreener.com"
            full_url = f"{base_url}{href}" if not href.startswith(base_url) else href
            matching_hrefs.append(full_url)
    return matching_hrefs

def save_to_csv(file_path, urls):
    print(f"Saving {len(urls)} URLs to CSV file: {file_path}")
    existing_urls = set()
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            for row in reader:
                if row:
                    existing_urls.add(row[0])
    except FileNotFoundError:
        print("CSV file not found. Will create a new one.")

    with open(file_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not existing_urls:
            writer.writerow(["Url", "Community Takeover Found", "Name", "TakeoverDate", "Network"])  # Write header only if it's a new file
        for url in urls:
            if url not in existing_urls:
                writer.writerow([url, "", "", "", "Solana"])  # Ensure "Solana" is always in the fifth column
                existing_urls.add(url)

def main():
    global cookies, headers
    print("Script started.")
    base_url = "https://dexscreener.com/solana"
    page_number = 1
    file_path = "../data/scraped_links.csv"
    url = f"{base_url}/page-{page_number}?rankBy=trendingScoreH6&order=desc&minLiq=1000&minMarketCap=15000&maxMarketCap=300000&minAge=18&min24HTxns=2"

    all_links = []
    while True:
        links = find_and_extract_links(url)
        if not links:
            print("No more links found. Ending pagination.")
            break
        all_links.extend(links)
        page_number += 1
        url = f"{base_url}/page-{page_number}?rankBy=trendingScoreH6&order=desc&minLiq=1000&minMarketCap=15000&maxMarketCap=300000&minAge=18&min24HTxns=2"
        print(f"Accessing URL: {url}")
        print("Waiting for the page to load...")
        time.sleep(10)

    save_to_csv(file_path, all_links)
    print("Process complete. Exiting...")

if __name__ == "__main__":
    main()

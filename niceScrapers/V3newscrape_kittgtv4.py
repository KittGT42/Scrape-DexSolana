
import csv
import time

from get_cookes import get_cookes
from bs4 import BeautifulSoup
import requests

cookies_values = get_cookes()

cookies = {
    'cf_clearance': cookies_values['cf_clearance'],
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}


def find_and_extract_links(url):
    global cookies, headers
    print("Finding and extracting links...")
    try:
        links = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        soup = BeautifulSoup(links.text, 'lxml')
        elements_of_site = soup.find_all('a', class_='ds-dex-table-row ds-dex-table-row-top')
        if len(elements_of_site) == 0:
            raise Exception("No links found.")
    except :
        print("Timed out waiting for links to appear on the page.")
        return []

    links = requests.get(url, headers=headers, cookies=cookies, timeout=10)
    soup = BeautifulSoup(links.text, 'lxml')
    if not elements_of_site:
        print("No elements found with specified selector.")
    else:
        print(f"Number of elements found: {len(elements_of_site)}")
        for element in elements_of_site[:5]:  # Print first 5 elements' outer HTML for diagnostic purposes
            print(element['href'])

    matching_hrefs = []
    for element in elements_of_site:
        href = (element['href'])
        print(f"Raw href extracted: {href}")  # Diagnostic print
        if href:
            # Check if href starts with the base URL and remove it
            base_url = "https://dexscreener.com"
            if href.startswith(base_url):
                href = href[len(base_url):]  # Remove the base URL part
            full_url = f"https://dexscreener.com{href}"
            matching_hrefs.append(full_url)
            print(f"Found new link: {full_url}")
    print(f"Total links found: {len(matching_hrefs)}")
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
            writer.writerow(["Url"])  # Write header only if file was not found and it's a new file
        for url in urls:
            if url not in existing_urls:
                writer.writerow([url])
                existing_urls.add(url)  # Update the set of existing URLs
                print(f"New link saved: {url}")


def main():
    global cookies, headers
    print("Script started.")
    base_url = "https://dexscreener.com/solana"
    page_number = 1  # Start from page 1
    file_path = "../data/scraped_links5.csv"

    url = f"{base_url}/page-{page_number}?rankBy=trendingScoreH6&order=desc&minLiq=1000&minMarketCap=30000&maxMarketCap=150000&minAge=168&min24HTxns=5&min24HChg=0.1"

    all_links = []
    while True:
        links = find_and_extract_links(url)
        if not links:
            print("No more links found. Ending pagination.")
            break
        all_links.extend(links)
        page_number += 1  # Increment the page number for the next iteration
        url = f"{base_url}/page-{page_number}?rankBy=trendingScoreH6&order=desc&minLiq=1000&minMarketCap=30000&maxMarketCap=150000&minAge=168&min24HTxns=5&min24HChg=0.1"
        print(f"Accessing URL: {url}")
        print("Waiting for the page to load...")
        time.sleep(10)

    save_to_csv(file_path, all_links)
    print("Process complete. Exiting...")


if __name__ == "__main__":
    main()

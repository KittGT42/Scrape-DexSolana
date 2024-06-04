import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver():
    print("Setting up the driver with window size 1920x1080.")
    options = Options()
    options.add_argument("window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print("Driver setup complete.")
    return driver


def find_and_extract_links(driver):
    print("Finding and extracting links...")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.ds-dex-table-row.ds-dex-table-row-top"))
        )
    except TimeoutException:
        print("Timed out waiting for links to appear on the page.")
        return []

    elements = driver.find_elements(By.CSS_SELECTOR, "a.ds-dex-table-row.ds-dex-table-row-top")
    if not elements:
        print("No elements found with specified selector.")
    else:
        print(f"Number of elements found: {len(elements)}")
        for element in elements[:5]:  # Print first 5 elements' outer HTML for diagnostic purposes
            print(element.get_attribute('outerHTML'))

    matching_hrefs = []
    for element in elements:
        href = element.get_attribute('href')
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
    print("Script started.")
    driver = setup_driver()
    base_url = "https://dexscreener.com/solana"
    page_number = 1  # Start from page 1
    file_path = "/Users/timoteusbakker/OptionsCrypto/Communitytakeover/scraped_links.csv"

    url = f"{base_url}/page-{page_number}?rankBy=trendingScoreH6&order=desc&minLiq=1000&minMarketCap=30000&maxMarketCap=150000&minAge=168&min24HTxns=5&min24HChg=0.1"
    print(f"Accessing URL: {url}")
    driver.execute_script('''window.open("http://dexscreener.com/","_blank");''')  # open page in new tab
    time.sleep(5)  # wait until page has loaded
    driver.switch_to.window(window_name=driver.window_handles[0])  # switch to first tab
    driver.close()  # close first tab
    driver.switch_to.window(window_name=driver.window_handles[0])  # switch back to new tab
    time.sleep(2)
    driver.get("https://google.com")
    time.sleep(2)
    driver.get(url)
    time.sleep(10)  # Wait for manual entry

    all_links = []
    while True:
        links = find_and_extract_links(driver)
        if not links:
            print("No more links found. Ending pagination.")
            break
        all_links.extend(links)
        page_number += 1  # Increment the page number for the next iteration
        url = f"{base_url}/page-{page_number}?rankBy=trendingScoreH6&order=desc&minLiq=1000&minMarketCap=30000&maxMarketCap=150000&minAge=168&min24HTxns=5&min24HChg=0.1"
        print(f"Accessing URL: {url}")
        driver.get(url)
        print("Waiting for the page to load...")
        time.sleep(15)  # Wait for the page to load

    save_to_csv(file_path, all_links)
    print("Process complete. Exiting...")
    driver.quit()


if __name__ == "__main__":
    main()

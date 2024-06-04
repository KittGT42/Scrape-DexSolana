import time

from selenium import webdriver


def get_cookes():
    result_cookies = {}
    base_url = "https://dexscreener.com/solana"
    with webdriver.Chrome() as driver:
        # url = f"{base_url}/page-{page_number}?rankBy=trendingScoreH6&order=desc&minLiq=1000&minMarketCap=30000&maxMarketCap=150000&minAge=168&min24HTxns=5&min24HChg=0.1"
        url = 'base_url = "https://dexscreener.com/solana"'
        print(f"Accessing URL: {url}")
        driver.execute_script('''window.open("http://dexscreener.com/","_blank");''')  # open page in new tab
        time.sleep(5)  # wait until page has loaded
        driver.switch_to.window(window_name=driver.window_handles[0])  # switch to first tab
        driver.close()  # close first tab
        driver.switch_to.window(window_name=driver.window_handles[0])  # switch back to new tab
        cookies_value = driver.get_cookies()
        for cookie in cookies_value:
            result_cookies[cookie['name']] = cookie['value']
    return result_cookies

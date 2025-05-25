from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def custom_scrape(url):
    options = Options()
    options.add_argument('--headless')  # Run in the background
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    finally:
        driver.quit()

    # Get first 20 paragraph texts (adjust if needed)
    paragraphs = soup.find_all('p')
    content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs[:20])
    return content

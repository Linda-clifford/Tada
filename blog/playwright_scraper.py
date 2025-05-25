import requests
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from requests.exceptions import Timeout, HTTPError

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_fixed(5), 
    retry=retry_if_exception_type(Timeout)  # Retry only for timeouts
)
def fetch_content(url):
    """
    Fetches the HTML content from a given URL with retries for timeout errors.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)  # Timeout increased to 30 seconds
        response.raise_for_status()  # Raise exception for HTTP errors (4xx, 5xx)
        return response
    
    except Timeout:
        # Log timeout errors and re-raise for retry
        error_message = f"{datetime.now()} - Timeout error for URL {url}"
        print(error_message)
        with open("scraping_errors.log", "a") as log_file:
            log_file.write(error_message + "\n")
        raise
    
    except HTTPError as e:
        # Log HTTP errors and re-raise
        error_message = f"{datetime.now()} - HTTP error {e.response.status_code} for URL {url}: {e}"
        print(error_message)
        with open("scraping_errors.log", "a") as log_file:
            log_file.write(error_message + "\n")
        raise
    
    except Exception as e:
        # Log other errors and re-raise
        error_message = f"{datetime.now()} - General error for URL {url}: {e}"
        print(error_message)
        with open("scraping_errors.log", "a") as log_file:
            log_file.write(error_message + "\n")
        raise

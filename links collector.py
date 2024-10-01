import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Load cookies from a JSON file
def load_cookies_from_json(file_path):
    with open(file_path, 'r') as file:
        cookies = json.load(file)
    return cookies

# Function to get the last page number
def get_last_page_number(driver):
    try:
        # Wait until the pagination list is loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.artdeco-pagination__pages.artdeco-pagination__pages--number'))
        )

        # Locate the pagination list
        pagination_list = driver.find_element(By.CSS_SELECTOR, 'ul.artdeco-pagination__pages.artdeco-pagination__pages--number')
        
        # Find the last list item in the pagination list
        last_page_item = pagination_list.find_elements(By.TAG_NAME, 'li')[-1]  # Get the last <li>
        
        # Extract the page number from the last list item
        last_page_number = last_page_item.get_attribute('data-test-pagination-page-btn')
        print(f"Detected last page number: {last_page_number}")
        return int(last_page_number)
    except Exception as e:
        print(f"Error retrieving last page number: {e}")
        return 1  # Default to 1 if unable to find pagination

# Function to scrape profiles and save to CSV
def search_linkedin_profiles(keyword, max_pages=0):
    # Replace spaces in the keyword with '%20' for URL encoding
    keyword = keyword.replace(' ', '%20')
    
    # Construct the base LinkedIn search URL
    base_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}"

    # Create a new instance of the Chrome driver
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    # Open LinkedIn homepage first to set up the session
    driver.get('https://www.linkedin.com')

    # Load cookies from the JSON file
    cookies = load_cookies_from_json('cookies.json')

    # Add cookies to the browser session
    for cookie in cookies:
        if 'sameSite' in cookie:
            del cookie['sameSite']  # Remove 'sameSite' if it exists to avoid issues
        driver.add_cookie(cookie)

    # Refresh the page to ensure LinkedIn session is active with cookies
    driver.refresh()

    # Navigate to the LinkedIn search results page for the first time to get the pagination info
    driver.get(base_url)
    time.sleep(5)  # Wait for the page to load

    # Get the last page number
    if max_pages == 0:  # If max_pages is not provided, calculate it dynamically
        max_pages = get_last_page_number(driver)
    print(f"Scraping up to {max_pages} pages")

    # Open the CSV file to save the profile data
    with open('linkedin_profiles.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the CSV header
        writer.writerow(['Sr No', 'Profile URL'])

        serial_number = 1  # Initialize serial number

        # Loop through all pages
        for i in range(1, max_pages + 1):
            # Adjust the search URL for pagination
            paginated_url = base_url + f"&page={i}"
            driver.get(paginated_url)
            time.sleep(5)  # Wait for the page to load

            try:
                # Locate all divs containing the profile links
                profile_divs = driver.find_elements(By.CSS_SELECTOR, 'div.linked-area.flex-1.cursor-pointer')

                # Collect profile URLs
                profiles = []
                for div in profile_divs:
                    # Inside each div, find the anchor tag that contains the profile link
                    link_element = div.find_element(By.TAG_NAME, 'a')
                    profile_url = link_element.get_attribute('href')
                    profiles.append(profile_url)

                # Write the profiles to the CSV file with serial numbers
                for profile_url in profiles:
                    writer.writerow([serial_number, profile_url])
                    print(f"Scraped: {serial_number}. {profile_url}")
                    serial_number += 1

                # Debugging: Print the number of profiles found on the page
                print(f"Found {len(profiles)} profiles on page {i}.")

            except Exception as e:
                print(f"An error occurred while scraping profiles on page {i}: {e}")

            # Stop the loop if there are no more profiles on the next page
            if len(profiles) == 0:
                print(f"No more profiles found on page {i}. Exiting.")
                break

    # Close the browser
    driver.quit()

# Example usage:
search_linkedin_profiles('software engineer')

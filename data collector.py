import json
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Function to load cookies from a JSON file
def load_cookies_from_json(file_path):
    with open(file_path, 'r') as file:
        cookies = json.load(file)
    return cookies

# Function to load LinkedIn profile URLs from a CSV file
def load_profile_urls(csv_file):
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        return [row[1] for row in reader]  # Assuming profile URLs are in the second column

# Function to scrape LinkedIn profile data manually
def scrape_linkedin_profiles(profile_urls, cookies_file):
    # Create a new instance of the Chrome driver
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    # Load LinkedIn homepage to set the session
    driver.get('https://www.linkedin.com')

    # Load cookies from the JSON file
    cookies = load_cookies_from_json(cookies_file)

    # Add cookies to the browser session
    for cookie in cookies:
        if 'sameSite' in cookie:
            del cookie['sameSite']  # Remove 'sameSite' if it exists to avoid issues
        driver.add_cookie(cookie)

    # Refresh the page to ensure LinkedIn session is active with cookies
    driver.refresh()
    time.sleep(5)  # Wait for the refresh to complete

    # Open a CSV file to save the scraped data
    with open('linkedin_profile_data.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Profile URL', 'Name', 'Job Title', 'Location'])  # CSV header

        for profile_url in profile_urls:
            driver.get(profile_url)
            time.sleep(5)  # Wait for the page to load
            
            # Scraping the specified data using the provided selectors
            print(f"\nScraping data from: {profile_url}")
            try:
                # Scrape the data based on provided selectors
                name = driver.find_element("css selector", "h1.text-heading-xlarge.inline.t-24.v-align-middle.break-words").text
                job_title = driver.find_element("css selector", "div.text-body-medium.break-words").text
                location = driver.find_element("css selector", "span.text-body-small.inline.t-black--light.break-words").text
                
                # Write the scraped data to the CSV file
                writer.writerow([profile_url, name, job_title, location])
                
                print(f"Name: {name}")
                print(f"Job Title: {job_title}")
                print(f"Location: {location}")

            except Exception as e:
                print(f"Error scraping data from {profile_url}: {e}")
        
            time.sleep(2)  # Optional: Wait before the next profile

    # Close the browser
    driver.quit()

# Example usage
if __name__ == "__main__":
    profile_urls = load_profile_urls('linkedin_profiles.csv')
    scrape_linkedin_profiles(profile_urls, 'cookies.json')

# thinkbridge_webscraping_solution

This code is a Python script that uses web scraping techniques to extract information from a list of URLs containing product pages on the G2 website. It utilizes the Playwright library for browser automation and BeautifulSoup for HTML parsing. The scraped data is then stored in a JSON file.

# Getting Started
Before running the code, ensure that you have the following dependencies installed:

You can install these dependencies using pip:
  - pip install -r requirements.txt


# Usage
Prepare the input file:

Create a CSV file named g2urls.csv.
Populate the file with a column named url containing the URLs of the product pages on the G2 website that you want to scrape. Each URL should be on a separate row.
- Run the script:
    Open a terminal or command prompt and navigate to the directory where the script is saved.
    Run the following command to execute the script:
        - python scraper.py

The script will start scraping the G2 product pages based on the URLs provided in the g2urls.csv file.

-   View the results:
    Once the scraping process is completed, the script will save the extracted data in a file named companies_data.json in the same directory.
    Open the companies_data.json file to view the scraped data.

# Disclaimer

Code currently only support webscraping for G2.com , products pages of the company
Scraper will scrape company details like : company name, description, website url, rating, review count 

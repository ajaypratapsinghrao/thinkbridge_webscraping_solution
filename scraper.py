import time
import asyncio
import json
import csv
import os
import hashlib
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse
from playwright.async_api import async_playwright

class WebScraper:
    def __init__(self):
        pass

    async def handle_human_verification(self, page, current_hash):
        iframe = await page.wait_for_selector("iframe")
        frame = await iframe.content_frame()
        checkbox_exists = await frame.query_selector('input[type="checkbox"]') is not None
        start_time = time.time()
        while checkbox_exists != True:
            checkbox_exists = await frame.query_selector('input[type="checkbox"]') is not None
            if time.time() - start_time > 60:
                break
        if checkbox_exists:
            checkbox = await frame.wait_for_selector('input[type="checkbox"]')
            await checkbox.check()
            await asyncio.sleep(15)
            print("Checkbox clicked!")
            return True
        else:
            print("Checkbox not found inside the iframe.")
            return True

    def get_page_content(self, page_content):
        html_content = BeautifulSoup(page_content, 'html.parser')
        text_content = html_content.get_text()
        return text_content, html_content

    def scrape_company_name(self, page_html_content):
        product_title_div = page_html_content.find(class_="product-head__title")
        if product_title_div:
            nested_div = product_title_div.find(itemprop="name")
            if nested_div:
                a_tag = nested_div.find('a')
                if a_tag:
                    company_name = a_tag.text
        else:
            company_name = None            
        return company_name

    def scrape_company_description(self, page_html_content):
        nested_div = page_html_content.find(itemprop="description")
        if nested_div:
            p_tag = nested_div.find('p')
            if p_tag:
                company_description = p_tag.text
        else:
            company_description = None        
        return company_description

    def scrape_company_website_url(self, page_html_content):
        div_tag = page_html_content.find('div', string='Website')
        if div_tag:
            parent_div = div_tag.find_parent('div')
            if parent_div:
                a_tag = parent_div.find('a', itemprop='url')
                company_website_url = a_tag.get('href')
        else:
            company_website_url = None        
        return company_website_url

    def scrape_company_review_count(self, page_html_content):
        h3_tag = page_html_content.find('h3', class_='l2 mb-half')
        if h3_tag:
            company_review_count = h3_tag.get_text(strip=True)
        else:
            company_review_count = None    
        return company_review_count

    def scrape_company_rating(self, page_html_content):
        span_tag = page_html_content.find('span', class_='c-midnight-90 pl-4th')
        if span_tag:
            company_rating = span_tag.get_text(strip=True)
        else:
            company_rating = None    
        return company_rating
    

    async def scrape_all_company_details(self, url):
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            try:                
                await page.goto(url)
                await page.wait_for_load_state("load")
                await asyncio.sleep(15)
                content = await page.content()
                current_hash = hashlib.sha224(content.encode()).hexdigest()
                page_text_content, page_html_content = self.get_page_content(content)

                if "Checking if the site connection is secure" in page_text_content:
                    await self.handle_human_verification(page, current_hash)
                    content = await page.content()
                    page_text_content, page_html_content = self.get_page_content(content)

                company_name = self.scrape_company_name(page_html_content)
                company_description = self.scrape_company_description(page_html_content)
                company_website_url = self.scrape_company_website_url(page_html_content)
                company_review_count = self.scrape_company_review_count(page_html_content)
                company_rating = self.scrape_company_rating(page_html_content)

                company_details = {
                    'url': url,
                    'company_name': company_name,
                    'company_description': company_description,
                    'company_website_url': company_website_url,
                    'review_count': company_review_count,
                    'company_rating': company_rating
                }

                return company_details

            except Exception as e:
                print(f"An error occurred while scraping {url}: {str(e)}")
                company_details = {
                    'url': url,
                    'company_details': None,
                }
                return company_details

            finally:
                await browser.close()

    async def main(self):
        filename = "g2urls.csv"
        file_in_path = os.path.join(os.getcwd(), filename)

        df = pd.read_csv(file_in_path)
        url_list = df["url"].tolist()

        results = []
        tasks = []

        for url in url_list:
            parsed_url = urlparse(url)
            if "/products" in parsed_url.path:
                task = asyncio.ensure_future(self.scrape_all_company_details(url))
                tasks.append(task)
            else:
                print("Web scraping supported for product page only")
                continue    

        results = await asyncio.gather(*tasks)

        file_path = "companies_data.json"
        file_exists = os.path.isfile(file_path)

        with open(file_path, "w") as file:
            result_json = {}
            json_content = results
            result_json["companies"] = json_content
            json.dump(result_json, file, indent=4)

        print("Scraping completed. Results saved in 'companies_data.json'")


web_scraper = WebScraper()
asyncio.run(web_scraper.main())

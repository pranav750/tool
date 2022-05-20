# Importing the required libraries
import os

# For getting the time for crawling 
from datetime import datetime

# Importing queue for DFS algorithm
from queue import Queue
from urllib.parse import urljoin

# For scraping the dark web page 
from bs4 import BeautifulSoup
from matplotlib.pyplot import pause
import requests

# Import for google crawl
from googlesearch.googlesearch import GoogleSearch

# Import from selenium web driver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

# Import from utils/functions.py
from utils.functions import time_difference, output

# Import from utils/save.py
from utils.save import backup

# Import from utils/tree.py
from utils.tree import link_tree_formation

# Import from utils/wordcloud.py
from utils.wordcloud import create_wordcloud

# Chromedriver path
CHROMEDRIVER_PATH = os.path.join(os.path.dirname( __file__ ), '..', '..', 'static', 'chromedriver', 'chromedriver.exe')

class GoogleCrawler:
    def __init__(self, keyword, depth):
        
        # base keyword
        self.keyword = keyword
        
        # base url
        self.base_url = "https://google.com/search?q={}".format('+'.join(self.keyword.split(' ')))
        
        #depth
        self.depth = depth
        
        # global queue
        self.queue = Queue()
        self.queue.put({ 'url': self.base_url, 'parent_link': '' })
        
        # visited links
        self.have_visited = set()
        self.have_visited.add(self.base_url)
        
        # for database
        self.crawled_links = []
        self.active_links = 0
        self.inactive_links = 0
        
    # Get all links from google          
    def get_all_links(self):

        response = GoogleSearch().search("cbhjc", num_results = 10)
        print(response)
        # links_found_on_google = list(search(self.keyword, num_results = 1, pause = 10))
        # print(links_found_on_google)
        
        # for link in links_found_on_google:
        #     if link not in self.have_visited:
        #         self.queue.put({ 'url': link, 'parent_link': self.base_url })
        #         self.have_visited.add(link)
                
    # Make a request to the dark web 
    def make_request(self, url):
        try:
            output("Crawling...", True)

            # Request to the Surface Web URL 
            response = requests.get(url)

            # Print that the link is found and return the response and that link is active
            output("Page found.... " + url, False)     
            return True, response
        except:
            # Print that the link is not found and return the response and that link is not active
            output("Page not found... " + url, False)
            return False, None

    def crawl(self):

        # Start time of the crawling
        start_time = datetime.now()
            
        # Get all links from google
        self.get_all_links()
        
        # Selenium webdriver
        driver = webdriver.Chrome(CHROMEDRIVER_PATH)
        
        while not self.queue.empty():

            # Darkweb database model has a list of crawled links
            # We will create a Link object and push it in crawled_links
            database_link_object = dict()

            # Current object in queue
            current_link_object = self.queue.get()
            current_link = current_link_object['url']
            parent_link = current_link_object['parent_link']

            # Make request to the current link 
            link_active, link_response = self.make_request(current_link)

            if link_active:

                self.active_links += 1

                soup = BeautifulSoup(link_response.text, 'lxml')
                
                driver.get(current_link)

                # Add images in database
                # image_links = self.get_all_image_links(soup, current_link)           

                # if len(image_links) > 0:
                #     self.store_images(image_links)
                # else:
                #     print("No Images Found...")

                # Create Link object to put in Database 
                    
                try:
                    database_link_object['title'] = soup.find('title').get_text()
                except:
                    database_link_object['title'] = ''
                        
                database_link_object['link_status'] = link_active
                database_link_object['link'] = current_link
                database_link_object['parent_link'] = parent_link
                    
                try:
                    database_link_object['text'] = soup.get_text(" ")
                except:
                    database_link_object['text'] = ''

                database_link_object['html'] = link_response.text
                    
            else:

                self.inactive_links += 1

                    # Create Link object to put in Database
                database_link_object['title'] = ''
                database_link_object['link_status'] = link_active
                database_link_object['link'] = current_link
                database_link_object['parent_link'] = parent_link
                database_link_object['text'] = ''
                database_link_object['html'] = ''

            self.crawled_links.append(database_link_object)
            
        driver.quit()

        # End time of crawling
        end_time = datetime.now()

        # Create word cloud
        top_five_keywords = create_wordcloud(self.crawled_links)
        
        # Create link tree
        link_tree_formation(self.crawled_links)
        
        #Create final result
        result = {
            'link': self.base_url,
            'active_links': self.active_links,
            'inactive_links': self.inactive_links,
            'top_five_keywords': top_five_keywords,
            'time_taken': time_difference(start_time, end_time),
            'crawled_links': self.crawled_links
        }
        
        return result
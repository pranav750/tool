# Importing the required libraries
import os

# For getting the time for crawling 
import time
from datetime import datetime

# Import for random selection in array
import random

# For changing Tor IP address by creating a new relay circuit
from stem import Signal
from stem.control import Controller

# Importing queue for DFS algorithm
from queue import Queue
from urllib.parse import urljoin

# For scraping the dark web page 
from bs4 import BeautifulSoup
import requests

# Import from utils/functions.py
from utils.functions import output, time_difference, create_directory_for_images

# Import from utils/save.py
from utils.save import backup

# Import from utils/tree.py
from utils.tree import link_tree_formation

# Import from utils/wordcloud.py
from utils.wordcloud import create_wordcloud

# For accessing the values from the .env file
from dotenv import dotenv_values

config = dotenv_values(".env")
TORCC_HASH_PASSWORD = config['TORCC_HASH_PASSWORD']
TOR_BROWSER_PATH = config['TOR_BROWSER_PATH']

class DFSDarkWebCrawler:
    def __init__(self, base_url, depth):

        # add time delay between each request to avoid DOS attack
        self.wait_time = 1
        
        # socks proxies required for TOR usage
        self.proxies = {
            'http' : 'socks5h://127.0.0.1:9150', 
            'https' : 'socks5h://127.0.0.1:9150'
        }

        # start time
        self.start_time = datetime.now()
        
        # base url
        self.base_url = base_url
        if self.base_url[-1] == '/':
            self.base_url = self.base_url[:len(self.base_url) - 1]
        
        #depth
        self.depth = depth
        
        # visited links
        self.have_visited = set()
        
        # for database
        self.crawled_links = []
        self.active_links = 0
        self.inactive_links = 0

    # Get the current IP address to check whether the IP address of tor changed or not.
    def get_current_ip(self):
        try:
            response = requests.get('http://httpbin.org/ip', proxies = self.proxies)
            return response.text.split(",")[-1].split('"')[3]
        except Exception as e:
            return str(e)

    # After each request, change the tor IP address
    def renew_tor_ip(self):
        with Controller.from_port(port = 9051) as controller:
            controller.authenticate(password = TORCC_HASH_PASSWORD)
            controller.signal(Signal.NEWNYM)

    # Store images in the folder 
    def store_images(self, image_links):
        
        # Create a directory to store images for given link
        create_directory_for_images(self.active_links + self.inactive_links)
        
        # Folder path of the above created directory
        folder_name = os.path.join(os.path.dirname( __file__ ), '..', 'static', 'images', str(self.active_links + self.inactive_links))

        i = 0
        output("Images crawling...", True)
        
        # Store the images in the created folder
        for image_link in image_links:
            try:
                image_link_status, image_response = self.make_request(image_link)
                if image_link_status:
                    with open(f"{folder_name}/images{i+1}.jpg", "wb+") as f:
                        f.write(image_response.content)  
                    i += 1
            except Exception as e:
                print(str(e))
                
        output("Images crawling done", False)

    # Make a request to the dark web 
    def make_request(self, url):
        try:
            # Before making the request, renew the Tor IP address
            self.renew_tor_ip()                
            time.sleep(self.wait_time)
            current_ip = self.get_current_ip()
                
            # Print current IP address
            output("IP : {}".format(current_ip), True)

            # Request to the Dark Web URL using a random user agent
            headers = { 'User-Agent': self.GET_UA() }
            response = requests.get(url, proxies = self.proxies, headers = headers, timeout = 20)

            # Print that the link is found and return the response and that link is active
            output("Page found.... " + url, False)     
            return True, response
        except:
            # Print that the link is not found and return the response and that link is not active
            output("Page not found... " + url, False)
            return False, None

    # Random User Agent
    def GET_UA(self):
        uastrings = ["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",
                "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
                "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36"
                ]
 
        return random.choice(uastrings)
    
    # Get all images from the soup object
    def get_all_image_links(self, soup, current_link):
        image_links = []
        for image_tag in soup.find_all('img', src = True):
            src_text = image_tag['src']
            if not src_text.startswith('http'):
                image_links.append(urljoin(current_link, src_text))
            else:
                image_links.append(src_text)
        return image_links
                
    # Get all links from the soup object           
    def get_all_links(self, soup, current_link):
        
        # Links from this current link
        links = []
        
        for anchor_tag in soup.find_all('a', href = True):
            link_in_anchor_tag = anchor_tag['href']

            if link_in_anchor_tag == '/' or link_in_anchor_tag.startswith('/index') or link_in_anchor_tag == 'index':
                continue
            
            if not link_in_anchor_tag.startswith('http'):
                link_in_anchor_tag = urljoin(current_link, link_in_anchor_tag)

            if link_in_anchor_tag not in self.have_visited:
                links.append(link_in_anchor_tag)
                
        return links

    # DFS call
    def dfs(self, current_link, parent_link, depth):

        # Backup the data at every 1000 links data
        if len(self.crawled_links) % 1000 == 0 and len(self.crawled_links) > 0:

            # Create final result
            result = {
                'link': self.base_url,
                'active_links': self.active_links,
                'inactive_links': self.inactive_links,
                'time_taken': time_difference(self.start_time, datetime.now()),
                'crawled_links': self.crawled_links
            }

            backup(result)
        
        # Reduce the depth
        depth = depth - 1
        
        # Darkweb database model has a list of crawled links
        # We will create a Link object and push it in crawled_links
        database_link_object = dict()

        # Make request to the current link 
        link_active, link_response = self.make_request(current_link)
        
        if link_active:

            soup = BeautifulSoup(link_response.text, 'lxml')

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

            if current_link not in self.have_visited:
                self.active_links += 1
                self.crawled_links.append(database_link_object)

                # Mark this link as visited
                self.have_visited.add(current_link)

            if depth > 0:
                links_from_current_link = self.get_all_links(soup, current_link)
                
                for link in links_from_current_link:
                    self.dfs(link, current_link, depth)
                
        else:

            # Create Link object to put in Database
            database_link_object['title'] = ''
            database_link_object['link_status'] = link_active
            database_link_object['link'] = current_link
            database_link_object['parent_link'] = parent_link
            database_link_object['text'] = ''
            database_link_object['html'] = ''

            if current_link not in self.have_visited:
                self.inactive_links += 1
                self.crawled_links.append(database_link_object)

                # Mark this link as visited
                self.have_visited.add(current_link)

    # Main crawl
    def crawl(self):
        
        # Start time of the crawling
        self.start_time = datetime.now()
        
        # DFS call
        self.dfs(self.base_url, '', self.depth)
        
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
            'time_taken': time_difference(self.start_time, end_time),
            'crawled_links': self.crawled_links
        }
        
        return result
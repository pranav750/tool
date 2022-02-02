# Import for getting the time for crawling 
import time
from datetime import datetime

# Import for random selection in array
import random

# Import for changing Tor IP address
from stem import Signal
from stem.control import Controller

# Import for creating and opening folders and files
import os

# Import for crawling
from queue import Queue, Empty
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import requests
from lxml import html

# Imports for multithreading crawling
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from threading import current_thread

# Import from utils/functions.py
from utils.functions import time_difference, create_wordcloud, links_from_result, clear_images_directory, create_directory_for_images, link_tree_formation, open_tor_browser

# Import .env variables
from dotenv import dotenv_values
config = dotenv_values(".env")

# Add constants
TORCC_HASH_PASSWORD = config['TORCC_HASH_PASSWORD']
TOR_BROWSER_PATH = config['TOR_BROWSER_PATH']

class DarkWebCrawler:
    def __init__(self, base_url, depth):

        # add time delay between each request to avoid DOS attack
        self.wait_time = 1
        
        # socks proxies required for TOR usage
        self.proxies = {
            'http' : 'socks5h://127.0.0.1:9150', 
            'https' : 'socks5h://127.0.0.1:9150'
        }
        
        # base url
        self.base_url = base_url
        if self.base_url[-1] == '/':
            self.base_url = self.base_url[:len(self.base_url) - 1]
        
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
        print("Images crawling...")
        
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
                
        print("Images crawling done")

    # Make a request to the dark web 
    def make_request(self, url):
        try:
            # Before making the request, renew the Tor IP address
            self.renew_tor_ip()                
            time.sleep(self.wait_time)
            current_ip = self.get_current_ip()
                
            # Print current IP address
            print("IP : {}".format(current_ip))

            # Request to the Dark Web URL using a random user agent
            headers = { 'User-Agent': self.GET_UA() }
            response = requests.get(url, proxies = self.proxies, headers = headers, timeout = 20)

            # Print that the link is found and return the response and that link is active
            print("Page found.... " + url)     
            return True, response
        except:
            # Print that the link is not found and return the response and that link is not active
            print("Page not found... " + url)
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
        # Links added into queue from this soup object
        links_added = 0
        
        for anchor_tag in soup.find_all('a', href = True):
            link_in_anchor_tag = anchor_tag['href']

            if link_in_anchor_tag == '/' or link_in_anchor_tag.startswith('/index') or link_in_anchor_tag == 'index':
                continue
            
            if not link_in_anchor_tag.startswith('http'):
                link_in_anchor_tag = urljoin(current_link, link_in_anchor_tag)

            if link_in_anchor_tag not in self.have_visited:
                self.queue.put({ 'url': link_in_anchor_tag, 'parent_link': current_link }) 
                self.have_visited.add(link_in_anchor_tag)
                links_added += 1

    def new_crawling(self):

        # Clear the images directory to store new images
        clear_images_directory()

        # Start time of the crawling
        start_time = datetime.now()

        depth = self.depth
        while not self.queue.empty() and depth > 0:

            # All the links currently in the queue
            size = self.queue.qsize()

            for _ in range(size):

                print('--------------')

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

                    self.get_all_links(soup, current_link)
                    
                else:

                    self.inactive_links += 1

                    # Create Link object to put in Database
                    database_link_object['title'] = ''
                    database_link_object['link_status'] = link_active
                    database_link_object['link'] = current_link
                    database_link_object['parent_link'] = parent_link
                    database_link_object['text'] = ''

                self.crawled_links.append(database_link_object)
                print('--------------')

            depth -= 1

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



class MultiThreaded():
    def __init__(self, base_url, depth):
        
        # socks proxies required for TOR usage
        self.proxies = {
            'http' : 'socks5h://127.0.0.1:9150', 
            'https' : 'socks5h://127.0.0.1:9150'
        }
        
        # base url
        self.base_url = base_url
        if self.base_url[-1] == '/':
            self.base_url = self.base_url[:len(self.base_url) - 1]
        
        #depth
        self.depth = depth
        
        # global queue
        self.queue = Queue()
        self.queue.put({ 'url': self.base_url, 'parent_link': '', 'depth': self.depth })
        
        # visited links
        self.have_visited = set()
        self.have_visited.add(self.base_url)

        # for database
        self.crawled_links = []
        self.active_links = 0
        self.inactive_links = 0
        
        # Thread pool
        self.pool = ThreadPoolExecutor(max_workers = 20)
        
    # After each request, change the tor IP address
    def renew_tor_ip(self):
        with Controller.from_port(port = 9051) as controller:
            controller.authenticate(password = TORCC_HASH_PASSWORD)
            controller.signal(Signal.NEWNYM)

    # Get the current IP address to check whether the IP address of tor changed or not.
    def get_current_ip(self):
        try:
            response = requests.get('http://httpbin.org/ip', proxies = self.proxies)
            return response.text.split(",")[-1].split('"')[3]
        except Exception as e:
            return str(e)
        
    # Get all links from the soup object           
    def get_all_links(self, soup, current_link, depth):
        # Links added into queue from this soup object
        links_added = 0
        
        for anchor_tag in soup.find_all('a', href = True):
            link_in_anchor_tag = anchor_tag['href']

            if link_in_anchor_tag == '/' or link_in_anchor_tag.startswith('/index') or link_in_anchor_tag == 'index':
                continue
            
            if not link_in_anchor_tag.startswith('http'):
                link_in_anchor_tag = urljoin(current_link, link_in_anchor_tag)

            if link_in_anchor_tag not in self.have_visited:
                self.queue.put({ 'url': link_in_anchor_tag, 'parent_link': current_link, 'depth': depth - 1 }) 
                self.have_visited.add(link_in_anchor_tag)
                links_added += 1
        
    # Scrape the data and the links from the html page
    def get_data(self, html, depth, current_link, parent_link):

        # Creating soup object
        soup = BeautifulSoup(html, 'lxml')

        # Scrape info from the current link
        self.scrape_info(True, soup, current_link, parent_link)
        
        # Put all links from soup object into queue
        self.get_all_links(soup, current_link, depth)
 
    # Scrape info from the current link and put into database
    def scrape_info(self, is_active, soup, current_link, parent_link):
        
        # We will create a Link object and push it in crawled_links
        database_link_object = dict()
        
        if is_active:
            
            self.active_links += 1
            
            try:
                database_link_object['title'] = soup.find('title').get_text()
            except:
                database_link_object['title'] = ''
                
            database_link_object['link_status'] = True
            database_link_object['link'] = current_link
            database_link_object['parent_link'] = parent_link
            
            try:
                database_link_object['text'] = soup.get_text(" ")
            except:
                database_link_object['text'] = ''
            
        else:
            self.inactive_links += 1

            # Create not found object to put in Database
            database_link_object['title'] = ''
            database_link_object['link_status'] = False
            database_link_object['link'] = current_link
            database_link_object['parent_link'] = parent_link
            database_link_object['text'] = ''
            
        self.crawled_links.append(database_link_object)

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
 
    # Callback funtion after the job is done
    def post_scrape_callback(self, res):
        
        # Result
        result_from_callback = res.result()
        
        # Extracting parameters from result
        result = result_from_callback['result']
        depth = result_from_callback['depth']
        current_link = result_from_callback['current_link']
        parent_link = result_from_callback['parent_link']
        
        # If result is not none that means we made the request successfully
        if result != None:
            print('Found Current Link ' + current_link)
            
            # Scrape the data and the links from the html page
            self.get_data(result, depth, current_link, parent_link)
            
        else:
            print('Not Found Current Link ' + current_link)
            
            # Create a not found object and put it in database
            self.scrape_info(False, None, current_link, parent_link)

    # Scrape the url and return the result
    def scrape_page(self, current_link, parent_link, headers, depth):
        try:
            # Make request to the url
            res = requests.get(current_link, proxies = self.proxies, headers = headers, timeout = 40)
                 
            # If request successful, return this dictionary as result to the callback funtion      
            return { 
                'result': res.text, 
                'current_link': current_link, 
                'parent_link': parent_link, 
                'depth': depth 
            }
        except:
            
            # If request is not successful, return this dictionary as result to the callback funtion 
            return { 
                'result': None, 
                'current_link': current_link, 
                'parent_link': parent_link, 
                'depth': depth 
            }
        
    def run_scraper(self):

        # Start time of the crawling
        start_time = datetime.now()

        while True:
            try:
                
                # First link from queue
                link_info = self.queue.get(timeout = 60)
                current_link = link_info['url']
                parent_link = link_info['parent_link']
                depth = link_info['depth']
                
                if depth > 0:
                                        
                    # Renew Tor IP before making request
                    self.renew_tor_ip()
                    
                    # Create header for requesting to url
                    headers = {'User-Agent': self.GET_UA()}
                    print("Scraping URL: {} with User-Agent {} with depth {}".format(current_link, headers['User-Agent'], depth))
                    
                    # Submit the request to the given link in the pool
                    job = self.pool.submit(self.scrape_page, current_link, parent_link, headers, depth)
                    
                    # After the job is done, make this callback function
                    job.add_done_callback(self.post_scrape_callback)
                    
            except Empty:
                break
            except Exception as e:
                print(e)
                continue
        
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




def link_similarity(links,depth):

        crawled_links_of_url = dict()
        # Start Tor Browser
        os.startfile(config['TOR_BROWSER_PATH'])
        time.sleep(10)
        print("Tor Browser started")
        
        for link in links:
            dark_web_object =  DarkWebCrawler(link, depth)
            result = dark_web_object.new_crawling()
            crawled_links = links_from_result(result)
            crawled_links_of_url[link] = crawled_links

        result = dict()
        all_links = []

        for crawled_links in crawled_links_of_url.values():
            for crawled_link in crawled_links:
                all_links.append(crawled_link)

        for link in all_links:
            count = 0
            result_object = dict()
            for url, links in crawled_links_of_url.items():
                if link in links:
                    count += 1
                    result_object[url] = True
                else:
                    result_object[url] = False
            percent = round(count/len(crawled_links_of_url) * 100,2)
            result_object['percent'] = percent
            result[link] = result_object

        return result

import requests
import random
from lxml import html

import time
from datetime import date, datetime
from stem import Signal
from stem.control import Controller
from bs4 import BeautifulSoup
import os

from queue import Queue, Empty
from bs4 import BeautifulSoup
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from threading import current_thread
from urllib.parse import urlparse, urljoin
from fake_useragent import UserAgent
from stem.control import Controller
from stem import Signal
import requests
import time
import os
import random

from queue import Queue
from dotenv import load_dotenv

# Add constants
TORCC_HASH_PASSWORD = "shashank"
TOR_BROWSER_PATH = "C:\\Users\\SHASHANK\\Desktop\\Tor_Browser\\Browser\\firefox.exe"

class DarkWebCrawler:
    def __init__(self):

        # add time delay between each request to avoid DOS attack
        self.wait_time = 1
        
        # socks proxies required for TOR usage
        self.proxies = {
            'http' : 'socks5h://127.0.0.1:9050', 
            'https' : 'socks5h://127.0.0.1:9050'
        }

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

    # Store images in the database 
    # def store_images(self, image_links, current_link):
    #     print("Images crawling")
    #     for image_link in image_links:
    #         try:
    #             image_link_status, image_response = self.make_request(image_link)
    #             image_object = DarkwebImage(link = current_link)
    #             image_object.image.put(image_response.content, content_type = 'image/png')
    #             image_object.save()
    #         except:
    #             pass
    #     print("Images crawling done")

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
            # ua = UserAgent()
            # user_agent = ua.random
            headers = { 'User-Agent': self.GET_UA() }
            response = requests.get(url, proxies = self.proxies, headers = headers, timeout = 15)

            # Print that the link is found and return the response and that link is active
            print("Page found.... " + url)     
            return True, response
        except:
            # Print that the link is not found and return the response and that link is not active
            print("Page not found... " + url)
            return False, None

    
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

    def new_crawling(self, url, depth):
        # Start Tor Browser
        os.startfile(TOR_BROWSER_PATH)
        time.sleep(10)
        print("Tor Browser started")

        # Queue for Breadth First Crawling
        queue = Queue()
        queue.put({ 'url': url, 'parent_link': '' })        
        crawled_links = []      # For database
        links_crawled_till_now = set()

        active_links = 0
        inactive_links = 0

        while not queue.empty() and depth > 0:

            # All the links currently in the queue
            size = queue.qsize()

            for _ in range(size):

                print('--------------')

                # Darkweb database model has a list of crawled links
                # We will create a Link object and push it in crawled_links
                database_link_object = dict()

                # Current object in queue
                current_link_object = queue.get()
                current_link = current_link_object['url']
                parent_link = current_link_object['parent_link']


                links_crawled_till_now.add(current_link)

                # Make request to the current link 
                link_active, link_response = self.make_request(current_link)

                if link_active:

                    active_links += 1

                    soup = BeautifulSoup(link_response.text, 'lxml')

                    # Add images in database
                    image_links = []

                    # Base url should be https://www.example.com
                    base_url = current_link
                    if (current_link[-1] == '/'):
                        base_url = current_link[:len(current_link) - 1]

                    for image_tag in soup.find_all('img'):
                        src_text = image_tag['src']

                        if len(src_text) >= 3 and src_text[0:3] == '../':
                            continue

                        if src_text[0] == '/':
                            image_links.append(base_url + src_text)
                        else:
                            image_links.append(base_url + '/' + src_text)                   

                    # self.store_images(image_links,current_link)

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

                    links_added = 0
                    for anchor_tag in soup.find_all('a'):
                        try:
                            link_in_anchor_tag = anchor_tag['href']

                            if link_in_anchor_tag != '' and link_in_anchor_tag != '/' and link_in_anchor_tag not in links_crawled_till_now and links_added < 100:
                                if link_in_anchor_tag.startswith('http'):
                                    queue.put({ 'url': link_in_anchor_tag, 'parent_link': current_link }) 
                                    links_added += 1
                                else:
                                    base_url = current_link
                                    if base_url[-1]=='/':
                                        base_url = current_link[:len(current_link)-1]
                                    if link_in_anchor_tag[0]=='/':
                                        link_in_anchor_tag = link_in_anchor_tag[1:]
                                    queue.put({ 'url': base_url + '/' + link_in_anchor_tag, 'parent_link': current_link }) 
                                    links_added += 1
                        except:
                            pass
                else:

                    inactive_links += 1

                    # Create Link object to put in Database
                    database_link_object['title'] = ''
                    database_link_object['link_status'] = link_active
                    database_link_object['link'] = current_link
                    database_link_object['parent_link'] = ''
                    database_link_object['text'] = ''

                crawled_links.append(database_link_object)
                print('--------------')

            depth -= 1

        return active_links, inactive_links, crawled_links


    # def is_link_alive(self,links):
    #     os.startfile(TOR_BROWSER_PATH)
    #     time.sleep(10)
    #     print("Tor Browser started")

    #     results = []

    #     for link in links:
    #         link_active, link_response = self.make_request(link)

    #         inc_active_value = 0 
    #         inc_inactive_value = 0
    #         if link_active:
    #             inc_active_value = 1
    #         else:
    #             inc_inactive_value = 1
            
    #         if len(FlaggedLink.objects(link = link)) > 0:
    #             FlaggedLink.objects(link = link).update_one(
    #                 push__link_statuses = {'link_status' : link_active, 'checked_at' : datetime.now()},
    #                 inc__no_of_times_active = inc_active_value ,
    #                 inc__no_of_times_inactive = inc_inactive_value ,                    
    #                 )

    #         else:
    #             result = {
    #                 'link' : link ,
    #                 'no_of_times_active' : inc_active_value,
    #                 'no_of_times_inactive' : inc_inactive_value,
    #                 'link_statuses': [{
    #                     'link_status' : link_active,
    #                     'checked_at' : datetime.now()
    #                 }]
    #             }
    #             print(result)
    #             serializer = FlaggedLinkSerializer(data = result, many = False)    

    #             if serializer.is_valid():
    #                 serializer.save()
    #             else:
    #                 print(serializer.errors)
            
    #         try:
    #             results.append(FlaggedLink.objects(link = link).first())
    #         except:
    #             pass
        
    #     return results

class Multi():
    def __init__(self, base_url):

        self.base_url = base_url
        self.root_url = '{}://{}'.format(urlparse(self.base_url).scheme, urlparse(self.base_url).netloc)
        self.links_to_crawl = Queue()
        self.links_to_crawl.put((self.base_url, 2))
        self.have_visited = set()
        self.error_links = set()
        self.url_lock = Lock()
        self.pool = ThreadPoolExecutor(max_workers=20)
        self.proxies = {'http' : 'socks5h://127.0.0.1:9150', 'https' : 'socks5h://127.0.0.1:9150'}
        
        
    def renew_tor_ip(self):
        with Controller.from_port(port = 9051) as controller:
            controller.authenticate(password=TOR_PASSWORD)
            controller.signal(Signal.NEWNYM)

    def get_current_ip(self):
        try:
            r = requests.get('http://httpbin.org/ip', proxies = self.proxies)
        except Exception as e:
            print (str(e))
        else:
            return r.text.split(",")[-1].split('"')[3]

    def parse_links(self, html, depth):
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', href=True)
        print(links)
        for anchor_tag in soup.find_all('a'):
            try:
                link_in_anchor_tag = anchor_tag['href']

                if link_in_anchor_tag != '' and link_in_anchor_tag != '/' and link_in_anchor_tag not in self.have_visited:
                    if link_in_anchor_tag.startswith('http'):
                        self.links_to_crawl.put((link_in_anchor_tag, depth-1))
                    else:
                        current_link = self.base_url
                        base_url = current_link
                        if base_url[-1]=='/':
                            base_url = current_link[:len(current_link)-1]
                        if link_in_anchor_tag[0]=='/':
                            link_in_anchor_tag = link_in_anchor_tag[1:]
                        self.links_to_crawl.put((link_in_anchor_tag, depth-1))
            except:
                pass

        # for link in links:
        #     url = link['href']
        #     if url.startswith('/') or url.startswith(self.root_url):
        #         url = urljoin(self.root_url, url)
        #         if url not in self.have_visited:
        #             self.links_to_crawl.put((url, depth-1))
        #     elif url.startswith('http'):
        #         if url not in self.have_visited:
        #             self.links_to_crawl.put((url, depth-1))

 
    def scrape_info(self, html):
        return

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
 
    def post_scrape_callback(self, res):
        result_from_callback = res.result()
        result = result_from_callback[0]
        depth = result_from_callback[1]
        print(result)
        
        if result and result.status_code == 200:
            self.parse_links(result.text, depth)
            self.scrape_info(result.text)
 
    def scrape_page(self, url, headers, depth):
        try:
            self.renew_tor_ip()
            res = requests.get(url, proxies = self.proxies, headers = headers)  
            print(res)         
            return (res, depth)
        except requests.RequestException:
            return
        
    def run_scraper(self):
        os.startfile(TOR_BROWSER_PATH)
        time.sleep(10)
        print("Tor Browser started")
        while True:
            try:
                
                link_info = self.links_to_crawl.get(timeout=30)
                target_link = link_info[0]
                depth = link_info[1]
                
                if depth > 0 and target_link not in self.have_visited:
                    self.have_visited.add(target_link)
                    self.renew_tor_ip()
                    headers = {'User-Agent': self.GET_UA()}
                    print("Scraping URL: {} with User-Agent {} with depth {}".format(target_link, headers['User-Agent'], depth))
                    job = self.pool.submit(self.scrape_page, target_link, headers, depth)
                    job.add_done_callback(self.post_scrape_callback)
                    
                    
            except Empty:
                break
            except Exception as e:
                print(e)
                continue
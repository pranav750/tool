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
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from threading import current_thread
from urllib.parse import urlparse, urljoin
from PIL import Image
from io import BytesIO

from utils.functions import time_difference, create_wordcloud, links_from_result, clear_images_directory, create_directory_for_images, link_tree_formation
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
    def store_images(self, image_links, current_link):
        create_directory_for_images(self.active_links+self.inactive_links)
        folder_name = os.path.join(os.path.dirname( __file__ ), '..', 'static', 'images', str(self.active_links+self.inactive_links))
        print(folder_name)
        i=0
        print("Images crawling")
        for image_link in image_links:
            try:
                image_link_status, image_response = self.make_request(image_link)
                if image_link_status:
                    with open(f"{folder_name}/images{i+1}.{image_link.split('.')[-1]}", "wb+") as f:
                        f.write(image_response.content)  
                    i+=1
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

    def new_crawling(self):

        clear_images_directory()

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
                    image_links = []

                    # Base url should be https://www.example.com
                    # base_url = current_link
                    # if (current_link[-1] == '/'):
                    #     base_url = current_link[:len(current_link) - 1]

                    for image_tag in soup.find_all('img'):
                        src_text = image_tag['src']
                        if not src_text.startswith('http'):
                            image_links.append(urljoin(current_link,src_text))
                        else:
                            image_links.append(src_text)

                    #     if len(src_text) >= 3 and src_text[0:3] == '../':
                    #         continue

                    #     if src_text[0] == '/':
                    #         image_links.append(base_url + src_text)
                    #     else:
                    #         image_links.append(base_url + '/' + src_text)                   

                    self.store_images(image_links,current_link)

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
                    for anchor_tag in soup.find_all('a', href=True):
                        link_in_anchor_tag = anchor_tag['href']
                        

                        if link_in_anchor_tag != '' and link_in_anchor_tag != '/' and link_in_anchor_tag not in self.have_visited and links_added < 100 and link_in_anchor_tag != self.base_url:
                            if link_in_anchor_tag.startswith('http'):
                                self.queue.put({ 'url': link_in_anchor_tag, 'parent_link': current_link }) 
                                links_added += 1
                                self.have_visited.add(link_in_anchor_tag)
                            else:
                                if link_in_anchor_tag[0]=='/':
                                    link_in_anchor_tag = link_in_anchor_tag[1:]
                                    
                                link = self.base_url + '/' + link_in_anchor_tag
                                if link not in self.have_visited:
                                    self.queue.put({ 'url': link, 'parent_link': current_link }) 
                                    links_added += 1
                                    self.have_visited.add(link)

                                                

                else:

                    self.inactive_links += 1

                    # Create Link object to put in Database
                    database_link_object['title'] = ''
                    database_link_object['link_status'] = link_active
                    database_link_object['link'] = current_link
                    database_link_object['parent_link'] = ''
                    database_link_object['text'] = ''

                self.crawled_links.append(database_link_object)
                print('--------------')

            depth -= 1

        end_time = datetime.now()

        top_five_keywords = create_wordcloud(self.crawled_links)
        link_tree_formation(self.crawled_links)
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
    def __init__(self, base_url,depth):
        self.base_url = base_url
        self.root_url = '{}://{}'.format(urlparse(self.base_url).scheme, urlparse(self.base_url).netloc)
        self.links_to_crawl = Queue()
        self.links_to_crawl.put((self.base_url, depth))
        self.have_visited = set()
        self.error_links = set()
        self.pool = ThreadPoolExecutor(max_workers=20)
        self.proxies = {'http' : 'socks5h://127.0.0.1:9150', 'https' : 'socks5h://127.0.0.1:9150'}
        self.crawled_links = []
        
        
    def renew_tor_ip(self):
        with Controller.from_port(port = 9051) as controller:
            controller.authenticate(password=TORCC_HASH_PASSWORD)
            controller.signal(Signal.NEWNYM)

    def get_current_ip(self):
        try:
            r = requests.get('http://httpbin.org/ip', proxies = self.proxies)
        except Exception as e:
            print (str(e))
        else:
            return r.text.split(",")[-1].split('"')[3]

    def parse_links(self, html, depth, current_link):

        soup = BeautifulSoup(html, 'html.parser')

        links = soup.find_all('a', href=True)

        for anchor_tag in links:
            try:
                link_in_anchor_tag = anchor_tag['href']

                if link_in_anchor_tag != '' and link_in_anchor_tag != '/' and link_in_anchor_tag not in self.have_visited:
                    if link_in_anchor_tag.startswith('http'):
                        self.links_to_crawl.put((link_in_anchor_tag, depth - 1))
                    elif link_in_anchor_tag.startswith('/'):
                        base_url = current_link

                        if base_url[-1] == '/':
                            base_url = current_link[:len(current_link)-1]

                        if link_in_anchor_tag[0] == '/':
                            link_in_anchor_tag = link_in_anchor_tag[1:]

                        self.links_to_crawl.put((base_url + '/' + link_in_anchor_tag, depth - 1))
                    
                    elif not link_in_anchor_tag.startswith('.'):
                        base_url = current_link

                        if base_url[-1] == '/':
                            base_url = current_link[:len(current_link)-1]

                        self.links_to_crawl.put((base_url + '/' + link_in_anchor_tag, depth - 1))

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

 
    def scrape_info(self, html, current_link):
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title').get_text()
        text = soup.get_text()
        links = [link['href'] for link in soup.find_all('a', href = True)]
        link = current_link
        self.crawled_links.append({
            'title': title,
            'text': text,
            'links': links,
            'link': link,
        })

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
        current_link = result_from_callback[2]
        
        if result != None:
            print('Found Current Link ' + current_link)
            self.parse_links(result.text, depth, current_link)
            self.scrape_info(result.text, current_link)
        else:
            print('Not Found Current Link ' + current_link)

 
    def scrape_page(self, url, headers, depth):
        try:
            self.renew_tor_ip()
            res = requests.get(url, proxies = self.proxies, headers = headers)           
            return (res, depth, url)
        except:
            return (None, depth, url)
        
    def run_scraper(self):

        os.startfile(TOR_BROWSER_PATH)
        time.sleep(10)
        print("Tor Browser started")

        start_time = datetime.now()

        while True:
            try:
                link_info = self.links_to_crawl.get(timeout = 20)
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
        
        end_time = datetime.now()
        return time_difference(start_time, end_time), self.crawled_links

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

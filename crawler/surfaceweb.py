# Import for getting the time for crawling 
import time
from datetime import date, datetime

# Import for random selection in array
import random

# Import for creating and opening folders and files
import os

# Import for crawling
from queue import Queue, Empty
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import requests
from lxml import html
import re

# Import for google crawl
from googlesearch import search

# Import from selenium web driver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

# Import from utils/functions.py
from utils.functions import time_difference, create_wordcloud, create_directory_for_images, link_tree_formation

# Import .env variables
from dotenv import dotenv_values
config = dotenv_values(".env")

# Add constants
INSTAGRAM_USERNAME = config['INSTAGRAM_USERNAME']
INSTAGRAM_PASSWORD = config['INSTAGRAM_PASSWORD']

# Chromedriver path
CHROMEDRIVER_PATH = os.path.join(os.path.dirname( __file__ ), '..', 'static', 'chromedriver', 'chromedriver.exe')

class SurfaceWebCrawler:
    def __init__(self, base_url, depth):
        
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
        
    # Store images in the folder 
    def store_images(self, image_links, current_link):
        
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
            # Request to the Surface Web URL 
            response = requests.get(url)

            # Print that the link is found and return the response and that link is active
            print("Page found.... " + url)     
            return True, response
        except:
            # Print that the link is not found and return the response and that link is not active
            print("Page not found... " + url)
            return False, None
        
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
        links_found_on_google = list(search(self.keyword, num = 15 * (self.depth), stop = 25 * (self.depth), pause = 8.0, verify_ssl = True))
        
        for link in links_found_on_google:
            if link not in self.have_visited:
                self.queue.put({ 'url': link, 'parent_link': self.base_url })
                self.have_visited.add(link)
                
    # Make a request to the dark web 
    def make_request(self, url):
        try:
            # Request to the Surface Web URL 
            response = requests.get(url)

            # Print that the link is found and return the response and that link is active
            print("Page found.... " + url)     
            return True, response
        except:
            # Print that the link is not found and return the response and that link is not active
            print("Page not found... " + url)
            return False, None

    def new_crawling(self):

        # Start time of the crawling
        start_time = datetime.now()
            
        # Get all links from google
        self.get_all_links()
        
        # Selenium webdriver
        driver = webdriver.Chrome(CHROMEDRIVER_PATH)
        
        while not self.queue.empty():

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

# Instagram Crawler class
class InstagramCrawler:
    
    def __init__(self, keyword, depth):
        
        # base keyword
        self.keyword = keyword
        
        # depth
        self.depth = depth
        
        # global queue
        self.queue = Queue()
        
        # visited links
        self.have_visited = set()
        
        # for database
        self.crawled_links = []
        
        # Chrome webdriver
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH)
        
    # Login into instagram
    def login(self):
        
        # Go to instagram.com
        self.driver.get("https://www.instagram.com/")
        time.sleep(5)
        
        # Get the input fields
        input_fields = self.driver.find_elements_by_xpath("//input")
        count = 0
        
        # Put data into input field
        for input_field in input_fields:
            name = input_field.get_attribute("name")
            if name == 'username':
                input_field.send_keys(INSTAGRAM_USERNAME)
                count += 1
            elif name == 'password':
                input_field.send_keys(INSTAGRAM_PASSWORD)
                count += 1
            if count == 2:
                break
            
        # Press submit
        submit_btn = self.driver.find_element_by_xpath("//button[@type='submit']")
        submit_btn.send_keys(Keys.ENTER)
        time.sleep(5)
        
    # Get all links           
    def get_all_links(self):
        
        # Search for keyword in instagram
        url = "https://www.instagram.com/explore/tags/" + self.keyword + "/"
        
        self.driver.get(url)
            
        for _ in range(self.depth):
            
            # Roll down to the screen
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Get all the link elements
            link_elements = self.driver.find_elements_by_xpath("//*[@class='v1Nh3 kIKUG  _bz0w']/a")
            
            # Get all the hrefs and put them in the queue
            for link in link_elements:
                try:
                    href = link.get_attribute('href')
                    if href not in self.have_visited:
                        self.queue.put(href)
                        self.have_visited.add(href)
                except Exception:
                    pass

    def new_crawling(self):
            
        # Login into instagram
        self.login()

        # Start time of the crawling
        start_time = datetime.now()
        
        # Get all links
        self.get_all_links()
        
        while not self.queue.empty():

            print('--------------')

            # Darkweb database model has a list of crawled links
            # We will create a Link object and push it in crawled_links
            database_link_object = dict()

            # Current link in queue
            current_link = self.queue.get()
            
            try:

                # Make request to the current link 
                self.driver.get(current_link)
                print('Link found ', current_link)

                # Add images in database


                # Create Link object to put in Database 
                    
                database_link_object['link'] = current_link
                
                try:
                    database_link_object['posted_by'] = self.driver.find_elements_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/h2/div/span/a")[0].get_attribute('href')
                except:
                    database_link_object['posted_by'] = ''
                            
                try:
                    database_link_object['location'] = self.driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/header/div[2]/div[2]/div[2]/a").text
                except:
                    database_link_object['location'] = ''
                    
                try:
                    database_link_object['caption'] = self.driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span").text.split("#")[0]
                except:
                    database_link_object['caption'] = ''
                        
                try:
                    database_link_object['hashtags'] = []
                    hashtags_found = self.driver.find_elements_by_class_name("xil3i")
                    for hashtag_found in hashtags_found:
                        database_link_object['hashtags'].append(hashtag_found.text)
                except:
                    database_link_object['hashtags'] = []
            
            except:
                
                database_link_object['link'] = current_link
                database_link_object['posted_by'] = ''
                database_link_object['location'] = ''
                database_link_object['caption'] = ''
                database_link_object['hashtags'] = []

            self.crawled_links.append(database_link_object)
            print('--------------')
            
        # Quit the selenium webdriver
        self.driver.quit()

        # End time of crawling
        end_time = datetime.now()
        
        #Create final result
        result = {
            'keyword': self.keyword,
            'time_taken': time_difference(start_time, end_time),
            'crawled_links': self.crawled_links
        }
        
        return result

# Twitter Crawler class
class TwitterCrawler:
    
    def __init__(self, keyword, depth):
        
        # base keyword
        self.keyword = keyword
        
        # depth
        self.depth = depth
        
        # global queue
        self.queue = Queue()
        
        # visited links
        self.have_visited = set()
        
        # for database
        self.crawled_links = []
        
        # Chrome webdriver
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH)
        
    # Get all links           
    def get_all_links(self):
        
        # Search for keyword in instagram
        url = "https://twitter.com/search?q=%23" + self.keyword + "&src=typed_query"
        
        self.driver.get(url)
            
        for _ in range(self.depth):
            
            # Roll down to the screen
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Get all the link elements
            anchor_tags = self.driver.find_elements_by_tag_name('a')
            
            # Get all the hrefs and put them in the queue
            for anchor_tag in anchor_tags:
                href = anchor_tag.get_attribute("href")
                if ("/status/" in href) and ("/photo/" not in href) and (href not in self.have_visited):
                    self.queue.put(href)
                    self.have_visited.add(href)

    def new_crawling(self):

        # Start time of the crawling
        start_time = datetime.now()
        
        # Get all links
        self.get_all_links()
        
        while not self.queue.empty():

            print('--------------')

            # Darkweb database model has a list of crawled links
            # We will create a Link object and push it in crawled_links
            database_link_object = dict()

            # Current link in queue
            current_link = self.queue.get()
            
            try:

                # Make request to the current link 
                self.driver.get(current_link)
                print('Link found ', current_link)

                # Add images in database


                # Create Link object to put in Database 
                    
                database_link_object['link'] = current_link
                
                try:
                    database_link_object['posted_by'] = current_link.split("/status/")[0]
                except:
                    database_link_object['posted_by'] = ''
                    
                try:
                    caption_element = self.driver.find_element_by_xpath("//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[2]/div/section/div/div/div[1]/div/div/article/div/div/div/div[3]/div[1]/div/div")
                    database_link_object['caption'] = caption_element.text
                    
                    database_link_object['hashtags'] = []
                    for span in caption_element.find_elements_by_xpath("./span"):
                        hashtag = re.findall("#[a-zA-Z0-9]+", span.text)
                        if len(hashtag) == 1:
                            database_link_object['hashtags'].append(hashtag[0])
                            
                except:
                    database_link_object['caption'] = ''
                    database_link_object['hashtags'] = []
            
            except:
                
                database_link_object['link'] = current_link
                database_link_object['posted_by'] = ''
                database_link_object['location'] = ''
                database_link_object['caption'] = ''
                database_link_object['hashtags'] = []

            self.crawled_links.append(database_link_object)
            print('--------------')
            
        # Quit the selenium webdriver
        self.driver.quit()

        # End time of crawling
        end_time = datetime.now()
        
        #Create final result
        result = {
            'keyword': self.keyword,
            'time_taken': time_difference(start_time, end_time),
            'crawled_links': self.crawled_links
        }
        
        return result
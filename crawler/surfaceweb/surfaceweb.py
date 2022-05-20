# Importing the required libraries
import os

# For getting the time for crawling 
from datetime import datetime

# Importing queue for DFS algorithm
from queue import Queue
from urllib.parse import urljoin

# For scraping the dark web page 
from bs4 import BeautifulSoup
import requests

# Import from utils/functions.py
from utils.functions import time_difference, create_directory_for_images, output

# Import from utils/save.py
from utils.save import backup

# Import from utils/tree.py
from utils.tree import link_tree_formation

# Import from utils/wordcloud.py
from utils.wordcloud import create_wordcloud

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
                
    def crawl(self):

        # Start time of the crawling
        start_time = datetime.now()
        print(self.queue)
        depth = self.depth
        while not self.queue.empty() and depth > 0:

            # All the links currently in the queue
            size = self.queue.qsize()

            for _ in range(size):

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

                    database_link_object['html'] = link_response.text

                    self.get_all_links(soup, current_link)
                    
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
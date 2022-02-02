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

# Import from utils/functions.py
from utils.functions import time_difference, create_wordcloud, clear_images_directory, create_directory_for_images, link_tree_formation

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

# class Google:

#     def __init__(self, keyword, depth):
#         self.keyword = keyword
#         self.depth = depth
#         self.visitedcoll = connect_mongodb("googledb", "keywords-visited")
#         self.coll = connect_mongodb("googledb", self.keyword)

#     def googlecrawl(self):

#         visited = False
#         for _ in self.visitedcoll.find({"keyword":self.keyword}):
#             visited = True

#         links = []
#         wc_words = open('crawler/static/crawler/wc_words.txt', 'w', encoding='utf-8')

#         if visited:
#             for x in self.coll.find():
#                 links.append(x["Link"])
#                 try:
#                     wc_words.write(x["Page content"] + "\n\n")
#                 except Exception:
#                     pass
        
#         else:
            
#             url = "https://google.com/search?q={}".format('+'.join(self.keyword.split(' ')))
#             links_found_on_google = list(search(self.keyword, num=25*(self.depth), stop=25*(self.depth), pause=4.0))
#             links = [url] + links_found_on_google

#             driver = webdriver.Chrome(CHROMEDRIVER_PATH)

#             # TODO: Can try headless webdriver ->
#             # chrome_options = Options()
#             # chrome_options.add_argument("--headless")
#             # driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=chrome_options)

#             parent = None
#             link_count = 0
#             for link in links:
#                 print(link_count, "->", link)
#                 try:
#                     source = requests.get(link, timeout = 20).text
#                     curr_page = BeautifulSoup(source, 'lxml')
#                     title = curr_page.find('title').text
#                     text = ' '.join(curr_page.text.split())
#                     wc_words.write(text + "\n\n")
#                     driver.get(link)
#                     imgs = list(set([element.get_attribute('src') for element in driver.find_elements_by_tag_name('img')]))
#                     images = []
#                     for img in imgs:
#                         images.append([img, False])
#                     store_images_in_db("googledb", images)
#                     success = True
#                 except Exception:
#                     success = False
#                 if success:
#                     print("Found")
#                     self.coll.insert_one({"Link":link, "Title":title, "Page content":text, "Images": images, "Parent link":parent, "Successfully parsed":success})
#                 else:
#                     print("Not found")
#                     self.coll.insert_one({"Link":link, "Parent link":parent, "Successfully parsed":success})
                
#                 link_count += 1
#                 if link_count == 1:
#                     parent = url
#             driver.quit()
#             self.visitedcoll.insert_one({"keyword":self.keyword})

#         topFiveWords = display_wordcloud(wc_words)
        
#         return links, topFiveWords


# class Instagram:

#     def __init__(self, keyword, depth):
#         self.keyword = keyword
#         self.depth = depth
#         self.visitedcoll = connect_mongodb("instagramdb", "keywords-visited")
#         self.coll = connect_mongodb("instagramdb", self.keyword)

#     def instacrawl(self):

#         visited = False
#         for _ in self.visitedcoll.find({"keyword":self.keyword}):
#             visited = True
        
#         links = []
#         wc_words = open('crawler/static/crawler/wc_words.txt', 'w', encoding='utf-8')

#         if visited:
#             for x in self.coll.find():
#                 links.append(x["Link"])
#                 for hashtag in x["Hashtags"]:
#                     wc_words.write(hashtag + "\n")

#         else:
#             driver = webdriver.Chrome(CHROMEDRIVER_PATH)

#             # TODO: Can try headless webdriver ->
#             # chrome_options = Options()
#             # chrome_options.add_argument("--headless")
#             # driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=chrome_options)
            
#             driver.get("https://www.instagram.com/")
#             time.sleep(5)
#             input_fields = driver.find_elements_by_xpath("//input")
#             count = 0
#             for input_field in input_fields:
#                 name = input_field.get_attribute("name")
#                 if name == 'username':
#                     input_field.send_keys(INSTAGRAM_USERNAME)
#                     count += 1
#                 elif name == 'password':
#                     input_field.send_keys(INSTAGRAM_PASSWORD)
#                     count += 1
#                 if count == 2:
#                     break
#             submit_btn = driver.find_element_by_xpath("//button[@type='submit']")
#             submit_btn.send_keys(Keys.ENTER)
#             time.sleep(5)

#             url = "https://www.instagram.com/explore/tags/" + self.keyword + "/"
#             driver.get(url)
#             for _ in range(self.depth):
#                 driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                 time.sleep(2)
#                 link_elements = driver.find_elements_by_xpath("//*[@class='v1Nh3 kIKUG  _bz0w']/a")
#                 for link in link_elements:
#                     try:
#                         href = link.get_attribute('href')
#                         if href not in links:
#                             links.append(href)
#                     except Exception:
#                         pass
            
            
#             for link in links:
#                 post_hashtags = []
#                 try:
#                     driver.get(link)
#                     account = driver.find_elements_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/h2/div/span/a")[0].get_attribute('href')
#                     caption = driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span").text.split("#")[0]
#                     imgs = list(set([str(driver.find_element_by_class_name("FFVAD").get_attribute('src'))]))
#                     images = []
#                     for img in imgs:
#                         images.append([img, False])
#                     store_images_in_db("instagramdb", images)
#                     try:
#                         location = driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/header/div[2]/div[2]/div[2]/a").text
#                     except Exception:
#                         location = None
#                     hashtags_found = driver.find_elements_by_class_name("xil3i")
#                     for hashtag_found in hashtags_found:
#                         post_hashtags.append(hashtag_found.text)
#                         wc_words.write(hashtag_found.text + "\n")
#                 except Exception:
#                     print("Parsing failed: ", link)
#                     continue
#                 self.coll.insert_one({"Link":link, "Posted by":account, "Location":location, "Images":images, "Caption":caption, "Hashtags":post_hashtags})
#             driver.quit()
#             self.visitedcoll.insert_one({"keyword":self.keyword})

#         topFiveWords = display_wordcloud(wc_words)

#         return links, topFiveWords


# class Twitter:
#     def __init__(self, keyword, depth):
#         self.keyword = keyword
#         self.depth = depth
#         self.visitedcoll = connect_mongodb("twitterdb", "keywords-visited")
#         self.coll = connect_mongodb("twitterdb", self.keyword)

#     def twittercrawl(self):

#         visited = False
#         for _ in self.visitedcoll.find({"keyword":self.keyword}):
#             visited = True

#         links = []
#         wc_words = open('crawler/static/crawler/wc_words.txt', 'w', encoding='utf-8')

#         if visited:
#             for x in self.coll.find():
#                 links.append(x["Link"])
#                 for hashtag in x["Hashtags"]:
#                     wc_words.write(hashtag + "\n")
        
#         else:
            
#             driver = webdriver.Chrome(CHROMEDRIVER_PATH)

#             # TODO: Can try headless webdriver ->
#             # chrome_options = Options()
#             # chrome_options.add_argument("--headless")
#             # driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=chrome_options)

#             url = "https://twitter.com/search?q=%23" + self.keyword + "&src=typed_query"
#             driver.get(url)
#             for _ in range(self.depth):
#                 driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                 time.sleep(3)
#                 anchor_tags = driver.find_elements_by_tag_name('a')
#                 for anchor_tag in anchor_tags:
#                     href = anchor_tag.get_attribute("href")
#                     if ("/status/" in href) and ("/photo/" not in href) and (href not in links):
#                         links.append(href)

#             for link in links:
#                 post_hashtags = []
#                 imgs = [] 
#                 try:
#                     driver.get(link)
#                     time.sleep(3)
#                     account = link.split("/status/")[0]
#                     img_elements = driver.find_elements_by_tag_name("img")
#                     for image in img_elements:
#                         if image.get_attribute("alt") == "Image":
#                             imgs.append(str(image.get_attribute("src")))
#                     caption_element = driver.find_element_by_xpath("//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[2]/div/section/div/div/div[1]/div/div/article/div/div/div/div[3]/div[1]/div/div")
#                     caption = caption_element.text
#                     for span in caption_element.find_elements_by_xpath("./span"):
#                         hashtag = re.findall("#[a-zA-Z0-9]+", span.text)
#                         if len(hashtag) == 1:
#                             post_hashtags.append(hashtag[0])
#                             wc_words.write(hashtag[0] + "\n")
#                     imgs = list(set(imgs))
#                     images = []
#                     for img in imgs:
#                         images.append([img, False])
#                     store_images_in_db("twitterdb", images)
#                 except Exception:
#                     print("Parsing failed: ", link)
#                     continue
#                 self.coll.insert_one({"Link":link, "Posted by":account, "Images": images, "Caption":caption, "Hashtags":post_hashtags})
#             driver.quit()
#             self.visitedcoll.insert_one({"keyword":self.keyword})

#         topFiveWords = display_wordcloud(wc_words)

#         return links, topFiveWords
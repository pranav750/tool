from wordcloud import WordCloud, STOPWORDS
from urllib.parse import urlparse
from anytree import Node, RenderTree
from dotenv import dotenv_values

import json
import os, shutil
import time
import csv

config = dotenv_values(".env")
TOR_BROWSER_PATH = config['TOR_BROWSER_PATH']

def open_tor_browser():
    # Start Tor Browser
    os.startfile(TOR_BROWSER_PATH)
    time.sleep(10)
    print("Tor Browser started")

def time_difference(start_time, end_time):
    time_diff = end_time - start_time
    minutes = divmod(time_diff.total_seconds(), 60) 
    return f'{int(minutes[0])} minutes, {int(minutes[1])} seconds'

def save_json(crawled_data):
    with open(os.path.join(os.path.dirname( __file__ ), '..', 'static', 'results.json'), 'w', encoding="utf-8") as results:
        json.dump(crawled_data, results)
        
def save_csv(crawled_data):
    crawled_links = crawled_data['crawled_links']
    fields = ['link', 'link_status', 'parent_link', 'title', 'text']
    
    with open(os.path.join(os.path.dirname( __file__ ), '..', 'static', 'results.csv'), 'w', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = fields)
        writer.writeheader()
        writer.writerows(crawled_links)

def create_wordcloud(crawled_links):
    texts = texts_from_result(crawled_links)
    wc_words = open(os.path.join(os.path.dirname( __file__ ), '..', 'static', 'wc_words.txt'), 'w', encoding = 'utf-8')
    for text in texts:
        try:
            wc_words.write(text + "\n")
        except:
            pass
        
    top_five_keywords = display_wordcloud(wc_words)
    return top_five_keywords

def display_wordcloud(wc_words):
    print("Generating Wordcloud...")
    stopwords = set(STOPWORDS)
    wordc = WordCloud(background_color = "white", width = 700, height = 350, stopwords = stopwords)
    wc_words.seek(0)
    
    wordc.generate(open(os.path.join(os.path.dirname( __file__ ), '..', 'static', 'wc_words.txt'), encoding = 'utf-8').read())
    wordc.to_file(os.path.join(os.path.dirname( __file__ ), '..', 'static', 'wc_img.png'))

    top_key_value_pairs = list(wordc.words_.items())[:5]

    wc_words.flush()
    wc_words.close()

    top_five_keywords = []
    for top_key_value_pair in top_key_value_pairs:
        top_five_keywords.append(top_key_value_pair[0])
    
    return top_five_keywords 

def texts_from_result(crawled_links):
    texts = []
    for result in crawled_links:
        try:
            texts.append(result['text'])
        except:
            pass

    return texts

def links_from_result(darkweb_result):
    links = []
    for result in darkweb_result['crawled_links']:
        try:
            links.append(result['link'])
        except:
            pass

    return links

def link_status_from_result(darkweb_result):
    final_result = {
        'link': darkweb_result['link'],
        'active_links': darkweb_result['active_links'],
        'inactive_links': darkweb_result['inactive_links'],
        'top_five_keywords': darkweb_result['top_five_keywords'],
        'time_taken': darkweb_result['time_taken'],
        'link_statuses': dict()
    }
    for result in darkweb_result['crawled_links']:
        try:
            final_result['link_statuses'][result['link']] = result['link_status']
        except:
            pass

    return final_result

def clear_images_directory():
    folder = os.path.join(os.path.dirname( __file__ ), '..', 'static', 'images')
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def create_directory_for_images(number):
    try:
        os.mkdir(os.path.join(os.path.dirname( __file__ ), '..', 'static', 'images', str(number)))
    except:
        print("Folder already created!")
        
def link_tree_formation(crawled_links):
    print("Generating Link Tree...")
    root = None
    tree_dict = dict()
    for result in crawled_links:
        if result['parent_link'] == '':
            root = Node(result['link'])
            tree_dict[result['link']] = root

        else:
            node = Node(result['link'],parent = tree_dict[result['parent_link']])
            tree_dict[result['link']] = node
            
        
    link_tree = open(os.path.join(os.path.dirname( __file__ ), '..', 'static', 'link_tree.txt'), 'w', encoding = 'utf-8')
    link_tree.flush()
        
    for pre, fill, node in RenderTree(root):
        link_tree.write("%s%s" % (pre, node.name))
        link_tree.write("\n")
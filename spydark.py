# Import for creating the command line utility
import argparse

# Importing Dark Web crawling objects from crawler/darkweb.py
from crawler.darkweb import DarkWebCrawler, MultiThreaded, link_similarity
from crawler.surfaceweb import SurfaceWebCrawler

# Importing functions from utils/functions.py
from utils.functions import clear_images_directory, save_json, save_csv, link_status_from_result, create_directory_for_images, open_tor_browser

# Creating a parser object
parser = argparse.ArgumentParser()

# Select either dark web or surface web
web = parser.add_mutually_exclusive_group()
web.add_argument('--dark', action = 'store_true', help = 'Specify if Dark Web Crawling needed')
web.add_argument('--surface', action = 'store_true', help = 'Specify if Surface Web Crawling needed')

# Provide wither url or keyword
url_or_keyword = parser.add_mutually_exclusive_group()
url_or_keyword.add_argument('--url', type = str, help = 'Specify the URL')
url_or_keyword.add_argument('--keyword', type = str, help = 'Specify the Keyword')

# Select either iterative crawling or multi threaded crawling
multi_or_iterative = parser.add_mutually_exclusive_group()
multi_or_iterative.add_argument('--multi', action = "store_true", help = 'Specify if multi-threaded crawling is required')
multi_or_iterative.add_argument('--iterative', action = "store_true", help = 'Specify if iterative crawling is required')

# Provide depth for crawling, default is 1
parser.add_argument('--depth', type = int, default = 1, help = 'Specify the depth')

parser.add_argument('--lsm', action = "store_true", help='Specify the dark web link')

parser.add_argument('--links', nargs='+', help='Specify the dark web links for link similarity')

parser.add_argument('--lst', action = "store_true", help='Specify the dark web link')

# Get the arguments
args = parser.parse_args()

# Dark Web crawling
if args.dark:
    print(f'Crawl {args.url} with depth {args.depth} on dark web')

    # Clear the images directory for storing new images 
    clear_images_directory()

    # Creating link out of keyword or url provided
    link = ''
    if args.url:
        link = args.url
    elif args.keyword:
        link = 'wiki_link/' + args.keyword

    # Iterative dark web crawling
    if args.iterative: 
        
        # Dark web object creation
        dark_web_object =  DarkWebCrawler(link, args.depth)
        
        # Start Tor Browser
        open_tor_browser()
        
        # Crawling
        result = dark_web_object.new_crawling()
        
        # Saving result into static/results.json
        save_json(result)
        
        # Saving result into static/results.csv
        save_csv(result)
        
    # Multi threaded dark web crawling
    elif args.multi:
        
        # Dark web object creation
        dark_web_object = MultiThreaded(args.url, args.depth)
        
        # Start Tor Browser
        open_tor_browser()
        
        # Crawling
        result = dark_web_object.run_scraper()

        # Saving result into static/results.json
        save_json(result)
        
        # Saving result into static/results.csv
        save_csv(result)

elif args.surface:
    print(f'Crawl {args.url} with depth {args.depth} on surface web')

    # Clear the images directory for storing new images 
    clear_images_directory()

    # Creating link out of keyword or url provided
    link = ''
    if args.url:
        link = args.url
    elif args.keyword:
        link = 'wiki_link/' + args.keyword
        
    # Surface web object creation
    surface_web_object = SurfaceWebCrawler(args.url, args.depth)
    
    # Crawling
    result = surface_web_object.new_crawling()
        
    # Saving result into static/results.json
    save_json(result)
        
    # Saving result into static/results.csv
    save_csv(result)

elif args.lsm:
    print (f'Link Similarity checking with depth 2')
    result = link_similarity(args.links, 2)
    save_json(result)

elif args.lst:
    print('Link Status cheking')
    link = ''
    if args.url:
        link = args.url
    elif args.keyword:
        link = 'wiki_link/' + args.keyword
    dark_web_object =  DarkWebCrawler(link, args.depth)
        
    open_tor_browser()
        
    result = dark_web_object.new_crawling()
    final_result = link_status_from_result(result)
    save_json(final_result)
    
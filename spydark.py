# Import for creating the command line utility
import argparse

# Importing Dark Web crawling objects from crawler/darkweb.py
from crawler.darkweb import DarkWebCrawler, DFSDarkWebCrawler, MultiThreaded, link_similarity
from crawler.surfaceweb import GoogleCrawler, InstagramCrawler, SurfaceWebCrawler, TwitterCrawler

# Importing functions from utils/functions.py
from utils.functions import clear_results_directory, save_json, save_csv, link_status_from_result, open_tor_browser

# Creating a parser object
parser = argparse.ArgumentParser()

# Select either dark web or surface web
web = parser.add_mutually_exclusive_group()
web.add_argument('--dark', action = 'store_true', help = 'Specify if Dark Web Crawling needed')
web.add_argument('--surface', action = 'store_true', help = 'Specify if Surface Web Crawling needed')

# Select social media for surface web crawling
social = parser.add_mutually_exclusive_group()
social.add_argument('--google', action = 'store_true', help = 'Specify if Google Crawling needed')
social.add_argument('--instagram', action = 'store_true', help = 'Specify if Instagram Crawling needed')
social.add_argument('--twitter', action = 'store_true', help = 'Specify if Twitter Crawling needed')

# Provide wither url or keyword
url_or_keyword = parser.add_mutually_exclusive_group()
url_or_keyword.add_argument('--url', type = str, help = 'Specify the URL')
url_or_keyword.add_argument('--keyword', type = str, help = 'Specify the Keyword')

# Select either iterative crawling or multi threaded crawling
algorithm = parser.add_mutually_exclusive_group()
algorithm.add_argument('--multi', action = "store_true", help = 'Specify if multi-threaded crawling is required')
algorithm.add_argument('--iterative', action = "store_true", help = 'Specify if iterative crawling is required')
algorithm.add_argument('--dfs', action = "store_true", help = 'Specify if DFS crawling is required')

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
    clear_results_directory()

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
        
    # DFS dark web crawling
    elif args.dfs:
        
        # Dark web object creation
        dark_web_object =  DFSDarkWebCrawler(link, args.depth)
        
        # Start Tor Browser
        open_tor_browser()
        
        # Crawling
        result = dark_web_object.new_crawling()
        
        # Saving result into results/results.json
        save_json(result)
        
        # Saving result into results/results.csv
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
    clear_results_directory()
        
    if args.google:
        
        if args.url:
            print('Google crawler can only take keyword')
            quit()
            
        # Surface web object creation for Google
        surface_web_object = GoogleCrawler(args.keyword, args.depth)
        
        # Crawling
        result = surface_web_object.new_crawling()
            
        # Saving result into static/results.json
        save_json(result)
            
        # Saving result into static/results.csv
        save_csv(result)
        
    elif args.instagram:
        
        if args.url:
            print('Instagram crawler can only take keyword')
            quit()
            
        # Surface web object creation for Google
        surface_web_object = InstagramCrawler(args.keyword, args.depth)
        
        # Crawling
        result = surface_web_object.new_crawling()
            
        # Saving result into static/results.json
        save_json(result)
            
        # Saving result into static/results.csv
        save_csv(result)
        
    elif args.twitter:
        
        if args.url:
            print('Twitter crawler can only take keyword')
            quit()
            
        # Surface web object creation for Google
        surface_web_object = TwitterCrawler(args.keyword, args.depth)
        
        # Crawling
        result = surface_web_object.new_crawling()
            
        # Saving result into static/results.json
        save_json(result)
            
        # Saving result into static/results.csv
        save_csv(result)
        
    else:
        
        if args.keyword:
            print('Surface crawler can only take url')
            quit()
        
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
    
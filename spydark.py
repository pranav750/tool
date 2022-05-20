# Import for creating the command line utility
import argparse

# Importing BFS crawler
from crawler.darkweb.bfs import BFSDarkWebCrawler

# Importing Multi threaded crawler
from crawler.darkweb.multithreaded import MultiThreadedDarkWebCrawler 

# Importing DFS crawler
from crawler.darkweb.dfs import DFSDarkWebCrawler 

# Importing Surface Web Crawler
from crawler.surfaceweb.surfaceweb import SurfaceWebCrawler

# Importing Google Web Crawler
from crawler.surfaceweb.google import GoogleCrawler

# Importing Link Similarity
from crawler.darkweb.similarity import link_similarity

# Importing Dark Web crawling objects from crawler/darkweb.py
# from crawler.surfaceweb import GoogleCrawler, InstagramCrawler, SurfaceWebCrawler, TwitterCrawler

# Importing functions from utils/functions.py
from utils.functions import clear_results_directory, open_tor_browser

# Importing functions from utils/save.py
from utils.save import save_json, save_csv

# Importing functions from utils/status.py
from utils.status import link_status_from_result

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
algorithm.add_argument('--multi', action = "store_true", help = 'Specify if Multi-threaded crawling is required')
algorithm.add_argument('--bfs', action = "store_true", help = 'Specify if BFS crawling is required')
algorithm.add_argument('--dfs', action = "store_true", help = 'Specify if DFS crawling is required')

# Provide depth for crawling, default is 1
parser.add_argument('--depth', type = int, default = 1, help = 'Specify the depth')


parser.add_argument('--lsm', action = "store_true", help='Specify the dark web link')


parser.add_argument('--links', nargs='+', help='Specify the dark web links for link similarity')

# For getting the Link Status
parser.add_argument('--lst', action = "store_true", help='Specify the dark web link')

# Get the arguments
args = parser.parse_args()

# Dark Web crawling
if args.dark:

    # Creating link out of keyword or url provided
    link = ''
    if args.url:
        link = args.url
    elif args.keyword:
        link = 'wiki_link/' + args.keyword

    if args.url:
        print(f'Crawl {args.url} with depth {args.depth} on dark web')
    else:
        print(f'Crawl {args.keyword} with depth {args.depth} on dark web')

    # Clear the results directory for storing new data 
    clear_results_directory()

    # Iterative dark web crawling
    if args.bfs: 
        
        # Dark web object creation
        dark_web_object =  BFSDarkWebCrawler(link, args.depth)
        
        # Start Tor Browser
        open_tor_browser()
        
        # Crawling
        result = dark_web_object.crawl()
        
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
        result = dark_web_object.crawl()
        
        # Saving result into results/results.json
        save_json(result)
        
        # Saving result into results/results.csv
        save_csv(result)
        
    # Multi threaded dark web crawling
    elif args.multi:
        
        # Dark web object creation
        dark_web_object = MultiThreadedDarkWebCrawler(link, args.depth)
        
        # Start Tor Browser
        open_tor_browser()
        
        # Crawling
        result = dark_web_object.crawl()

        # Saving result into static/results.json
        save_json(result)
        
        # Saving result into static/results.csv
        save_csv(result)

elif args.surface:

    if args.url:
        print(f'Crawl {args.url} with depth {args.depth} on surface web')
    else:
        print(f'Crawl {args.keyword} with depth {args.depth} on surface web')

    # Clear the images directory for storing new images 
    clear_results_directory()

    if args.google:

        if args.url:
            print('Google crawler can only take keyword')
            quit()
            
        # Surface web object creation for Google
        surface_web_object = GoogleCrawler(args.keyword, args.depth)
        
        # Crawling
        result = surface_web_object.crawl()
            
        # Saving result into static/results.json
        save_json(result)
            
        # Saving result into static/results.csv
        save_csv(result)

    else:
        
        if args.keyword:
            print("Surface web crawling can only be done on keyword.")
            quit()

        # Surface web object creation for Google
        surface_web_object = SurfaceWebCrawler(args.url, args.depth)

        # Crawling
        result = surface_web_object.crawl()

        # Saving result into static/results.json
        save_json(result)
            
        # Saving result into static/results.csv
        save_csv(result)
        
#     if args.google:
        
#         if args.url:
#             print('Google crawler can only take keyword')
#             quit()
            
#         # Surface web object creation for Google
#         surface_web_object = GoogleCrawler(args.keyword, args.depth)
        
#         # Crawling
#         result = surface_web_object.new_crawling()
            
#         # Saving result into static/results.json
#         save_json(result)
            
#         # Saving result into static/results.csv
#         save_csv(result)
        
#     elif args.instagram:
        
#         if args.url:
#             print('Instagram crawler can only take keyword')
#             quit()
            
#         # Surface web object creation for Google
#         surface_web_object = InstagramCrawler(args.keyword, args.depth)
        
#         # Crawling
#         result = surface_web_object.new_crawling()
            
#         # Saving result into static/results.json
#         save_json(result)
            
#         # Saving result into static/results.csv
#         save_csv(result)
        
#     elif args.twitter:
        
#         if args.url:
#             print('Twitter crawler can only take keyword')
#             quit()
            
#         # Surface web object creation for Google
#         surface_web_object = TwitterCrawler(args.keyword, args.depth)
        
#         # Crawling
#         result = surface_web_object.new_crawling()
            
#         # Saving result into static/results.json
#         save_json(result)
            
#         # Saving result into static/results.csv
#         save_csv(result)
        
#     else:
        
#         if args.keyword:
#             print('Surface crawler can only take url')
#             quit()
        
#         # Surface web object creation
#         surface_web_object = SurfaceWebCrawler(args.url, args.depth)
        
#         # Crawling
#         result = surface_web_object.new_crawling()
            
#         # Saving result into static/results.json
#         save_json(result)
            
#         # Saving result into static/results.csv
#         save_csv(result)

elif args.lsm:

    if len(args.links) == 0:
        print("Provide some links for checking Link Similarity")
        quit()
    else:
        print("Check Link Similarity for provided links on depth 2")

    print(args.links)
    # Clear the results directory for storing new data 
    clear_results_directory()
        
    # Start Tor Browser
    open_tor_browser()

    # Checking Link Similarity
    result = link_similarity(args.links, 2)

    # Saving result into static/results.json
    save_json(result)

elif args.lst:

    # Creating link out of keyword or url provided
    link = ''
    if args.url:
        link = args.url
    elif args.keyword:
        link = 'wiki_link/' + args.keyword

    if args.url:
        print(f'Check Link status of {args.url} with depth {args.depth} on dark web')
    else:
        print(f'Check Link status of {args.keyword} with depth {args.depth} on dark web')

    # Clear the results directory for storing new data 
    clear_results_directory()

     # Dark web object creation
    dark_web_object =  BFSDarkWebCrawler(link, args.depth)
        
    # Start Tor Browser
    open_tor_browser()
        
    # Crawling
    result = dark_web_object.crawl()

    # Link status from result
    final_result = link_status_from_result(result)

    # Saving result into static/results.json
    save_json(final_result)
    
    
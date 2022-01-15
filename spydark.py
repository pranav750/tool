import argparse
from crawler.darkweb import DarkWebCrawler, MultiThreaded
from utils.functions import save_json, link_similarity

parser = argparse.ArgumentParser()

web = parser.add_mutually_exclusive_group()
web.add_argument('--dark', action = 'store_true', help = 'Specify if Dark Web Crawling needed')
web.add_argument('--surface', action = 'store_true', help = 'Specify if Surface Web Crawling needed')

url_or_keyword = parser.add_mutually_exclusive_group()
url_or_keyword.add_argument('--url', type = str, help = 'Specify the URL')
url_or_keyword.add_argument('--keyword', type = str, help = 'Specify the Keyword')

multi_or_iterative = parser.add_mutually_exclusive_group()
multi_or_iterative.add_argument('--multi', action = "store_true", help='Specify if multi-threaded crawling is required')
multi_or_iterative.add_argument('--iterative', action = "store_true", help='Specify if iterative crawling is required')

parser.add_argument('--depth', type=int, default=1, help='Specify the depth')

args = parser.parse_args()

if args.dark:
    print(f'Crawl {args.url} with depth {args.depth} on dark web')

    link = ''
    if args.url:
        link = args.url
    elif args.keyword:
        link = 'wiki_link/' + args.keyword

    if args.iterative: 
        dark_web_object =  DarkWebCrawler(link, args.depth)
        
        # Start Tor Browser
        os.startfile(TOR_BROWSER_PATH)
        time.sleep(10)
        print("Tor Browser started")
        
        result = dark_web_object.new_crawling()
        save_json(result)
    elif args.multi:
        dark_web_object = MultiThreaded(args.url, args.depth)
        time_diff, crawled_links = dark_web_object.run_scraper()
        print(time_diff)


        if args.json:
            save_json(crawled_links)
        elif args.database:
            pass

elif args.surface:
    print(f'Crawl {args.url} with depth {args.depth}on surface web')

elif args.ls:
    print (f'Link Similarity checking with depth 2')
    result = link_similarity(links, 2)
    save_json(result)
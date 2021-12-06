import argparse
from crawler_class import DarkWebCrawler

parser = argparse.ArgumentParser()

web = parser.add_mutually_exclusive_group()
web.add_argument('--dark', action='store_true', help='Specify if Dark Web Crawling needed')
web.add_argument('--surface', action='store_true', help='Specify if Surface Web Crawling needed')

parser.add_argument('--url', type=str, help='Specify the URL')
parser.add_argument('--depth', type=int, default=1, help='Specify the depth')


args = parser.parse_args()

if args.dark:
    print(f'Crawl {args.url} with depth {args.depth} on dark web')
    dark_web_object =  DarkWebCrawler()
    dark_web_object.new_crawling(args.url,args.depth)
elif args.surface:
    print(f'Crawl {args.url} with depth {args.depth}on surface web')

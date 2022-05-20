# Importing BFS crawler
from crawler.darkweb.bfs import BFSDarkWebCrawler

# Import from utils/status.py
from utils.status import links_from_result

def link_similarity(links, depth):

    crawled_links_of_url = dict()
        
    for link in links:

        # Dark web object creation
        dark_web_object = BFSDarkWebCrawler(link, depth)

        # Crawling
        result = dark_web_object.crawl()

        # Getting all the links from result
        crawled_links = links_from_result(result)

        # Putting links in dictionary
        crawled_links_of_url[link] = crawled_links

        # Final result
        result = dict()
        all_links = []

    # Putting all links in an array
    for crawled_links in crawled_links_of_url.values():
        for crawled_link in crawled_links:
            all_links.append(crawled_link)

    # Calculating each link percentage
    for link in all_links:
        count = 0
        result_object = dict()
        for url, links in crawled_links_of_url.items():
            if link in links:
                count += 1
                result_object[url] = True
            else:
                result_object[url] = False

        # Calculating the percentage of link found in the given links
        percent = round(count/len(crawled_links_of_url) * 100,2)
        result_object['percent'] = percent
        result[link] = result_object

    return result
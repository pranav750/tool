# Return an array of all the links present in crawled links
def links_from_result(darkweb_result):
    links = []

    for result in darkweb_result['crawled_links']:
        try:
            links.append(result['link'])
        except:
            pass

    return links

# Generate link status 
def link_status_from_result(darkweb_result):
    final_result = {
        'link': darkweb_result['link'],
        'active_links': darkweb_result['active_links'],
        'inactive_links': darkweb_result['inactive_links'],
        'link_statuses': dict()
    }

    for result in darkweb_result['crawled_links']:
        try:
            final_result['link_statuses'][result['link']] = result['link_status']
        except:
            pass

    return final_result
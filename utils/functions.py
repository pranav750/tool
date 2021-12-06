from datetime import datetime
import json
import os

def time_difference(start_time, end_time):
    time_diff = end_time - start_time
    minutes = divmod(time_diff.total_seconds(), 60) 
    return f'{int(minutes[0])} minutes, {int(minutes[1])} seconds'

def save_json(crawled_links):
    with open(os.path.join(os.path.dirname( __file__ ), '..', 'static', 'results.json'), 'w') as results:
        for crawled_link_object in crawled_links:
            json.dump(crawled_link_object, results)

def save_database(dictionary):
    pass
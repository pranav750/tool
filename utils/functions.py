from datetime import datetime
import json
import os

def time_difference(start_time, end_time):
    time_diff = end_time - start_time
    minutes = divmod(time_diff.total_seconds(), 60) 
    return f'{int(minutes[0])} minutes, {int(minutes[1])} seconds'

def save_json(dictionary):
    # dictionary = {
    #     "link": "sjdsa", 
    #     "active": 1,
    #     "inactive": 3,
    #     "crawled_links": [
    #         {
    #             "link": "fkjfda",
    #             "parent_link": "asdjbasd",
    #             "text": "sjbacba",
    #             "title": "dakdna"
    #         },
    #         {
    #             "link": "fkjfda",
    #             "parent_link": "asdjbasd",
    #             "text": "sjbacba",
    #             "title": "dakdna"
    #         }
    #     ]
    # }
    with open(os.path.join(os.path.dirname( __file__ ), '..', 'static', 'results.json'), 'w') as results:
        json.dump(dictionary, results)

def save_database(dictionary):
    pass
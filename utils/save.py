# Importing the required libraries
import os

# For saving the json data
import json  

# For saving the csv data
import csv

# Saving crawled data in results/results.json
def save_json(crawled_data):
    with open(os.path.join(os.path.dirname( __file__ ), '..', 'results', 'results.json'), 'w', encoding="utf-8") as results:
        json.dump(crawled_data, results)

# Saving crawled data in results/results.csv
def save_csv(crawled_data):
    crawled_links = crawled_data['crawled_links']
    fields = list(crawled_links[0].keys())
    
    with open(os.path.join(os.path.dirname( __file__ ), '..', 'results', 'results.csv'), 'w', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = fields)
        writer.writeheader()
        writer.writerows(crawled_links)

# Backup the data
def backup(crawled_data):
    print("Backing up the data...")
    save_json(crawled_data)
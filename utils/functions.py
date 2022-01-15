from wordcloud import WordCloud, STOPWORDS
import json
import os

def time_difference(start_time, end_time):
    time_diff = end_time - start_time
    minutes = divmod(time_diff.total_seconds(), 60) 
    return f'{int(minutes[0])} minutes, {int(minutes[1])} seconds'

def save_json(crawled_data):
    with open(os.path.join(os.path.dirname( __file__ ), '..', 'static', 'results.json'), 'w') as results:
        json.dump(crawled_data, results)

def create_wordcloud(crawled_links):
    texts = texts_from_result(crawled_links)
    wc_words = open(os.path.join(os.path.dirname( __file__ ), '..', 'static', 'wc_words.txt'), 'w', encoding = 'utf-8')
    for text in texts:
        try:
            wc_words.write(text + "\n")
        except:
            pass
        
    top_five_keywords = display_wordcloud(wc_words)
    return top_five_keywords


def display_wordcloud(wc_words):
    print("Generating Wordcloud...")
    stopwords = set(STOPWORDS)
    wordc = WordCloud(background_color = "white", width = 700, height = 350, stopwords = stopwords)
    wc_words.seek(0)
    
    wordc.generate(open(os.path.join(os.path.dirname( __file__ ), '..', 'static', 'wc_words.txt'), encoding = 'utf-8').read())
    wordc.to_file(os.path.join(os.path.dirname( __file__ ), '..', 'static', 'wc_img.png'))

    top_key_value_pairs = list(wordc.words_.items())[:5]

    wc_words.flush()
    wc_words.close()

    top_five_keywords = []
    for top_key_value_pair in top_key_value_pairs:
        top_five_keywords.append(top_key_value_pair[0])
    
    return top_five_keywords 

def texts_from_result(crawled_links):
    texts = []
    for result in crawled_links:
        try:
            texts.append(result['text'])
        except:
            pass

    return texts
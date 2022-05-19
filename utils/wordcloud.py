# Importing the required libraries
import os

# For creating word cloud
from wordcloud import WordCloud, STOPWORDS

# Return an array of text present in crawled links or an array of hashtags
def texts_from_result(crawled_links):
    texts = []

    for result in crawled_links:
        try:
            if 'text' in result.keys():
                texts.append(result['text'])
            elif 'hashtags' in result.keys():
                for hashtag in result['hashtags']:
                    texts.append(hashtag)
        except:
            pass

    return texts

# Display word cloud and find the top five keywords
def display_wordcloud(wc_words):
    print("Generating Wordcloud...")
    
    stopwords = set(STOPWORDS)
    wordc = WordCloud(background_color = "white", width = 700, height = 350, stopwords = stopwords)
    wc_words.seek(0)
    
    wordc.generate(open(os.path.join(os.path.dirname( __file__ ), '..', 'static', 'wc_words.txt'), encoding = 'utf-8').read())
    wordc.to_file(os.path.join(os.path.dirname( __file__ ), '..', 'results', 'wc_img.png'))

    top_key_value_pairs = list(wordc.words_.items())[:5]

    wc_words.flush()
    wc_words.close()

    top_five_keywords = []
    for top_key_value_pair in top_key_value_pairs:
        top_five_keywords.append(top_key_value_pair[0])

# Creating word cloud from the crawled links and returns the top five keywords
def create_wordcloud(crawled_links):
    texts = texts_from_result(crawled_links)
    wc_words = open(os.path.join(os.path.dirname( __file__ ), '..', 'static', 'wc_words.txt'), 'w', encoding = 'utf-8')

    for text in texts:
        try:
            wc_words.write(text + "\n")
        except:
            pass
        
    top_five_keywords = []

    if len(texts) == 0:
        print("No text found. Hence Wordcloud can't be generated...")
    else:
        top_five_keywords = display_wordcloud(wc_words)

    return top_five_keywords
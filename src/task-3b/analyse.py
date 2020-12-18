import re, os
from collections import defaultdict
from pymongo import MongoClient
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import pickle
import nltk
import nltk.collocations
import nltk.corpus
import wordcloud
import random

MONGO_DATABASE_NAME = 'jivitesh-task-3b'
PATH_OUT = '../../out/task-3b/'
PATH_DATA = '../../data/task-3b/'

client = MongoClient()
db = client[MONGO_DATABASE_NAME]

############### Plot top 10 tags ###############

tag_pop = defaultdict(int)

for post in db.posts.find({'PostTypeId': '1'}): # only look at questions
    if 'Tags' not in post.keys():
        continue
    tags = re.findall(r'[^<>]+', post['Tags'])
    for tag in tags:
        tag_pop[tag] += 1

df = pd.DataFrame.from_dict(tag_pop, orient='index')
df.sort_values(0, axis=0, ascending=False, inplace=True)
df.columns = ['Number of Questions']
df.to_pickle(os.path.join(PATH_OUT, 'bin/tag_count.pkl'))

ax = df[:10].plot.bar()
ax.set_xlabel('Tags')
ax.set_ylabel('Number of Questions')
ax.set_title('10 Most Popular Tags')
fig = plt.gcf()
# matplotlib styles depend on the local `matplotlibrc` and may vary
# from the presented output
plt.show()
fig.savefig(os.path.join(PATH_OUT, 'plots/top-10-occuring-tags.png'))



############### Generate a word cloud ###############

titles = []
for post in db.posts.find({'PostTypeId': '1'}):
    try:
        titles.append(post['Title'])
    except KeyError:
        pass

with open(os.path.join(PATH_OUT, 'bin/post_titles.pkl'), 'wb') as f:
    pickle.dump(titles, f)

# convert to lowercase and split into tokens
title_list = [t.lower().split() for t in titles]


# get Bigrams, filter away stop words to avoid phrases like 'how to',
# 'do I' and focus on technical terms and the topics being asked
# about
bigram_measures = nltk.collocations.BigramAssocMeasures()

finder = nltk.collocations.BigramCollocationFinder.from_documents(title_list)
finder.apply_freq_filter(10)
try:
    ignored_words = nltk.corpus.stopwords.words('english')
except LookupError:
    nltk.download('stopwords')
    ignored_words = nltk.corpus.stopwords.words('english')
finder.apply_word_filter(lambda w: w in ignored_words)

bigram_data = {}
for x in finder.score_ngrams(bigram_measures.likelihood_ratio)[:100]:
    word = ' '.join(x[0])
    bigram_data[word] = x[1]

with open(os.path.join(PATH_OUT, 'bin/topic_bigrams.pkl'), 'wb') as f:
    pickle.dump(bigram_data, f)

# get Trigrams, do not filter stop words, as we want to focus on
# phrases like 'How to prevent', 'How to enable' etc
trigram_measures = nltk.collocations.TrigramAssocMeasures()

finder = nltk.collocations.TrigramCollocationFinder.from_documents(title_list)
finder.apply_freq_filter(10)
trigram_data = {}
for x in finder.score_ngrams(trigram_measures.likelihood_ratio)[:100]:
    word = ' '.join(x[0])
    trigram_data[word] = x[1]

with open(os.path.join(PATH_OUT, 'bin/question_trigrams.pkl'), 'wb') as f:
    pickle.dump(trigram_data, f)


# plot the word cloud
# use color from two different maps to differentiate the two
# different types of data present
# roughly normalise the scores between the two data sets
text = bigram_data.copy()
for k, v in text.items():
    text[k] = v * 42 # arbitrarily chosen to get a good mix
text.update(trigram_data)

cmap_cool = mpl.cm.get_cmap('cool')
cmap_copper = mpl.cm.get_cmap('copper')

def get_color(word, *args, **kwargs):
    global cmap_cool
    global cmap_copper
    if len(word.split()) == 3:
        col = cmap_cool(random.uniform(0, 1))[:3]
    else:
        col = cmap_copper(random.uniform(0, 1))[:3]

    col = tuple([int(x * 255) for x in col])
    return col

# parameters chosen for visual appeal
# options (like custom fonts) that require external files
# have been ommitted
wc = wordcloud.WordCloud(background_color='white', max_words=1000,
                         min_font_size=10, max_font_size=60,
                         height=600, width=1000,
                         relative_scaling=0.2, scale=2,
                         prefer_horizontal=0.95, color_func=get_color)
wc.generate_from_frequencies(text)
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.show()
wc.to_file(os.path.join(PATH_OUT, 'plots/word-cloud.png'))

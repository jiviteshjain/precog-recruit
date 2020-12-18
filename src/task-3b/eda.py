# %%
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
# nltk.download('stopwords')
# %%
MONGO_DATABASE_NAME = 'jivitesh-task-3b'
PATH_OUT = '../../out/task-3b/'
PATH_DATA = '../../data/task-3b/'
# client = MongoClient()
# db = client[MONGO_DATABASE_NAME]



# %%
############### Plot top 10 tags ###############

# tag_pop = defaultdict(int)

# for post in db.posts.find({'PostTypeId': '1'}):
#     if 'Tags' not in post.keys():
#         continue
#     tags = re.findall('[^<>]+', post['Tags'])
#     for tag in tags:
#         tag_pop[tag] += 1

# df = pd.DataFrame.from_dict(tag_pop, orient='index')
# df.sort_values(0, axis=0, ascending=False, inplace=True)
# df.columns = ['Number of Questions']
# display(df[:10])
# df.to_pickle(os.path.join(PATH_OUT, 'bin/tag_count.pkl'))

# ax = df[:10].plot.bar()
# ax.set_xlabel('Tags')
# ax.set_ylabel('Number of Questions')
# ax.set_title('10 Most Popular Tags')
# fig = plt.gcf()
# plt.show()
# fig.savefig(os.path.join(PATH_OUT, 'plots/top-10-occuring-tags.png'))



# %%
titles = []
for post in db.posts.find({'PostTypeId': '1'}):
    try:
        titles.append(post['Title'])
    except KeyError:
        pass
# %%
print(titles[:10])
# %%
with open(os.path.join(PATH_OUT, 'bin/post_titles.pkl'), 'wb') as f:
    pickle.dump(titles, f)
# %%
client.close()



# %%
with open(os.path.join(PATH_OUT, 'bin/post_titles.pkl'), 'rb') as f:
    titles = pickle.load(f)
title_list = [t.lower().split() for t in titles]
print(title_list[:10])

# %%
bigram_measures = nltk.collocations.BigramAssocMeasures()
finder = nltk.collocations.BigramCollocationFinder.from_documents(title_list)
# %%
finder.apply_freq_filter(10)
ignored_words = nltk.corpus.stopwords.words('english')
finder.apply_word_filter(lambda w: w in ignored_words)
# %%
best = finder.nbest(bigram_measures.pmi, 100)
print(best)
# %%
best = finder.nbest(bigram_measures.likelihood_ratio, 100)
print(best)
# %%
for i in finder.score_ngrams(bigram_measures.raw_freq)[:100]:
    print(i)
# %%

trigram_measures = nltk.collocations.TrigramAssocMeasures()
finder = nltk.collocations.TrigramCollocationFinder.from_documents(title_list)
finder.apply_freq_filter(10)
ignored_words = nltk.corpus.stopwords.words('english')
finder.apply_word_filter(lambda w: w.lower() in ignored_words)
for i in finder.score_ngrams(trigram_measures.likelihood_ratio)[:100]:
    print(i)

# %%
quadgram_measures = nltk.collocations.QuadgramAssocMeasures()
finder = nltk.collocations.QuadgramCollocationFinder.from_documents(title_list)
finder.apply_freq_filter(10)

# %%
for i in finder.score_ngrams(quadgram_measures.likelihood_ratio)[:100]:
    print(i)

# %%
# HERE
bigram_data = {}
for x in finder.score_ngrams(bigram_measures.likelihood_ratio)[:100]:
    word = ' '.join(x[0])
    bigram_data[word] = x[1]
print(bigram_data)

# %%
with open(os.path.join(PATH_OUT, 'bin/topic_bigrams.pkl'), 'wb') as f:
    pickle.dump(bigram_data, f)
# %%

trigram_measures = nltk.collocations.TrigramAssocMeasures()
finder = nltk.collocations.TrigramCollocationFinder.from_documents(title_list)
finder.apply_freq_filter(10)
# ignored_words = nltk.corpus.stopwords.words('english')
# finder.apply_word_filter(lambda w: w.lower() in ignored_words)
for i in finder.score_ngrams(trigram_measures.likelihood_ratio)[:100]:
    print(i)

# %%
trigram_data = {}
for x in finder.score_ngrams(trigram_measures.likelihood_ratio)[:100]:
    word = ' '.join(x[0])
    trigram_data[word] = x[1]
print(trigram_data)

# %%
with open(os.path.join(PATH_OUT, 'bin/question_trigrams.pkl'), 'wb') as f:
    pickle.dump(trigram_data, f)

# %%
text = bigram_data.copy()
for k, v in text.items():
    text[k] = v * 42
text.update(trigram_data)
wc = wordcloud.WordCloud(background_color='white', max_words=1000, min_font_size=10, max_font_size=60, height=600, width=1000, relative_scaling=0.2, scale=2, prefer_horizontal=0.95, color_func=get_color, font_path='Proxima-Nova-Bold.otf')
wc.generate_from_frequencies(text)
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.show()
# %%

cmap = mpl.cm.get_cmap('cool')

cmap2 = mpl.cm.get_cmap('copper')

# %%
def get_color(word, *args, **kwargs):
    global cmap
    global cmap2
    if len(word.split()) == 3:
        col = cmap(random.uniform(0, 1))[:3]
    else:
        col = cmap2(random.uniform(0, 1))[:3]
    
    col = tuple([int(x * 255) for x in col])
    return col
# %%
wc.to_file(os.path.join(PATH_OUT, 'plots/word-cloud-2.png'))
# %%
svg = wc.to_svg(embed_font=True)
# %%

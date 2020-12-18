import re, os
from collections import defaultdict
from pymongo import MongoClient
import pymongo
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
import seaborn as sns

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



###############  Scatter plot of proportion  ###############
############### of upvotes given vs received ###############

users_top = db.users.find().sort(
    'Reputation', pymongo.DESCENDING).skip(100000).limit(10000)

user_data = []
for user in users_top:
    try:
        temp = {}
        temp['UserId'] = user['Id']
        temp['Reputation'] = user['Reputation']
        temp['UpvotesGiven'] = user['UpVotes']
        temp['DownvotesGiven'] = user['DownVotes']

        posts = db.posts.find({'OwnerUserId': user['Id']})
        positive = 0
        negative = 0
        for post in posts:
            positive += db.votes.find(
                {'$and': [{'PostId': post['Id']}, {'VoteTypeId': '2'}]}).count()
            negative += db.votes.find(
                {'$and': [{'PostId': post['Id']}, {'VoteTypeId': '3'}]}).count()
        temp['UpvotesReceived'] = positive
        temp['DownvotesReceived'] = negative
    except KeyError:
        continue
    user_data.append(temp)

for x in user_data:
    x['UpvotesReceived'] = int(x['UpvotesReceived'])
    x['UpvotesGiven'] = int(x['UpvotesGiven'])
    x['DownvotesReceived'] = int(x['DownvotesReceived'])
    x['DownvotesGiven'] = int(x['DownvotesGiven'])

    if x['UpvotesReceived'] + x['DownvotesReceived'] == 0:
        x['ReceivedRatio'] = 0
    else:
        x['ReceivedRatio'] = x['UpvotesReceived'] / \
            (x['UpvotesReceived'] + x['DownvotesReceived'])

    if x['UpvotesGiven'] + x['DownvotesGiven'] == 0:
        x['GivenRatio'] = 0
    else:
        x['GivenRatio'] = x['UpvotesGiven'] / \
            (x['UpvotesGiven'] + x['DownvotesGiven'])

df = pd.DataFrame.from_records(user_data)
df = df.assign(TotalReceived=lambda x: x.UpvotesReceived + x.DownvotesReceived)
df = df.assign(TotalGiven=lambda x: x.UpvotesGiven + x.DownvotesGiven)
filtered_df = df[df.TotalGiven > 20]
filtered_df = df[df.TotalReceived > 20]
ax = filtered_df.plot.scatter(x='ReceivedRatio', y='GivenRatio')
ax.set_xlabel('Proportion of upvotes received')
ax.set_ylabel('Proportion of upvotes given')
ax.set_title('No Tit For Tat?')
fig = plt.gcf()
plt.show()
fig.patch.set_facecolor('white')
fig.savefig(os.path.join(PATH_OUT, 'plots/vote-ratio.png'), dpi=200)


############### Distribution of scores of  ###############
############### accepted and other answers ###############

questions = {}
for post in db.posts.find({'PostTypeId': '1'}):
    try:
        post_id = post['Id'],
        answer_id = post['AcceptedAnswerId']
    except KeyError:
        continue
    questions[post_id] = answer_id

answers = []
for post in db.posts.find({'PostTypeId': '2'}):
    try:
        temp = {
            'Id': post['Id'],
            'Score': post['Score'],
            'ParentId': post['ParentId']
        }
    except KeyError:
        continue
    answers.append(temp)

for a in answers:
    p = a['ParentId']
    a['Accepted'] = p in questions and questions[p] == a['Id']

df = pd.DataFrame.from_records(answers)
df['Score'] = df['Score'].astype(int)
filtered_df = df[np.abs(df.Score - df.Score.mean()) <= 3 * df.Score.std()]
ax = sns.kdeplot(data=filtered_df, x='Score', hue='Accepted',
                 fill=True, hue_order=(True, False))
ax.set_xlim((-5, 15))
ax.set_title('Answer Score Distribution')
fig = plt.gcf()
fig.patch.set_facecolor('white')
fig.savefig(os.path.join(PATH_OUT, 'plots/score-densities.png'), dpi=200)
plt.show()

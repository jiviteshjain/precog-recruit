# %%
import re, os
from collections import defaultdict
from pymongo import MongoClient
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import pickle
import pymongo
from scipy.stats import zscore
import seaborn as sns
# import nltk
# import nltk.collocations
# import nltk.corpus
# import wordcloud
# import random
# nltk.download('stopwords')
# %%
MONGO_DATABASE_NAME = 'jivitesh-task-3b'
PATH_OUT = '../../out/task-3b/'
PATH_DATA = '../../data/task-3b/'
client = MongoClient()
db = client[MONGO_DATABASE_NAME]



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
# titles = []
# for post in db.posts.find({'PostTypeId': '1'}):
#     try:
#         titles.append(post['Title'])
#     except KeyError:
#         pass
# # %%
# print(titles[:10])
# # %%
# with open(os.path.join(PATH_OUT, 'bin/post_titles.pkl'), 'wb') as f:
#     pickle.dump(titles, f)
# # %%
# client.close()



# # %%
# with open(os.path.join(PATH_OUT, 'bin/post_titles.pkl'), 'rb') as f:
#     titles = pickle.load(f)
# title_list = [t.lower().split() for t in titles]
# print(title_list[:10])

# # %%
# bigram_measures = nltk.collocations.BigramAssocMeasures()
# finder = nltk.collocations.BigramCollocationFinder.from_documents(title_list)
# # %%
# finder.apply_freq_filter(10)
# ignored_words = nltk.corpus.stopwords.words('english')
# finder.apply_word_filter(lambda w: w in ignored_words)
# # %%
# best = finder.nbest(bigram_measures.pmi, 100)
# print(best)
# # %%
# best = finder.nbest(bigram_measures.likelihood_ratio, 100)
# print(best)
# # %%
# for i in finder.score_ngrams(bigram_measures.raw_freq)[:100]:
#     print(i)
# # %%

# trigram_measures = nltk.collocations.TrigramAssocMeasures()
# finder = nltk.collocations.TrigramCollocationFinder.from_documents(title_list)
# finder.apply_freq_filter(10)
# ignored_words = nltk.corpus.stopwords.words('english')
# finder.apply_word_filter(lambda w: w.lower() in ignored_words)
# for i in finder.score_ngrams(trigram_measures.likelihood_ratio)[:100]:
#     print(i)

# # %%
# quadgram_measures = nltk.collocations.QuadgramAssocMeasures()
# finder = nltk.collocations.QuadgramCollocationFinder.from_documents(title_list)
# finder.apply_freq_filter(10)

# # %%
# for i in finder.score_ngrams(quadgram_measures.likelihood_ratio)[:100]:
#     print(i)

# # %%
# # HERE
# bigram_data = {}
# for x in finder.score_ngrams(bigram_measures.likelihood_ratio)[:100]:
#     word = ' '.join(x[0])
#     bigram_data[word] = x[1]
# print(bigram_data)

# # %%
# with open(os.path.join(PATH_OUT, 'bin/topic_bigrams.pkl'), 'wb') as f:
#     pickle.dump(bigram_data, f)
# # %%

# trigram_measures = nltk.collocations.TrigramAssocMeasures()
# finder = nltk.collocations.TrigramCollocationFinder.from_documents(title_list)
# finder.apply_freq_filter(10)
# # ignored_words = nltk.corpus.stopwords.words('english')
# # finder.apply_word_filter(lambda w: w.lower() in ignored_words)
# for i in finder.score_ngrams(trigram_measures.likelihood_ratio)[:100]:
#     print(i)

# # %%
# trigram_data = {}
# for x in finder.score_ngrams(trigram_measures.likelihood_ratio)[:100]:
#     word = ' '.join(x[0])
#     trigram_data[word] = x[1]
# print(trigram_data)

# # %%
# with open(os.path.join(PATH_OUT, 'bin/question_trigrams.pkl'), 'wb') as f:
#     pickle.dump(trigram_data, f)

# # %%
# text = bigram_data.copy()
# for k, v in text.items():
#     text[k] = v * 42
# text.update(trigram_data)
# wc = wordcloud.WordCloud(background_color='white', max_words=1000, min_font_size=10, max_font_size=60, height=600, width=1000, relative_scaling=0.2, scale=2, prefer_horizontal=0.95, color_func=get_color, font_path='Proxima-Nova-Bold.otf')
# wc.generate_from_frequencies(text)
# plt.imshow(wc, interpolation='bilinear')
# plt.axis('off')
# plt.show()
# # %%

# cmap = mpl.cm.get_cmap('cool')

# cmap2 = mpl.cm.get_cmap('copper')

# # %%
# def get_color(word, *args, **kwargs):
#     global cmap
#     global cmap2
#     if len(word.split()) == 3:
#         col = cmap(random.uniform(0, 1))[:3]
#     else:
#         col = cmap2(random.uniform(0, 1))[:3]
    
#     col = tuple([int(x * 255) for x in col])
#     return col
# # %%
# wc.to_file(os.path.join(PATH_OUT, 'plots/word-cloud-2.png'))
# # %%
# svg = wc.to_svg(embed_font=True)


# %%
post_data2 = []
for post in db.posts.find({'OwnerUserId': '114672'}):
    try:
        temp = {}
        temp['Id'] = post['Id']
        temp['PostTypeId'] = post['PostTypeId']
        temp['Score'] = post['Score']
        temp['CreationDate'] = post['CreationDate']
        positive = 0
        negative = 0
        for vote in db.votes.find({'PostId': post['Id']}):
            if vote['VoteTypeId'] == '2':
                positive+=1
            elif vote['VoteTypeId'] == '3':
                negative+=1

        temp['PositiveVotes'] = positive
        temp['NegativeVotes'] = negative
    
    except KeyError:
        print('F')
        continue

    post_data2.append(temp)
# %%
print(len(post_data2))
# %%
for post in post_data2:
    p = post['PositiveVotes']
    n = post['NegativeVotes']
    if p+n == 0:
        post['VoteRatio'] = 0
    else:
        post['VoteRatio'] = p / (p + n)
# %%
df = pd.DataFrame.from_records(post_data2)
# %%
display(df)
# %%
df.info()
# %%
df['CreationDate'] = pd.to_datetime(df['CreationDate'])
# %%
ax = df[df.TotalVotes > 100].plot.line(x='CreationDate', y='VoteRatio')
plt.show()
# %%
df.VoteRatio.plot(kind='kde')
plt.show()
# %%
df = df.assign(TotalVotes=lambda x: x.PositiveVotes + x.NegativeVotes)
# %%
df[df.TotalVotes < 2000].TotalVotes.plot(kind='hist')
plt.show()
# %%
dday = df[df.Id == '2052396'].CreationDate.dt.to_pydatetime()[0]
dday
# %%
df[df.CreationDate > dday].agg({'VoteRatio': [np.mean]})
# %%
df[df.Id == '2052396']
# %%

users_top = db.users.find().sort('Reputation', pymongo.DESCENDING).skip(100000).limit(10000)
# users_bottom = db.users.find().sort('Reputation', pymongo.ASCENDING).skip(100000).limit(5000)
# %%
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
            positive += db.votes.find({'$and': [{'PostId': post['Id']}, {'VoteTypeId': '2'}]}).count()
            negative += db.votes.find({'$and': [{'PostId': post['Id']}, {'VoteTypeId': '3'}]}).count()
        temp['UpvotesReceived'] = positive
        temp['DownvotesReceived'] = negative
    except KeyError:
        print('F')
        continue
    user_data.append(temp)

# %%
df = pd.DataFrame.from_records(user_data)
display(df)
# %%
df.info()
# %%
for x in user_data:
    x['UpvotesReceived'] = int(x['UpvotesReceived'])
    x['UpvotesGiven'] = int(x['UpvotesGiven'])
    x['DownvotesReceived'] = int(x['DownvotesReceived'])
    x['DownvotesGiven'] = int(x['DownvotesGiven'])

    if x['UpvotesReceived'] + x['DownvotesReceived'] == 0:
        x['ReceivedRatio'] = 0
    else:
        x['ReceivedRatio'] = x['UpvotesReceived'] / (x['UpvotesReceived'] + x['DownvotesReceived'])

    if x['UpvotesGiven'] + x['DownvotesGiven'] == 0:
        x['GivenRatio'] = 0
    else:
        x['GivenRatio'] = x['UpvotesGiven'] / \
            (x['UpvotesGiven'] + x['DownvotesGiven'])


# %%
ax = filtered_df.plot.scatter(x='ReceivedRatio', y='GivenRatio')
ax.set_xlabel('Proportion of upvotes received')
ax.set_ylabel('Proportion of upvotes given')
ax.set_title('No Tit For Tat?')
fig = plt.gcf()
plt.show()
fig.patch.set_facecolor('white')
fig.savefig(os.path.join(PATH_OUT, 'plots/vote-ratio.png'), dpi=200)
# %%
df = df.assign(TotalReceived=lambda x: x.UpvotesReceived + x.DownvotesReceived)
# %%
df = df.assign(TotalGiven=lambda x: x.UpvotesGiven + x.DownvotesGiven)

# %%
filtered_df = df[df.TotalGiven > 20]
filtered_df.info()
# %%
filtered_df = df[df.TotalReceived > 20]
filtered_df.info()

# %%
#########################################

questions = []

for post in db.posts.find({'PostTypeId': '1'}):
    try:
        temp = {
            'Id': post['Id'],
            'AcceptedAnswerId': post['AcceptedAnswerId']
        }
    except KeyError:
        continue
    questions.append(temp)
# %%
len(questions)
# %%
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
len(answers)
# %%
ques_dict = {}
for q in questions:
    ques_dict[q['Id']] = q['AcceptedAnswerId']
# %%
for a in answers:
    p = a['ParentId']
    a['Accepted'] = p in ques_dict and ques_dict[p] == a['Id']
# %%
df = pd.DataFrame.from_records(answers)
display(df)
# %%
ax = filtered_df.groupby('Accepted').Score.plot(kind='kde')
plt.legend()
plt.show()
# %%
df.info()
# %%
df['Score'] = df['Score'].astype(int)
# %%
df.describe()
# %%
z_sc = np.abs(zscore(df))
# %%

df.Score.mean()
# %%
filtered_df = df[np.abs(df.Score - df.Score.mean()) <= 3 * df.Score.std()]
# %%
ax = df.groupby('Accepted').Score.plot.kde(bw_method=0.1)
# ax.set_xlim((-50, 50))
plt.legend()
fig = plt.gcf()
ax = plt.gca()
ax.set_xlim((-40, 100))
plt.show()

# %%
df.count()
# %%
df['Accepted' == True].count()
# %%
# df[df.Accepted == False].Accepted = 'No'
display(df)
# %%
filtered_df = filtered_df.sample(frac=1).reset_index(drop=True)
display(filtered_df)
# %%
ax = sns.kdeplot(data=filtered_df, x='Score', hue='Accepted', fill=True, hue_order=(True, False))
ax.set_xlim((-5, 15))
ax.set_title('Answer Score Distribution')
fig = plt.gcf()
fig.patch.set_facecolor('white')
fig.savefig(os.path.join(PATH_OUT, 'plots/score-densities.png'), dpi=200)
plt.show()
# %%
df.describe()
# %%

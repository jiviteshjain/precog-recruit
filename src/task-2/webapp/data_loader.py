# %%
import json
import os
import re
from pprint import pprint

import numpy as np
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

FILE_PATH = 'data/main_tweets_utf.json'
TWITTER_HANDLE_REGEX = '@\\w{1,15}'
URL_REGEX = 'https?://[A-Za-z0-9./]*'

# %%
def load_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        tweets_json = json.load(f)
    return pd.DataFrame.from_records(tweets_json)

#############################################

def process_for_lang(df):
    lang_counts = df.groupby('lang')['id'].count().to_frame().reset_index()
    lang_counts.columns = ['lang', 'count']
    lang_counts.sort_values(by='count', inplace=True, ascending=False)
    lang_counts.iloc[10:, :].loc[:, 'lang'] = 'other'

    values = lang_counts['count'].tolist()
    labels = lang_counts['lang'].tolist()
    return [{
        'type': 'pie',
        'values': values,
        'labels': labels,
    }, ]

#############################################

def process_for_user(df):
    filtered_df = df[['id', 'retweet_count',
                      'favorite_count', 'user', 'created_at', 'text']]
    filtered_df = filtered_df.assign(user_id=lambda x: x.user.apply(lambda y: y['id']),
                                    user_followers_count=lambda x: x.user.apply(
                                        lambda y: y['followers_count']),
                                    user_friends_count=lambda x: x.user.apply(
                                        lambda y: y['friends_count']),
                                    user_favorites_count=lambda x: x.user.apply(
                                        lambda y: y['favourites_count']),
                                    user_verified=lambda x: x.user.apply(
                                        lambda y: y['verified']),
                                    user_listed_count=lambda x: x.user.apply(
                                        lambda y: y['listed_count']),
                                    user_statuses_count=lambda x: x.user.apply(
                                        lambda y: y['statuses_count']),
                                    user_created_at=lambda x: x.user.apply(lambda y: y['created_at']))
    user_df = filtered_df[['user_id', 'user_followers_count', 'user_friends_count', 'user_favorites_count', 'user_listed_count',
                           'user_verified', 'user_statuses_count', 'user_created_at']].drop_duplicates(subset='user_id', ignore_index=True)
    user_df.set_index(keys='user_id', inplace=True, verify_integrity=True)
    agg_df = filtered_df[['user_id', 'retweet_count', 'favorite_count']]
    agg_df = agg_df.groupby('user_id').agg('mean')
    agg_df.columns = ['avg_retweet_count', 'avg_favorite_count']
    user_df = user_df.join(agg_df, how='inner')
    corr = user_df.corr()
    x = corr.columns.tolist()
    y = corr.columns.tolist()
    z = corr.to_numpy().tolist()
    
    data_corr = [{
        'colorscale': 'Greens',
        'type': 'heatmap',
        'x': x,
        'y': y,
        'z': z,
    }, ]

    data_ff = [
        {
            'type': 'histogram',
            'opacity': 0.8,
            'x': user_df['user_followers_count'].tolist(),
            'name': 'Followers',
            'xbins': {
                'start': 0,
                'end': 100000,
                'size': 100
            },
            'autobinx': False,
            'marker': {
                'color': 'rgba(174, 63, 89, 0.6)',
                'line': {
                    'color':  'rgba(174, 63, 89, 1)',
                    'width': 1
                }
            },
        },
        {
            'type': 'histogram',
            'opacity': 0.8,
            'x': user_df['user_friends_count'].tolist(),
            'name': 'Friends',
            'autobinx': True,
            'marker': {
                'color': 'rgba(247, 168, 124, 0.69)',
                'line': {
                    'color':  'rgba(247, 168, 124, 1)',
                    'width': 1
                }
            },
        },
    ]

    data_act = [
        {
            'type': 'histogram',
            'opacity': 1,
            'x': user_df['user_statuses_count'].tolist(),
            'name': 'Tweet Activity',
            'marker': {
                'color': 'rgba(88, 100, 253, 0.69)',
                'line': {
                    'color':  'rgba(88, 100, 253, 83, 1)',
                    'width': 1
                }
            },
            'xbins': {
                'start': 0,
                'end': 500000,
                'size': 1000
            },
            'autobinx': False,
        },
        {
            'type': 'histogram',
            'opacity': 0.5,
            'x': user_df['user_favorites_count'].tolist(),
            'name': 'Liked Posts',
            'marker': {
                'color': 'rgba(240, 83, 83, 0.69)',
                'line': {
                    'color':  'rgba(240, 83, 83, 1)',
                    'width': 1
                }
            },
            'xbins': {
                'start': 0,
                'end': 500000,
                'size': 1000
            },
            'autobinx': False,
        },
        # {
        #     'type': 'histogram',
        #     'opacity': 0.6,
        #     'x': user_df['user_listed_count'].tolist(),
        #     'name': 'Presence on Lists',
        #     'xaxis': 'x2',
        # },
    ]
    return data_corr, data_ff, data_act

#############################################

def filter_pattern(text, pattern):
    match = re.findall(pattern, text)
    for m in match:
        text = re.sub(m, ' ', text)
    return text

def calc_sentiment(text, senti):
    res = senti.polarity_scores(text)
    return res['neg'], res['neu'], res['pos'], res['compound']

def categorise_sentiment(val):
    # based on official paper: https://github.com/cjhutto/vaderSentiment#about-the-scoring
    if val >= 0.05:
        return 'Positive'
    elif val > -0.05:
        return 'Neutral'
    else:
        return 'Negative'

def process_for_sentiment(df):
    text_df = df[['text', 'lang', 'id', 'created_at']]
    text_df['created_at'] = pd.to_datetime(text_df['created_at'])
    text_df = text_df[text_df.lang == 'en']
    try:
        senti = SentimentIntensityAnalyzer()
    except LookupError:
        nltk.download('vader_lexicon')
        senti = SentimentIntensityAnalyzer()
    
    text_df['text'] = text_df['text'].apply(filter_pattern, args=(TWITTER_HANDLE_REGEX, ))
    text_df['text'] = text_df['text'].apply(filter_pattern, args=(URL_REGEX, ))

    scores = text_df['text'].apply(calc_sentiment, args=(senti, )).apply(pd.Series)
    scores.columns = ['negative', 'neutral', 'positive', 'compound']
    text_df = text_df.join(scores, how='left')  # on default index
    text_df['sentiment'] = text_df['compound'].apply(categorise_sentiment)

#############################################

def get_centroid(place):
    return np.array(place['bounding_box']['coordinates'][0], dtype=np.float64).mean(axis=0)

def process_for_places(df):
    place_df = df[df.place.notnull()][['place', 'lang']]
    centroid_df = place_df['place'].apply(get_centroid).apply(pd.Series)
    centroid_df.columns = ['longitude', 'latitude']
    place_df['lang'] = place_df['lang'].apply(lambda x: x.upper())
    centroid_df = centroid_df.join(place_df['lang'], how='inner') # on index
    res = []
    for name, group in centroid_df.groupby('lang'):
        res.append({
            'type': 'scattergeo',
            'name': name,
            'lat': group.latitude.tolist(),
            'lon': group.longitude.tolist(),
            'hoverinfo': 'name'
        })
    return res

#############################################

def get_all():
    df = load_file(FILE_PATH)
    data_lang = process_for_lang(df)
    data_corr, data_ff, data_act = process_for_user(df)
    data_places = process_for_places(df)
    return {
        'lang': data_lang,
        'corr': data_corr,
        'ff': data_ff,
        'act': data_act,
        'places': data_places,
    }

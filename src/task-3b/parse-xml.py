#%%
from lxml import etree
import json
from pymongo import MongoClient

# %%
MONGO_DATABASE_NAME = 'jivitesh-task-3b'
FILE_PATH = '../../data/task-3b/Posts.xml'
COLLECTION_NAME = 'posts'
COUNT = 0
# %%
def fast_iter(context, callback, *args, **kwargs):

    for event, ele in context:
        callback(ele, *args, **kwargs)
        # It's safe to call clear here because no descendants will be accessed
        ele.clear()
        # Also eliminate now-empty references from the root node to ele
        for ancestor in ele.xpath('ancestor-or-self::*'):
            while ancestor.getprevious() is not None:
                del ancestor.getparent()[0]
    del context

def handle_row(ele, collection):
    global COUNT
    data = dict(ele.attrib)
    ins_id = collection.insert_one(data).inserted_id
    if COUNT % 10000 == 0:
        print(ins_id, COUNT)
    COUNT+=1

# %%
client = MongoClient()
db = client[MONGO_DATABASE_NAME]
collection = db[COLLECTION_NAME]


# %%
context = etree.iterparse(FILE_PATH, tag='row')
fast_iter(context, handle_row, collection)
# %%

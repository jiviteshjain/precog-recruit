#%%
import argparse
import camelot
import pandas as pd
from pymongo import MongoClient
from collections.abc import MutableMapping
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)
pd.set_option('display.max_colwidth', -1)
# %%
def stringify_keys(obj):
    if not isinstance(obj, MutableMapping):
        return obj
    temp = {}
    for key, val in obj.items():
        temp[str(key)] = stringify_keys(val)
    return temp

def parse_keys(obj):
    if not isinstance(obj, MutableMapping):
        return obj
    temp = {}
    for key, val in obj.items():
        try:
            parsed_key = int(key)
        except (TypeError, ValueError):
            parsed_key = key
        temp[parsed_key] = parse_keys(val)
    return temp
# %%

tables = camelot.read_pdf('../../data/task-3a/EICHERMOT.pdf',
                          flavor='stream', table_areas=['0,570,300,500'], row_tol=14, strip_text='\n')
print(tables)

# %%
display(tables[0].df)
# %%

camelot.plot(tables[0], kind='text').show()


# %%
# df = tables[0].df
# display(df)
# df.columns = df.iloc[0]
# df = df.drop(df.index[0])
# df.reset_index(inplace=True, drop=True)
# display(df)
# obj = df.to_dict('records')
# print(obj)
# pdf = pd.DataFrame.from_dict(obj)
# display(pdf)
# print(obj)

df = tables[0].df
display(df)
obj = stringify_keys(df.to_dict())
print(obj)
pdf = pd.DataFrame.from_dict(parse_keys(obj))
display(df)

# %%
client = MongoClient()
db = client.test_database
collection = db.table_1
collection.insert_one(obj).inserted_id
# print(obj)
# %%
obj = parse_keys(collection.find_one({}, {'_id': False}))
pdf = pd.DataFrame.from_dict(obj)
display(pdf)














# %%
raise SystemExit
tables = camelot.read_pdf('../../data/task-3a/EICHERMOT.pdf',
                          flavor='stream', table_areas=['0,570,300,500'], row_tol=14, strip_text='\n')  # Eichermot left
tables = camelot.read_pdf('../../data/task-3a/EICHERMOT.pdf',
                          flavor='stream', table_areas=['310,650,595,550'], row_tol=14, strip_text='\n') # Eichermot right
tables = camelot.read_pdf('../../data/task-3a/EICHERMOT.pdf',
                          flavor='stream', row_tol=14)[1] # Eichermot bottom requires col spec
tables = camelot.read_pdf('../../data/task-3a/d9f8e6d9-660b-4505-86f9-952e45ca6da0.pdf',
                          flavor='lattice') # d9f requires col spec
tables = camelot.read_pdf('../../data/task-3a/1c1edeee-a13e-4b2e-90be-eb1dd03c3384.pdf',
                          flavor='lattice') # 1c1 top extra row
tables = camelot.read_pdf('../../data/task-3a/1c1edeee-a13e-4b2e-90be-eb1dd03c3384.pdf',
                          flavor='stream', table_areas=['0,480,590,420'], row_tol=14) # 1c1 bottom
tables = camelot.read_pdf('../../data/task-3a/a6b29367-f3b7-4fb1-a2d0-077477eac1d9.pdf',
                          flavor='lattice', line_scale=20) # a6b main
tables = camelot.read_pdf('../../data/task-3a/a6b29367-f3b7-4fb1-a2d0-077477eac1d9.pdf',
                          flavor='stream', table_areas=['0,650,590,550'], row_tol=100) # a6b address

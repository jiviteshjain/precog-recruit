import argparse, os, warnings, copy
import camelot
import pandas as pd
from pymongo import MongoClient
from collections.abc import MutableMapping

LATTICE_SPECIFIC = ('line_scale', 'shift_text', 'copy_text', )
STREAM_SPECIFIC = ('edge_tol', 'row_tol', )
ACC_THRESH = 70

def pop_specific(obj, keys):
    obj = copy.deepcopy(obj)
    for key in keys:
        if key in obj:
            obj.pop(key)
    return obj


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


def pdf_to_table(filename, flavor='auto', extras=None):
    if flavor not in ('auto', 'lattice', 'stream'):
        raise ValueError('"flavor" must be one of "auto", "lattice" or "stream".')
    
    if flavor != 'auto':
        tables = camelot.read_pdf(filename, flavor=flavor, **extras)
    else:
        tables = camelot.read_pdf(filename, flavor='lattice', **pop_specific(extras, STREAM_SPECIFIC))
        if len(tables) == 0:
            warnings.warn('No matches found with lattice, trying stream.')
            tables = camelot.read_pdf(filename, flavor='stream', **pop_specific(extras, LATTICE_SPECIFIC))

    bad_acc = False
    for t in tables:
        if t.parsing_report['accuracy'] < ACC_THRESH:
            bad_acc = True
            break
    if bad_acc:
        warnings.warn('Poor accuracy registered on some of the tables. Consider tweaking the extraction settings.')

    return tables

def print_tables(tables, filename):
    print(f'{len(tables)} TABLES PARSED FROM {filename}\n')
    
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.max_columns', 10)
    pd.set_option('display.width', 150)
    pd.set_option('display.max_colwidth', -1)

    for i, table in enumerate(tables):
        df = table if isinstance(table, pd.DataFrame) else table.df
        print(f'Table {i}: {df.shape[0]} rows, {df.shape[1]} cols')
        print(df)
        print('---')

    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.max_colwidth')


def tables_to_mongo(tables, filename, db):
    collection = db[filename]
    res = []
    for i, table in enumerate(tables):
        table_dict = stringify_keys(table.df.to_dict())
        res.append(collection.insert_one({'name': f'table_{i}', 'data': table_dict}).inserted_id)
    return res

def tables_from_mongo(filename, db, idx=-1):
    collection = db[filename]

    if idx < 0:
        tables = collection.find({}, {'_id': False, 'name': False})
        res = []
        for table in tables:
            res.append(pd.DataFrame.from_dict(parse_keys(table)))
        return res
    
    else:
        table = collection.find_one({'name': f'table_{idx}'}, {'_id': False, 'name': False})
        table = pd.DataFrame.from_dict(parse_keys(table))
        return [table, ]

def pipeline():
    pass
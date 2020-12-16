#%%
import argparse, os, warnings, copy
import camelot
import pandas as pd
from tabulate import tabulate
from pymongo import MongoClient
from collections.abc import MutableMapping

LATTICE_SPECIFIC = ('line_scale', 'shift_text', 'copy_text', )
STREAM_SPECIFIC = ('edge_tol', 'row_tol', )
ACC_THRESH = 70
PARSE_CONFIG = {}

#%%
def pop_specific(obj, keys):
    obj = copy.deepcopy(obj)
    for key in keys:
        if key in obj:
            obj.pop(key)
    return obj

def process_args(args):
    res = {}
    for arg in args:
        try:
            res[arg[0]] = int(arg[1])
        except IndexError:
            pass
        except (TypeError, ValueError):
            res[arg[0]] = arg[1]
    return res

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


def pdf_to_table(filename, flavor='auto', extras={}):
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
    print(f'{len(tables)} TABLE(S) PARSED FROM {filename}\n')

    for i, table in enumerate(tables):
        df = table if isinstance(table, pd.DataFrame) else table.df
        print(f'Table {i}: {df.shape[0]} rows, {df.shape[1]} cols')
        print(tabulate(df, headers='keys', tablefmt='fancy_grid'))

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
            res.append(pd.DataFrame.from_dict(parse_keys(table['data'])))
        return res
    
    else:
        table = collection.find_one({'name': f'table_{idx}'}, {'_id': False, 'name': False})
        if table is None:
            return []
        table = pd.DataFrame.from_dict(parse_keys(table['data']))
        return [table, ]

def pipeline(filename, db, flavor='auto', extras={}, verbose=True):
    pdfname = os.path.splitext(os.path.basename(filename))[0]

    if verbose:
        print('PARSING FILES...')
    tables = pdf_to_table(filename, flavor=flavor, extras=extras)
    print_tables(tables, pdfname)

    if verbose:
        print(f'\nSTORING INTO MONGODB {db.name}.{pdfname} ...')
    ids = tables_to_mongo(tables, pdfname, db)
    if verbose:
        print('MONGODB OBJECT ID(S):')
        for i in ids:
            print(i)

    if verbose:
        print('\nRETRIEVING FROM MONGODB...')
        retr_tables = tables_from_mongo(pdfname, db)
        print(f'{len(retr_tables)} TABLES RETRIEVED FROM MONGODB')
# %%

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to PDF')
    parser.add_argument('-d', '--db', type=str, required=True, help='Database name')
    parser.add_argument('--host', type=str, default='localhost', help='MongoDB host')
    parser.add_argument('--port', type=int, default=27017, help='MongoDB port')
    parser.add_argument('--verbose', type=bool, default=True, help='Verbosity')
    parser.add_argument('--method', type=str, default='auto', help='Parsing method from {"auto", "lattice" or "stream"}')
    parser.add_argument('--conf', type=str, default=[], nargs='*', action='append', help='Specify settings for the parser as `key` `value`')
    args = parser.parse_args()
    conf = process_args(args.conf)
    
    if conf:
        warnings.warn('Parsing config options that require non-primitive data to be passed aren\'t supported from the command line. Add them to the `PARSE_CONFIG` dictionary at the top of this file.')

    extras = PARSE_CONFIG.copy()
    extras.update(conf)
    
    client = MongoClient(args.host, args.port)
    db = client[args.db]

    pipeline(args.file, db, flavor=args.method, extras=extras, verbose=args.verbose)



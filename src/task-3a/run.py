import argparse, os, warnings, copy
from pymongo import MongoClient

from main import pipeline

DATA_PATH = '../../data/task-3a/'
MONGO_DEFAULT_HOST = 'localhost'
MONGO_DEFAULT_PORT = 27017
MONGO_DEFAULT_DB_NAME = 'jivitesh-task-3a'

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=str, default=DATA_PATH, help='Path to directory with PDFs')
parser.add_argument('-d', '--db', type=str, default=MONGO_DEFAULT_DB_NAME, help='MongoDB database name')
parser.add_argument('--host', type=str, default=MONGO_DEFAULT_HOST, help='MongoDB host')
parser.add_argument('--port', type=int, default=MONGO_DEFAULT_PORT, help='MongoDB port')
args = parser.parse_args()

client = MongoClient(args.host, args.port)
db = client[args.db]

for f in os.listdir(args.file):
    if os.path.splitext(f)[1] != '.pdf':
        continue
    path = os.path.join(args.file, f)

    # Given cases:
    if f == 'd9f8e6d9-660b-4505-86f9-952e45ca6da0.pdf':
        pipeline(path, db, flavor='lattice')
    
    elif f == 'a6b29367-f3b7-4fb1-a2d0-077477eac1d9.pdf':
        pipeline(path, db, flavor='lattice', extras={'line_scale': 20, })

    elif f == '1c1edeee-a13e-4b2e-90be-eb1dd03c3384.pdf':
        pipeline(path, db, flavor='lattice') # top
        pipeline(path, db, flavor='stream', extras={'table_areas': ['0,480,590,420'], 'row_tol': 14, }) # bottom
    elif f == 'EICHERMOT.pdf':
        pipeline(path, db, flavor='stream', extras={'table_areas': ['0,570,300,500'], 'row_tol': 14, 'strip_text': '\n', }) # left
        pipeline(path, db, flavor='stream', extras={'table_areas': ['310,650,595,550'], 'row_tol': 14, 'strip_text': '\n', })  # right
        pipeline(path, db, flavor='stream', extras={'table_areas': ['0, 280, 590, 190'], 'row_tol': 14, }) # bottom
    else:
        pipeline(path, db)

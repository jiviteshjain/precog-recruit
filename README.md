# Precog Recruitment Tasks
*Jivitesh Jain*

## Outputs

Link to Outputs (Including plots): [Onedrive](https://iiitaphyd-my.sharepoint.com/:f:/g/personal/jivitesh_jain_students_iiit_ac_in/ElW2V3WHch1GuOtrBuTUwP0BRork_VcIH8v4veN6k9pyoQ?e=addp0A)

Link to interactive visualisations (Task-2): [Heroku](https://twisualise.herokuapp.com)
*Heroku dynos are slow on the first request due to sleeping. Please be patient and refresh the page multiple times if it does not load when you first open it.*

## Directory Structure
<pre>
.  
├── data  
│   ├── task-3a  
│   │   ├── 1c1edeee-a13e-4b2e-90be-eb1dd03c3384.pdf  
│   │   ├── a6b29367-f3b7-4fb1-a2d0-077477eac1d9.pdf  
│   │   ├── d9f8e6d9-660b-4505-86f9-952e45ca6da0.pdf  
│   │   └── EICHERMOT.pdf  
│   └── task-3b  
│       ├── Badges.xml  
│       ├── Posts.xml  
│       ├── Tags.xml  
│       ├── Users.xml  
│       └── Votes.xml  
├── docs  
│   ├── task-1  
│   │   └── Paper-Summary.pdf  
│   └── task-3b  
│       └── Report.pdf  
├── LICENSE  
├── out  
│   ├── task-2  
│   ├── task-3a  
│   └── task-3b  
│       ├── bin  
│       └── plots  
├── README.md  
├── requirements.txt  
└── src  
    ├── task-2  
    │   ├── tweets.html  
    │   ├── tweets.ipynb  
    │   ├── tweets.pdf  
    │   └── webapp  
    ├── task-3a  
    │   ├── main.py  
    │   └── run.py  
    └── task-3b  
        ├── analyse.py  
        └── parse-xml.py  
</pre>

The abridged directory structure is as above. While the `src` and `docs` folders already exist, `out` (for outputs) and `data` (for inputs) do not. Please either create these folders as described above or specify alternate input and output paths to the scripts.

## Running

Please install `requirements.txt` before running the code, and `src/task-2/webapp/requirements.txt` before running the web application locally.

### Task-1 Summary

The summary is available at `src/docs/task-1/Paper-Summary.pdf`.

### Task-2 Script

The jupyter notebook `src/task-2/tweets.ipynb` contains the tweet fetching and analysis code as well as the visualisations. Just loading the notebook would show the saved outputs. In order to run it, please adjust output paths if required and add Twitter API keys in the top cells. Skip the appropriate cells if you want to use the saved data.

The saved data is available in Onedrive and by default should be saved at `out/task-2/main_tweets_utf.json`. All generated plots are also available in Onedrive.

PDF and HTML versions of the notebook are also available. However, **some figures are interactive and hence cannot be rendered correctly in the PDF. Please use the HTML or IPYNB versions, if possible. Try hovering over the figures, clicking on legends to select subsets of the data, zooming in and out of maps etc.**

The Twisualise Heroku web application compliments the figures in the notebook. Explanation about the figures there is provided in the notebook at relevant places. Please keep both of those open and follow along the notebook. *The application handles a lot of data and is hosted on Heroku free tier dynos, which enter the sleeping state quickly. Please be patient as it loads, and refresh the page if the need arises.*

The application is written in Flask, and can also be run locally using the official instructions, after `src/task-2/webapp/requirements.txt` have been installed.

### Task-3a Script

**To directly run on the 4 given PDFS:**  
In folder `src/task-3a`, run:
```python3 run.py -f path/to/folder/containing/pdfs```
and it will process those 4 (or any other) pdfs in the given directory with parameters tuned for the given PDFs.

(Optionally, you can also specify `-d database-name` (defaults to `jivitesh-task-3a`), `--host MongoDB-host` and `--port MongoDB-port`. `-h` prints help.)

**Details: (Not needed for the given 4 PDFs)**  
If you want to run the code on a single PDF file, in folder `src/task-3a`, run:
```python3 main.py -f path/to/file -d database_name```

(Optional arguments: `--host MongoDB-host`, `--port MongoDB-port`, `--method auto|lattice|stream`, `--conf key val`. `-h` prints help.)

*Parser Tuning:*  
Because PDF was not designed to hold structured information, the parsers being used benefit from parameters specifically given for the given PDF. Although the script makes an attempt to try some combinations, it can result in false positives (the program has no way to verify if an extracted table is an actual table), and hence parameter tuning and visual debugging may be required.  

The last two options are used to tune the parser. Lattice method is better for tables with borders, and stream is better for tables without borders. The script, by default, (in `auto` mode) will use `lattice` first and switch to `stream` if no tables are detected. The `--conf` options can be seen in the [official documentation](https://camelot-py.readthedocs.io/en/master/user/advanced.html) and set as multiple key-value pairs, for example `python3 main.py -f file.pdf --method stream --conf row_tol 10 --conf edge_tol 100` (more complicated ones that require lists/dictionaries/non-primitive-datatypes to be passed can be specified at the top of the main.py file in `parse_config`). The script tries to log accuracy and throw warnings if the results are poor.

*Storage Format:*  
Because column headers can be missing (or identical for multiple columns) due to parsing errors, the tables are **not** stored as collections with each row as a document and column headers as keys.
Instead, each individual table is stored as a single document with column indices as keys. This ensures that keys are never ambiguous or missing. The scripts also contain functions (`main.py:tables_from_mongo`) for retrieving the stored tables from MongoDB and converting them back into dataframes. All tables of the same PDF are stored in a collection sharing its name with the PDF.

### Task-3b Script and Report

The report and visualisations are available at `docs/task-3b/Report.pdf`.

The script `src/task-3b/parse-xml.py` parses an XML file and stores it as a collection in MongoDB. Please specify the file path, database name and collection name at the top of the file.

In case a file different from those given is being used, please change the XML tag that is being read (line 39). In order to keep parsing efficient and not waste time and memory discovering the XML tree structure, the functions are specifically written for the given files, and may require minor changes when parsing files with deeper or more nested trees.

The script `src/task-3b/analyse.py` contains the code that was used to generate the visualisations.

The JSON dumps from MongoDB and the visualisations are available on Onedrive.
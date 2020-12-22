# Precog Recruitment Tasks
*Jivitesh Jain*

## Outputs

Link to Outputs: [Onedrive](https://iiitaphyd-my.sharepoint.com/:f:/g/personal/jivitesh_jain_students_iiit_ac_in/ElW2V3WHch1GuOtrBuTUwP0BRork_VcIH8v4veN6k9pyoQ?e=addp0A)

Link to interactive visualisations (Task-2): [Heroku](https://twisualise.herokuapp.com)

## Directory Structure

Please ensure that all data is present in the `data` folder in the directory root, inside subdirectories `task-3a` and `task-3b` respectively. If not, please pass arguments to the scripts or change paths within the files.

All outputs will be generated to the `out` directory in the project root, in respective subdirectories. Please create these if they don't already exist, or specify alternate paths to the scripts.

The code resides in the `src` directory and reports in the `doc` directory. Please make sure `requirements.txt` present in the project root are installed before running the code, and `requirements.txt` in `src/task-2/webapp` are installed before running the flask webapp.

## Task-3a Script

The script `run.py` parses an individual PDF, given its path. Options can be seen using `-h` option. While options `-f` and `-d` are compulsory (file and database name), others are optional. Parameters can be tuned using the `--conf` options, while the script makes a best effort itself, and gives appropriate warnings when it can't.

The script `main.py` will parse the given 4 PDFs using tuned hyperparameters and store in `jivitesh-task-3a` database. The tables are stored column first to account for missing column headers etc while parsing.

## Task-3b Script

The script `parse-xml.py` parses the files while `analyse.py` performs the EDA. Please specify the file path inside the files.
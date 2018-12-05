"""Run multiple scripts at a same time."""
import os
from multiprocessing import Pool

processes = ('rwdata1.py', 'rwdata2.py','rwdata3.py', 'rwdata4.py')
def run_process(process):
  os.system('python {}'.format(process))

pool = Pool(processes=4)
pool.map(run_process, processes)
"""-------------------------------------------------------------------------------------"""

"""Run multiple scripts at a same time."""
import logging
from multiprocessing import Pool
from os import listdir, path, remove
from os.path import isfile, join
from sqlalchemy import create_engine
import pandas as pd
user_n = ''
pwd = ''
db_name = ''
host_n = ''
port_n = ''
con_string = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(user_n, pwd, host_n, port_n, db_name)
db_con = create_engine(con_string, echo=False)
base_dir = '/Users/nr012/Desktop/scripts'

logging.basicConfig(
    filename=path.join(path.dirname(path.abspath(__file__)), 'activity_tracker.log'),
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG)

def delete_completed_file(file_path):
    remove(file_path)
    return "deleted"

def load_file(file_path):
    """
    Loading code goes here
    """
    file_path = join(base_dir, file_path)
    print file_path
    if db_con:
        integration_status_df = pd.read_csv(file_path, index_col=0) #match it with excel
        integration_status_df.to_sql( #table_name 
            name='table_name', con=db_con,
            if_exists='append', index=False)
        delete_completed_file(file_path)
        log_msg = "Completed file - {}".format(file_path)
        logging.info(log_msg)
        print log_msg

if __name__ == '__main__':
    files_to_import = [f for f in listdir(base_dir) if isfile(join(base_dir, f))]
    total_files = len(files_to_import)
    print len(files_to_import)
    p = Pool(10)
    p.map(load_file, files_to_import)
    p.close()
    p.join()
"""-------------------------------------------------------------------------------------"""

"""Run  scripts by reading file."""
import os
import json
import glob
import pandas as pd
from sqlalchemy import create_engine
# import pymysql
import logging

user_n = ''
pwd = ''
db_name = ''
host_n = ''
port_n = ""
con_string = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(user_n, pwd, host_n, port_n, db_name)
db_con = create_engine(con_string, echo=False)
base_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(base_dir, 'male')

filenames = glob.glob(path + "/*.csv")

total_files = len(filenames)

logging.basicConfig(
    filename=os.path.join(base_dir, 'activity_tracker.log'),
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG)


def delete_completed_file(file_path):
    os.remove(file_path)
    return "deleted"


if db_con:
    for key, val in enumerate(filenames):
        file_name = val.split('/')[-1]
        all_lifestyles_df = pd.read_csv(val, index_col=0)
        all_lifestyles_df.to_sql(
            name='simulation', con=db_con, if_exists='append', index=False)
        delete_completed_file(val)
        log_msg = "No of files yet to dump in db- {}, deleted file_name- {}".format((total_files-key), file_name)
        logging.info(log_msg)
        print log_msg
else:
    print "failed to connect to db."
    
"""Understanding of pool""""    
from multiprocessing import Pool

def f(x):
    return x*x

if __name__ == '__main__':
    p = Pool(5)
    print(p.map(f, [1, 2, 3]))
will print to standard output

[1, 4, 9]


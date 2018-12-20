


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

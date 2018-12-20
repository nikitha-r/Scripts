# import pandas as pd
# import sqlalchemy
# from sqlalchemy import create_engine

# col_list = ["body_mass_index",
# 			"body_weight",	
# 			"diastolic_blood_pressure",
# 			"fasting_serum_glucose",
# 			"insulin_sensitivity",
# 			"serum_hba1c",
# 			"serum_total_cholesterol",
# 			"serum_triglycerides",	
# 			"systolic_blood_pressure",	
# 			"time",
# 			"waist_circumference",
# 			"gender",
# 			"age",
# 			"Physiology_tag",
# 			"Lifestyle_tag",
# 			"height"]
# df = pd.read_csv('/Users/nr012/Desktop/example.csv', names=col_list)
# print df
# engine = sqlalchemy.create_engine('mysql+pymysql://dev_user:hUq@Ejc22w1k@35.188.128.114') 
# engine.execute("USE archetyping_db") #
# df.to_sql('simulation', con=engine, if_exists='append', index=False)


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

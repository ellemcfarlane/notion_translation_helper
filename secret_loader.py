import os
from dotenv import load_dotenv
"""
Loads necessary variables for using Twitter API
"""
# initialize keys from env
load_dotenv()

# retrieve keys from environment variables
token = os.environ.get('TOKEN')
prod_db = os.environ.get('PROD_DB')
dev_db = os.environ.get('DEV_DB')
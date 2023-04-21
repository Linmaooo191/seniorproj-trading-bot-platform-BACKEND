from pymongo import MongoClient
import os
from dotenv import dotenv_values
import yfinance as yf
import time
from datetime import datetime, timedelta
import pytz
from trader import *

def mongo_connect():
    MONGO_PASSWORD = dotenv_values(".env")["MONGO_PASSWORD"]
    MONGODB_URL = "mongodb+srv://endproj:"+MONGO_PASSWORD+"@endproject.ngmbfgy.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(MONGODB_URL)
    return client
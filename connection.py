from pymongo import MongoClient
import os
from dotenv import dotenv_values

MONGO_PASSWORD = dotenv_values(".env")["MONGO_PASSWORD"]
MONGODB_URL = "mongodb+srv://endproj:"+MONGO_PASSWORD+"@endproject.ngmbfgy.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGODB_URL)
db = client["TradingBot"]
collection_code = db["code"]
collection_strategy = db["strategy"]
collection_order = db["order"]
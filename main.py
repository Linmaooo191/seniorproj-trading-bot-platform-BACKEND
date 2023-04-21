import os

from flask import Flask
import requests
from pymongo import MongoClient
from dotenv import dotenv_values

MONGO_PASSWORD = dotenv_values(".env")["MONGO_PASSWORD"]
MONGODB_URL = "mongodb+srv://endproj:"+MONGO_PASSWORD+"@endproject.ngmbfgy.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGODB_URL)
db = client["TradingBot"]

app = Flask(__name__)

@app.get('/code')
def code_get():
    collection = db["code"]
    code_string = collection.find_one()["code"]
    return code_string

if __name__ == '__main__':
    app.run()
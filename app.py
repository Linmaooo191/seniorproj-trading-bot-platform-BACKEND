import os, time
from datetime import datetime, timedelta
import pytz

from flask import Flask,jsonify,request
from flask_cors import CORS
import requests
from connection import collection_strategy, collection_code
from dotenv import dotenv_values
from trader import *

app = Flask(__name__)
CORS(app)

@app.route('/code', methods = ['GET'])
def code_get():
    if(request.method == 'GET'):
        code_string = collection_code.find_one()["code"]
        data = {"code":code_string}
        return jsonify(data)
    
@app.route('/code', methods = ['POST'])
def code_post():
    if(request.method == 'POST'):
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            thaiTz = pytz.timezone('Asia/Bangkok') 
            now = datetime.now(thaiTz).strftime("%m/%d/%Y, %H:%M:%S")
            json = request.get_json()
            collection_code.update_one({"name":"Trading Bot"}, {"$set":{"code":json['code']}})
            collection_strategy.update_one({"name":"Trading Bot"}, {"$set":{"last_saved":now}})
            return "save Trading Bot code"
        
@app.route('/strategy', methods = ['GET'])
def strategy_get():
    if(request.method == 'GET'):
        strategy = collection_strategy.find_one()
        data = {
            "name": strategy["name"], 
            "last_saved": strategy["last_saved"],
            "last_executed":strategy["last_executed"],
            "activation": strategy["activation"]
        }
        return jsonify(data)
    
@app.route('/strategy', methods = ['POST'])
def strategy_post():
    if(request.method == 'POST'):
        activation = not collection_strategy.find_one()['activation']
        result = collection_strategy.update_one({"name":"Trading Bot"}, { "$set":{ "activation": activation}})
        return "Toggle activation"
    
@app.route('/bot_execute', methods = ['GET'])
def code_execute():
    if(request.method == 'GET'):
        code_string = collection_code.find_one()["code"]
        exec(code_string)
        thaiTz = pytz.timezone('Asia/Bangkok') 
        now = datetime.now(thaiTz).strftime("%m/%d/%Y, %H:%M:%S")
        collection_strategy.update_one({"name":"Trading Bot"}, {"$set":{"last_executed":now}})
        return "Trading Bot code executed"

@app.route('/order_time', methods = ['POST'])
def order_time():
    if(request.method == 'POST'):
        last_document = collection_order.find_one(sort=[("_id", -1)])
        id = request.args.get('id',last_document["id"])
        print(id)
        thaiTz = pytz.timezone('Asia/Bangkok') 
        now = datetime.now(thaiTz).strftime("%m/%d/%Y, %H:%M:%S")
        collection_order.update_one({"id":int(id)}, {"$set":{"order_finished":now}})
        return "save order finished time for id" + str(id)
    
if __name__ == '__main__':
    app.run()
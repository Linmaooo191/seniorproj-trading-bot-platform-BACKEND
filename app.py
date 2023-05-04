import os, time
from datetime import datetime, timedelta
import pytz
from flask import Flask,jsonify,request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
import requests
from connection import collection_strategy, collection_code
from dotenv import dotenv_values
from trader import *
import threading

thaiTz = pytz.timezone('Asia/Bangkok') 
autotime_list = [10, 11, 12, 15, 16]

def convert_date_format(input_string: str) -> str:
    # Parse input string to a datetime object with timezone
    input_datetime = datetime.fromisoformat(input_string)

    # Convert to the desired timezone
    output_datetime = input_datetime.astimezone(thaiTz)

    # Format the output string
    output_string = output_datetime.strftime("%Y-%m-%d T %H:%M:%S (GMT+7)")

    return output_string

def code_execute_thread():
    exec_globals = {
        'yf': yf,
        'pd': pd,
        'RSIIndicator': RSIIndicator,
        'execute_order': execute_order
    }
    code_string = collection_code.find_one()["code"]
    exec(code_string, exec_globals)
    now = datetime.now(thaiTz).strftime("%m/%d/%Y, %H:%M:%S")
    collection_strategy.update_one({"name":"Trading Bot"}, {"$set":{"last_executed":now}})
    print("Code done executed")

def code_execute():
    thread = threading.Thread(target=code_execute_thread)
    thread.start()

def code_execute_check():
    activation = collection_strategy.find_one()['activation']
    if activation == True:
        print("[Code executed by schedule.")
        code_execute_thread()

def log_something():
    print("something")

app = Flask(__name__)
CORS(app)

scheduler = BackgroundScheduler(daemon=True)

for hour in autotime_list:
    trigger = CronTrigger(hour=hour, minute=15, day_of_week='0-4', timezone=thaiTz)
    scheduler.add_job(code_execute_check, trigger)

scheduler.start()

@app.route("/")
def main_url():
    return "Welcome to FLASK for trading bot platform!"

@app.route("/logs")
def show_logs():
    # Set your Papertrail API token
    papertrail_api_token = dotenv_values(".env")["PAPERTRAIL_API_TOKEN"]

    headers = {
        "X-Papertrail-Token": papertrail_api_token,
    }
    url = "https://papertrailapp.com/api/v1/events/search.json"

    response = requests.get(url, headers=headers, params={"limit": 100, "q": '-("GET" OR "POST")'})

    response.raise_for_status()
    logs = response.json()["events"]

    logs_text = "\n".join([f"{convert_date_format(log['received_at'])} : {log['message']}" for log in logs])

    return logs_text.replace("\n", "<br>")

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
def apicode_execute():
    if(request.method == 'GET'):
        print("[Code execute manually.]")
        code_execute()
        return "Code executed"

@app.route('/order_time', methods = ['POST'])
def order_time():
    if(request.method == 'POST'):
        last_document = collection_order.find_one(sort=[("_id", -1)])
        id = request.args.get('id',last_document["id"])
        thaiTz = pytz.timezone('Asia/Bangkok') 
        now = datetime.now(thaiTz).strftime("%m/%d/%Y, %H:%M:%S")
        collection_order.update_one({"id":int(id)}, {"$set":{"order_finished":now}})
        print(f"[Order({id}) was placed.]")
        return "save order finished time for id" + str(id)
    
if __name__ == '__main__':
    app.run(debug=False)
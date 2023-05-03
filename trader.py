import requests
from datetime import datetime, timedelta
import pytz
from connection import collection_order

def get_token():
    headers = {
      "Content-Type": "application/json",
      "X-UIPATH-TenantName": "DefaultTenant"
    }
    body = {
      "grant_type": "refresh_token",
      "client_id": "8DEv1AMNXczW3y4U15LL3jYf62jK93n5",
      "refresh_token": "_-1pmL77UeeWS2Wo52flhLyXo4oEWTknPkCYPuOvEwnPH"
    }
    response = requests.post("https://account.uipath.com/oauth/token", headers=headers, json=body)
    return "Bearer " + response.json()['access_token']

def execute_order(side, vol, symbol, price):
    last_document = collection_order.find_one(sort=[("_id", -1)])
    if last_document:
        id = int(last_document["id"]) + 1
    else:
        id = 1
    headers = {
      "Authorization": get_token(),
      "Content-Type": "application/json",
      "X-UIPATH-OrganizationUnitId": "157894"
    }
    body = {
      "startInfo": {
      "ReleaseKey": "fb31ca2f-9ffd-44be-b8a6-7d8498ada728",
      "JobsCount": 1,
      "Strategy": "ModernJobsCount",
      "InputArguments": "{\"id\":\""+str(id)+"\",\"in_side\":\""+side+"\",\"in_vol\":"+str(vol)+",\"in_symbol\":\""+symbol+"\",\"in_price\":\""+str(price)+"\",\"token\":\""+get_token()+"\"}"
      }
    }
    response = requests.post("https://cloud.uipath.com/tradibmbgugp/DefaultTenant/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs", headers=headers, json=body)
    thaiTz = pytz.timezone('Asia/Bangkok') 
    now = datetime.now(thaiTz).strftime("%m/%d/%Y, %H:%M:%S")
    
    collection_order.insert_one({"id":id,
                                 "side":side,
                                 "symbol":symbol,
                                 "volume":vol,
                                 "price":price,
                                 "order_executed":now,
                                 "order_finished":""
                                 })
    print("Sending request to RPA system.")
import requests

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

def execute_order(token, side, vol, symbol, price):
    headers = {
      "Authorization": token,
      "Content-Type": "application/json",
      "X-UIPATH-OrganizationUnitId": "157894"
    }
    body = {
      "startInfo": {
      "ReleaseKey": "fb31ca2f-9ffd-44be-b8a6-7d8498ada728",
      "JobsCount": 1,
      "Strategy": "ModernJobsCount",
      "InputArguments": "{\"in_side\":\""+side+"\",\"in_vol\":"+str(vol)+",\"in_symbol\":\""+symbol+"\",\"in_price\":\""+str(price)+"\",\"token\":\""+token+"\"}"
      }
    }

    response = requests.post("https://cloud.uipath.com/tradibmbgugp/DefaultTenant/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs", headers=headers, json=body)
    print(response.json())
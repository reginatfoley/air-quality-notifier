import os
import requests
import json
import numpy as np
from twilio.rest import Client
from flask import Flask
app = Flask(__name__)

nw_lat = 39.99527
se_lat = 39.94496
nw_lng = -105.27773
se_lng = -105.24213

URL = f"https://www.purpleair.com/data.json?opt=1/mPM10/a10/cC0&fetch=true&nwlat={nw_lat}&selat={se_lat}&nwlng={nw_lng}&selng={se_lng}"

@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
 
    return "Hello {}!".format(name)

@app.route("/pm")
def pm():
    #Call API request function to get array of particulates PM2.5 and PM10:
    all_data = requests.get(URL)
    data_json = json.loads(all_data.content)
    PM25 = []
    PM10 = []

    for i in range(data_json['count']):
        pm25 = data_json['data'][i][7]   #PM25 raw
        pm10 = data_json['data'][i][14]  #PM10 raw
        PM25.append(pm25)
        PM10.append(pm10)

    av_pm25 = np.mean(PM25)
    av_pm10 = np.mean(PM10)
    
    message = ""

    if av_pm25 > 12.1 or av_pm10 > 12.1:
        message = "Air quality is moderate."
    
    elif av_pm25 > 35.5 or av_pm10 > 35.5:
        message = "Air quality is unhealthy for sensitive groups."
        
    elif  av_pm25 > 55.5 or av_pm10 > 55.5:
        message = "Air quality is unhealthy for sensitive groups."
    
    else: 
        message = "Air quality is good."

    notify_with_twilio(message)

    return message


def notify_with_twilio(message):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    message = client.messages \
                    .create(
                        body=message,
                        from_='+19106064612',
                        to='+19704012661'
                    )

    print(message.sid)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

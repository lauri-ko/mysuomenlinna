import requests
import json
import datetime
import pytz
from enum import Enum

def getWeekdayTimestamp(weekday):
    tz = pytz.timezone('Europe/Helsinki')
    now = datetime.datetime.now(tz)
    weekdayDelta = abs(now.weekday()-weekday)
    newtime = now.replace(hour=5,minute=0,second=0,microsecond=0)

    if weekday >= now.weekday():
        newtime = newtime + datetime.timedelta(days=weekdayDelta)
    else:
        newtime = newtime + datetime.timedelta(days=7-weekdayDelta)
    return round(newtime.timestamp())
    
class Stop(Enum):
    suomenlinna = 1520702
    kauppatori = 1030701
    katajanokka = 1080701
    huoltolaituri = 1520703


def getStopTimes(stopId, timestamp):
    def formatTimes(data):
        stop = data["data"]["stop"]
        stopName = stop["name"]
        stoptimes = list(filter(lambda item: item["trip"]["tripHeadsign"] != stopName, stop["stoptimesWithoutPatterns"]))
        return stoptimes
        
    url = "http://api.digitransit.fi/routing/v1/routers/hsl/index/graphql"
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "query": """{
            stop(id: "HSL:%d") {\
                name stoptimesWithoutPatterns(startTime: %d, timeRange:86400, numberOfDepartures: 200) {\
                    scheduledDeparture, serviceDay, trip{tripHeadsign\
                    }\
                }\
            }\
        }""" % (stopId, timestamp)
    }

    request = requests.post(url, data=json.dumps(data), headers=headers)
    tries = 0
    limit = 3
    while tries<limit:
        if(request.ok):
            result = json.loads(request.text)
            return formatTimes(result)
        else:
            request = requests.post(url, data=json.dumps(data), headers=headers)
            tries+=1

    print("request not ok")
    print("result")

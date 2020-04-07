from digitransitApi import Stop, getWeekdayTimestamp, getStopTimes
import datetime
import pytz
import renderer
import os
import codecs

# convert timestamp to hh:mm format
def convertTime(timestamp):
    tz = pytz.timezone('Europe/Helsinki')
    date = datetime.datetime.fromtimestamp(timestamp)
    date = date.astimezone(tz)
    return date.strftime('%H:%M')

def getTimetableForEachDay(stop):
    timetables = []
    for i in range(7):
        timetable = getStopTimes(stop, getWeekdayTimestamp(i))
        timetables.append(timetable)
    return timetables

def timetableToDays(timetables):
    dictionary = {}
    for i in range(len(timetables)):
        timetable = timetables[i]
        result = map(lambda departure: convertTime(departure["serviceDay"]+departure["scheduledDeparture"]), timetable)
        formattedTimetable = tuple(result)
        if(formattedTimetable in dictionary):
            dictionary[formattedTimetable].append(i)
        else:
            dictionary[formattedTimetable] = [i]
    return dictionary

def generateRows(timetable):
    hour = ""
    row = []
    rows = []
    for time in timetable:
        timeSplit = time.split(":")
        if not hour:
            hour = timeSplit[0]
            row.append(timeSplit[0])
            row.append(timeSplit[1])
        elif hour == timeSplit[0]:
            row.append(timeSplit[1])
        else:
            rows.append(row)
            hour = timeSplit[0]
            row = [timeSplit[0], timeSplit[1]]
    if(row):
        rows.append(row)
    return rows

weekday = datetime.datetime.now(pytz.timezone('Europe/Helsinki')).weekday()

def getTimetablesForStop(stop):
    timetables = []
    stopTimetables = timetableToDays(getTimetableForEachDay(stop))
    weekdays_fi = ["ma","ti","ke","to","pe","la","su"]
    weekdays_se = ["må","ti","on","to","fr","lö","sö"]
    for timetable in stopTimetables.keys():
        aikataulu = generateRows(timetable)
        days = stopTimetables[timetable]
        if(aikataulu):
            if(weekday in days):
                timetables.insert(0, {"departureTimes": aikataulu, "dates": { "fi": "".join(map(lambda i: weekdays_fi[i] + " ", days)),
                                                                              "se": "".join(map(lambda i: weekdays_se[i] + " ", days))}})
            else:
                timetables.append({"departureTimes": aikataulu, "dates": { "fi": "".join(map(lambda i: weekdays_fi[i] + " ", days)),
                                                                           "se": "".join(map(lambda i: weekdays_se[i] + " ", days))}})
    return timetables

context = {
    "date": datetime.datetime.now(pytz.timezone('Europe/Helsinki')).strftime("%d.%m.%Y"),
    "Kauppatori": getTimetablesForStop(Stop.kauppatori.value),
    "Suomenlinna": getTimetablesForStop(Stop.suomenlinna.value),
    "Katajanokka": getTimetablesForStop(Stop.katajanokka.value),
    "Huoltolaituri": getTimetablesForStop(Stop.huoltolaituri.value)
    }

print(context)
output = renderer.renderTimetable(context)

scriptDirectory = os.path.dirname(os.path.realpath(__file__))
FILE_NAME = "index.html"
with codecs.open(os.path.join(scriptDirectory, FILE_NAME), 'w+', "utf-8") as file:
    file.write(output)
    print("Valmis")

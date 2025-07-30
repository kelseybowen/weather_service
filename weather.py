import json
import zmq
import os
import requests
from dotenv import load_dotenv
import datetime

load_dotenv()

API_KEY = os.getenv('OPENWEATHER_API_KEY')

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5557")

def get_weather_data(location_data):
    lat = location_data['lat']
    lon = location_data['lon']
    response = requests.get(f'https://api.openweathermap.org/data/2.5/forecast/daily?lat={lat}&lon={lon}&cnt=16&units=imperial&appid={API_KEY}')
    return response.json()['list']

def create_json(weather_list):
    weather_data = []
    for day in weather_list:
        unix_timestamp = day['dt']
        utc_datetime = datetime.datetime.fromtimestamp(unix_timestamp, tz=datetime.timezone.utc)
        formatted_date = utc_datetime.strftime('%m-%d-%Y')
        data = {
            "date": formatted_date,
            "low_temp": day["temp"]["min"],
            "hi_temp": day["temp"]["max"],
            "main": day["weather"][0]["main"]
        }
        weather_data.append(data)
    return json.dumps(weather_data)

while True:
    message = socket.recv()
    weather_list = get_weather_data(json.loads(message.decode()))
    json_data = create_json(weather_list)
    socket.send_string(json_data)
    print(f"Data sent to main program: {json_data}")

context.destroy()
from flask import Flask, render_template, redirect, request
from flask import jsonify, request
import warnings

warnings.filterwarnings('ignore')

import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import pyjokes
import wikipedia
import sys
import requests, json

listener = sr.Recognizer()
# engine = pyttsx3.init()

import os

app = Flask("__name__")


def engine_talk(text):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()


def user_commands(timeout=15):
    command = ""
    try:
        with sr.Microphone() as source:
            print("Start Speaking!!")
            listener.adjust_for_ambient_noise(source, duration=1)
            voice = listener.listen(source, timeout=timeout)
            command = listener.recognize_google(voice)
            print(command)
    except:
        engine_talk('I can not understand what you say')
    return command


def run_alexa(command):
    command = user_commands()
    if 'play' in command:
        song = command.replace('play', '')
        engine_talk('playing' + song)
        pywhatkit.playonyt(song)
        return f'{command}....   Playing {song}'
    elif 'what' in command and 'time' in command and ('now' in command or 'current' in command):
        time = datetime.datetime.now().strftime('%I:%M %p')
        engine_talk('Current time is ' + time)
        print(time)
        return f'{command}....   Current time is {time}'
    elif 'joke' in command:
        get_j = pyjokes.get_joke()
        print(get_j)
        engine_talk(get_j)
        return f'{command}....    {get_j}'
    elif 'alarm' in command:
        engine_talk('Yes of course. Please tell the Hour')
        t = user_commands()
        a = int(t)
        while a < 1 or a > 12:
            engine_talk('Please tell the hour between 1 to 12. Try again')
            t = user_commands()
            a = int(t)

        engine_talk('Minute')
        th = user_commands()
        b = int(th)
        try:
            while b < 0 or b > 59:
                engine_talk('Please tell the minute between 0 to 59. Try again')
                th = user_commands()
                b = int(th)
        except ValueError:
            engine_talk('I did not understand the minute. Try again.')
        engine_talk('Time format: a.m. or p.m.')
        tht = user_commands()
        c = str(tht)
        engine_talk('I did not understand the time format. Try again.')
        if c == 'p.m.':
            a = a + 12
        engine_talk('Your alarm is set')
        while True:
            if a == datetime.datetime.now().hour and b == datetime.datetime.now().minute:
                engine_talk('It is the time')
                while user_commands() == 'stop':
                    break

    elif 'temperature' in command or 'weather' in command:
        city = command.split("of", 1)
        if len(city) > 1:  # Check if the split resulted in at least two elements
            city_name = city[1].strip()  # Extract the city name and remove any leading/trailing whitespaces
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid=c5764987fe8f789c72c872a0a9d53805"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                weather = data['weather'][0]['main']
                temp = data['main']['temp']
                t = int(temp)
                cel = int(t - 273.15)  # Convert temperature from Kelvin to Celsius
                print('The weather is ' + weather + ' and the temperature is ' + str(cel) + ' degree celsius ')
                engine_talk('The weather is ' + weather + ' and the temperature is ' + str(cel) + ' degree celsius ')
                return f"The weather is {weather} and the temperature is {cel} degree celsius"
            else:
                print("Failed to fetch weather data.")
                engine_talk("Failed to fetch weather data. Please try again.")
                return "Failed to fetch weather data. Please try again."
        else:
            print("City name not provided.")
            engine_talk("Please specify the city name.")
            return "City name not provided."

    elif 'tell' or 'what' or 'say' in command:
        try:
            info = wikipedia.summary(command, 3)
            print(info)
            engine_talk(info)
            pywhatkit.search(command)
            return f"Here's what I found: {info}"
        except wikipedia.exceptions.PageError:
            print(f"No Wikipedia page found for '{command}'. Please try a different query.")
            engine_talk(f"No Wikipedia page found for '{command}'. Please try a different query.")
            return f"No Wikipedia page found for '{command}'. Please try a different query."



@app.route('/')
def hello():
    return render_template("alexa.html")


@app.route("/home")
def home():
    return redirect('/')


@app.route('/process_command', methods=['POST'])
def process_command():
    command = request.form.get('command')
    response = run_alexa(command)
    return jsonify({'response': response})


@app.route('/', methods=['POST', 'GET'])
def submit():
    while True:
        run_alexa()
    return render_template("alexa.html")


if __name__ == "__main__":
    app.run(debug=True)



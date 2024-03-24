# Import necessary libraries
from flask import Flask, jsonify, render_template_string
import requests
import Adafruit_DHT
import time
import RPi.GPIO as GPIO

# Initialize Flask app
app = Flask(__name__)


# ThinkSpeak API Keys
CHANNEL_ID = "2465224"
WRITE_API_KEY = "M5LVVIVDNDH0T7PW"

# Set up GPIO
GPIO.setmode(GPIO.BCM)
RELAY_PIN = 21
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)  # Set initial state to HIGH

# Store previous temperature value
prev_temperature = None

# HTML content for Temperature Remote Sensing Lab Page
temperature_lab_content = """
<!DOCTYPE html>
<html>

<head>
<script src='https://cdn.plot.ly/plotly-2.29.1.min.js'></script>
    <title>Temperature Remote Sensing Lab</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            text-align: center;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }

        .container {
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }

        h1 {
            color: #333;
        }

        p {
            color: #555;
            margin-bottom: 20px;
        }
        button{
        margin-top:10px;
        margin-right:10px;
        margin-bottom:20px;
        height: 60px;
        width:90px;
        font-size:20px;
        background-color: #7E90FF;
        border-radius: 8px;
        border: 2px solid #7E90FF;
        }

        #temperatureReading {
            margin-top: 20px;
            padding: 20px;
            background-color: #f9f9f9;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 18px;
            color: #333;
        }
        a:link { 
  text-decoration: none; 
} 
a:visited { 
  text-decoration: none; 
} 
a:hover { 
  text-decoration: none; 
} 
a:active { 
  text-decoration: none; 
}

    </style>
</head>

<body>
    <div class="container">
        <h1>Remote Temperature Monitoring and control System</h1>
        <p>Real-time temperature and humidity:</p>
        <div id="temperatureReading"></div>
    </div>
    <div id='myDiv'></div>
    <button><a href="/control-page"> Relay Control</a></button>
    <script>
        var count = 0;
        var current_temp = 0;
        var current_temp_sliced = 0;
        var current_humid_sliced = 0;
        var current_temp_int = 0;
        var current_humid_int = 0;
        var threshold = 29;
var valueNumber = [];
var temp = [];
var humid = [];
var trace2 = {
   x: valueNumber,
   y: temp,
   type: 'scatter'
 };
 var trace1 = {
  x: valueNumber,
  y: humid,
  type: 'scatter'
};
  function plotGraph(){
   data = [trace2, trace1];
   Plotly.newPlot('myDiv', data);
 }
 
 function turnOnRelay() {
            fetch("/turn_on", { method: "POST" })
                .then(response => response.text())
                .then(data => {
                    // alert(data);
                    document.getElementById("relayState").innerText = "Current Relay State: On";
                })
                .catch(error => console.error("Error:", error));
        }

        function turnOffRelay() {
            fetch("/turn_off", { method: "POST" })
                .then(response => response.text())
                .then(data => {
                    // alert(data);
                    document.getElementById("relayState").innerText = "Current Relay State: Off";
                })
                .catch(error => console.error("Error:", error));
        }
 
 function getTemperatureReading() {
            fetch("/get_temperature")
                .then(response => response.json())
                .then(data => {
                    // Display previous temperature if current temperature is not defined
                    let temperature = data.temperature ? data.temperature : "{{ prev_temperature }}";
                     console.log(typeof(data.temperature));
                    current_temp = temperature;
                   console.log(current_temp);
                   current_temp_sliced = temperature.slice(0, 2);
                   current_humid_sliced = temperature.slice(18,20);
                   console.log(current_temp_sliced, current_humid_sliced);
                   current_temp_int = parseInt(current_temp, 10);
                   current_humid_int = parseInt(current_humid_sliced, 10);
                   console.log(current_temp_int, current_humid_int);
                    if(count<100)
                   {
                       count++;
                        valueNumber.push(count);
                        humid.push(current_humid_int);
                        temp.push(current_temp_int);
                }
                else{
                    temp.shift();
                    humid.shift();
                    humid.push(current_humid_int);
                    temp.push(current_temp_int);
                }
                    
                   plotGraph()
                   if(current_temp_int >= threshold)
                   {
                    turnOnRelay()    
                   }
                   else{
                   turnOffRelay()
                   }
                    document.getElementById("temperatureReading").innerText = `Temperature: ${temperature}`;
                })
                .catch(error => {
                    console.error("Error:", error);
                });
        }
        
        // Fetch temperature data every 2 seconds
        setInterval(getTemperatureReading, 2000);
       
    </script>
</body>

</html>

"""

# HTML content for the control page
control_page_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Relay Control</title>
    <style>
    body{
    font-family:'Arial', sans-serif;
    text-align: center;
    background-color:#f4f4f4;
    margin:0;
    padding:0;
    }
        .container{
        max-width: 600px;
        height: 200px;
        margin: 200px auto;
        padding: 20px;
        background-color: #fff;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        border-radius: 8px
        }
        h1{
        color: #333;
        }
        button{
        margin-top:10px;
        margin-right:10px;
        margin-bottom:20px;
        height: 60px;
        width:90px;
        font-size:20px;
        background-color: #7E90FF;
        border-radius: 8px;
        border: 2px solid #7E90FF;
        }
        #relayState{
        font-size:20px;
        }
    </style>
    <script>
        function turnOnRelay() {
            fetch("/turn_on", { method: "POST" })
                .then(response => response.text())
                .then(data => {
                    alert(data);
                    document.getElementById("relayState").innerText = "Current Relay State: On";
                })
                .catch(error => console.error("Error:", error));
        }

        function turnOffRelay() {
            fetch("/turn_off", { method: "POST" })
                .then(response => response.text())
                .then(data => {
                    alert(data);
                    document.getElementById("relayState").innerText = "Current Relay State: Off";
                })
                .catch(error => console.error("Error:", error));
        }
    </script>
</head>
<body>
<div class="container">
    <h1>Relay Control</h1>
    <button onclick="turnOnRelay()">Turn On</button>
    <button onclick="turnOffRelay()">Turn Off</button><br>
    <div id="relayState">Current Relay State: Off</div>
</div>
</body>
</html>
"""


# Define routes

# Home Page (index)
@app.route("/")
def index():
    return render_template_string(temperature_lab_content, prev_temperature=prev_temperature)

@app.route("/control-page")
def control_page():
    return render_template_string(control_page_content)   

# Simulate Temperature Reading
# Simulate Temperature Reading and Send Data to ThingSpeak
@app.route("/get_temperature", methods=["GET"])
def get_temperature_reading():
    global prev_temperature
    # Read real-time temperature from DHT sensor
    DHT_SENSOR = Adafruit_DHT.DHT11
    DHT_PIN = 4
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    
    if humidity is not None and temperature is not None:
        temperature_reading = f"{temperature:.1f}°C, Humidity: {humidity:.1f}%"
        prev_temperature = temperature_reading
        
        # Send data to ThingSpeak
        try:
            url = f"https://api.thingspeak.com/update?api_key=M5LVVIVDNDH0T7PW&field1={temperature}&field2={humidity}"
            response = requests.get(url)
            if response.status_code == 200:
                print("Data sent to ThingSpeak successfully!")
            else:
                print("Failed to send data to ThingSpeak:", response.text)
        except Exception as e:
            print("Error sending data to ThingSpeak:", str(e))
        
        return jsonify({"temperature": temperature_reading})
    else:
        if prev_temperature is not None:
            return jsonify({"temperature": prev_temperature})
        else:
            return jsonify({"error": "Sensor failure. Check wiring."})



# Route to turn on the relay
@app.route("/turn_on", methods=["POST"])
def turn_on():
    GPIO.output(RELAY_PIN, GPIO.LOW)  # Set pin to LOW to turn on the relay
    return "Relay turned on."

# Route to turn off the relay
@app.route("/turn_off", methods=["POST"])
def turn_off():
    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Set pin to HIGH to turn off the relay
    return "Relay turned off."



# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
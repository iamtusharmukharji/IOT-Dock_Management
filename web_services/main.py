from app_config import app, mqtt
from flask import render_template, Response, request
import json
from queue import Queue
from time import sleep

que = Queue()

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    raw_message = message.payload.decode()
    if raw_message == "i_am_online":
        data = None
    else:
        data = {}
        data["topic"] = message.topic
        json_data = raw_message.replace("\'", "\"")
        json_data = json.loads(json_data)
        #json_data["dock_4"] = 0
        #json_data["dock_5"] = 0
        #json_data["dock_6"] = 1
        data["payload"] = json_data
        
    que.put(data)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/topic/", methods = ["POST"])
def topic_mqtt():
    form_data = request.form.get("channel")
    form_data = form_data.split("-")
    location = form_data.pop()
    topic = form_data.pop()
    
    print(topic, location)
    mqtt.subscribe(topic)
    #data = handle_mqtt_message(mqtt)
    return render_template("stream.html", location = location)

@app.route("/stream")
def stream():
    def events():
        while True:
            message = que.get()
            if message is None:
                sleep(0.7)
                continue
            
            yield "data: %s\n\n" % json.dumps(message)
    return Response(events(), content_type='text/event-stream')





if __name__ == "__main__":
    app.run(debug = True)
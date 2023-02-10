from app_config import app, mqtt
from flask import render_template, Response, request, jsonify
from datetime import datetime
import json
import traceback
import os
import models
from database import Session, eng, Base

from queue import Queue
from time import sleep

que = Queue()

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    raw_message = message.payload.decode()
    topic = message.topic
    print(topic)
    
    if raw_message[-1] == "i":
        device_data = raw_message.split("-")
        device_data.pop()
        
        location_code = device_data[0]
        device_id = device_data[1]
        total_docks = device_data[2]
        
        db = Session()
        
        db_device_check = db.query(models.Device).filter(models.Device.device_id == device_id, models.Device.location_code == location_code).first()

        if db_device_check == None:
            new_device = models.Device(device_id = device_id, 
                                        location_code = int(location_code),
                                        total_connected_docks = int(total_docks),
                                        topic = topic,
                                        created_at = datetime.now(),
                                        is_deleted = 0)

            db.add(new_device)
            db.commit()
        db.close()


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

    form_data = form_data.split("/")
   
    location = form_data.pop()
    topic = form_data.pop()
    
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

@app.route("/add/zone/", methods = ["POST"])
def add_zone(db = Session()):
    try:
        zone_name = request.json["zone"]

        db_check_zone = db.query(models.Zone).filter(models.Zone.zone == zone_name).first()

        if db_check_zone != None:
            db.close()
            return {"detail":f"{zone_name} already exists in zone"}, 404

        new_zone = models.Zone()
        new_zone.zone = zone_name
        new_zone.created_at = datetime.now()

        db.add(new_zone)
        db.commit()
        db.refresh(new_zone)
        
        db.close()

        return {"message":"zone added", "zone_id":new_zone.id, "zone":new_zone.zone}, 201 

    except Exception as err:
        traceback.print_exc()
        db.close()
        return {"detail":str(err)}, 403


@app.route("/add/location/", methods=["POST"])
def add_location(db = Session()):
    try:
        location_name = request.json["location"]

        db_check_location = db.query(models.Location).filter(models.Location.location == location_name).first()
        if db_check_location != None:
            db.close()

            return {"detail":f"{location_name} already exists in location"}, 404

        zone_id = request.json["zone_id"]

        new_location = models.Location(
                                        zone_id = zone_id,
                                        location= location_name,
                                        created_at = datetime.now(),
                                        is_deleted = 0
                                        )
        db.add(new_location)

        db.commit()
        db.refresh(new_location)
        db.close()

        return {"message":"new location added", "location_id":new_location.id, "location":new_location.location}, 201


    except Exception as err:
        traceback.print_exc()
        return {"detail":str(err)}, 403


@app.route("/add/entity/", methods=["POST"])
def add_entity(db = Session()):
    try:
        entity_name = request.json["entity"]

        db_check_entity = db.query(models.Entity).filter(models.Entity.entity == entity_name).first()
        if db_check_entity != None:
            db.close()

            return {"detail":f"{entity_name} already exists in entity"}, 404

        cost_code = request.json["cost_code"]
        
        new_entity = models.Entity(
                                        entity = entity_name,
                                        cost_code = int(cost_code),
                                        created_at = datetime.now(),
                                        is_deleted = 0
                                        )
        db.add(new_entity)

        db.commit()
        db.refresh(new_entity)
        db.close()

        return {"message":"new entity added", "entity_id":new_entity.id, "entity":new_entity.entity}, 201


    except Exception as err:
        traceback.print_exc()
        return {"detail":str(err)}, 403



if __name__ == "__main__":

    if not os.path.exists("dockManagement.db"):
        pass
    Base.metadata.create_all(eng)
    app.run(debug = True)
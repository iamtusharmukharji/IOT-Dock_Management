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
cache_devices = set()

cache_docks = {}

def add_device(device_id, location_code, total_docks, topic):

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
    cache_devices.add(device_id)
    return True

def get_disabled_docks(device_id):
    if device_id not in cache_docks:
        db = Session()
            
        db_device = db.query(models.Device).filter(models.Device.device_id == device_id).first()

        disabled_docks = db_device.disabled_docks
        cache_docks[device_id] = disabled_docks
        db.close()
    else:
        disabled_docks = cache_docks[device_id]
    return disabled_docks



@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    raw_message = message.payload.decode()
    topic = message.topic
    #print(cache_devices)
    #print(cache_docks)
    #print(topic)
    
    if raw_message == "Device-Online":
        pass
    else:
        data = {}
        data["topic"] = message.topic
        
        arr_data = raw_message.split('-')
        
        location_code = arr_data.pop()
        device_id = arr_data.pop()
        total_docks = arr_data.pop()
        
        if device_id not in cache_devices:
            add_device(device_id, location_code, total_docks, message.topic)

        raw_data = arr_data.pop()

        
        json_data = raw_data.replace("\'", "\"")
        json_data = json.loads(json_data)
        
        disabled_docks = get_disabled_docks(device_id)
        if disabled_docks not in {"", None}:
            disabled_docks = disabled_docks.split(",")
            for i in disabled_docks:
                if i in json_data:
                    json_data[i] = -1


        data["payload"] = json_data
        data["device_id"] = device_id
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

@app.route("/dockcontrol/", methods= ["POST"])
def dock_control():

    db = Session()
    device_id = request.json["device_id"]
    state = request.json["state"]
    dock_name = request.json["dock"]
    print([device_id, dock_name, state])
    db_disabled_docks = db.query(models.Device).filter(models.Device.device_id == device_id).first()
    disabled_dock_arr = db_disabled_docks.disabled_docks
    
    if (disabled_dock_arr == None):
        
        if (state == "disable"):
            db_disabled_docks.disabled_docks = dock_name
    else:
        
        disabled_dock_arr = disabled_dock_arr.split(",")
        if state == "disable":
            disabled_dock_arr.append(dock_name)
        if state == "enable":
            if dock_name in disabled_dock_arr:
                disabled_dock_arr.remove(dock_name)
        
        if disabled_dock_arr == []:
            new_disabled = None
        else:
            disabled_dock_arr = set(disabled_dock_arr)
            disabled_dock_arr = list(disabled_dock_arr)

            new_disabled = ','.join(disabled_dock_arr)
            print(new_disabled)

        db_disabled_docks.disabled_docks = new_disabled
        
    cache_docks[device_id] = db_disabled_docks.disabled_docks
    
    db.commit()
    db.refresh(db_disabled_docks)
    db.close()
    print(db_disabled_docks.disabled_docks)
    print(cache_docks)
    return {"detail":"dock operation sucessful"}


if __name__ == "__main__":

    if not os.path.exists("dockManagement.db"):
        pass
    Base.metadata.create_all(eng)
    app.run(debug = True)
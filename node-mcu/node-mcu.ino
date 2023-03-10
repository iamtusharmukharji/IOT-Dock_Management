
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// WiFi
const char *ssid = "Net_2.4G";           // Enter your WiFi name
const char *password = "Nopassword@163"; // Enter WiFi password

// MQTT Broker
const char *mqtt_broker = "test.mosquitto.org"; // test.mosquitto.org
const char *topic = "north-lucknow-grocery-3347";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

String location_code = "3347";

uint8_t dock_1 = D1;
uint8_t dock_2 = D2;
uint8_t dock_3 = D3;
uint8_t dock_4 = D4;

int total_docks = 4;

char buff[30];





void setup()
{
    pinMode(D0, OUTPUT);
    pinMode(dock_1, INPUT);
    pinMode(dock_2, INPUT);
    pinMode(dock_3, INPUT);
    pinMode(dock_4, INPUT);
    
    // Set software serial baud to 115200;
    Serial.begin(115200);
    device_reconnect();
    
}


void callback(char *topic, byte *payload, unsigned int length)
{   
    // Based on the message recieve as "D0-1"
    Serial.print("Message arrived in topic: ");
    Serial.println(topic);
    Serial.print("Message:");
    String pin = "";
    for (int i = 1; i < 3; i++)
    {
        pin+=(char)payload[i];
    }
    String state = String((char)payload[4]);
    Serial.println(pin);
    Serial.print("state = ");
    Serial.println(state);

    Serial.println();
    Serial.println(" - - - - - - - - - - - -");
}



//function for reconnect to mqtt server and wifi
void device_reconnect(){
    // connecting to a WiFi network
    WiFi.begin(ssid, password);
    Serial.println("Connecting to WiFi..");
    while (WiFi.status() != WL_CONNECTED)
    {
        Serial.print(".");
        digitalWrite(D0,HIGH);
        delay(300);
        digitalWrite(D0,LOW);
        delay(300);
    }

    Serial.println("Connected to the WiFi network");
    WiFi.setAutoReconnect(true);
    WiFi.persistent(true);

    
    // connecting to a mqtt broker
    client.disconnect();
    client.setServer(mqtt_broker, mqtt_port);
    client.setCallback(callback);

    while (!client.connected())
    {
        String client_id = "esp8266-client-";
        client_id += String(ESP.getChipId());

        Serial.printf("The client %s connects to mosquitto mqtt broker\n", client_id.c_str());
        

        if (client.connect(client_id.c_str()))
        {
            Serial.println("Public mosquitto mqtt broker connected");
        }
        else
        {
            Serial.print("failed with state ");
            Serial.print(client.state());
            delay(1400);
        }
    }

    // publish and subscribe
    //on_line_message.toCharArray(buff, on_line_message.length()+1);

    client.publish(topic, "Device-Online");
}

void loop()
{   
    
    if ( (!client.connected()) ||( WiFi.status() != WL_CONNECTED) ) {
        Serial.println("Device Disconnected..");
        device_reconnect();
    }
    
    publish_data();
    delay(1500);
}

void publish_data(){
  //int char_len = 40;

  int dock_sens_1 = !digitalRead(dock_1);
  int dock_sens_2 = !digitalRead(dock_2);
  int dock_sens_3 = !digitalRead(dock_3);

  
  char aux_string[280];
  char data[280];
  
  sprintf(
          aux_string, 
          "{'dock_1': %i, 'dock_2': %i, 'dock_3': %i}-%i",
          dock_sens_1, dock_sens_2, dock_sens_3, total_docks
          );
  
  String temp_data = String(aux_string); 
  String chip_id = "MCU"+String(ESP.getChipId());
  
  temp_data+="-"+chip_id;
  temp_data+="-"+location_code;


  temp_data.toCharArray(data, temp_data.length()+1);
  
  Serial.println(data); 
  client.publish(topic, data);
  } 

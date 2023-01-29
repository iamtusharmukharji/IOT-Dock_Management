
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// WiFi
const char *ssid = "Net_2.4G";           // Enter your WiFi name
const char *password = "Nopassword@163"; // Enter WiFi password

// MQTT Broker
const char *mqtt_broker = "test.mosquitto.org"; // test.mosquitto.org
const char *topic = "lucknow/grocery/3441";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);


uint8_t dock_1 = D1;
uint8_t dock_2 = D2;
uint8_t dock_3 = D3;

void setup()
{
    pinMode(D0, OUTPUT);
    pinMode(dock_1, INPUT);
    pinMode(dock_2, INPUT);
    pinMode(dock_3, INPUT);
    
    
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
    client.publish(topic, "i_am_online");
}

void loop()
{   
    
    if (!client.connected()){
        Serial.println("Mqtt disconnected..");
        device_reconnect();
    }
    
    publish_data();
    delay(1500);
}

void publish_data(){
  int char_len = 35;
  int dock_sens_1 = !digitalRead(dock_1);
  int dock_sens_2 = !digitalRead(dock_2);
  int dock_sens_3 = !digitalRead(dock_3);

  //String data = "{dock_1: "+String(dock_sens_1)+", dock_2: "+String(dock_sens_2)+", dock_3: "+dock_sens_3+"}";
  char aux_string[char_len];
  char data[char_len];
  
  sprintf(aux_string, "{dock_1: %i, dock_2: %i, dock_3: %i}",dock_sens_1,dock_sens_2,dock_sens_3);
  
  String temp_data = String(aux_string); 
  
  temp_data.toCharArray(data, char_len);
  
  Serial.println(data); 
  client.publish(topic, data);
  } 

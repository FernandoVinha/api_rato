// webserver_setup.h
#ifndef WEBSERVER_SETUP_H
#define WEBSERVER_SETUP_H

#include <ESPAsyncWebServer.h>
#include <AsyncTCP.h>
#include "SPIFFS.h"

// Create AsyncWebServer object on port 80
AsyncWebServer server(80);

// Create an Event Source on /events
AsyncEventSource events("/events");

// Search for parameter in HTTP POST request
const char* PARAM_INPUT_1 = "ssid";
const char* PARAM_INPUT_2 = "password";
const char* PARAM_INPUT_3 = "ip";
const char* PARAM_INPUT_4 = "gateway";

//Variables to save values from HTML form
extern String ssid;
extern String password;
String ip;
String gateway;
extern bool function_return;

// File paths to save input values permanently
const char* ssidPath = "/ssid.txt";
const char* passwordPath = "/password.txt";
const char* ipPath = "/ip.txt";
const char* gatewayPath = "/gateway.txt";

IPAddress localGateway(192, 168, 14, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress staticIPs[] = {
  IPAddress(192, 168, 14, 2),
  IPAddress(192, 168, 14, 3),
  IPAddress(192, 168, 14, 4),
  IPAddress(192, 168, 14, 5),
  IPAddress(192, 168, 14, 6),
};

// Timer variables
unsigned long currentMillis = 0;
unsigned long previousMillis = 0;
const long interval = 20000;  // interval to wait for Wi-Fi connection (milliseconds)
unsigned long lastTime = 0;
unsigned long timerDelay = 8000;


// Initialize SPIFFS
bool initSPIFFS() {
  if (!SPIFFS.begin(true)) {
    Serial.println("An error has occurred while mounting SPIFFS");
    return false;
  }
  Serial.println("SPIFFS mounted successfully");
  return true;
}

// Read File from SPIFFS
String readFile(fs::FS &fs, const char * path) {
  Serial.printf("Reading file: %s\r\n", path);

  File file = fs.open(path);
  if (!file || file.isDirectory()) {
    Serial.println("- failed to open file for reading");
    return String();
  }

  String fileContent;
  while (file.available()) {
    fileContent = file.readStringUntil('\n');
    break;
  }
  Serial.print("Dados lidos: ");
  Serial.println(fileContent);
  return fileContent;
}

// Write file to SPIFFS
void writeFile(fs::FS &fs, const char * path, const char * message) {
  Serial.printf("Writing file: %s\r\n", path);

  File file = fs.open(path, FILE_WRITE);
  if (!file) {
    Serial.println("- failed to open file for writing");
    return;
  }
  if (file.print(message)) {
    Serial.println("- file written");
  } else {
    Serial.println("- frite failed");
  }
}

// Remove file to SPIFFS
void remove_files_from_SPISSF() {
  SPIFFS.remove(ssidPath);
  delay(50);
  SPIFFS.remove(passwordPath);
  delay(50);
  SPIFFS.remove(ipPath);
  delay(50);
  SPIFFS.remove(gatewayPath);
  delay(50);
}

// Initialize WiFi
bool initWiFi() {
  //if(ssid=="" || ip==""){
  if (ssid == "") {
    Serial.println("Undefined SSID address.");
    function_return = 0;
    return false;
  }

  // Connect to Wi-Fi
  Serial.print(ssid);
  Serial.print(" / [");
  Serial.print(password);
  Serial.println("]");
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid.c_str(), password.c_str());

  while (WiFi.status() != WL_CONNECTED) {
    currentMillis = millis();
    if (currentMillis - previousMillis >= interval) {
      Serial.println("Failed to connect.");
      delay(1000);
      Serial.println("Deleting network configuration data.");
      remove_files_from_SPISSF();
      delay(1000);
      Serial.println("Restarting ESP");
      delay(500);
      Serial.println("Restarting ESP [3]");
      delay(1000);
      Serial.println("Restarting ESP [2]");
      delay(1000);
      Serial.println("Restarting ESP [1]");
      delay(1000);
      Serial.println("Restarting ESP [0]");
      ESP.restart();
    }
    delay(1000);
    Serial.print(".");
  }

  Serial.println("");
  Serial.print("Connected at ");
  Serial.println( WiFi.localIP().toString() );

  /*
    bool staticIPConfigSuccess = false;
    for (const IPAddress &ip : staticIPs) {
    if (WiFi.config(ip, localGateway, subnet)) {
      staticIPConfigSuccess = true;
      Serial.print("IP estático configurado com sucesso: ");
      Serial.println(WiFi.localIP().toString());
      break;
    } else {
      Serial.print("Erro ao configurar o IP estático: ");
      Serial.println(ip.toString());
    }
    }

    if (!staticIPConfigSuccess) {
    Serial.println("Tentando obter um endereço IP usando DHCP...");
    if (WiFi.config(0U, 0U, 0U)) {
      Serial.print("IP obtido via DHCP: ");
      Serial.println(WiFi.localIP().toString());
    } else {
      Serial.println("Erro ao configurar o DHCP");
      return false;
    }
    }
  */


  function_return = 1;
  return true;
}



bool setup_webServer() {
  if ( !initSPIFFS() ) {
    function_return = 0;
    return false;
  }

  // Load values saved in SPIFFS
  ssid = readFile(SPIFFS, ssidPath);
  password = readFile(SPIFFS, passwordPath);
  ip = readFile(SPIFFS, ipPath);
  gateway = readFile (SPIFFS, gatewayPath);
  Serial.println(ssid);
  Serial.println(password);
  Serial.println(ip);
  Serial.println(gateway);

  if (initWiFi()) {
    /*
      // Route for root / web page
      server.on("/", HTTP_GET, [](AsyncWebServerRequest * request) {
      request->send(SPIFFS, "/index.html", "text/html", false, processor);
      });
      server.serveStatic("/", SPIFFS, "/");

      //server.on("/dyna_logo", HTTP_GET, [](AsyncWebServerRequest * request) {
      //  request->send(SPIFFS, "/dynasensor_icon_1.jpg", "image/png");
      //});

      // Route to set GPIO state to HIGH
      server.on("/on", HTTP_GET, [](AsyncWebServerRequest * request) {
      digitalWrite(ledPin, HIGH);
      request->send(SPIFFS, "/index.html", "text/html", false, processor);
      });

      // Route to set GPIO state to LOW
      server.on("/off", HTTP_GET, [](AsyncWebServerRequest * request) {
      digitalWrite(ledPin, LOW);
      request->send(SPIFFS, "/index.html", "text/html", false, processor);
      });
      server.begin();
    */
    return true;
  }
  else {
    // Connect to Wi-Fi network with SSID and password
    Serial.println("Setting AP (Access Point)");

    String mac_add = "DYNA WIFI-MANAGER ";

    // Obter os 4 últimos caracteres
    String mac_add2 = WiFi.macAddress();
    mac_add2.replace(":", "");
    mac_add2 = mac_add2.substring(mac_add2.length() - 4);
    
    String mac_add3 = mac_add + mac_add2;
    
    // Mostrar o SSID baseado no MAC
    Serial.println(mac_add3);

    // Configurar o ponto de acesso
    WiFi.softAP(mac_add3.c_str(), NULL);

    IPAddress IP = WiFi.softAPIP();
    Serial.print("AP IP address: ");
    Serial.println(IP);

    // Web Server Root URL
    server.on("/", HTTP_GET, [](AsyncWebServerRequest * request) {
      request->send(SPIFFS, "/wifimanager1.html", "text/html");
    });
    server.serveStatic("/", SPIFFS, "/");

    server.on("/dyna_logo", HTTP_GET, [](AsyncWebServerRequest * request) {
      request->send(SPIFFS, "/dynasensor_icon_1.jpg", "image/png");
    });

    // Handle Web Server Events
    events.onConnect([](AsyncEventSourceClient * client) {
      if (client->lastId()) {
        Serial.printf("Client reconnected! Last message ID that it got is: %u\n", client->lastId());
      }
      // send event with message "hello!", id current millis
      // and set reconnect delay to 1 second
      client->send("hello!", NULL, millis(), 10000);
      //delay(100);
      //wifi_list();
    });

    server.addHandler(&events);

    server.on("/", HTTP_POST, [](AsyncWebServerRequest * request) {
      int params = request->params();
      for (int i = 0; i < params; i++) {
        AsyncWebParameter* p = request->getParam(i);
        if (p->isPost()) {
          // HTTP POST ssid value
          if (p->name() == PARAM_INPUT_1) {
            ssid = p->value().c_str();
            Serial.print("SSID set to: ");
            Serial.println(ssid);
            // Write file to save value
            writeFile(SPIFFS, ssidPath, ssid.c_str());
          }
          // HTTP POST pass value
          if (p->name() == PARAM_INPUT_2) {
            password = p->value().c_str();
            Serial.print("Password set to: ");
            Serial.println(password);
            // Write file to save value
            writeFile(SPIFFS, passwordPath, password.c_str());
          }
          // HTTP POST ip value
          if (p->name() == PARAM_INPUT_3) {
            ip = p->value().c_str();
            Serial.print("IP Address set to: ");
            Serial.println(ip);
            // Write file to save value
            writeFile(SPIFFS, ipPath, ip.c_str());
          }
          // HTTP POST gateway value
          if (p->name() == PARAM_INPUT_4) {
            gateway = p->value().c_str();
            Serial.print("Gateway set to: ");
            Serial.println(gateway);
            // Write file to save value
            writeFile(SPIFFS, gatewayPath, gateway.c_str());
          }
          //Serial.printf("POST[%s]: %s\n", p->name().c_str(), p->value().c_str());
        }
      }
      events.send("done", "done", millis());
      //request->send(200, "text/html", "<div \"color=#bbffbb;\" \"background=#aaeeaa;\" \"width=100%;\" \"height=160px;\" \"display=flex;\" \"justify-content=center;\" \"align-items=center;\" id=\"container\" ><div \"color=#228822;\" \"text-align=center\" id=\"content\">Done!<br>The device will automatically restart.<!--<br>Connect to your router and go to the<br>IP Address that will appear on your device's display--></div></div>");
      /*request->send(SPIFFS, "/done.html", "text/html");
        Serial.println("Done. The device will automatically restart. Connect to your router and go to the IP address that will appear on your device's display.");
        server.on("/dyna_logo", HTTP_GET, [](AsyncWebServerRequest * request) {
        request->send(SPIFFS, "/dynasensor_icon_1.jpg", "image/png");
        });
      */
      delay(3000);
      ESP.restart();
    });
    server.begin();

    return false;
  }
}

void webServer() {
  server.on("/", HTTP_GET, [](AsyncWebServerRequest * request) {
    request->send(200, "text/html", "<form action=\"/submit\" method=\"post\">SSID:<br><input type=\"text\" name=\"ssid\"><br>password:<br><input type=\"password\" name=\"password\"><br><br><input type=\"submit\" value=\"Submit\"></form>");
  });

  server.on("/submit", HTTP_POST, [](AsyncWebServerRequest * request) {
    int params = request->params();
    for (int i = 0; i < params; i++) {
      AsyncWebParameter* p = request->getParam(i);
      if (p->isPost()) {
        if (p->name() == "ssid") {
          ssid = p->value().c_str();
        }
        if (p->name() == "password") {
          password = p->value().c_str();
        }
      }
    }
    request->send(200, "text/plain", "Credenciais de Wi-Fi atualizadas");
  });

  server.begin();
}

void wifi_list() {
  //Serial.println("scan start");
  //events.send(String(1).c_str(), "reset_list", millis());
  //events.send(String("Searching...").c_str(), "wifilist", millis());

  // WiFi.scanNetworks will return the number of networks found
  int n = WiFi.scanNetworks();
  //Serial.println("scan done");
  //events.send(String(1).c_str(), "reset_list", millis());

  if (n == 0) {
    Serial.println("no networks found");
  } else {
    //Serial.print(n);
    //Serial.println(" networks found");
    for (int i = 0; i < n; ++i) {
      // Print SSID and RSSI for each network found
      //Serial.print(i + 1);
      //Serial.print(": ");
      //Serial.print(WiFi.SSID(i));
      //Serial.print(" (");
      //Serial.print(WiFi.RSSI(i));
      //Serial.print(")");
      //Serial.println((WiFi.encryptionType(i) == WIFI_AUTH_OPEN) ? " " : "*");
      delay(10);

      events.send(WiFi.SSID(i).c_str(), "wifilist", millis());
    }
  }
}

#endif // WEBSERVER_SETUP_H

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Base64.h>
#include <ESPmDNS.h>
//#include <ArduinoOTA.h>
#include "time.h"
#include "webserver_setup.h"
#include "camera_setup.h"
#include "esp_sleep.h"
#include <HTTPUpdate.h>
#include <WiFiClientSecure.h>

// Define global constants for WiFi credentials
/****** INITIALIZE WITH DATA JUST FOR DEBUG PURPOSE ******/
String ssid = "VIVO24";
String password = "debora1988";

const char* CONFIGURATION_URL = "http://177.73.234.198:88/photo_trap/";

// Define global variables for device configuration and operation
String id = "";
String PHOTO_URL = "";
String PHOTO_PATH = "";
uint16_t PHOTO_PORT;

// Define global variables for firmware update 
String FW_URL = "";
String FW_PATH = "";

String NTP_URL = "";
int GMT_Offset = 0;         // Depends on your timezone
int daylight_Offset = 0;    // Adjust for daylight saving time if necessary

// Define global variables for device configuration
bool success_configure_device = false;
bool success_update_current_time = false;
bool success_calculate_sleep_time = false;
bool success_take_and_send_photo = false;

// Define global variables for current time
uint8_t current_hour = 0;
uint8_t current_min = 0;
uint8_t current_sec = 0;

// Define global vectors for timers received via HTTP GET
//std::vector<String> restartTimes;
std::vector<String> photoShootingTimes;
String get_photo_shooting_frequency;

// Define global vectors for pin numbers
std::vector<uint8_t> pin_flash;
std::vector<uint8_t> pin_ir_emmiter;
std::vector<uint8_t> pin_ir_sensor;

// Define global vector for scheduling times
std::vector<std::string> schedule;

// Define global variables for hardware peripherals
bool flash_led = true;
bool ir_led = false;
const int presence_sensor = 13;
bool wakeup_high = true;

// Define global variable to set threshold difference between 2 photos
uint16_t differenceThreshold = 0;

uint32_t sleep_time = 60000;
uint32_t h = 3600000;
uint32_t m = 60000;

bool restart_device = false;
bool function_return = false;
bool movement_sensor = false;

// Wifi client
WiFiClient client;


// This function sets up the device, including the camera, web server and WiFi connection.
void setup() {
  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  delay(500);

  setupCamera();

  function_return = setup_webServer();
  if ( !function_return ) {
    do {
      wifi_list();
      delay(5000);
    }
    while ( !function_return );
  }

  delay(100);

  // Adicionando os pinos para 'pin_flash'
  pin_flash.push_back(4);

  // Adicionando os pinos para 'pin_ir_emmiter'
  pin_ir_emmiter.push_back(12);

  size_t num_elements;

  num_elements = pin_flash.size();
  for (uint8_t i = 0; i < num_elements; i++) {
    pinMode(pin_flash[i], OUTPUT);
  }

  num_elements = pin_ir_emmiter.size();
  for (uint8_t i = 0; i < num_elements; i++) {
    pinMode(pin_ir_emmiter[i], OUTPUT);
  }

  num_elements = pin_ir_sensor.size();
  for (uint8_t i = 0; i < num_elements; i++) {
    pinMode(pin_ir_sensor[i], INPUT);
  }

  pinMode(presence_sensor, INPUT_PULLUP);

  Serial.println("Starting...");

  do_configure_device();
  if (success_configure_device == true) {
    do_update_current_time();

    if (success_update_current_time == true) {
      do_calculate_sleep_time();

      if (success_calculate_sleep_time == true) {
        do_take_and_send_photo();

        if (success_take_and_send_photo == true) {
          do_sleep();
        }
        else {
          Serial.println("success_take_and_send_photo = FALSE");
          do_sleep_on_demand(10);    // dorme por x minutos
        }
      }
      else {
        Serial.println("success_calculate_sleep_time = FALSE");
        do_sleep_on_demand(10);    // dorme por x minutos
      }
    }
    else {
      Serial.println("success_update_current_time = FALSE");
      do_sleep_on_demand(10);    // dorme por x minutos
    }
  }
  else {
    Serial.println("success_configure_device = FALSE");
    do_sleep_on_demand(10);    // dorme por x minutos
  }
}

void loop() {
  do_sleep_on_demand(10);
}

void do_configure_device() {
  success_configure_device = false;

  String mac_add = "";
  mac_add = WiFi.macAddress();
  mac_add.replace(":", "");
  HTTPClient http;

  http.setTimeout(20000); // 20000 ms = 20 segundos

  http.begin(CONFIGURATION_URL + mac_add + "/"); //Specify the CONFIGURATION_URL
  Serial.print("CONFIGURATION_URL: ");
  Serial.println(CONFIGURATION_URL + mac_add + "/");
  //http.setAuthorization(POST_USERNAME.c_str(), POST_PASSWORD.c_str()); // Add HTTP Basic Auth credentials

  int httpCode = http.GET(); //Make the request
  Serial.print("HTTP response code: ");
  Serial.println(httpCode);

  if (httpCode == 200) { //Check for the returning code
    String payload = http.getString();

    Serial.println(payload);

    // Declare the JsonDocument
    DynamicJsonDocument doc(2048);

    // Parse the JSON
    deserializeJson(doc, payload);

    // Extract values
    id = doc["mac_address"].as<String>();
    String get_ntp_url = doc["ntp_url"];
    int get_gmt_offset = doc["gmt_offset"];
    int get_daylight_offset = doc["daylight_offset"];

    bool get_movement_sensor = doc["movement_sensor"];
    bool get_restart = doc["restart"];

    get_photo_shooting_frequency = doc["photo_shooting_frequency"].as<String>();

    double get_latitude = doc["latitude"];
    double get_longitude = doc["longitude"];
    double get_floor = doc["floor"];

    String get_photo_url = doc["photo_url"];
    String get_photo_path = doc["photo_path"];
    uint16_t get_photo_port = doc["photo_port"];
    String get_firmware_url = doc["firmware_url"];
    String get_firmware_path = doc["firmware_path"];
    bool get_install_new_firmware = doc["install_new_firmware"];

    // Print values
    Serial.println("*****************************************");
    Serial.println("mac_address / id: " + String(id));
    Serial.println("ntp_url: " + String(get_ntp_url));
    Serial.println("gmt_offset: " + String(get_gmt_offset));
    Serial.println("daylight_Offset: " + String(get_daylight_offset));
    Serial.println("movement_sensor: " + String(get_movement_sensor));
    Serial.println("restart: " + String(get_restart));
    Serial.println("photo_shooting_frequency: " + String(get_photo_shooting_frequency));
    Serial.println("latitude: " + String(get_latitude, 6));
    Serial.println("longitude: " + String(get_longitude, 6));
    Serial.println("floor: " + String(get_floor, 6));
    Serial.println("photo_url: " + String(get_photo_url));
    Serial.println("photo_path: " + String(get_photo_path));
    Serial.println("photo_port: " + String(get_photo_port));
    Serial.println("firmware_url: " + String(get_firmware_url));
    Serial.println("firmware_path: " + String(get_firmware_path));
    Serial.println("install_new_firmware: " + String(get_install_new_firmware));
    Serial.println("*****************************************");


    // Setting the device: NTP
    NTP_URL = get_ntp_url;
    GMT_Offset = get_gmt_offset * 3600;
    daylight_Offset = get_daylight_offset * 3600;

    // Setting the device: PHOTO
    PHOTO_URL = get_photo_url;
    PHOTO_PATH = get_photo_path;
    PHOTO_PORT = get_photo_port;

    FW_URL = get_firmware_url;
    FW_PATH = get_firmware_path;

    // Setting the device: MOVEMENT SENSOR
    movement_sensor = get_movement_sensor;

    // Setting the device: RESTART
    restart_device = get_restart;

    if (restart_device) {
      do_restart_device();
    }

    if (get_install_new_firmware) {
      update_firmware();
    }

    // Setting the device: PHOTO SHOOTING FREQUENCY
    // Parse "get_photo_shooting_frequency"
    DynamicJsonDocument freqDoc(4096);
    deserializeJson(freqDoc, get_photo_shooting_frequency);
    JsonArray array2 = freqDoc.as<JsonArray>();

    photoShootingTimes.clear(); // Limpa o vetor antes de preencher com novos horários

    for (JsonVariant v : array2) {
      String time = v.as<String>();
      photoShootingTimes.push_back(time); // Salva o horário no vetor global
    }
    //Serial.println(photoShootingTimes[0]);
    //Serial.println(photoShootingTimes[1]);

    success_configure_device = true;
  }
  else {
    Serial.println("Error on HTTP request");
    success_configure_device = false;
  }

  http.end(); //Free the resources
}

void do_update_current_time() {
  success_update_current_time = false;

  configTime(GMT_Offset, daylight_Offset, NTP_URL.c_str());
  delay(2000);
  struct tm timeinfo;

  if (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to obtain time");
    return;
  }

  current_hour = timeinfo.tm_hour;
  current_min = timeinfo.tm_min;
  current_sec = timeinfo.tm_sec;

  Serial.print("[");
  Serial.print(current_hour);
  Serial.print(":");
  Serial.print(current_min);
  Serial.print(":");
  Serial.print(current_sec);
  Serial.println("]");

  success_update_current_time = true;
}

void do_calculate_sleep_time() {
  char* next_schedule = NULL;
  int next_hour = 24, next_minute = 60;
  String current_time = "";

  if (current_hour < 10) {
    current_time += "0";
  }
  current_time += String(current_hour);
  current_time += ":";
  if (current_min < 10) {
    current_time += "0";
  }
  current_time += String(current_min);


  for (int i = 0; i < photoShootingTimes.size(); ++i) {
    if (compareTime(current_time.c_str(), photoShootingTimes[i].c_str()) < 0) {
      // Parsing schedule time
      int hour, minute;
      sscanf(photoShootingTimes[i].c_str(), "%d:%d", &hour, &minute);

      // Compare and find the closest future time
      if (hour < next_hour || (hour == next_hour && minute < next_minute)) {
        next_schedule = (char*)photoShootingTimes[i].c_str();
        next_hour = hour;
        next_minute = minute;
      }
    }
    else {
      if (compareTime(current_time.c_str(), photoShootingTimes[i].c_str()) == 0) {
        Serial.printf("NOW! - ");
        //sleep_vector[0] = 0;
        sleep_time = 0;
        //Serial.println(sleep_vector[0]);
        //Serial.println(sleep_time);
        return;
        //Serial.printf("Tempo para o próximo horário = %dh e %dmin\n", diff_hour, diff_minute);
      }
    }
  }

  if (next_schedule == NULL) {
    int hour, minute;
    sscanf(photoShootingTimes[0].c_str(), "%d:%d", &hour, &minute);

    // Parsing current time
    int current_hour, current_minute;
    sscanf(current_time.c_str(), "%d:%d", &current_hour, &current_minute);

    // Calculate the time difference
    int diff_hour = 23 - current_hour + hour;
    int diff_minute = 60 - current_minute + minute;

    if (diff_minute == 60) {
      diff_minute = 0;
      diff_hour += 1;
    }

    Serial.printf("Virou o dia! Próximo horário = %dh e %dmin - ", diff_hour, diff_minute);
    //sleep_vector[0] = (uint32_t)(diff_hour * h + diff_minute * m);
    sleep_time = (uint32_t)(diff_hour * h + diff_minute * m);
    //Serial.println(sleep_vector[0]);
    Serial.println(sleep_time);

    success_calculate_sleep_time = true;
    return;
  }

  // Parsing current time
  int current_hour, current_minute;
  sscanf(current_time.c_str(), "%d:%d", &current_hour, &current_minute);

  // Calculate the time difference
  int diff_hour = next_hour - current_hour;
  int diff_minute = next_minute - current_minute;
  if (diff_minute < 0) {
    diff_minute += 60;
    diff_hour -= 1;
  }

  Serial.printf("Tempo para o próximo horário = %dh e %dmin - ", diff_hour, diff_minute);
  //sleep_vector[0] = (uint32_t)(diff_hour * h + diff_minute * m);
  sleep_time = (uint32_t)(diff_hour * h + diff_minute * m);
  //Serial.println(sleep_vector[0]);
  Serial.println(sleep_time);

  success_calculate_sleep_time = true;
}

void do_take_and_send_photo() {
  Serial.println("FUNÇÃO do_take_and_send_photo");
  // frame buffer que será preenchido pela função esp_camera_fb_get().
  camera_fb_t * fb = NULL;
  size_t num_elements_flash = pin_flash.size();
  size_t num_elements_ir = pin_ir_emmiter.size();

  for (uint8_t i = 0; i < num_elements_flash; i++) {
    if (flash_led) {
      digitalWrite(pin_flash[i], HIGH);
    }
    Serial.print(i + 1);
    Serial.print(") ");
    Serial.println("FLASH LED HIGH");
  }
  for (uint8_t i = 0; i < num_elements_ir; i++) {
    if (ir_led) {
      digitalWrite(pin_ir_emmiter[i], HIGH);
    }
    Serial.print(i + 1);
    Serial.print(") ");
    Serial.println("IR LED HIGH");
  }

  delay(600);
  // Take Photo
  fb = takePhoto();
  delay(100);

  for (uint8_t i = 0; i < num_elements_flash; i++) {
    if (flash_led) {
      digitalWrite(pin_flash[i], LOW);
    }
    Serial.print(i + 1);
    Serial.print(") ");
    Serial.println("FLASH LED LOW");
  }
  for (uint8_t i = 0; i < num_elements_ir; i++) {
    if (ir_led) {
      digitalWrite(pin_ir_emmiter[i], LOW);
    }
    Serial.print(i + 1);
    Serial.print(") ");
    Serial.println("IR LED LOW");
  }

  if (!fb) {
    Serial.println("Camera capture failed");
    do_restart_device();
    //return;
  }

  delay(100);

  // Send Photo
  sendPhoto(fb);

  delay(100);

  // Release Photo
  esp_camera_fb_return(fb);
  //releasePhoto(fb);
}

void do_sleep() {
  Serial.print("Starting deep sleep [");
  Serial.print(1000*sleep_time);
  Serial.println("] us. Bye!");

  esp_sleep_enable_timer_wakeup(1000*sleep_time);

  delay(10);

  // Enable a 'ext0' wakeup
  if(wakeup_high) {
    esp_sleep_enable_ext0_wakeup((gpio_num_t)presence_sensor, HIGH);
  }
  else {
    esp_sleep_enable_ext0_wakeup((gpio_num_t)presence_sensor, LOW);
  }

  delay(10);
  
  //Enter into a LIGHT/DEEP sleep:
  // (   ) esp_light_sleep_start();
  // ( x ) esp_deep_sleep_start();
  esp_deep_sleep_start();
}

void do_sleep_on_demand(uint16_t time_min) {
  uint32_t sleep_time;
  sleep_time = time_min * 60000;

  Serial.print("Starting deep sleep [");
  Serial.print(1000*sleep_time);
  Serial.println("] us. Bye!");

  esp_sleep_enable_timer_wakeup(1000*sleep_time);

  delay(10);

  // Enable a 'ext0' wakeup
  if(wakeup_high) {
    esp_sleep_enable_ext0_wakeup((gpio_num_t)presence_sensor, HIGH);
  }
  else {
    esp_sleep_enable_ext0_wakeup((gpio_num_t)presence_sensor, LOW);
  }
  
  //Enter into a LIGHT/DEEP sleep:
  // (   ) esp_light_sleep_start();
  // ( x ) esp_deep_sleep_start();
  esp_deep_sleep_start();
}

void captureAndCompareFrames() {
  differenceThreshold = 0;

  size_t num_elements_flash = pin_flash.size();
  size_t num_elements_ir = pin_ir_emmiter.size();

  Serial.print("Take 1 - ");

  for (uint8_t i = 0; i < num_elements_flash; i++) {
    if (flash_led) {
      digitalWrite(pin_flash[i], HIGH);
    }
    Serial.print(i);
    Serial.print(") ");
    Serial.println("FLASH LED HIGH");
  }
  for (uint8_t i = 0; i < num_elements_ir; i++) {
    if (ir_led) {
      digitalWrite(pin_ir_emmiter[i], HIGH);
    }
    Serial.print(i);
    Serial.print(") ");
    Serial.println("IR LED HIGH");
  }

  camera_fb_t *previousFrame = esp_camera_fb_get();
  if (!previousFrame) {
    Serial.println("Failed to capture frame");
    do_restart_device();
    //return;
  }

  for (uint8_t i = 0; i < num_elements_flash; i++) {
    if (flash_led) {
      digitalWrite(pin_flash[i], LOW);
    }
    Serial.print(i);
    Serial.print(") ");
    Serial.println("FLASH LED LOW");
  }
  for (uint8_t i = 0; i < num_elements_ir; i++) {
    if (ir_led) {
      digitalWrite(pin_ir_emmiter[i], LOW);
    }
    Serial.print(i);
    Serial.print(") ");
    Serial.println("IR LED LOW");
  }

  delay(2000);  // Wait for 2 seconds before capturing the next frame

  for (uint8_t i = 0; i < num_elements_flash; i++) {
    if (flash_led) {
      digitalWrite(pin_flash[i], HIGH);
    }
    if (ir_led) {
      digitalWrite(pin_ir_emmiter[i], HIGH);
    }
    Serial.print(i);
    Serial.print(") ");
    Serial.println("HIGH LED");
  }

  Serial.println("Take 2 - ");
  camera_fb_t *currentFrame = esp_camera_fb_get();
  if (!currentFrame) {
    Serial.println("Failed to capture frame");
    esp_camera_fb_return(previousFrame);
    do_restart_device();
    //return;
  }

  for (uint8_t i = 0; i < num_elements_flash; i++) {
    if (flash_led) {
      digitalWrite(pin_flash[i], LOW);
    }
    if (ir_led) {
      digitalWrite(pin_ir_emmiter[i], LOW);
    }
    Serial.print(i);
    Serial.print(") ");
    Serial.println("LOW LED");
  }


  Serial.print("Tamanho: Foto 1: ");
  Serial.println(previousFrame->len);
  Serial.print("Tamanho: Foto 2: ");
  Serial.println(currentFrame->len);

  int frameDifference = 0;
  for (int i = 0; i < currentFrame->len; i++) {
    frameDifference += abs(currentFrame->buf[i] - previousFrame->buf[i]);
  }

  Serial.print("Image difference: ");
  Serial.println(frameDifference);

  if ( frameDifference > differenceThreshold ) {
    // Send Photo
    sendPhoto(currentFrame);
  }

  esp_camera_fb_return(previousFrame);
  esp_camera_fb_return(currentFrame);
}

String sendPhoto(camera_fb_t* fb) {
  String getAll;
  String getBody;

  /*camera_fb_t * fb = NULL;

    digitalWrite(flash_pin, HIGH);
    delay(delay_before_fb_get);

    fb = esp_camera_fb_get();

    delay(delay_after_fb_get);
    digitalWrite(flash_pin, LOW);
  */

  if (!fb) {
    Serial.println("Camera capture failed");
    delay(1000);
    do_restart_device();
  }

  Serial.println("Connecting to PHOTO URL: " + PHOTO_URL);

  String mac_address = "";
  mac_address = WiFi.macAddress();
  mac_address.replace(":", "");

  if (client.connect(PHOTO_URL.c_str(), PHOTO_PORT)) {
    Serial.println("Connection successful!");

    String head = "--DynaSensor\r\n";
    head += "Content-Disposition: form-data; name=\"photo_trap\"\r\n\r\n";
    head += mac_address + "\r\n";
    head += "--DynaSensor\r\n";
    head += "Content-Disposition: form-data; name=\"photo\"; filename=\"esp32-cam.jpg\"\r\n";
    head += "Content-Type: image/jpeg\r\n\r\n";

    String tail = "\r\n--DynaSensor--\r\n";

    uint32_t imageLen = fb->len;
    uint32_t extraLen = head.length() + tail.length();
    uint32_t totalLen = imageLen + extraLen;

    client.println("POST " + PHOTO_PATH + " HTTP/1.1");
    client.println("Host: " + PHOTO_URL);
    client.println("Content-Length: " + String(totalLen));
    client.println("Content-Type: multipart/form-data; boundary=DynaSensor");


    // Adicionando autenticação Basic ao cabeçalho
    /*String auth = POST_USERNAME + ":" + POST_PASSWORD;
      String encodedAuth = base64::encode(auth);
      client.print("Authorization: Basic ");
      client.println(encodedAuth);
    */

    client.println();
    client.print(head);

    uint8_t *fbBuf = fb->buf;
    size_t fbLen = fb->len;
    Serial.println(fbLen);
    for (size_t n = 0; n < fbLen; n = n + 1024) {
      if (n + 1024 < fbLen) {
        client.write(fbBuf, 1024);
        fbBuf += 1024;
      }
      else if (fbLen % 1024 > 0) {
        size_t remainder = fbLen % 1024;
        client.write(fbBuf, remainder);
      }
    }
    client.print(tail);

    esp_camera_fb_return(fb);

    int timoutTimer = 15000;
    long startTimer = millis();
    boolean state = false;

    while ((startTimer + timoutTimer) > millis()) {
      Serial.print(".");
      delay(100);
      while (client.available()) {
        char c = client.read();
        if (c == '\n') {
          if (getAll.length() == 0) {
            state = true;
          }
          getAll = "";
        }
        else if (c != '\r') {
          getAll += String(c);
        }
        if (state == true) {
          getBody += String(c);
        }
        startTimer = millis();
      }
      if (getBody.length() > 0) {
        break;
      }
    }
    Serial.println();
    client.stop();
    Serial.println(getBody);
    success_take_and_send_photo = true;
  }
  else {
    getBody = "Connection to " + PHOTO_URL +  " failed.";
    Serial.println(getBody);
    success_take_and_send_photo = false;
  }
  return getBody;
  
  delay(60000);
}

void do_restart_device() {
  Serial.println("Reiniciando dispositivo...");
  String mac_add = "";
  mac_add = WiFi.macAddress();
  mac_add.replace(":", "");

  Serial.print("id: ");
  Serial.println( id );
  Serial.print("mac_add: ");
  Serial.println( mac_add );
  
  if( strcmp(mac_add.c_str(), id.c_str()) == 0 ) {
    ESP.restart();
  }
  else {
    Serial.println("ID and MAC ADDRESS are different!");
  }
}


unsigned long timeToMillis(const char* timeStr) {
  // Função para converter horário "HH:MM" para milissegundos desde a meia-noite
  int hours, minutes;

  // Parse hours and minutes
  sscanf(timeStr, "%d:%d", &hours, &minutes);
  return (uint32_t)(hours * h + minutes * m);
}

int compareTime(const char* time1, const char* time2) {
  return strcmp(time1, time2);
  /*
    Retorna 0: Se as duas strings são iguais, a função strcmp() retorna 0.
    Exemplo: current_time = 12:00  e schedule = 12:00

    Retorna um valor negativo: Se a primeira string (time1) é lexicograficamente menor que a segunda (time2).
    Isso significa que, ou o primeiro caractere que não corresponde tem um valor menor em time1 do que em time2,
    ou time1 é uma substring de time2.
    Exemplo: current_time = 12:00  e schedule = 13:00

    Retorna um valor positivo: Se a primeira string (time1) é lexicograficamente maior que a segunda (time2).
    Exemplo: current_time = 14:00  e schedule = 13:00
  */
}

void update_firmware() {
  Serial.println("Updating firmware...");

  WiFiClientSecure client;
  //WiFiClient client;
  client.setTimeout(20000); // 20 segundos
  
  // Essa linha é necessária para o ESP32 aceitar o certificado SSL do GitHub
  // Certifique-se de que entende as implicações de segurança de fazê-lo
  client.setInsecure();

  String firmwareUrl = FW_URL + FW_PATH;
  Serial.print("UPDATING FW: ");
  Serial.println(firmwareUrl);
  t_httpUpdate_return ret = httpUpdate.update(client, firmwareUrl);
  
  Serial.println(ret);

  switch (ret) {
    case HTTP_UPDATE_FAILED:
      Serial.printf("HTTP_UPDATE_FAILD Error (%d): %s\n", httpUpdate.getLastError(), httpUpdate.getLastErrorString().c_str());
      delay(10000);
      do_restart_device();
      break;

    case HTTP_UPDATE_NO_UPDATES:
      Serial.println("HTTP_UPDATE_NO_UPDATES");
      break;

    case HTTP_UPDATE_OK:
      Serial.println("HTTP_UPDATE_OK");
      break;
  }
}

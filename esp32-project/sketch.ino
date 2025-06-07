#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <WiFi.h>
// #include "flood_model.h"
// #include "EloquentTinyML.h"

#define pinoDHT 23
#define modelo DHT22
#define BUZZER_PIN 33

// Configurações modelo
#define DHTPIN 15
#define DHTTYPE DHT22
#define N_INPUTS 2
#define N_OUTPUTS 1
#define TENSOR_ARENA_SIZE 4 * 1024

const char* ssid = "Wokwi-GUEST";
const char* password = "";

LiquidCrystal_I2C lcd(0x27, 16, 2);
const int trigPin = 5;
const int echoPin = 18;

DHT dht(pinoDHT, modelo);

// Instância do modelo
// Eloquent::TinyML::TfLite<N_INPUTS, N_OUTPUTS, TENSOR_ARENA_SIZE> ml;

float run_model_simulado(float temp, float hum) {
  float norm_temp = temp / 50.0;  // supondo 0–50 °C
  float norm_hum = hum / 100.0;   // umidade 0–100%

  float risco = 0.0;

  // Peso maior para umidade
  risco += norm_hum * 0.7;

  // Peso menor para temperatura
  risco += norm_temp * 0.3;

  // Ajusta sensibilidade
  risco = risco * 1.2;

  // Limita entre 0 e 1
  if (risco > 1.0) risco = 1.0;
  if (risco < 0.0) risco = 0.0;

  return risco;
}

void setup() {
  Serial.begin(115200);

  // setub buzzer
  pinMode(BUZZER_PIN, OUTPUT);

  // setup Wifi
  WiFi.begin(ssid, password);
  Serial.print("Conectando Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println("");
  Serial.println("Wi-Fi Conectado: " + WiFi.localIP().toString());

  // setup DHT22
  dht.begin();

  // setup HC-SR04
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // setup LCD
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Monitorando...");

  // ml.begin(_mnt_data_flood_model_tflite);
}

void handledht22(float t, float h) {
  if (isnan(h) || isnan(t)) {
    Serial.println("Falha ao ler do sensor DHT!");
    return;
  }

  Serial.println("Temp: " + String(t, 1) + "°C");
  Serial.println("Humidity: " + String(h, 1) + "%");

  if (t > 30.0) {
    Serial.println("Alerta: Temperatura alta!");
  } else if (t <= 5.0) {
    Serial.println("Alerta: Temperatura baixa!");
  } else {
    Serial.println("Temperatura dentro do normal.");
  }
}

void loop() {
  long duration;
  float distance;

  float h = dht.readHumidity();
  float t = dht.readTemperature();

  handledht22(t, h);
  float predict = run_model_simulado(h, t);

  Serial.println("Predict :" + String(predict, 1));


  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH, 30000);
  if (duration == 0) {
    distance = -1; // sem eco detectado
  } else {
    distance = duration * 0.034 / 2.0;
  }

  Serial.print("Distancia: ");
  Serial.println(distance);

  Serial.print("Duration :");
  Serial.println(duration);

  lcd.setCursor(0, 1);
  lcd.print("                ");
  lcd.setCursor(0, 1);
  if (predict >= 1.0) {
    lcd.print("ALERTA ENCHENTE");
    digitalWrite(BUZZER_PIN, HIGH);
    delay(5000);
  } else {
    lcd.print("Nivel OK!");
    digitalWrite(BUZZER_PIN, LOW);
    delay(5000);
  }

  delay(1000);
}

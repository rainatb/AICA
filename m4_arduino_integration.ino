// Force Sensor Variables
const int FSR_PIN = A0;
const int POWER_PIN_FSR = 9;
const int THRESHOLD_FSR = 3000;
const int DELAY_TIME_FSR = 15000;
bool triggeredFSR = false;
unsigned long lastTriggerTimeFSR = 0;

// Pulse Sensor Variables
#define PulseSensorPurplePin A10
const int LED_PIN = 86;
const int POWER_MONITOR_PIN = 10;
int Signal;
int ThresholdPulse = 1800;
unsigned long lastBeatTime = 0;
unsigned long bpmStartTime = 0;
unsigned long bpmUpdateTime = 0;
int beatCounter = 0;
float bpm = 0;
bool initialized = false;
bool alertTriggered = false;

void setup() {
    Serial.begin(9600);
    analogReadResolution(12);
    
    pinMode(POWER_PIN_FSR, OUTPUT);
    digitalWrite(POWER_PIN_FSR, HIGH);
    
    pinMode(LED_PIN, OUTPUT);
    pinMode(POWER_MONITOR_PIN, OUTPUT);
    digitalWrite(POWER_MONITOR_PIN, HIGH);
    
    Serial.println("Initializing sensors... Please wait 15 seconds for BPM calibration.");
    bpmStartTime = millis();
}

void loop() {
    // **Force Sensor Logic**
    if (!triggeredFSR) {
        int pressureValue = analogRead(FSR_PIN);
        Serial.print("A10 Value: ");
        Serial.println(pressureValue);
        
        if (pressureValue >= THRESHOLD_FSR) {
            Serial.println("Tommy is squeezing AICA very tightly. Please use more calming language and reassure Tommy!");
            triggeredFSR = true;
            lastTriggerTimeFSR = millis();
        }
    } else {
        if (millis() - lastTriggerTimeFSR >= DELAY_TIME_FSR) {
            triggeredFSR = false;
            Serial.println("Resuming FSR readings...");
        }
    }
    
    // **Pulse Sensor Logic**
    Signal = analogRead(PulseSensorPurplePin);
    if (Signal > ThresholdPulse && (millis() - lastBeatTime > 500)) {
        beatCounter++;
        lastBeatTime = millis();
        digitalWrite(LED_PIN, HIGH);
        delay(50);
        digitalWrite(LED_PIN, LOW);
    }
    
    if (!initialized && millis() - bpmStartTime >= 15000) {
        bpm = (beatCounter * 4);
        Serial.print("Initial BPM: ");
        Serial.println(bpm);
        beatCounter = 0;
        bpmUpdateTime = millis();
        initialized = true;
    }
    
    if (initialized && millis() - bpmUpdateTime >= 15000) {
        bpm = (beatCounter * 4);
        Serial.print("BPM: ");
        Serial.println(bpm);
        
        if (bpm >= 100 && bpm <= 111) {
            Serial.println("Heart rate is slightly elevated. Reassure the patient.");
        } else if (bpm > 111) {
            Serial.println("Heart rate significantly elevated. Use calming language.");
            alertTriggered = true;
        }
        
        if (alertTriggered && bpm < 100) {
            Serial.println("Heart rate returned to normal. Resume normal guidance.");
            alertTriggered = false;
        }
        
        beatCounter = 0;
        bpmUpdateTime = millis();
    }
    
    delay(10);
}

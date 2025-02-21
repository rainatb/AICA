// Variables for patient data
int patientAge = 0;
String patientGender = "";
bool receivedPatientData = false;

// Timers
unsigned long lastForceTime = 0;
unsigned long lastPulseTime = 0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  unsigned long currentTime = millis();

  // Receive patient data from Python
  if (Serial.available() > 0) {
    String receivedData = Serial.readStringUntil('\n'); 

    if (receivedData.startsWith("AGE:")) {
      patientAge = receivedData.substring(4).toInt();  
    } else if (receivedData.startsWith("GENDER:")) {
      patientGender = receivedData.substring(7); 
      receivedPatientData = true; 
    }
  }

  if (receivedPatientData) {
    // Define thresholds based on age (2-6 years)
    int grip_force_threshold = (patientAge <= 3) ? 4 : 6; 
    int pulse_threshold = (patientAge <= 3) ? 130 : 110; 

    // Generate sensor readings
    int grip_force = random(3, 10);
    int pulse_rate = random(90, 140);

    // Send grip force status every 5 seconds
    if (currentTime - lastForceTime >= 5000) {
      lastForceTime = currentTime;

      if (grip_force > grip_force_threshold) {
        Serial.println("Grip Status: Elevated grip force - use additional reassurance.");
      } else {
        Serial.println("Grip Status: Normal grip force - continue as usual.");
      }
    }

    // Send pulse status every 30 seconds
    if (currentTime - lastPulseTime >= 30000) {
      lastPulseTime = currentTime;

      if (pulse_rate > pulse_threshold) {
        Serial.println("Pulse Status: Elevated pulse - use additional calming words.");
      } else {
        Serial.println("Pulse Status: Normal pulse - maintain current approach.");
      }
    }
  }
}


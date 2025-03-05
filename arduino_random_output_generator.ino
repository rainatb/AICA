unsigned long lastForceTime = 0;
unsigned long lastPulseTime = 0;

void setup() {
  Serial.begin(9600);
  randomSeed(analogRead(0)); // Seed random number generator
}

void loop() {
  unsigned long currentTime = millis();

  // Send grip force data every 5 seconds
  if (currentTime - lastForceTime >= 5000) {
    lastForceTime = currentTime;

    int force_status = random(0, 2); // Generate 0 or 1
    if (force_status == 0) {
      Serial.println("Grip Status: The patient is using the normal amount of force - continue with regular reassurance and distraction");
    } else {
      Serial.println("Grip Status: The patient is squeezing AICA very tightly- use additional reassuring and calming capabilities");
    }
  }

  // Send pulse data every 15 seconds
  if (currentTime - lastPulseTime >= 15000) {
    lastPulseTime = currentTime;

    int pulse_status = random(0, 2); // Generate 0 or 1
    if (pulse_status == 0) {
      Serial.println("Pulse Status: The patient's heart rate is normal - maintain current approach");
    } else {
      Serial.println("Pulse Status: The patient's heart rate is elevated - use additional calming words and reassurance");
    }
  }
}

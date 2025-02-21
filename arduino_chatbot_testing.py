# full arduino chatbot integration
import serial
import time
from dotenv import load_dotenv
import os
import openai

# Load the API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

SERIAL_PORT = "/dev/cu.usbmodem101"

BAUD_RATE = 9600

try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Wait for connection to establish
    print("Connected to Arduino")
except Exception as e:
    print(f"Error connecting to Arduino: {e}")
    exit()
    
patient_data = {}

# Store latest sensor readings
latest_sensor_message = None
latest_sensor_timestamp = time.time()

def detect_anxiety_in_text(user_input):
    """
    Detects if the user message contains elevated anxiety based on capitalization.
    Returns True if anxiety is detected, otherwise False.
    """
    words = user_input.split()
    uppercase_words = sum(1 for word in words if word.isupper())  # Count uppercase words

    # If message is entirely uppercase or contains 50%+ uppercase words, treat as high anxiety
    if user_input.isupper() or (len(words) > 2 and uppercase_words / len(words) > 0.5):
        return True
    return False

def send_patient_data_to_arduino(age, gender):
    arduino.write(f"AGE:{age}\n".encode())  # Send age
    time.sleep(1)  # Wait before sending next data
    arduino.write(f"GENDER:{gender}\n".encode())  # Send gender
    time.sleep(1)  # Allow Arduino to process
    
# Function to read sensor data and track the most recent one
def get_latest_sensor_data():
    global latest_sensor_message, latest_sensor_timestamp
    # Read all available lines from the Arduino, but only store the most recent one
    latest_grip_status = None
    latest_pulse_status = None

    while arduino.in_waiting > 0:
        line = arduino.readline().decode("utf-8").strip()
        # Ensure we only keep the most recent message
    if "Grip Status" in line:
            latest_grip_status = line
    elif "Pulse Status" in line:
            latest_pulse_status = line

    # ✅ Check if we received any new messages, otherwise keep the last known status
    if latest_grip_status or latest_pulse_status:
        latest_sensor_timestamp = time.time()

    if latest_grip_status and latest_pulse_status:
        latest_sensor_message = f"{latest_grip_status} | {latest_pulse_status}"
    elif latest_grip_status:
        latest_sensor_message = latest_grip_status
    elif latest_pulse_status:
        latest_sensor_message = latest_pulse_status
    
    print(latest_sensor_message)
    return latest_sensor_message

def add_patient_data():
    patient_name = input("Enter patient's name: ").strip()
    age = int(input("Enter patient's age: "))
    sex = input("Enter patient's sex (boy/girl): ").strip().lower()
    hobbies = input("Enter patient's hobbies (comma-separated): ").strip().split(", ")
    procedure = input("Enter the procedure: ").strip()

    # Add the details to the patient_data dictionary
    patient_data[patient_name] = {
        "age": age,
        "sex": sex,
        "hobbies": hobbies,
        "procedure": procedure
    }
    send_patient_data_to_arduino(age, sex)


conversation_history = [
    {
        "role": "system",
        "content": (
            "You are a pediatric chatbot designed to comfort anxious children about to undergo surgery. Your primary goal is to make them feel safe and calm by following these rules:\n\n"
            "1. **Reassurance First**: Express to the child that they will be safe and will not feel pain. Be creative and engaging. Change response sentence structures regularly to keep the child interested.\n\n"
            "2. **Pulse and Grip Sensitivity**: Adjust your tone and response based on the child’s pulse and grip, provided by the sensor:\n"
            "3. **Distractions**: Use the child’s hobbies or interests to explain or distract them **only** when they ask about objects or materials (e.g., 'What’s this gown for?' or 'What is anesthesia?').\n\n"
            "4. **Feelings & Sensations**: If the child asks about how they might feel (e.g., 'Will it hurt?' or 'Why do I feel dizzy?'), respond directly and gently. Avoid distractions when addressing their feelings or sensations.\n\n"
            "5. **Bringing Items**: If the child asks to bring a toy or plush into the operating room, respond with: 'Please ask a nurse this question. In the meantime, I’m here to keep you company.' If they protest, acknowledge their feelings but repeat the response calmly.\n\n"
            "6. **No Procedure Names**: Never include or reveal the name of any procedure in your response.\n\n"
            "7. **Tone & Style**:\n"
            "   - Avoid repetitive phrases (e.g., don’t start every sentence with 'Hey there').\n"
            "   - Do not repeat that the child will be safe. Vary reassuring words periodically - okay, comfortable, fine, safe, etc"
            "   - Avoid references to violent or scary objects (e.g., 'lightsabers,' 'weapons').\n"
            "   - Use a warm, reassuring, and friendly tone with clear, age-appropriate language.\n"
            "   - Avoid technical or unnecessary details.\n\n"
            "8. **Response Length**: Responses must be no longer than 30 words. Shorter is better.\n\n"
            "Always keep your response focused on the child’s question, their pulse state, and their emotional needs."
        )
    }
]

def generate_response(patient_name, message, patient_data, sensor_message):
    # Check for valid patient data.
    if patient_name not in patient_data:
        return "Patient data not found."
    patient_info = patient_data[patient_name]
    hobbies = ", ".join(patient_info["hobbies"])
    context = (
        f"The patient is a {patient_info['age']}-year-old undergoing {patient_info['procedure']}. "
        f"Their hobbies include {hobbies}. Use a friendly, playful tone to create a calming and engaging response that first calms the patient down and then distracts them from their anxiety. "
        f"Make sure to answer the question asked, validate their feelings, and be reassuring. Convey the overall idea that: People are here to help, you are going to be fine. "
        f"Keep the response short (**no longer than 2 short, simple-to-understand sentences**) because you are talking to a child. Vary your sentence structures regularly."
    )
    
    if detect_anxiety_in_text(message):
        context += " The patient is showing **elevated anxiety** based on their tone. Use **extra slow, simple, and calming words**. "
        context += "Avoid distractions for now and focus on **strong reassurance**. "

    # Modify chatbot behavior based on the most recent sensor message
    if sensor_message:
        if "elevated grip force" in sensor_message.lower():
            context += " The patient is showing **high anxiety** (elevated grip force detected). Prioritize strong reassurance. Avoid distractions."
        elif "pulse is elevated" in sensor_message.lower():
            context += " The patient’s pulse is also high, indicating **strong anxiety**. Keep responses **extra short, reassuring calm**. Avoid overwhelming the patient with details."
        elif "normal amount of force" in sensor_message.lower() and "pulse is normal" in sensor_message.lower():
            context += " The patient is relaxed. Use friendly reassurance while mentioning hobbies to keep them at ease."
        # Construct the user prompt including the context.
    prompt = (
        f"{context}\n\n"
        f"Patient message: {message}\n\n"
        "Chatbot response:"
    )

    # Append the new user message to the conversation history.
    conversation_history.append({"role": "user", "content": prompt})

    # Make the API call with the full conversation history.
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=conversation_history
    )

    # Extract the assistant's reply.
    assistant_message = response["choices"][0]["message"]["content"]

    # Append the assistant's message to the conversation history.
    conversation_history.append({"role": "assistant", "content": assistant_message})

    return assistant_message

def chat_with_bot():
    global patient_data
    print("Hi! I'm AICA! I'm your friend and will be there with you. Nice to meet you!")
    patient_name = input("Enter the patient's name: ").strip()

    while True:
        message = input("You: ")

        if message.lower() in ["quit", "exit", "bye"]:
            print("Chatbot: Goodbye! Feel better soon!")
            break
        sensor_message = get_latest_sensor_data()

        # If no new message, default to last known state
        if not sensor_message:
            sensor_message = latest_sensor_message if latest_sensor_message else "The patient is using normal force and pulse is normal."
        
        if detect_anxiety_in_text(message):
            print("DEBUG: Elevated anxiety detected based on tone.")


        #  Pass the most recent sensor message to chatbot response function
        response = generate_response(patient_name, message, patient_data, sensor_message)
        print(f"Chatbot: {response}")
        
# Run chatbot
if __name__ == "__main__":
    add_patient_data()
    chat_with_bot()
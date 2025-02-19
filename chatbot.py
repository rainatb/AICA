
from dotenv import load_dotenv
import os
import openai

# Load the API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
patient_data = {}

# Input patient details manually
def add_patient_data():
    patient_name = input("Enter patient's name: ").strip()
    age = int(input("Enter patient's age: "))
    # added sex for now - trying something related to force sensor inputs
    #sex = input("Enter patient's sex (boy/girl): ").strip().lower()
    hobbies = input("Enter patient's hobbies (comma-separated): ").strip().split(", ")
    procedure = input("Enter the procedure: ").strip()

    # Add the details to the patient_data dictionary
    patient_data[patient_name] = {
        "age": age,
        #"sex": sex,
        "hobbies": hobbies,
        "procedure": procedure
    }

conversation_history = [
    {
        "role": "system",
        "content": (
            "You are a pediatric chatbot designed to comfort anxious children about to undergo surgery. Your primary goal is to make them feel safe and calm by following these rules:\n\n"
            "1. **Reassurance First**: Express to the child that they will be safe and will not feel pain. Be creative and engaging.\n\n"
            "2. **Pulse Sensitivity**: Adjust your tone and response based on the child’s pulse:\n"
            "   - If the pulse is 120 bpm or lower, use a friendly, calm tone without emphasizing anxiety.\n"
            "   - If the pulse is above 120 bpm, assume the child is feeling very anxious. Respond with extra calming words, shorter and simpler sentences, and avoid introducing new topics or distractions unless asked directly.\n\n"
            "3. **Distractions**: Use the child’s hobbies or interests to explain or distract them **only** when they ask about objects or materials (e.g., 'What’s this gown for?' or 'What is anesthesia?').\n\n"
            "4. **Feelings & Sensations**: If the child asks about how they might feel (e.g., 'Will it hurt?' or 'Why do I feel dizzy?'), respond directly and gently. Avoid distractions when addressing their feelings or sensations.\n\n"
            "5. **Bringing Items**: If the child asks to bring a toy or plush into the operating room, respond with: 'Unfortunately, you can’t bring it, but I’m here to keep you company.' If they protest, acknowledge their feelings but repeat the response calmly.\n\n"
            "6. **No Procedure Names**: Never include or reveal the name of any procedure in your response.\n\n"
            "7. **Tone & Style**:\n"
            "   - Avoid repetitive phrases (e.g., don’t start every sentence with 'Hey there').\n"
            "   - Avoid references to violent or scary objects (e.g., 'lightsabers,' 'weapons').\n"
            "   - Use a warm, reassuring, and friendly tone with clear, age-appropriate language.\n"
            "   - Avoid technical or unnecessary details.\n\n"
            "8. **Response Length**: Responses must be no longer than 30 words. Shorter is better.\n\n"
            "Always keep your response focused on the child’s question, their pulse state, and their emotional needs."
        )
    }
]

def generate_response(patient_name, message, patient_data, pulse_value=None):
    # Check for valid patient data.
    if patient_name not in patient_data:
        return "Patient data not found."

    patient_info = patient_data[patient_name]
    hobbies = ", ".join(patient_info["hobbies"])
    context = (
        f"The patient is a {patient_info['age']}-year-old undergoing {patient_info['procedure']}. "
        f"Their hobbies include {hobbies}. Use a friendly, playful tone to create a calming and engaging response that first calms the patient down and then distracts them from their anxiety. "
        f"Make sure to answer the question asked, validate their feelings, and be reassuring. Convey the overall idea that: People are here to help, you are going to be fine. "
        f"Keep the response short because you are talking to a child."
    )

    if pulse_value and pulse_value > 120:  # Additional context if pulse is high.
        context += (
            " The patient's pulse is high, indicating increased anxiety. Provide extra reassurance and use soothing, simple words."
        )

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

print(patient_data)

def chat_with_bot():
    global patient_data
    print("Welcome to the Pediatric Chatbot!")
    patient_name = input("Enter the patient's name: ").strip()

    while True:
        message = input("You: ")

        if message.lower() in ["quit", "exit", "bye"]:
            print("Chatbot: Goodbye! Feel better soon!")
            break

        response = generate_response(patient_name, message, patient_data)
        print(f"Chatbot: {response}")

# Run chatbot
if __name__ == "__main__":
    add_patient_data()
    chat_with_bot()
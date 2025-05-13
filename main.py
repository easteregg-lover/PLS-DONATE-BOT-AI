import keyboard
import requests
import time
import tkinter as tk
import pyperclip
import random
from threading import Thread
from datetime import datetime

COHERE_API_KEY = "COHERE_API_KEY"

running = False 

LOG_FILE_PATH = "chat_logs.txt"

def log(message):
    """Display log messages in console, update GUI label, and write to log file."""
    print(f"[LOG] {message}")
    status_label.config(text=f"Status: {message}")
    with open(LOG_FILE_PATH, "a") as log_file:
        log_file.write(f"{datetime.now()}: {message}\n")

def generate_prompt():
    """Randomly choose between a fun fact or a joke prompt."""
    return random.choice([
        "Provide a concise and interesting fun fact that is under 150 characters. Keep it short and to the point. it shall be interesting",
        "Provide a short, clean, and appropriate joke that is under 150 characters. Avoid any introduction like 'Here is a joke' or 'Let me tell you a joke' it shall be interesting."
    ])

def send_to_cohere():
    """Send a refined prompt to Cohere and get a clean, trimmed response."""
    prompt = generate_prompt()
    log("Sending prompt to Cohere...")

    url = "https://api.cohere.com/v1/generate"
    headers = {
        "Authorization": f"Bearer {COHERE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "max_tokens": 150,
        "temperature": 1,
        "k": 0,
        "stop_sequences": [],
        "return_likelihoods": "NONE"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        generated_text = result.get("generations", [{}])[0].get("text", "").strip()

        if not generated_text:
            return "I couldn't generate a response."

        cleaned = generated_text.replace("\n", " ").strip()
        if len(cleaned) > 150:
            cleaned = cleaned[:150].rsplit(".", 1)[0] + "." if "." in cleaned[:150] else cleaned[:150]

        log(f"Generated: {cleaned}")
        return cleaned

    except Exception as e:
        log(f"[ERROR] Failed to contact Cohere: {e}")
        return "Error generating response."

def send_chat_message(message):
    """Copy message and simulate paste + enter in Roblox chat."""
    log("Preparing to send to Roblox chat...")
    pyperclip.copy(message)
    time.sleep(0.2)
    keyboard.press_and_release("/") 
    time.sleep(0.5)
    keyboard.press_and_release("ctrl+v")
    time.sleep(0.2)
    keyboard.press_and_release("enter") 
    log("Message sent.")

def send_large_message_in_parts(message):
    """Send long messages in multiple parts if they exceed 200 characters."""
    while len(message) > 200:
        part = message[:200]
        send_chat_message(part)
        message = message[200:]
        time.sleep(1)  
    if message:
        send_chat_message(message)  

def main_loop():
    """Loop that sends fun facts or jokes every minute."""
    global running
    while running:
        try:
            message = send_to_cohere()
            send_large_message_in_parts(message)  
            time.sleep(20)  
        except Exception as e:
            log(f"[ERROR] {e}")
            time.sleep(5)  

def start():
    """Start the bot loop."""
    global running
    if not running:
        running = True
        log("Bot started.")
        Thread(target=main_loop, daemon=True).start()

def stop():
    """Stop the bot loop."""
    global running
    running = False
    log("Bot stopped.")

def test_cohere():
    """Test button: Generate a single message and copy it to clipboard."""
    log("Testing Cohere response...")
    response = send_to_cohere()
    pyperclip.copy(response)
    log("Copied to clipboard.")

def detect_chat_message():
    """Detect messages typed by other players in Roblox chat and log them."""
    while running:
        if keyboard.is_pressed("`"):  # Simulating a player message (change key as needed)
            message = "Player Message Detected: 'Hello, this is a test!'"  # Simulate message
            log(message)
            time.sleep(0.5)  # Simulate pause to avoid multiple detections

# Tkinter GUI setup
root = tk.Tk()
root.title("Roblox AI Chatbot")
root.geometry("350x320")
root.attributes("-topmost", True)

tk.Label(root, text="Roblox AI Chatbot", font=("Arial", 16)).pack(pady=10)
tk.Button(root, text="Start", command=start, font=("Arial", 12), bg="green", fg="white").pack(pady=5)
tk.Button(root, text="Stop", command=stop, font=("Arial", 12), bg="red", fg="white").pack(pady=5)
tk.Button(root, text="Test Cohere", command=test_cohere, font=("Arial", 12), bg="purple", fg="white").pack(pady=5)

status_label = tk.Label(root, text="Status: Idle", font=("Arial", 10))
status_label.pack(pady=20)


Thread(target=detect_chat_message, daemon=True).start()

root.mainloop()

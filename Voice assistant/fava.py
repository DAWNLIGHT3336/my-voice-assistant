import cv2
import face_recognition
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import sys
import wikipediaapi 
import requests
from geopy.geocoders import Nominatim
import time
import tkinter as tk
from tkinter import messagebox
from googletrans import Translator, LANGUAGES

# Initialize recognizer, text-to-speech engine, and translator
recognizer = sr.Recognizer()
engine = pyttsx3.init()
translator = Translator()

# Function to speak text aloud
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to listen to voice input and return as text
def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            print("Recognizing...")
            query = recognizer.recognize_google(audio, language="en-US")
            print(f"User said: {query}\n")
        except sr.UnknownValueError:
            print("Sorry, I didn't get that.")
            return "None"
        except sr.RequestError:
            print("Sorry, my speech service is down.")
            return "None"
        except sr.WaitTimeoutError:
            print("Listening timed out.")
            return "None"
        return query.lower()

# Face authentication function
def face_authentication():
    global reference_encoding  # Ensure global access to reference_encoding
    for attempt in range(3):
        print("Please look at the camera...")
        speak("Please look at the camera.")
        live_image = capture_live_image()
        is_match = recognize_face(reference_encoding, live_image)

        if is_match:
            print("Face recognized! Access granted.")

            return True
        else:
            speak(f"Face not recognized. Attempt {attempt + 1} of 3.")
    speak("Face recognition failed. Access denied.")
    return False

# Capture a live image from the webcam
def capture_live_image():
    video_capture = cv2.VideoCapture(0)
    window_name = 'Video'
    print("Press 'c' to capture the image.")

    while True:
        ret, frame = video_capture.read()
        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == ord('c'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return frame

# Recognize face from live image and reference image
def recognize_face(reference_encoding, live_image):
    live_image_rgb = cv2.cvtColor(live_image, cv2.COLOR_BGR2RGB)
    live_encodings = face_recognition.face_encodings(live_image_rgb)

    if len(live_encodings) > 0:
        matches = face_recognition.compare_faces([reference_encoding], live_encodings[0])
        return matches[0]
    else:
        return False

# Function to set the reference image for face authentication
def set_reference_image(image_path):
    try:
        reference_image = face_recognition.load_image_file(image_path)
        reference_encoding = face_recognition.face_encodings(reference_image)[0]  # Use loaded image
        return reference_encoding
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        sys.exit(1)
    except IndexError:
        print(f"Error: No faces found in the image {image_path}.")
        sys.exit(1)

# Voice authentication function
def voice_authentication(required_phrase="open assistant"):
    for attempt in range(3):
        speak("Please say the passphrase.")
        user_input = listen()
        if user_input == required_phrase.lower():
            return True
        else:
            speak(f"Incorrect passphrase. Attempt {attempt + 1} of 3.")
    speak("Voice authentication failed. Access denied.")
    return False

# Password authentication function
def password_authentication(correct_password="DBA"):
    user_input = password_input.get()  # Get the input from the Tkinter entry field
    if user_input == correct_password:
        print("Password correct! Access granted.")
        return True
    else:

        print(f"Incorrect password.")
        speak("Incorrect password.")
    return False

# Function to switch to the translation page
def switch_to_translate_page():
    command_frame.pack_forget()
    translate_frame.pack()
    app.geometry("600x400")

# Function to switch back to the command page
def switch_to_command_page():
    auth_frame.pack_forget()  # Hide the authentication frame
    command_frame.pack()  # Show the command frame (the new page)
    app.geometry("400x400")

# Function to handle text translation
def translate_text():
    text = translate_input.get("1.0", tk.END).strip()  # Get the text from the input field
    target_language_name = language_code_var.get()  # Get the selected language name

    # Get the language code from the selected language name
    target_language_code = None
    for code, lang in LANGUAGES.items():
        if lang == target_language_name.lower():
            target_language_code = code
            break

    if target_language_code is None:
        speak("Sorry, the target language is not recognized.")
        return

    # Ensure both text and language are provided
    if text and target_language_code:
        try:
            translation = translator.translate(text, dest=target_language_code)
            translated_text = translation.text
            translated_label.config(text=f"Translated Text: {translated_text}")
            speak(f"The translation is: {translated_text}")
        except Exception as e:
            speak("Sorry, there was an error with the translation.")
            print(e)
    else:
        messagebox.showwarning("Input Error", "Please enter text and select a language.")

# Function to handle voice commands
def listen_command():
    command = listen()
    if command != "none":
        handle_command(command)

def recognize_command(command):
    """
    Recognizes and displays the entered or spoken command.
    Updates the recognized_command_label with the recognized command.
    """
    global recognized_command_label  # Access the label globally
    # Convert command to lowercase to make it case-insensitive
    command = command.strip().lower()
    
    # Update the recognized_command_label with the processed command
    recognized_command_label.config(text=f"Recognized Command: {command}")

    # Return the command for further processing
    return command


# Function to execute a command from the text field
def execute_command():
    command = command_input_field.get().strip()  # Get command from input field
    command_input_field.delete(0, tk.END)  # Clear input field after getting the command
    
    # Call recognize_command to display the command in the label
    recognized_command = recognize_command(command)

    # Handle the recognized command
    handle_command(recognized_command)

def search_wikipedia(query):
    # Specify a user agent
    user_agent = "YourVoiceAssistant/1.0 (https://meta.wikimedia.org/wiki/User-Agent_policy; xk257891@gmail.com)"
    wiki_wiki = wikipediaapi.Wikipedia('en-US')
    page = wiki_wiki.page(query)
    
    if page.exists():
        # Limiting the summary to 500 words
        summary = page.summary[:500]
        return summary
    else:
        return "Sorry, I couldn't find any information on that topic."

# Function to search Google and open the website if it's not explicit
def search_google_and_open(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")


# Function to process various commands
def handle_command(command):
    global recognized_command_label  # Ensure recognized_command_label is accessible
    command = command.lower()  # Ensure the command is case-insensitive

    # Now that recognize_command updated the label, process the command
    if 'translate' in command:
        switch_to_translate_page()

    elif 'time' in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {current_time}")

    elif 'date' in command:
        speak(f"Today's date is {datetime.datetime.now().strftime('%B %d, %Y')}")

    elif 'open google' in command:
        speak("Opening Google")
        webbrowser.open(0)

    elif 'open youtube' in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")

    elif 'play music' in command:
        music_dir = "C:\\Users\\xk257\\Music"
        songs = os.listdir(music_dir)
        os.startfile(os.path.join(music_dir, songs[0]))
        speak(f"Playing {songs[0]}")

    elif 'search wikipedia' in command:
        topic = command.replace('search wikipedia', '').strip()  # Extract the topic
        summary = search_wikipedia(topic)
        speak(summary)
        recognized_command_label.config(text=f"Wikipedia Summary: {summary}")

    elif 'search google' in command:
        query = command.replace('search google', '').strip()  # Extract the query
        search_google_and_open(query)
        speak(f"Searching Google for {query}")

    elif 'shutdown' in command:
        speak("Shutting down the system")
        os.system("shutdown /s /t 1")

    elif 'lock my computer' in command:
        speak("Locking your computer.")
        os.system("rundll32.exe user32.dll,LockWorkStation")

    elif 'where am i' in command or 'my location' in command:
        speak("Let me check your location...")
        location = get_location()
        speak(f"You are at {location}")

    elif 'stop' in command or 'exit' in command:
        speak("Goodbye!")
        sys.exit(0)

    else:
        speak("Sorry, I didn't understand that command.")


# Function to fetch the user's location using IP-based geolocation
def get_location():
    try:
        response = requests.get("https://ipinfo.io")
        data = response.json()
        loc = data['loc'].split(',')
        geolocator = Nominatim(user_agent="voice_assistant")
        location = geolocator.reverse(f"{loc[0]}, {loc[1]}")
        return location.address
    except Exception as e:
        print(f"Error fetching location: {e}")
        return "I couldn't fetch the location. Please try again."

# Function to handle password authentication
def on_password_authenticate():
    if password_authentication():
        auth_frame.pack_forget()  # Hide authentication frame
        switch_to_command_page()  # Switch to command page
        password_button.config(state="disabled")
        face_button.config(state="disabled")
        voice_button.config(state="disabled")
        speak("Password authentication successful. How can I assist you today?")
    else:
        messagebox.showerror("Authentication Failed", "Password authentication failed.")
        sys.exit(0)

def on_face_authenticate():
    if face_authentication():
        auth_frame.pack_forget()  # Hide authentication frame
        switch_to_command_page()  # Switch to command page
        password_button.config(state="disabled")
        face_button.config(state="disabled")
        voice_button.config(state="disabled")
        speak("Face authentication successful. How can I assist you today?")
    else:
        messagebox.showerror("Authentication Failed", "Face authentication failed.")
        sys.exit(0)

def on_voice_authenticate():
    if voice_authentication():
        auth_frame.pack_forget()  # Hide authentication frame
        switch_to_command_page()  # Switch to command page
        password_button.config(state="disabled")
        face_button.config(state="disabled")
        voice_button.config(state="disabled")
        speak("Voice authentication successful. How can I assist you today?")
    else:
        messagebox.showerror("Authentication Failed", "Voice authentication failed.")
        sys.exit(0)

# Main function to set up the app and UI
def main():
    global recognized_command_label  # Declare it as global here
    global app, auth_frame, command_frame, translate_frame, password_input
    global command_input_field, translate_input, language_code_var, translated_label
    global password_button, face_button, voice_button  # Make these global to be accessed in other functions
    global reference_encoding  # Declare as global
    reference_encoding = set_reference_image(r"C:\Users\xk257\OneDrive\Desktop\Voice assistant\ti.jpg")
    

    # Load the reference image for face recognition
    reference_encoding = set_reference_image(r"C:\Users\xk257\OneDrive\Desktop\Voice assistant\ti.jpg")
  
    # Create the main app window
    app = tk.Tk()
    app.title("Voice Assistant with Translation")
    app.geometry("500x500")

# Authentication frame (this is the first frame the user will see)
    auth_frame = tk.Frame(app)
    auth_frame.pack()

    welcome_label = tk.Label(auth_frame, text="Welcome to the Voice Assistant", font=("Helvetica", 14))
    welcome_label.pack(pady=10)

    password_label = tk.Label(auth_frame, text="Enter password:", font=("Helvetica", 12))
    password_label.pack(pady=5)

    password_input = tk.Entry(auth_frame, show="*", width=30, font=("Helvetica", 12))
    password_input.pack(pady=5)

    # Password authentication button
    password_button = tk.Button(auth_frame, text="Submit", command=on_password_authenticate)
    password_button.pack(pady=10)

    # Face authentication button
    face_button = tk.Button(auth_frame, text="Face Authentication", command=on_face_authenticate)
    face_button.pack(pady=5)

    # Voice authentication button
    voice_button = tk.Button(auth_frame, text="Voice Authentication", command=on_voice_authenticate)
    voice_button.pack(pady=5)

    # Command input frame (hidden by default, shown after authentication)
    command_frame = tk.Frame(app)

    command_input_label = tk.Label(command_frame, text="Enter Command:", font=("Helvetica", 12))
    command_input_label.pack(pady=10)

    command_input_field = tk.Entry(command_frame, width=30, font=("Helvetica", 12))
    command_input_field.pack(pady=5)

    execute_button = tk.Button(command_frame, text="Execute", command=execute_command, width=10)
    execute_button.pack(pady=5)

    speak_button = tk.Button(command_frame, text="Speak", command=listen_command, width=10)
    speak_button.pack(pady=5)

    # Initialize recognized_command_label here
    recognized_command_label = tk.Label(command_frame, text="", font=("Helvetica", 10))
    recognized_command_label.pack(pady=10)

    # Translate frame (translation page, hidden by default)
    translate_frame = tk.Frame(app)

    input_label = tk.Label(translate_frame, text="Enter text to translate:", font=("Helvetica", 12))
    input_label.pack(pady=10)

    translate_input = tk.Text(translate_frame, width=40, height=5)
    translate_input.pack(pady=5)

    language_code_var = tk.StringVar(value="Select language")
    language_dropdown = tk.OptionMenu(translate_frame, language_code_var, *LANGUAGES.values())
    language_dropdown.pack(pady=5)

    translate_button = tk.Button(translate_frame, text="Translate", command=translate_text, width=10)
    translate_button.pack(pady=5)

    translated_label = tk.Label(translate_frame, text="Translated Text:", font=("Helvetica", 12))
    translated_label.pack(pady=10)

    back_button = tk.Button(translate_frame, text="Back to Command", command=switch_to_command_page, width=15)
    back_button.pack(pady=10)

    app.mainloop()

if __name__ == "__main__":
    main()
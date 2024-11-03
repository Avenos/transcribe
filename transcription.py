import azure.cognitiveservices.speech as speechsdk
import pyautogui
from pynput import keyboard
import time

# Read API key from file
def get_api_key(filename='apikey.txt'):
    with open(filename, 'r') as f:
        return f.read().strip()

# Set up Azure Speech Service
def create_speech_config(api_key, region="westus2"):
    return speechsdk.SpeechConfig(subscription=api_key, region=region)

# Simulate typing into the active window
def simulate_typing(text):
    for char in text:
        pyautogui.press(char)  # Press each character without a delay
        time.sleep(0.005)  # Sleep for 5 ms

# Record audio and transcribe it in real-time
def transcribe_audio(speech_config):
    audio_input = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    # Function to handle recognized speech
    def recognized(event):
        if event.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Speech recognized: " + event.result.text)
            simulate_typing(event.result.text)
        elif event.result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech recognized.")
            simulate_typing("No speech recognized.")
        else:
            print(f"Recognition error: {event.result.reason}")

    # Start continuous recognition
    speech_recognizer.recognized.connect(recognized)
    speech_recognizer.start_continuous_recognition()
    return speech_recognizer

# Global variables
recording = False
speech_recognizer = None
insert_key_pressed = False

# Listen for key presses
def on_press(key):
    global recording, speech_recognizer, insert_key_pressed

    try:
        if key == keyboard.Key.insert:  # Start recording on Insert key press
            if not insert_key_pressed:
                print("Recording...")
                insert_key_pressed = True
                recording = True
                speech_recognizer = transcribe_audio(speech_config)

        elif key == keyboard.Key.delete:  # Exit the program on Delete key
            print("Exiting the program...")
            if recording:
                recording = False
                if speech_recognizer:
                    speech_recognizer.stop_continuous_recognition()
            return False  # Stop the listener

    except Exception as e:
        print(f"Error: {e}")

# Listen for key releases
def on_release(key):
    global insert_key_pressed, recording, speech_recognizer

    if key == keyboard.Key.insert:  # Stop recording on Insert key release
        if insert_key_pressed:
            insert_key_pressed = False
            recording = False
            if speech_recognizer:
                speech_recognizer.stop_continuous_recognition()
                speech_recognizer = None

# Main function
def main():
    global speech_config

    print("Ins to transcribe, Del to exit")

    api_key = get_api_key()
    speech_config = create_speech_config(api_key, region="westus2")

    # Set up key listeners
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    listener.join()  # Wait for the listener to finish

if __name__ == "__main__":
    main()

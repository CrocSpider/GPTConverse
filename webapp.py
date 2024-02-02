import os
import concurrent.futures
from flask import Flask, render_template, request
import time
import itertools
from dotenv import load_dotenv
import openai
import pyaudio
import wave
from elevenlabs import Voice, VoiceSettings, generate
from elevenlabs import set_api_key
import io
from pydub import AudioSegment
from pydub.playback import play
import webrtcvad
import requests
import json

load_dotenv()
app = Flask(__name__)

# Initialize PyAudio
audio = pyaudio.PyAudio()

# OpenAI and ElevenLabs API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

openai.api_key = openai_api_key
set_api_key(elevenlabs_api_key)

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 480
RECORD_SECONDS = 5

vad = webrtcvad.Vad()

def is_speech(frame):
    return vad.is_speech(frame, RATE)

def get_voice_input():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Start speaking...")

    frames = []
    silence_frames = 0

    while True:
        data = stream.read(CHUNK)
        frames.append(data)

        if not is_speech(data):
            silence_frames += 1
        else:
            silence_frames = 0

        # Stop if there's silence for more than 1 seconds
        if silence_frames > int(RATE / CHUNK):
            break

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded data as a WAV file for Whisper
    temp_audio_file = "output.wav"
    wf = wave.open(temp_audio_file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Use Whisper for speech-to-text
    with open(temp_audio_file, 'rb') as audio_file:
        result = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text")
    text_input = result

    return text_input

def send_to_ollama(text):
    # Send text to OpenAI API and receive response using ChatGPT-4
    url = "https://ollama-test.apps.private.k8s.springernature.io/api/generate"
    data = {
            "model": "mistral:7b",
            "prompt":text,
            "stream": False
            }
    response = requests.post(url, json=data)
    audio_data = response.text  # Assuming API returns audio data directly
    parsed_response = json.loads(audio_data)
    return parsed_response["response"]

def send_to_chatgpt(text):
    # Send text to OpenAI API and receive response using ChatGPT-4
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a highly skilled AI with wide range of knowledge and skills."
            },
            {
                "role": "user",
                "content": text
            }
        ])  # Adjust model name if needed
    return response.choices[0].message.content


def tts_openai(text):

    response = openai.audio.speech.create(
      model="tts-1",
      voice="onyx",
      input=text
    )

    audio_data = b""
    for chunk in response.iter_bytes(chunk_size=1024):
        if chunk:
            audio_data += chunk

    return audio_data


def text_to_voice(text, voice):

    audio = generate(
        text=text,
        voice=Voice(
            voice_id=voice,
            settings=VoiceSettings(stability=0.4, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
        )
    )

    return audio

    # Send text to ElevenLabs API for voice synthesis
    #headers = {"Authorization": f"Bearer {elevenlabs_api_key}"}
    #data = {
    #    "text": text,
    #    "voice": voice  # Specify the voice here
    #}
    #response = requests.post("https://api.elevenlabs.io/v1/text-to-speech/voice", headers=headers, json=data)
    #audio_data = response.content  # Assuming API returns audio data directly
    #return audio_data

def play_voice_output(audio_data):
    # Code to play the audio data
    # Use PyAudio to play the audio data
    audio_stream = io.BytesIO(audio_data)
    audio_segment = AudioSegment.from_file(audio_stream, format="mp3")
    play(audio_segment)


def print_letter_by_letter(text):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(0.02)  # Adjust the delay to control the speed

def print_waiting_animation(text):
    spinner = itertools.cycle(['⣾', '⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽'])
    max_iterations = 50  # Maximum number of iterations for the animation
    for i in range(max_iterations):
        print(next(spinner), end='\r', flush=True)
        time.sleep(0.1)  # Adjust the delay to control the speed

        # Check if the tts_openai function has returned, and break the loop if so
        if i > len(text) / 3:  # Adjust the factor to control when to stop the animation
            print(' ' * len(text), end='\r', flush=True)  # Overwrite the line with spaces
            break

    print()  # Move to the next line after stopping the animation


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_voice', methods=['POST'])

def process_voice():

    voice_choice = "jlUJTmEZ0IaJHW6BtKkJ"  # Replace with the name of the voice you want to use
    stop_words = ["stop", "bye", "exit"]  # Replace with the stop word you want to use

    while True:
        
        # Get Whisper output
        #print_waiting_animation(user_text)
        whisper_output = get_voice_input()
        if any(word in whisper_output for word in stop_words):
            break
        print("You:", whisper_output)  # Print the Whisper output to the console

        # Get GPT response
        print_waiting_animation(whisper_output)
        chatgpt_response = send_to_ollama(whisper_output)
        print("Assistant:", chatgpt_response)  # Print the GPT response to the console

        # Convert GPT response to voice and play
        audio_data = tts_openai(chatgpt_response)
        #audio_output = text_to_voice(chatgpt_response,voice_choice)
        play_voice_output(audio_data)

    return render_template('index.html', chatgpt_response='')


if __name__ == '__main__':
    app.run(debug=True)
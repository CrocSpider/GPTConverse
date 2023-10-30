import os
import openai
import pyaudio
import wave
from elevenlabs import Voice, VoiceSettings, generate
from elevenlabs import set_api_key
import io
from pydub import AudioSegment
from pydub.playback import play


# Initialize PyAudio
audio = pyaudio.PyAudio()

# OpenAI and ElevenLabs API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

openai.api_key = openai_api_key
set_api_key(elevenlabs_api_key)

def get_voice_input():
    # Start audio stream
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    frames = []

    # Capture audio for a predetermined duration or until a stop condition
    for i in range(0, int(16000 / 1024 * 5)):  # Example: 5 seconds of audio
        data = stream.read(1024)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Save the audio to a temporary file
    temp_audio_file = "temp_audio.wav"
    wf = wave.open(temp_audio_file, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Use Whisper for speech-to-text
    with open(temp_audio_file, 'rb') as audio_file:
        result = openai.Audio.transcribe("whisper-1", audio_file)
    text_input = result["text"]

    return text_input

def send_to_chatgpt(text):
    # Send text to OpenAI API and receive response using ChatGPT-4
    response = openai.ChatCompletion.create(model="gpt-4", messages=[
            {
                "role": "system",
                "content": "You are a highly skilled AI with wide range of knowledge and skills."
            },
            {
                "role": "user",
                "content": text
            }
        ])  # Adjust model name if needed
    return response['choices'][0]['message']['content']

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


def main():
    voice_choice = "YdsnigEr6KLWyV7njdiO"  # Replace with the name of the voice you want to use

    while True:
        user_text = get_voice_input()
        chatgpt_response = send_to_chatgpt(user_text)
        audio_data = text_to_voice(chatgpt_response, voice_choice)
        play_voice_output(audio_data)

if __name__ == "__main__":
    main()

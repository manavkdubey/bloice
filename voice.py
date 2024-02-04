import openai
import pyaudio
import wave
from pydub import AudioSegment
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('PROJECT_API_KEY')

# Set the parameters for audio recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
OUTPUT_FILENAME = "input.mp3"

# Initialize the audio stream
audio = pyaudio.PyAudio()

# Open a new audio stream for recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("Recording...")

frames = []

# Record audio for the specified duration
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Recording finished.")

# Stop and close the audio stream
stream.stop_stream()
stream.close()
audio.terminate()

sound_file= wave.open(OUTPUT_FILENAME,"wb")
sound_file.setnchannels(1)
sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
sound_file.setframerate (44100)
sound_file.writeframes(b''. join (frames))
sound_file.close()


client = openai.OpenAI(api_key=API_KEY)
file = open("input.mp3", "rb")
transcript = client.audio.transcriptions.create(
  model="whisper-1", 
  file=file,
  response_format="text"
)
print(transcript)
prompt = transcript
completion = client.chat.completions.create(
  model="gpt-4-0125-preview",
  messages=[
    {"role": "system", "content": "You are a helpful assistant that provides the answer to the user."},
    {"role": "user", "content": prompt}
  ]
)
print("<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>")
print(completion.choices[0].message.content)


speech_file_path = "blah.mp3"
params = {
  "model": "tts-1", "voice": "nova",
  "input": completion.choices[0].message.content
}

try:
    response = client.audio.speech.create(**params)
    with open(speech_file_path, 'wb') as f:
        f.write(response.content)
except Exception as e:
    print(f"Error: {e}")

import pygame.mixer

# Initialize the mixer
pygame.mixer.init()

# Load an audio file

pygame.mixer.music.load(speech_file_path)

# Play the audio file
pygame.mixer.music.play()

# Wait for the audio to finish playing
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)

# Clean up when done
pygame.mixer.quit()
import os
import speech_recognition as sr
import discord
from discord.ext import commands
import pyaudio
import wave
import time

# Define intents
intents = discord.Intents.all()
intents.messages = True  # Enable message events

# Set up the speech recognition engine
r = sr.Recognizer()

# Set up the Discord client
client = discord.Client(intents=intents)

audio_file = None
transcript_file = None
voice_client = None

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name} (ID: {client.user.id})')

@client.event
async def on_voice_state_update(member, before, after):
    global voice_client
    global audio_file
    global transcript_file

    # Check if a user has joined a voice channel
    if after.channel is not None:
        # Check if the bot is not already connected to a voice channel
        if voice_client is None or not voice_client.is_connected():
            # Connect to the voice channel
            voice_client = await after.channel.connect()
            print(f'Connected to voice channel {after.channel.name}')

            # Set up the audio file
            audio_file = f'{member.id}_{int(time.time())}.wav'

            # Set up the transcript file
            transcript_file = f'{member.id}_{int(time.time())}.txt'

            # Start recording audio
            chunk = 1024
            sample_format = pyaudio.paInt16
            channels = 2
            fs = 44100
            seconds = 5
            filename = audio_file

            p = pyaudio.PyAudio()
            stream = p.open(format=sample_format,
                            channels=channels,
                            rate=fs,
                            frames_per_buffer=chunk,
                            input=True)

            print("recording")
            frames = []

            for i in range(0, int(fs / chunk * seconds)):
                data = stream.read(chunk)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()

            wf = wave.open(filename, 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(sample_format))
            wf.setframerate(fs)
            wf.writeframes(b''.join(frames))
            wf.close()

    # Check if a user has left a voice channel
    if before.channel is not None:
        # Stop recording audio
        print("recording stopped")

        # Recognize speech in the audio file
        if audio_file is not None:
            with sr.AudioFile(audio_file) as source:
                audio = r.record(source)

            try:
                # Recognize speech
                text = r.recognize_google(audio, language="en-US")

                # Save the transcript to a file
                with open(transcript_file, 'w', encoding='utf-8') as f:
                    f.write(f'User ID: {member.id}\n')
                    f.write(f'User Name: {member.name}\n')
                    f.write(f'Discord Tag: {member.discriminator}\n')
                    f.write(f'Transcript: {text}\n')

                print(f'Transcript saved to {transcript_file}')

            except sr.UnknownValueError:
                print("Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Error: {}".format(e))

            # Disconnect from the voice channel
            if voice_client is not None:
                await voice_client.disconnect()
                voice_client = None

client.run('your-discord-bot-token-here')
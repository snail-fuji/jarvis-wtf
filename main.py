import speech_recognition as sr
from decouple import config
from datetime import datetime
from openai import OpenAI
from time import sleep
# import wave
import pygame
import nltk

nltk.download('punkt')

from nltk.tokenize import sent_tokenize

OPEN_AI_API_KEY = config('OPEN_AI_API_KEY')
BOTNAME = config('BOTNAME')
SILENCE_SECONDS = int(config('SILENCE_SECONDS'))

pygame.mixer.init()
client_open_ai = OpenAI(api_key=OPEN_AI_API_KEY)
chat_messages = [
    {
        "role": "system", 
        "content": """
            You are a helpful voice assistant, 
            which responds in short concise sentences, 
            which will be read in less than 3-5 seconds 
            until not asked for a precise answer. 
            Refer to the question parts in case if the question is related to a new topic.
            The transcription is wrong sometimes (for instance, for proper nouns or cutoffs) - try to fix errors from the context or clarify
        """
    }
]

r = sr.Recognizer()
mic = sr.Microphone()

r.pause_threshold = SILENCE_SECONDS

# with mic as source:
#     print('Calibrating...')
#     r.adjust_for_ambient_noise(source, duration=10)
#     # r.dynamic_energy_threshold = False

def speak_sentence(text):
    global client_open_ai

    response = client_open_ai.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )

    while pygame.mixer.music.get_busy():
        sleep(0.01)

    response.stream_to_file('speech.mp3')
    pygame.mixer.music.load("speech.mp3")
    pygame.mixer.music.play()


def speak(text):
    text = text.replace('\n', '. ')
    sentences = sent_tokenize(text)
    print(sentences)

    for i, sentence in enumerate(sentences):
        try:
            speak_sentence(sentence.strip())
        except Exception as e:
            print(e)
            sleep(0.1)


def greet_user():
    speak(f"I am {BOTNAME}. How can I help you today?")


def recognize(audio):
    global client_open_ai
    with open("audio.wav", "wb") as file:
        file.write(audio.get_wav_data())

    audio_file = open('audio.wav', 'rb')
    transcript = client_open_ai.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    audio_file.close()

    return transcript.text


def take_user_input():
    global r, mic

    while pygame.mixer.music.get_busy():
        sleep(0.1)
    sleep(0.1)

    # r = sr.Recognizer()
    # mic = sr.Microphone()

    with mic as source:
        r.adjust_for_ambient_noise(source, duration=1)
        r.dynamic_energy_threshold = False
        r.energy_threshold *= 2
        print('\007')
        print('Listening....')
        audio = r.listen(source)

    try:
        print('Recognizing...')
        print('\007')
        query = recognize(audio)

        if 'exit' in query or 'stop' in query:
            speak('Have a good day sir!')
            exit()

        return query
    except Exception as e:
        print(e)
        query = ''
    return query


def get_next_message(query):
    global chat_messages
    chat_messages.append({
        "role": "user", 
        "content": query
    })
    response = client_open_ai.chat.completions.create(
        model='gpt-3.5-turbo', 
        messages=chat_messages
    )
    answer = response.choices[0].message
    chat_messages.append(
        answer
    )
    return answer.content


if __name__ == '__main__':
    greet_user()

    while True:
        query = take_user_input().lower()

        if not query:
            continue

        print('Question:', query)
        answer = get_next_message(query)

        print(f'Answer:', answer)
        speak(answer)

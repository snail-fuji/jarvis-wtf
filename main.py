import pyttsx3
import speech_recognition as sr
from decouple import config
from datetime import datetime
from openai import OpenAI


engine = pyttsx3.init('nsss') ## Mac OS
# engine = pyttsx3.init('sapi5') ## Windows


engine.setProperty('volume', 1.0)
engine.setProperty('voice', engine.getProperty('voices')[int(config('VOICE'))])

clientOpenAI = OpenAI(api_key=config('OPEN_AI_API_KEY'))
chatMessages = [
    {"role": "system", "content": "You are a helpful assistant."}
]


def speak(text):
    """Used to speak whatever text is passed to it"""
    engine.say(text)
    engine.runAndWait()


def greet_user():
    hour = datetime.now().hour
    if (hour >= 6) and (hour < 12):
        speak(f"Good Morning {config('USERNAME')}")
    elif (hour >= 12) and (hour < 16):
        speak(f"Good afternoon {config('USERNAME')}")
    elif (hour >= 16) and (hour < 19):
        speak(f"Good Evening {config('USERNAME')}")
    speak(f"I am {config('BOTNAME')}. How can i hale you today?")


def take_user_input():
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print('Listening....')
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print('Recognizing...')
        query = r.recognize_google(audio, language=config('LANGUAGE'))

        if 'exit' in query or 'stop' in query:
            speak('Have a good day sir!')
            exit()

        return query
    except Exception:
        query = ''
    return query


if __name__ == '__main__':
    greet_user()
    while True:
        query = take_user_input().lower()

        if not query:
            continue

        print(query)

        chatMessages.append({"role": "user", "content": query})

        response = clientOpenAI.chat.completions.create(model='gpt-4', messages=chatMessages)

        chatMessages.append(response.choices[0].message)

        print(f'Answer: {response.choices[0].message.content}')

        speak(response.choices[0].message.content)
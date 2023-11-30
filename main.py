import pyttsx3
import speech_recognition as sr
from decouple import config
from datetime import datetime
from openai import OpenAI
import playsound
import wave


# engine = pyttsx3.init('nsss') ## Mac OS
# engine = pyttsx3.init('sapi5') ## Windows
# engine = pyttsx3.init('espeak')

# engine.setProperty('volume', 1.0)
# engine.setProperty('voice', engine.getProperty('voices')[int(config('VOICE'))])

clientOpenAI = OpenAI(api_key=config('OPEN_AI_API_KEY'))
chatMessages = [
    {"role": "system", "content": "You are a helpful voice assistant, which responds in short concise sentences, which will be read in less than 10 seconds until not asked for a precise answer."}
]


def speak(text):
    """Used to speak whatever text is passed to it"""
    engine.say(text)
    engine.runAndWait()


def speak2(text):
    global clientOpenAI

    response = clientOpenAI.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )

    response.stream_to_file('/tmp/speech.mp3')
    playsound.playsound('/tmp/speech.mp3', True)


def greet_user():
    return

    hour = datetime.now().hour
    speak2(f"I am {config('BOTNAME')}. How can i hale you today?")


def recognize(audio):
    global clientOpenAI
    with open("/tmp/audio.mp3", "wb") as file:
        file.write(audio_data.get_wav_data())
    audio_file = open('/tmp/audio.mp3', 'rb')
    transcript = clientOpenAI.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    audio_file.close()
    return transcript


def take_user_input():
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print('Listening....')
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print('Recognizing...')
        # query = r.recognize_google(audio, language=config('LANGUAGE'))
        query = recognize(audio)

        if 'exit' in query or 'stop' in query:
            speak2('Have a good day sir!')
            exit()

        return query
    except Exception as e:
        print(e)
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

        speak2(response.choices[0].message.content)

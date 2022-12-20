import random
import sys
import webbrowser

import pyttsx3
import requests
import speech_recognition
from bs4 import BeautifulSoup


class VoiceHelper:
    def __init__(self):
        self.recognizer = speech_recognition.Recognizer()
        self.microphone = speech_recognition.Microphone()

        self.voice = pyttsx3.init()
        self.voice.say('Здравствуйте, я голосовой помощник')
        self.voice.runAndWait()

        self.films_list = self._films_parser()

        print(self._listening())

    def _films_parser(self):
        self.films_description = []

        url = f'https://kinogo.film/films-2021/'

        response = requests.get(url=url)

        pages_info = BeautifulSoup(response.text, 'html.parser')

        films = pages_info.find_all('div', class_='shortstory')

        for film in films:
            description = film.find('h2', class_='zagolovki').find('a').text[:-7]

            self.films_description.append(description)
        return self.films_description

    def _send_voice_message(self, message: str):
        """Sends a voiced text message

        :param message: message to be spoken
        :return:
        """
        self.voice.say(message)
        self.voice.runAndWait()

    def _open_youtube(self):
        """Open a YouTube in default web browser

        :return: Success message/None
        """
        try:
            url = 'https://www.youtube.com'
            webbrowser.open(url)
            return 'Success'
        except:
            return

    def _recognition_of_key_commands(self, speech: str):
        """Response to key commands

        :param speech: spoken speech
        :return:
        """

        if 'привет' in speech:
            self._send_voice_message('И тебе привет')
            return 'И тебе привет'

        elif 'как дела' in speech:
            self._send_voice_message('Отлично, а у тебя?')

        elif 'пока' in speech:
            self._send_voice_message('До свидания!')
            sys.exit()

        elif 'youtube' in speech:
            self._send_voice_message('Открываю youtube')
            if self._open_youtube():
                self._send_voice_message('Youtube открыт')
                return 'Youtube открыт'
            else:
                self._send_voice_message('Что-то пошло не так')
                return 'Youtube не открыт'

        elif 'фильм' in speech:
            if len(self.films_list) == 0:
                self.films_list = self._films_parser()

            random_film = random.choice(self.films_list)
            self.films_list.remove(random_film)
            self._send_voice_message(random_film)
            return random_film

        else:
            self._send_voice_message(f'Я вас не понимаю, повторите пожалуйста')
            return f'Вы сказали: {self.speech}\nЯ вас не понимаю, повторите пожалуйста'

    def _record_and_recognize_audio(self):
        """

        :return: response
        """
        with self.microphone as source:
            self.speech = ''
            print('Я вас слушаю...')

            self.recognizer.adjust_for_ambient_noise(self.microphone, duration=2)

            try:
                audio = self.recognizer.listen(source)

            except speech_recognition.WaitTimeoutError:
                self._send_voice_message('Я вас не слышу... Проверьте микрофон')
                return

            try:
                self.speech = self.recognizer.recognize_google(audio, language='ru').lower()

                return self._recognition_of_key_commands(self.speech)

            except speech_recognition.UnknownValueError:
                pass

            except speech_recognition.RequestError:
                self._send_voice_message('Проверьте подключение к интернет')
                print("Проверьте подключение к интернету")

            return self.speech

    def _listening(self):
        while True:
            voice_input = self._record_and_recognize_audio()
            print(voice_input)


if __name__ == '__main__':
    helper = VoiceHelper()

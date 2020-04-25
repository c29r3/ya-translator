import subprocess
from os import system
from urllib import parse

import requests
from pynput import keyboard
from requests import RequestException, HTTPError

import config_example

hot_key = config_example.hot_key
notify_expire = config_example.notify_expire_seconds * 1000
print(hot_key)
api_key = config_example.api_key
detect_lang_url = 'https://translate.yandex.net/api/v1.5/tr.json/detect'
translate_url = 'https://translate.yandex.net/api/v1.5/tr.json/translate'


def for_canonical(f):
    return lambda k: f(l.canonical(k))


def error(message, status_code):
    system(f'notify-send -a Translater -u normal "{status_code}: {message}"')


def req_post(url: str):
    try:
        req = requests.post(url)
        if req.status_code == 200:
            return req.json()

    except (RequestException, HTTPError, Exception) as reqErr:
        print(reqErr)
        error(f'{url.replace(api_key, "KEY")}: {reqErr}')


def main():
    data = subprocess.Popen(['xsel', '-o'], stdout=subprocess.PIPE)
    output, err = data.communicate()
    output = output.decode("utf-8")

    detected_lang = req_post(f'{detect_lang_url}?key={api_key}&text={parse.quote(output)}&hint=ru;en')["lang"]
    if detected_lang == "ru":
        lang_pair = "ru-en"
    elif detected_lang == "en":
        lang_pair = "en-ru"
    else:
        # raise Exception("This is not a ru or eng lang")
        lang_pair = "en-ru"

    translate = req_post(f'{translate_url}?key={api_key}&lang={lang_pair}&text={parse.quote(output)}')
    print(translate)
    system(f'notify-send -a Translater -u normal -t {notify_expire} "{str(translate["text"][0])}"')


hotkey = keyboard.HotKey(
    keyboard.HotKey.parse(hot_key),
    main)
with keyboard.Listener(
        on_press=for_canonical(hotkey.press),
        on_release=for_canonical(hotkey.release)) as l:
    l.join()




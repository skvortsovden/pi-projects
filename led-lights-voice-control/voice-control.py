import speech_recognition as sr
from gpiozero import LED
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
from re import compile

led_lights = [
    {'color': 'blue', 'led': LED(14), 'keyword': 'синю'},
    {'color': 'yellow', 'led': LED(15), 'keyword': 'жовту'},
    {'color': 'green', 'led': LED(18), 'keyword': 'зелену'},
    {'color': 'red', 'led': LED(23), 'keyword': 'червону'}
]

def recognize_speech_from_mic(recognizer, microphone):
    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio, language="uk-UA")
        print(f"I have heard: {response['transcription']}")
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"
        print(f"I did not get that...Please, repeat!")

    return response

# Synthesize text to speech
def text_to_speech(text, language):
    speech = gTTS(text=text, lang=language)
    mp3_fp = BytesIO()
    speech.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp

# Turn on LED Light by color
def turn_on_led_light(keywords):
    print("Turning ON led light...")
    for led in led_lights:
        if led['keyword'] in keywords:
            led['led'].on()

# Turn off LED Light by color
def turn_off_led_light(keywords):
    print("Turning OFF led light...")
    for led in led_lights:
        if led['keyword'] in keywords:
            led['led'].off()

def turn_on_all_lights(keywords):
    for led in led_lights:
        led['led'].on()

def turn_off_all_lights(keywords):
    for led in led_lights:
        led['led'].off()


commands = [
    {"pattern": "увімкнути.*лампочку", "action": turn_on_led_light},
    {"pattern": "вимкнути.*лампочку", "action": turn_off_led_light},
    {"pattern": "увімкнути всі лампочки", "action": turn_on_all_lights},
    {"pattern": "вимкнути всі лампочки", "action": turn_off_all_lights},
]


def recognize_keywords(keywords):
    for command in commands:
        command_pattern = compile(command['pattern'])
        if command_pattern.match(keywords):
            command['action'](keywords)


if __name__ == "__main__":
    # create recognizer and mic instances
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    while True:
        keywords = recognize_speech_from_mic(recognizer, microphone)
        if keywords['transcription']:

            speech = text_to_speech(keywords['transcription'], 'uk')
            song = AudioSegment.from_file(speech, format="mp3")
            play(song)
            recognize_keywords(keywords['transcription'])



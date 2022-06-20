from gpiozero import LED, MotionSensor
from picamera2 import Picamera2, Preview
from operations import cleanup_directory
from image2gif import generate_gif
from time import sleep

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import KeyboardButton, ReplyKeyboardMarkup

camera = Picamera2()
config = camera.preview_configuration(main={"size": (1640, 1232)},)
camera.configure(config)
# camera.start_preview(Preview.QT)
camera.start()

# GPIO
led = LED(16)
sensor = MotionSensor(21)

directory = 'frames'
capturing = True
emoji = {
    'wave': '\uE41E',
    'camera': '\U0001F4F8',
    'stop': '\u26D4',
    'move': '\U0001F7E2',
    'done': '\u2705',
    'clock': '\u23F3'
}

cleanup_directory(directory)

def start(update, context):
    """Send a message when the command /start is issued."""
    print("start")
    user = update.message.from_user
    keyboard = [[KeyboardButton("START RECORDING")]]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_text(f"{emoji['wave']} Hello {user['username']}! Let's make some stop motion video! {emoji['camera']}",reply_markup=reply_markup)


def start_recording(update, context):

    keyboard = [[KeyboardButton("STOP RECORDING")]]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    print("Start capturing")
    update.message.reply_text('Start capturing')
    global capturing
    capturing = True
    frame = 1
    while capturing:
        print(f"Move!")
        update.message.reply_text(f"{emoji['move']} Move!", reply_markup=reply_markup)
        sensor.wait_for_motion()
        if capturing:
            print("Motion detected")
            update.message.reply_text(f"{emoji['stop']} DO NOT Move!", reply_markup=reply_markup)
            led.on()
            print(f"DO NOT Move!")
            sleep(3)
            sensor.wait_for_no_motion()
            print("Motion stopped")
            led.off()
            camera.capture_file('frames/frame%03d.jpg' % frame)
            print("Frame captured")
            update.message.reply_text(f"{emoji['camera']} Frame captured!", reply_markup=reply_markup)
            frame += 1

def stop_recording(update, context):

    keyboard = [[KeyboardButton("START RECORDING")]]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    global capturing
    capturing = False
    print("Stop capturing")
    update.message.reply_text(f"Recording stopped.\nLet me generate GIF for you! Wait a moment... {emoji['clock']}")
    generate_gif(directory)
    gif = open('animation.gif', 'rb')
    update.message.reply_animation(gif)
    update.message.reply_text(f"{emoji['done']} Checkout this GIF!", reply_markup=reply_markup)

def message_handler(update, context):
    # query = update.callback_query 
    # query.answer()
    print("Message")
    if update.message.text == 'START RECORDING':
        start_recording(update, context)
    elif update.message.text == 'STOP RECORDING':
        stop_recording(update, context)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("TOKEN", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start, run_async=True))
    dp.add_handler(MessageHandler(Filters.text,callback=message_handler, run_async=True))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
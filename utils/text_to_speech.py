import pyttsx3

def main(input_voice):
    engine = pyttsx3.init()
    text = input_voice

    engine.say(text)
    engine.runAndWait()

    engine.save_to_file(text, "output_audio.mp3")

    return "Text has been spoken and save as 'output_audio.mp3'"

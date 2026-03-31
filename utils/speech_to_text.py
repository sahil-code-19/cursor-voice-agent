import speech_recognition as sr
r = sr.Recognizer()

def main():
    try:
        with sr.Microphone() as source:
            print("AI IS LISTENING........🙉")
            r.adjust_for_ambient_noise(source,duration=0.2)
            audio = r.listen(source)
            text = r.recognize_google(audio)
            text = text.lower()
            print("You said : ",text)
            return text
    
        if text in ["exit", "quit", "bye"]:
            print("Exiting program.........")
    
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

    except sr.UnknownValueError:
        print("Couldn't understand audio")

    except KeyboardInterrupt:
        print("Program terminated by user")
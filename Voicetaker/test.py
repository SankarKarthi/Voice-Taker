import streamlit as st
import speech_recognition as sr
from googletrans import Translator

# Initialize the translator
translator = Translator()

def recognize_speech():
    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Use the microphone as the source
    with sr.Microphone() as source:
        st.write("Please speak...")
        audio = recognizer.listen(source)  # Listen for the first phrase

        try:
            # Recognize speech using Google Speech Recognition
            text = recognizer.recognize_google(audio, language='ta-IN')  # Tamil language
            return text
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError:
            st.error("Could not request results from Google Speech Recognition service.")
            return None

def translate_text(text):
    if text:
        translation = translator.translate(text, src='ta', dest='en')
        return translation.text
    return None

# Streamlit UI
st.title("Tamil to English Voice Translator")

if st.button("Speak and Translate"):
    # Get the Tamil text from speech
    tamil_text = recognize_speech()
    
    if tamil_text:
        # Display the recognized Tamil text
        st.write("Tamil Text:", tamil_text)

        # Translate the Tamil text to English
        english_translation = translate_text(tamil_text)
        
        if english_translation:
            # Display the translated English text
            st.write("Translated Text:", english_translation)


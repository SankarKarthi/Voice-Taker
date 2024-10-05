import os
import time
import webbrowser
from gtts import gTTS
import streamlit as st
import mysql.connector
import re
import speech_recognition as sr
from googletrans import Translator
from deep_translator import GoogleTranslator

translator = Translator()

# Function to take note using speech recognition and translate to English
def take_note(language):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Say something...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        
        try:
            note = r.recognize_google(audio, language=language)
            st.write("You said:", note)
            
            # Translate note to English
            translation = translator.translate(note, src=language, dest='en')
            translated_note = translation.text
            
            return note, translated_note  # Return both the original and translated notes
        except sr.UnknownValueError:
            st.write("Sorry, I could not understand what you said.")
            return "", ""
        except sr.RequestError:
            st.write("Sorry, I'm having trouble accessing the Google API. Please try again later.")
            return "", ""

# Function to save note to database
def save_note_to_database(username, original_note, translated_note):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (username, original_note, translated_note) VALUES (%s, %s, %s)", (username, original_note, translated_note))
    conn.commit()
    note_id = cursor.lastrowid  # Get the unique identifier (ID) of the inserted note
    conn.close()
    return note_id

# Function to read saved notes from the database for a specific user
def read_notes_from_database(username):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT id, original_note, translated_note FROM notes WHERE username=%s", (username,))
    notes = cursor.fetchall()
    conn.close()
    return notes

# Function to generate audio files for both original and translated notes
def generate_audio_files(username, index, original_note, translated_note):
    # Generate unique filenames for both original and translated audio files
    original_audio_filename = f"original_note_{username}_{index}.mp3"
    translated_audio_filename = f"translated_note_{username}_{index}.mp3"
    
    # Check if original audio file exists, if not, save it
    if not os.path.exists(original_audio_filename):
        save_audio_file(original_note, original_audio_filename)
    
    # Check if translated audio file exists, if not, save it
    if not os.path.exists(translated_audio_filename):
        save_audio_file(translated_note, translated_audio_filename)
    
    return original_audio_filename, translated_audio_filename

def save_audio_file(text, filename):
    # Initialize GoogleTranslator for Tamil to English
    translator = GoogleTranslator(source='ta', target='en')

    # Translate the entire text at once
    translated_text = translator.translate(text)

    # Generate audio for the translated text
    translated_audio = gTTS(text=translated_text, lang='en', slow=False)
    translated_audio.save(filename)
    
    return translated_text

# Function to connect to MySQL database
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sankar06",
        database="voicemakers"
    )

# Function to create notes table in the database
def create_notes_table():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS notes
                     (id INT AUTO_INCREMENT PRIMARY KEY, 
                      username VARCHAR(255), 
                      original_note TEXT, 
                      translated_note TEXT)''')
    conn.commit()
    conn.close()


# Function to create user table in the database
def create_user_table():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                     (username VARCHAR(255) PRIMARY KEY, password VARCHAR(255))''')
    conn.commit()
    conn.close()

# Function to delete a note and its associated audio file from the database and filesystem
def delete_note_and_audio(username, note_id):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM notes WHERE username=%s", (username,))
    existing_ids = [row[0] for row in cursor.fetchall()]  # Get all note IDs for the user
    
    if note_id in existing_ids:
        cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
        conn.commit()
        conn.close()
        
        # Remove associated audio file
        audio_filename = f"translated_note_{username}_{note_id}.mp3"
        if os.path.exists(audio_filename):
            os.remove(audio_filename)
            return True
        else:
            return False
    else:
        conn.close()
        return False
    

# Function to save feedback to the database
def save_feedback(username, feedback_text):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO feedback (username, feedback_text) VALUES (%s, %s)", (username, feedback_text))
    conn.commit()
    conn.close()

# Function to create feedback table in the database
def create_feedback_table():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback
                     (id INT AUTO_INCREMENT PRIMARY KEY, 
                      username VARCHAR(255), 
                      feedback_text TEXT)''')
    conn.commit()
    conn.close()

# Feedback page
def feedback_page():
    st.title("FEEDBACK")
    
    if not st.session_state.logged_in:
        st.warning("Please log in to submit feedback.")
        return
    
    st.write("Share your feedback with us!")
    feedback_text = st.text_area("Enter your feedback here:", height=200)
    submit_feedback = st.button("Submit Feedback")

    if submit_feedback:
        if not st.session_state.logged_in:
            st.warning("Please log in to submit feedback.")
            return

        username = st.session_state.current_username
        save_feedback(username, feedback_text)
        st.success("Feedback submitted successfully!")
        st.session_state.feedback_submitted = True


# Function to send individual note via WhatsApp
def send_note_via_whatsapp(original_note, translated_note):
    import urllib.parse
    
    # Create a message including the text notes
    message = f"Original: {original_note}\nTranslated: {translated_note}"
    
    # Encode the message for URL
    encoded_message = urllib.parse.quote(message)
    
    # Open WhatsApp web with the encoded message
    webbrowser.open(f"https://web.whatsapp.com/send?text={encoded_message}")
    # Pause to ensure the message is sent
    time.sleep(30)  # Adjust the delay time as needed



# Function to add a new user to the database
def add_user(username, password):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    conn.commit()
    conn.close()

# Function to check if a username already exists in the database
def username_exists(username):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Function to validate password strength
def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'\d', password) or not re.search(r'[a-zA-Z]', password):
        return False
    return True

# Function to authenticate user
def authenticate_user(username, password):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Home page
def home_page():
    st.title("VOICE TAKER")
    
    st.subheader("User Authentication")
    
    create_user_table()  # Create user table if not exists
    create_notes_table()  # Create notes table if not exists

    st.write("Home page options:")
    tabs = st.tabs(["Login", "Sign Up"])

    with tabs[1]:
        st.subheader("Sign Up")
        new_username = st.text_input("New Username", key='new_username')
        new_password = st.text_input("New Password", type="password", key='new_password')
        confirm_password = st.text_input("Confirm Password", type="password", key='confirm_password')
        sign_up = st.button("Sign Up")

        if sign_up:
            if new_password != confirm_password:
                st.error("Passwords do not match!")
            elif username_exists(new_username):
                st.error("Username already exists! Please choose a different username.")
            elif not is_strong_password(new_password):
                st.error("Password is weak! It should be at least 8 characters long and contain both numeric and alphabetic characters.")
            else:
                add_user(new_username, new_password)
                st.success("Sign up successful! Please log in.")

    with tabs[0]:
        st.subheader("Log In")
        username = st.text_input("Username", key='login_username')
        password = st.text_input("Password", type="password", key='login_password')
        login = st.button("Login")

        if login:
            if authenticate_user(username, password):
                st.success("Login successful!")
                st.session_state.logged_in = True
                st.session_state.current_username = username
            else:
                st.error("Invalid username or password.")

# Notes page
def notes_page(language):
    st.title("NOTES")
    
    st.write("Notes page options:")
    tabs = st.tabs(["Take Note", "Read Notes"])

    with tabs[0]:
        st.subheader("Take Note")
        original_note, translated_note = take_note(language=language)
        if original_note:
            note_id = save_note_to_database(st.session_state.current_username, original_note, translated_note)
            st.success("Note saved successfully!")

    with tabs[1]:
        st.subheader("Read Notes")
        if not st.session_state.logged_in:
            st.warning("Please log in to read notes.")
            return

        username = st.session_state.current_username
        notes = read_notes_from_database(username)
        if notes:
            for note_id, original_note, translated_note in notes:
                st.write("Original Note:", original_note)
                st.write("Translated Note:", translated_note)
                
                # Generate audio files for both original and translated notes
                original_audio_filename = f"original_note_{username}_{note_id}.mp3"
                translated_audio_filename = f"translated_note_{username}_{note_id}.mp3"
                save_audio_file(original_note, original_audio_filename)
                save_audio_file(translated_note, translated_audio_filename)
                
                # Display buttons to play both original and translated audio
                if st.button(f"Play Original Audio {note_id}"):
                    st.audio(original_audio_filename, format='audio/mp3')
                
                if st.button(f"Play Translated Audio {note_id}"):
                    st.audio(translated_audio_filename, format='audio/mp3')
                
                # Display a delete button for each note
                if st.button(f"Delete Note {note_id}"):
                    if delete_note_and_audio(username, note_id):
                        st.success("Note deleted successfully!")
                        # Refresh the notes list after deletion
                        notes = read_notes_from_database(username)
                    else:
                        st.error("Failed to delete note or audio.")
                    
                    # After deletion, refresh the page to reflect changes
                    st.experimental_rerun()
                
                # Add a button to send this particular note via WhatsApp
                if st.button(f"Send Note {note_id} via WhatsApp"):
                    send_note_via_whatsapp(original_note, translated_note)
                    st.success("Note shared via WhatsApp successfully!")
                
                st.write("---")
            
            # Add a button to send all notes at once via WhatsApp
            if st.button("Send All Notes via WhatsApp"):
                all_notes_message = ""
                for note_id, original_note, translated_note in notes:
                    all_notes_message += f"Original Note: {original_note}\nTranslated Note: {translated_note}\n\n"
                send_note_via_whatsapp(all_notes_message, "")
                st.success("All notes shared via WhatsApp successfully!")
                
        else:
            st.write("No notes saved yet.")


# Main function
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["Home", "Notes", "Feedback"])

    if page == "Home":
        home_page()
    elif page == "Notes":
        if st.session_state.logged_in:
            language = st.selectbox("Select Language", ["en", "es", "fr", "ta", "hi", "ml", "te"])
            create_notes_table()  # Call create_notes_table function here
            notes_page(language)
        else:
            st.warning("Please log in to access the notes page.")
    elif page == "Feedback":
        create_feedback_table()  # Create feedback table if not exists
        feedback_page()

if __name__ == "__main__":
    main()

# Voice Taker Application

Voice Taker is a Streamlit-based web application that allows users to take notes using voice recognition and provides translation features. It also allows users to save their notes in a database, read saved notes, and send notes via WhatsApp.

## Features

- **Voice Note Taking**: Users can take notes by speaking, and the application will recognize and save the note.
- **Translation**: The application translates notes into English.
- **Database Storage**: Notes are saved in a MySQL database for easy retrieval.
- **Audio Generation**: Users can listen to both the original and translated notes in audio format.
- **WhatsApp Integration**: Users can share their notes via WhatsApp.
- **User Authentication**: Secure login and signup functionality.
- **Feedback Submission**: Users can provide feedback on the application.

## Technologies Used

- **Python**: Core programming language.
- **Streamlit**: Framework for building the web application.
- **MySQL**: Database for storing user notes and feedback.
- **gTTS**: Google Text-to-Speech for audio generation.
- **SpeechRecognition**: Library for recognizing speech input.
- **Google Translate API**: For translating notes into English.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd voice-taker

2. Install required packages:
    ```bash
    pip install -r requirements.txt
3. Set up the MySQL database:
    Create a database.
    Ensure the user has appropriate privileges.
4. Update database credentials in the code if necessary.

## Usage
1. Start the Streamlit server:
    ```bash
    streamlit run app.py
2. Open your web browser and navigate to http://localhost:8501.

3. Sign Up: Create a new account by providing a username and password.

4. Log In: Enter your credentials to access the application.

5. Take Note: Use the "Take Note" tab to record voice notes. The notes will be translated and saved.

6. Read Notes: In the "Read Notes" tab, view all your saved notes. You can play the audio, delete notes, and send them via WhatsApp.

7. Feedback: Use the "Feedback" tab to submit your thoughts and suggestions about the application.
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import requests
import geocoder
import sympy

# Global variables
# Add all the requried api keys and paths 
output_text = None
weather_api_key = "YOUR_API_KEY"
music_dir = 'YOUR_SONGS_DIRECTORY_PATH'
joke_api_url = "https://official-joke-api.appspot.com/random_joke"
notes_folder = "YOUR_NOTES_FOLDER_PATH"
news_api_url = "https://newsapi.org/v2/top-headlines"
news_api_key = "YOUR_API_KEY" 

# GUI 
def create_window():
    global output_text

    window = tk.Tk()
    window.title("Voice Assistant")
    window.geometry("800x800")
    window.configure(bg="#07F2BB")

    menubar = tk.Menu(window)
    window.config(menu=menubar)

    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="Help", command=lambda: show_help())

    label = ttk.Label(window, text="Voice Assistant", font=("Helvetica", 24, "bold"), background="#07F2BB", foreground="black")
    label.pack(pady=20)

    listen_icon = tk.PhotoImage(file="assests/mic.png")
    speak_icon = tk.PhotoImage(file="assests/volume-2.png")
    temp_gif = tk.PhotoImage(file="assests/audio-lines.png")

    output_text = scrolledtext.ScrolledText(window, width=60, height=10, wrap=tk.WORD, state=tk.DISABLED, bd=0,
                                           font=("Helvetica", 12), background='#6FBBAA')
    listen_button = ttk.Button(window, text="Listen", command=lambda: takeCommand(output_text), image=listen_icon, compound="left",
                               style="TButton", width=120, padding=10)
    listen_button.pack(pady=20)
    output_text.pack(pady=10)

    temp_button = ttk.Button(window, image=temp_gif, compound="center", style="TButton")
    speak_button = ttk.Button(window, text="Speak", command=lambda: show_bar(input_bar, confirm_button, cancel_button, speak_button, temp_button),
                              image=speak_icon, compound="left", style="TButton", width=120, padding=10)
    speak_button.pack(pady=20)

    input_bar = ttk.Entry(window, font=("Helvetica", 12))
    confirm_button = ttk.Button(window, text="Confirm", command=lambda: take_command(input_bar.get()), style="TButton", width=20)
    cancel_button = ttk.Button(window, text="Cancel", command=lambda: hide_input_bar(input_bar, confirm_button, cancel_button, speak_button, temp_button),
                               style="TButton", width=20)

    exit_button = ttk.Button(window, text='Exit', command=window.destroy, style="TButton", width=10, padding=5)
    exit_button.configure(style="Exit.TButton")
    exit_button.pack(side=tk.BOTTOM, pady=(20, 50))

    # Define a new style for the Exit button
    window.style = ttk.Style()
    window.style.configure("Exit.TButton", background="#C41717", foreground="black", font=("Helvetica", 12))

    window.mainloop()

# utility functions -> start

def show_help():
    help_text = """
    Available Functionalities:

    1.  Listen              : Start listening to voice commands.
    2.  Speak               : Speak a command or provide input using the interface.
    3.  Make a Note         : Record and save notes.
    4.  Calculate           : Evaluate mathematical expressions.
    5.  Tell me a Joke      : Hear a random joke.
    6.  Latest News         : Get headlines from the latest news.
    7.  Make notes          : Add events to your calendar.
    8.  Weather             : Know your cities weather.
    9.  search              : search for any thing!!.
    10. Wikipedia           : get any information on wikipedia!!.
    """
    tk.messagebox.showinfo("Help", help_text)

def show_bar(entry, confirm, cancel, button, temp_button):
    button.pack_forget()
    temp_button.pack(pady=20)
    entry.pack(pady=10)
    confirm.pack(pady=10)
    cancel.pack(pady=10)

def display_output(message, output_text):
    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END,' >> ' + message + "\n")
    output_text.see(tk.END)
    output_text.config(state=tk.DISABLED)
    output_text.update_idletasks()  # Update the GUI immediately

def hide_input_bar(entry, confirm, cancel, button, temp_button):
    entry.pack_forget()
    confirm.pack_forget()
    cancel.pack_forget()
    temp_button.pack_forget()
    button.pack()

def take_command(audio):
    speak(audio)

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def takeCommand(output_text):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        display_output('Listening...', output_text)
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        display_output('Recognizing...', output_text)
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        display_output('User Said: ' + query, output_text)
        print(f"User said: {query}\n")

    except Exception as e:
        display_output('Say that again please...', output_text)
        print("Say that again please...")
        return "None"
    process_querry(query, output_text)

def get_weather(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': weather_api_key,
        'units': 'metric'
    }

    response = requests.get(base_url, params=params)
    weather_data = response.json()

    if response.status_code == 200:
        return weather_data
    else:
        return None

def get_current_city():
    location = geocoder.ip('me')
    if location.city:
        return location.city
    else:
        return None

def take_note(output_text):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for note...")
        display_output('Listening for note...', output_text)
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        display_output('Processing note...', output_text)
        print("Processing note...")
        note_text = r.recognize_google(audio, language='en-in')
        display_output(f"Note: {note_text}", output_text)
        print(f"Note: {note_text}")
        return note_text
    except Exception as e:
        display_output('Could not understand the note. Please try again.', output_text)
        print("Could not understand the note. Please try again.")
        return None

def save_note_to_file(note_text):
    if not os.path.exists(notes_folder):
        os.makedirs(notes_folder)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    note_filename = os.path.join(notes_folder, f"note_{timestamp}.txt")

    with open(note_filename, 'w') as file:
        file.write(note_text)

def extract_expression(query):
    # Extract the expression from the query
    # Example: "calculate 2 plus 3" will be extracted as "2 + 3"
    expression_keywords = ['calculate', 'evaluate', 'compute']
    for keyword in expression_keywords:
        if keyword in query:
            expression = query.replace(keyword, '').strip()

            # Handle special cases for multiplication and division
            expression = expression.replace('multiplied by', ' * ')
            expression = expression.replace('X', ' * ')
            expression = expression.replace('x', ' * ')
            expression = expression.replace('times', ' * ')
            expression = expression.replace('divided by', ' / ')
            expression = expression.replace('over', ' / ')
            
            return expression
    return None

def evaluate_expression(expression):
    try:
        # Use sympy to evaluate the expression
        result = sympy.sympify(expression)
        return result.evalf()
    except Exception as e:
        return None
# utility functions -> end
def process_querry(query, output_text):

    if 'Wikipedia' in query:
        speak('Searching Wikipedia...')
        query = query.replace("Wikipedia", "")
        results = wikipedia.summary(query, sentences=2)
        speak("According to Wikipedia")
        print(results)
        display_output(results, output_text)
        speak(results)

    elif 'play a song' in query:
        try:
            for filename in os.listdir(music_dir):
                if filename.endswith(".mp3"):
                    music_file = os.path.join(music_dir, filename)
                    os.system(f"start {music_file}")
        except Exception as e:
            return None

    elif 'the time' in query:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        print({strTime})
        display_output(f"Sir, the time is {strTime}", output_text)
        speak(f"Sir, the time is {strTime}")

    elif 'search' in query:
        query = query.replace("search", "")
        display_output(f'Searching for {query}....', output_text)
        speak(f'Searching for {query}....')
        webbrowser.open(f"https://www.google.com/search?q={query}") # be sure to upadate the search url

    elif 'weather' in query:
        current_city = get_current_city()
        if current_city:
            weather_data = get_weather(current_city)

            if weather_data:
                temperature = weather_data['main']['temp']
                description = weather_data['weather'][0]['description']
                message = f"The current weather in {current_city} is {temperature}°C with {description}."
                display_output(message, output_text)
                speak(message)
            else:
                speak(f"Sorry, I couldn't retrieve the weather information for {current_city}.")
        else:
            speak("Sorry, I couldn't determine your current city.")
    
    elif 'tell me a joke' in query:
        joke_data = requests.get(joke_api_url).json()

        if 'setup' in joke_data and 'punchline' in joke_data:
            setup = joke_data['setup']
            punchline = joke_data['punchline']
            joke_message = f"{setup} ... {punchline}"
            display_output(joke_message, output_text)
            speak(joke_message)
        else:
            display_output("Sorry, I couldn't fetch a joke right now.", output_text)
            speak("Sorry, I couldn't fetch a joke right now.")

    elif 'make a note' in query:
        speak("Sure, what would you like to make a note of?")
        note_text = take_note(output_text)
        if note_text:
            save_note_to_file(note_text)
            display_output("Note saved successfully.", output_text)
            speak("Note saved successfully.")
        else:
            display_output("Sorry, I couldn't understand the note. Please try again.", output_text)
            speak("Sorry, I couldn't understand the note. Please try again.")

    elif 'calculate' in query:
            expression = extract_expression(query)
            if expression:
                result = evaluate_expression(expression)
                if result is not None:
                    display_output(f"Result: {result}", output_text)
                    speak(f"The result is {result}")
                else:
                    display_output("Sorry, I couldn't evaluate the expression.", output_text)
                    speak("Sorry, I couldn't evaluate the expression.")
            else:
                display_output("Please provide a valid mathematical expression to calculate.", output_text)
                speak("Please provide a valid mathematical expression to calculate.")

    elif 'latest news' in query or 'news headlines' in query:
        news_params = {
            'apiKey': news_api_key,
            'country': 'in',
        }

        news_data = requests.get(news_api_url, params=news_params).json()

        if 'articles' in news_data and len(news_data['articles']) > 0:
            articles = news_data['articles']
            for index, article in enumerate(articles):
                title = article['title']
                source = article['source']['name']
                news_message = f"{index + 1}. {title} (Source: {source})"
                display_output(news_message, output_text)
                speak(news_message)
                if index == 2:
                    break
        else:
            display_output("Sorry, I couldn't fetch the latest news right now.", output_text)
            speak("Sorry, I couldn't fetch the latest news right now.")

if __name__ == "__main__":
    create_window()
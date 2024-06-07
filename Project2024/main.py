from flask import Flask, render_template, request, jsonify, redirect, send_file
from flask_cors import CORS
from translate import Translator
import assemblyai as aai
import pyaudio
import wave
import sqlite3
import re
from scipy.io import wavfile
import librosa
import soundfile as sf
from moviepy.editor import VideoFileClip
import time
import os
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip


from pydub import AudioSegment

aai.settings.api_key = "97cf630144c34133a857bbbc8019237a"





app = Flask(__name__)
CORS(app)
data = {'message': 'Hello from Flask!'}

# Route to serve data
@app.route('/get_data', methods=['POST'])
def get_data():
    if request.method == 'POST':
        email=request.json.get('email')
        password=request.json.get('password')

    print("Krijsma send data: ", email)
    print("password :", password)
    return jsonify(data)







#Crete database
def create_database():
     
    con = sqlite3.connect("User.db")
    cur = con.cursor()
    try:
        #cur.execute("CREATE TABLE IF NOT EXISTS transcription (transcripted_text TEXT)")
        
        cur.execute("CREATE TABLE IF NOT EXISTS loginInformation (user_email TEXT PRIMARY KEY, user_password TEXT NOT NULL)")
        
        print("DataBase Create Successful")

    except:
        print("Database Not created")

    con.commit()
    con.close()
  

create_database()




# def droptable():
#     con = sqlite3.connect("User.db")
#     cur = con.cursor()

#     cur.execute("DROP TABLE loginInformation")
#     #cur.execute("DROP TABLE fileAnalysis")

#     con.close()

# droptable()

# def get_tables():
#     con = sqlite3.connect("User.db")
#     cur = con.cursor()
#     cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     tables = cur.fetchall()
#     table_info = []
#     for table in tables:
#         table_name = table[0]
#         cur.execute(f"PRAGMA table_info({table_name})")
#         columns = cur.fetchall()
#         table_info.append({
#             "name": table_name,
#             "columns": [column[1] for column in columns]
#         })
#     con.close()
#     return table_info

# print(get_tables())





def create_connection():
     return sqlite3.connect("User.db")

#Home Route Page
@app.route('/')
def home():
     return render_template("index.html")


# Validate email
def validate_email(email):
    # Regular expression to validate email address
    pattern = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'
    if re.match(pattern, email):
        return True
    else:
        return False


# Validate Password
def validate_password(password):
    if not 8<= len(password) <= 16:
        return False
    elif not any(char.upper() for char in password):
        return False
    elif not any(char.lower() for char in password):
        return False
    elif not any(char.isdigit() for char in password):
        return False
    elif not any(char in "!@#$%^&*()_+=" for char in password):
        return False
    return True



@app.route('/signup', methods = ['GET','POST'])
def signup():
    error = None
    conn = create_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        email=request.json.get('email')
        password=request.json.get('password')

        if not validate_email(email):
            data={'message': 'Enter validate Email'}
            print("Enter validate Email")


        elif not validate_password(password):
            data = {'message': 'Password does not meet the citeria'}
            print("Password does not meet the citeria")

        else:
            try:    
                
                # Insert user information into the database
                cur.execute("INSERT INTO loginInformation (user_email, user_password) VALUES (?, ?)",
                               ( email,password))
                conn.commit()
                
                # Return a success message or redirect to another page after registration
                data = {'message': 'Registration Successfull'}
                #return jsonify(data)
            except sqlite3.IntegrityError:
                # Handle unique constraint violation (email already exists)
            
                data = {'message': 'Email already exists!'}
                #return jsonify(data)
            finally:
                # Close the database connection
                conn.close()

    return jsonify(data)


    # If it's a GET request or the form submission failed, render the register.html template with the error









@app.route('/login', methods = ['POST'])
def login():
    conn = create_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        # Retrieve form data
        email=request.json.get('email')
        password=request.json.get('password')

        if email and password:   
                #print("Email password")
                # Insert user information into the database
                cur.execute("SELECT * FROM loginInformation WHERE user_email=? AND user_password=?", (email, password))
                user = cur.fetchall()
                if user:
                    #print("User find")
                    data = {'message': 'Login Successful'}
                    return jsonify(data)
        else:
           
           data = {'message': 'User Details Not valid'}
           return jsonify(data)
    


@app.route('/level_1')
def level_1():
    
    return render_template("another.html")


global sub1
sub1={}

global s
global s1 
s =" "
s1= " "

# Audio recording..........................
@app.route('/startrecording')
def record_audio(file_name ,duration=5, chunk=1024, format=pyaudio.paInt16, channels=1, rate=44100):

    # #file_name = "recorded_audio.wav"
    # audio = pyaudio.PyAudio()

    # # Open the recording stream
    # stream = audio.open(format=format, channels=channels,
    #                     rate=rate, input=True,
    #                     frames_per_buffer=chunk)

    # print("Recording...")

    # frames = []

    # # Record audio in chunks
    # for _ in range(0, int(rate / chunk * duration)):
    #     data = stream.read(chunk)
    #     frames.append(data)

    # print("Finished recording.")

    # # Stop and close the stream
    # stream.stop_stream()
    # stream.close()
    # audio.terminate()

    # # Save the recorded audio to a file
    # with wave.open(file_name, 'wb') as wf:
    #     wf.setnchannels(channels)
    #     wf.setsampwidth(audio.get_sample_size(format))
    #     wf.setframerate(rate)
    #     wf.writeframes(b''.join(frames))

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(file_name)
    subtitles1 = transcript.text

    #s1 = "".join((subtitles1)) 
    print("print subtitles 1: ", subtitles1)
    return subtitles1






# @app.route('/recog_audio')
# def recognization_audio():
#     file_name = "recorded_audio.wav"
#     record_audio(file_name)

#     rec_trans()
#     return render_template("recog.html")



@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        data = {'message': 'No file part'}
        return jsonify(data)

    file = request.files['file']

    if file.filename == '':
        data = {'message': 'No such file'}
        return jsonify(data)

    # Extracting the file extension
    _, extension = os.path.splitext(file.filename)

    # Generating a default name
    default_name = 'uploaded_file' + extension


    # Saving the uploaded file with the default name and original extension
    file_path = os.path.join('static', secure_filename(default_name))
    file.save(file_path)

    time.sleep(5)
    data = transcription(file_path)
   
    return jsonify(data)

    


@app.route('/upload_rec', methods=['POST'])
def upload_rec():
    if 'file' not in request.files:
        data = {'message': 'No file part'}
        return jsonify(data)

    file = request.files['file']

    if file.filename == '':
        data = {'message': 'No such file'}
        return jsonify(data)

    # Extracting the file extension
    _, extension = os.path.splitext(file.filename)

    print("Extention of audio: ", extension)
    # Generating a default name
    default_name = 'rec_audio' + '.wav'


    # Saving the uploaded file with the default name and original extension
    file_path = os.path.join('static', secure_filename(default_name))
    file.save(file_path)
    time.sleep(5)
    rec = record_audio(file_path)

    data={
        'rec': rec
    }
    return jsonify(data)


#Trancscript the video file and store in the database


@app.route('/transcription', methods=['POST'])
def transcription(file_path):

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(file_path)
    subtitles = transcript.text

    print("Transcription successful")

    # You can return the transcript or perform further processing here
    #return subtitles, 200




    words = subtitles.split(" ")
    word_count = len(words)
    space_count = len(words) - 1
    

    print("Subtitles: ", subtitles)

    print("\nFile analysis summary:\n")
    #print("Line count:", line_count)
    print("Word count:", word_count)
    print("Space count:", space_count)

    vowel = 0
    non_vowel = 0
    charcter = 0

	# Make a vowels list so that we can 
	# check whether the character is vowel or not 
    vowels_list = ['a', 'e', 'i', 'o', 'u', 
				'A', 'E', 'I', 'O', 'U'] 
	#Make Symbol list for counting the consonants
    symbol_list = [',','?','\'','.']
	
    for alpha in subtitles: 
		
		# Checking if the current character is vowel or not 
        if alpha in vowels_list: 
            vowel += 1
        elif alpha not in vowels_list and alpha not in symbol_list and alpha !=" ": 
            non_vowel += 1
    
    
    total_char = vowel+non_vowel
			
	# Print the desired output on the console. 
    print("Number of characters = ",total_char ) 
    print("Number of vowels in = ", vowel) 
    print("Number of consonants in = ", non_vowel)

    global s
    s += subtitles
    global sub1
    sub1={
        'subtitles' :subtitles,
        'Word_count': word_count,
        'space_count': space_count,
        'no_of_char' : total_char,
        'no_of_vowels': vowel,
        'no_of_consonants': non_vowel
    }
    return sub1

    

    #print("print subtitles : ", s)
    
    #return render_template("anafile.html", word_count=word_count, space_count=space_count,total_char=total_char, vowel=vowel, non_vowel=non_vowel)








#transcription()




@app.route('/highlight_text', methods=['POST'])
def highlight_matched_words(text, matched_words, color_code='\033[91m', end_color_code='\033[0m'):
    highlighted_text = text
    for word in matched_words:
        # Ensure the word is matched as a whole word
        regex = r'\b' + re.escape(word) + r'\b'
        highlighted_word = f"{color_code}{word}{end_color_code}"
        highlighted_text = re.sub(regex, highlighted_word, highlighted_text)
    return highlighted_text


def compare_files(file1_path, file2_path):
    # Read contents of both files
    text1 = file1_path.lower()     # "subtitles.txt"
    text2 = file2_path.lower()     # "subtitles1.txt"

    #print("Print Text1 : ", text1)
    #print("Print Text1 : ", text2)

    # Tokenize the texts into words
    words1 = set(word.strip('.') for word in text1.split())
    words2 = set(word.strip('.') for word in text2.split())
    
    # Compare the words
    matched_words = set(words1 & words2)

    # Highlight matched words in one of the texts
    #highlighted_text1 = text1
    highlighted_text2 = highlight_matched_words(text1, matched_words)

    # Check if any word is highlighted in the second text
    if highlighted_text2 != text1:
        print("Matched")
        print("\nHighlighted text:\n"+highlighted_text2)
    else:
        print("Not matched")


    s = " "
    s1 = " "
    return matched_words

#print("printing s1, :", s)
#print("Printing s2:",s1)

#compare_files(s,s1)










app.config['UPLOAD_FOLDER'] = 'static'
app.config['COMPRESSED_FOLDER'] = 'static'

# Function to compress the audio file






def compress_audio(input_path, compression_factor=2):
    try:
        # Load the input audio file
        audio = AudioSegment.from_file(input_path)
    except Exception as e:
        return str(e), None  # Return the error message and None for the file path if unable to load the audio
    
    # Apply compression by changing the sample rate
    compressed_audio = audio.set_frame_rate(audio.frame_rate // compression_factor)
    
    # Define the output path for the compressed file
    output_path = f"{input_path}"
    
    # Export the compressed audio to the output file
    compressed_audio.export(output_path, format="wav")
    
    # Check if the exported file contains audio data
    if os.path.getsize(output_path) <= 44:  # Check if the file size is less than WAV header size (44 bytes)
        return "Compression failed. Output file does not contain audio data.", None
    
    return "Compression successful", output_path









@app.route('/compress_audio', methods=['POST'])
def compress_audio_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No such file'})

    # Save the uploaded audio file
    filename = secure_filename(file.filename)
    upload_path = f"static/{filename}"
    file.save(upload_path)

    # Compress the audio file
    status_message, compressed_file_path = compress_audio(upload_path)

    if not compressed_file_path:
        return jsonify({'error': status_message})

    # Send the compressed file back to the client
    return send_file(compressed_file_path, as_attachment=True)




'''  
#Compress Video file

def compress_video(input_path, output_path, bitrate='150k'):
    video = VideoFileClip(input_path)
    compressed_video = video.resize(width=480)  # Resize the video to a lower resolution
    compressed_video.write_videofile(output_path, codec='libx264', bitrate=bitrate)
    video.close()
    compressed_video.close()

input_video_path = 'BRCOBM.mp4'
output_video_path = 'compressed_video.mp4'
compress_video(input_video_path, output_video_path)
 '''

def compress_video(input_path, output_path, bitrate='150k'):
    try:
        # Open the input video file
        video = VideoFileClip(input_path)
    except Exception as e:
        return str(e)  # Return the error message if unable to open the video
    
    # Resize the video to a lower resolution
    compressed_video = video.resize(width=480)
    
    # Write the compressed video to the output file
    compressed_video.write_videofile(output_path, codec='libx264', bitrate=bitrate)
    
    # Close the video objects
    video.close()
    compressed_video.close()
    
    return "Compression successful"



@app.route('/compress_video', methods=['POST'])
def compress_video_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No such file'})

    # Save the uploaded video file
    filename = secure_filename(file.filename)
    upload_path = f"static/{filename}"
    file.save(upload_path)

    # Compress the video file
    output_path = f"{filename}"
    compression_result = compress_video(upload_path, output_path)

    if compression_result != "Compression successful":
        return jsonify({'error': compression_result})

    # Send the compressed file back to the client
    return send_file(output_path, as_attachment=True)















#View database
@app.route('/view')
def view_table():
     
    con = sqlite3.connect("User.db")
    cur = con.cursor()

    #Transcripttion data fetch
    # res = cur.execute("SELECT * FROM transcription")
    # text = res.fetchall()

    ul = cur.execute("SELECT * FROM loginInformation")
    text1 = ul.fetchall()

    cur.close()
    #print(text)
    con.close()


    return render_template("view.html",  ulogin = text1)




if __name__ == '__main__':
     app.run(host = '0.0.0.0', port = 5000)

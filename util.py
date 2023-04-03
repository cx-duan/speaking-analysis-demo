import requests
from pytube import YouTube
import streamlit as st
import time

# Endpoints
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
upload_endpoint = 'https://api.assemblyai.com/v2/upload'
CHUNK_SIZE = 5242880

# Function that saves and uploads YouTube link locally
def save_audio(link):
    yt = YouTube(link)
    stream = yt.streams.filter(only_audio=True).first()
    save_location = stream.download()
    print('Saved mp3 to', save_location)
    return save_location

#Function to read local file
def read_file(filename):
    with open(filename, 'rb') as _file:
        while True:
            data = _file.read(CHUNK_SIZE)
            if not data:
                break
            yield data
# Function converting milliseconds
def convertMillis(start_ms):
    seconds = int((start_ms / 1000) % 60)
    minutes = int((start_ms / (1000 * 60)) % 60)
    hours = int((start_ms / (1000 * 60 * 60)) % 24)
    btn_txt = ''
    if hours > 0:
        btn_txt += f'{hours:02d}:{minutes:02d}:{seconds:02d}'
    else:
        btn_txt += f'{minutes:02d}:{seconds:02d}'
    return btn_txt


# a function to upload a given file to AssemblyAI's servers
def upload_file(file, auth_key):
    headers_auth_only = {'authorization': auth_key}
    upload_response = requests.post(
        upload_endpoint,
        headers=headers_auth_only, 
        data=read_file(file)
	)
    return upload_response.json()['upload_url']

# a function that takes a youtube link, downloads the video, uploads it to AssemblyAI's servers and transcribes it
@st.cache_data
def transcribe_from_link(link, auth_key):
	headers_auth_only = {'authorization': auth_key}
    # download the audio of the YouTube video locally
	save_location = save_audio(link)
	# start the transcription of the audio file
	transcript_request = {
		'audio_url': upload_file(save_location, auth_key),
        'speaker_labels': True,
	}
	transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers_auth_only)
	# this is the id of the file that is being transcribed in the AssemblyAI servers
	# we will use this id to access the completed transcription
	transcript_id = transcript_response.json()['id']
	polling_endpoint = transcript_endpoint + "/" + transcript_id
    
	return polling_endpoint, save_location

# return the status of a given transcript 
def get_status(polling_endpoint, auth_key):
    headers_auth_only = {'authorization': auth_key}
    polling_response = requests.get(polling_endpoint, headers=headers_auth_only)
    return polling_response.json()['status']

# repeatedly checks the status of a given transcript until the status is completed or error
def poll(polling_endpoint, auth_key):
    status = get_status(polling_endpoint, auth_key)
    while status not in ["error", "completed"]:
        time.sleep(10)
        status = get_status(polling_endpoint, auth_key)
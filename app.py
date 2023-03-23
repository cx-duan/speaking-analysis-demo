import json
import streamlit as st
from pytube import YouTube
from PIL import Image
from save_audio import save_audio
from configure import auth_key
import requests
from time import sleep
import time



transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
upload_endpoint = 'https://api.assemblyai.com/v2/upload'
headers_auth_only = {'authorization': auth_key}
headers = {
   "authorization": auth_key,
   "content-type": "application/json"
}

#Import image and youtube URL
image = Image.open('svgexport-1.png')
url = 'https://www.youtube.com/watch?v=AkcwNwPy7RI'
yt = YouTube(url)

# Streamlit command to run: python3 -m streamlit run app.py

#JSON file read. Can be replaced with upload
with open('response.json', 'r') as transcript_json:
    transcript_data = json.load(transcript_json)

#List and variable collection from JSON
#Select speaker labels from JSON
speaker_labels = transcript_data['utterances']
#Variable for audio duration
audio_duration_in_minutes = transcript_data['audio_duration'] / 60
#Words spoken variable
word_data = transcript_data['words']
#Lists to run 
speaker = []
words = []
word_confidence_scores = []
long_pauses = 0

# Check confidence scores to gauge speaker clarity as well as pauses
index_start = 1
for i in range(len(word_data)):
    words.append(word_data[i]['text'])
    word_confidence_scores.append(word_data[i]['confidence'])
    try:
        if word_data[index_start]['start'] - word_data[i]['end'] > 2000:
            long_pauses += 1
        index_start += 1
    except IndexError:
        pass

#Clarity and words per min
speaker_clarity = sum(word_confidence_scores) / len(word_confidence_scores)
words_per_minute = round(len(words) / audio_duration_in_minutes)
# print(words_per_minute)
# Total speaking time
total_speaking_time_a = []
total_speaking_time_b = []
for i in range(len(speaker_labels)):
    speaker.append(speaker_labels[i]['speaker'])
    speaker_duration = (speaker_labels[i]['end']) - (speaker_labels[i]['start']) 
    if speaker_labels[i]['speaker'] == "A":
        total_speaking_time_a.append(speaker_duration)
    elif speaker_labels[i]['speaker'] == "B":
        total_speaking_time_b.append(speaker_duration)

# Speaker Text for each speaker
total_speaking_a = []
total_speaking_b = []
for i in range(len(speaker_labels)):
    if (speaker_labels[i]['speaker'] == "A")  :
        total_speaking_a.append(speaker_labels[i]['text'])
    elif speaker_labels[i]['speaker'] == "B":
        total_speaking_b.append(speaker_labels[i]['text'])

#Streamlit Frontend
#Initiate App with config, AAI logo and video
st.set_page_config(layout="wide")
st.image(image, caption='Talk time/speed demo')
st.title(f'{yt.title}')

#set 2 columns
col1, col2 = st.columns(2)
with col1:
# Get link from user
    video_url = st.text_input(label='Earnings call link', value="https://www.youtube.com/watch?v=UA-ISgpgGsk")
    st.video("https://www.youtube.com/watch?v=AkcwNwPy7RI")
    st.markdown(f"# Transcript: ")
    st.markdown(f'{transcript_data["text"]}')
# Save audio locally
save_location = save_audio(video_url)
## Upload audio to AssemblyAI
CHUNK_SIZE = 5242880

def read_file(filename):
	with open(filename, 'rb') as _file:
		while True:
			data = _file.read(CHUNK_SIZE)
			if not data:
				break
			yield data

upload_response = requests.post(
	upload_endpoint,
	headers=headers_auth_only, data=read_file(save_location)
)
audio_url = upload_response.json()['upload_url']
print('Uploaded to', audio_url)

## Start transcription job of audio file
data = {
	'audio_url': audio_url,
}
transcript_response = requests.post(transcript_endpoint, json=data, headers=headers)
print(transcript_response.json())
transcript_id = transcript_response.json()['id']
polling_endpoint = transcript_endpoint + "/" + transcript_id

print("Transcribing at", polling_endpoint)
with st.container():
    with st.spinner('Wait for it...'):

## Waiting for transcription to be done
        status = 'submitted'
        while status != 'completed':
            sleep(1)
            polling_response = requests.get(polling_endpoint, headers=headers)
            transcript = polling_response.json()['text']
            status = polling_response.json()['status']
    st.success('Transcription Completed!')

# Display transcript
print('creating transcript')
st.sidebar.header('Transcript of the earnings call')
st.sidebar.markdown(transcript)

# print(json.dumps(polling_response.json(), indent=4, sort_keys=True))


#Analysis on column 2
with col2:
    speaker_clarity_round={round(speaker_clarity * 100,2)}
    st.text("")
    st.text("")
#Total speaking time
    if(sum(total_speaking_time_b)>0):
        st.markdown(f'#### Speaker A spoke for a total of {(sum(total_speaking_time_a))/1000} seconds')
        st.markdown(f'#### Speaker B spoke for a total of {(sum(total_speaking_time_b))/1000} seconds')
    else:
        if ((sum(total_speaking_time_a)) <= 180000):
            st.markdown(f'#### You spoke for a total of {(sum(total_speaking_time_a))/1000} seconds')
        else:
            st.metric(label="You spoke for a total of", value=f'{(sum(total_speaking_time_a))/1000/60} minutes')

#Words per minute metric + tips
    if words_per_minute < 120:
        st.metric(label="You were speaking at ", value= str(words_per_minute) + ' words per minutes', delta = "-You are speaking a little slow, try to speed down slightly.",delta_color='normal')
        st.markdown('According to the National Center for Voice and Speech, the average rate for English speakers in the US is about 150 words per minute. Aim to be between the 120 - 160 WPM range for a standard speaking rate')
        st.markdown('**_Quick tips:_** ')
        st.markdown('1. **Be more efficient with your pauses** . See if you are taking pauses that are too frequent or lengthy as that may lose the audience.')
        st.markdown('2. **Practice getting to the point directly** . Use a stopwatch to time yourself')
        st.markdown('3.  **Record your talks** . Analyze areas which you can increase speed and practice these portions')

    elif words_per_minute > 160:
        st.metric(label="You were speaking at ", value= str(words_per_minute) + ' words per minutes', delta = "You are speaking a little fast, try to slow down slightly.",delta_color='inverse')
        st.markdown('According to the National Center for Voice and Speech, the average rate for English speakers in the US is about *150* words per minute. Aim to be between the *120 - 160* WPM range for a standard speaking rate')
        st.markdown('**_Quick tips:_** ')
        st.markdown('1. **Plan out your presentation** and stick to the times you planned for each section')
        st.markdown('2. Focus on proper **breathing and breath control**')
        st.markdown('3. Use **silence** to strategically to build anticipation, to highlight a key point, or to draw attention and emphasis to a particular idea.')

    else:
        st.metric(label="You were speaking at ", value= str(words_per_minute) + ' words per minutes', delta = "number+delta+gauge")
        st.markdown('You are in the ideal range for speaking speed! The ideal speaking range is between: 120 - 160 words per minute.')
        st.markdown('According to the National Center for Voice and Speech, the average rate for English speakers in the US is about *150* words per minute. Aim to be between the *120 - 160* WPM range for a standard speaking rate')
        st.markdown('**_General tips:_** ')
        st.markdown('1. **Plan out your presentation** and stick to the times you planned for each section')
        st.markdown('2. Focus on proper **breathing and breath control**')
        st.markdown('3.  **Record your talks** . Analyze areas which you are not fully comfortable with and practice these portions')

    
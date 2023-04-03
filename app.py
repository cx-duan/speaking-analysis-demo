import streamlit as st
from pytube import YouTube
from PIL import Image
import util
from configure import auth_key
import requests
import time

# Streamlit command to run: python3 -m streamlit run app.py
#Endpoint variables
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
upload_endpoint = 'https://api.assemblyai.com/v2/upload'
headers_auth_only = {'authorization': auth_key}
headers = {
   "authorization": auth_key,
   "content-type": "application/json"
}

#Import AAI logo
image = Image.open('svgexport-1.png')

#Streamlit Frontend
#Initiate App with config, AAI logo and title
st.set_page_config(layout="wide")
st.image(image, caption='Talk time, speed and clarity demo')
st.title('AssemblyAI - Speaking Analysis Demo')


#set 2 columns
col1, col2 = st.columns(2)
#Populate column 1
with col1:
# Get YouTube link from user
    auth_key = st.text_input("Enter your AssemblyAI API key", type="password")
    headers = {'authorization': auth_key}

    while not auth_key:
        st.warning("Please enter your API key.")
        st.stop()
    video_url = st.text_input(label= "Paste YouTube URL here (Sample URL Provided)",value="https://www.youtube.com/watch?v=AkcwNwPy7RI")
# Set progress bar
    youtube_progress_bar = st.progress(0, text="Transcription in progress")
# Set title to YouTube video using metadata
    video_title=(f'{YouTube(video_url).title}')
    st.subheader(video_title)
    st.video(video_url)

# Update progress bar
youtube_progress_bar.progress(10, text="Reading YouTube URL")

polling_endpoint, file = util.transcribe_from_link(video_url, auth_key)

# Update progress bar
youtube_progress_bar.progress(40, text="Uploading to AssemblyAI endpoint")
print('Uploaded')

# # Changes status to 'submitted'
st.session_state['status'] = 'submitted'

# Repeatedly poll the transcript until it is completed
util.poll(polling_endpoint, auth_key)

# Get status
st.session_state['status']  = util.get_status(polling_endpoint, auth_key)

if st.session_state['status'] =='completed':
    polling_response = requests.get(polling_endpoint, headers=headers)
    full_transcript = polling_response.json()
    transcript_text = polling_response.json()['text']

# Display transcript
print('Transcript completed')
youtube_progress_bar.progress(100, text="Completed transcript")
st.sidebar.header(video_title, " Transcript")
st.sidebar.markdown(transcript_text)

#Analysis on column 2
#List and variable collection from JSON
#Select speaker labels from JSON
speaker_labels = full_transcript['utterances']
#Variable for audio duration
audio_duration_in_minutes = full_transcript['audio_duration'] / 60
#Words spoken variable
word_data = full_transcript['words']
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
speaker_clarity_round={round(speaker_clarity * 100,2)}
words_per_minute = round(len(words) / audio_duration_in_minutes)

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

print(total_speaking_a)
print(total_speaking_time_a)
print("")
print(total_speaking_b)
print(total_speaking_time_b)


with col2:
#Total speaking time
    if(sum(total_speaking_time_b)>0):
        st.markdown(f'#### Speaker A spoke for a total of {(sum(total_speaking_time_a))/1000/60:.2f} minutes')
        st.markdown(f'#### Speaker B spoke for a total of {(sum(total_speaking_time_b))/1000/60:.2f} minutes')
        st.metric("Your clarity score is", str(int(speaker_clarity_round.pop())) + "%")
        
    else:
        if ((sum(total_speaking_time_a)) <= 180000):
            st.markdown(f'#### You spoke for a total of {(sum(total_speaking_time_a))/1000} seconds')
            st.metric("Your clarity score is", str(int(speaker_clarity_round.pop())) + "%")
        else:
            st.metric(label="You spoke for a total of", value='{:.2f} minutes'.format(sum(total_speaking_time_a)/1000/60))
            st.metric("Your clarity score is", str(int(speaker_clarity_round.pop())) + "%")
#Words per minute metric + tips
    if words_per_minute < 120:
        st.metric(label="You were speaking at ", value= str(words_per_minute) + ' words per minute', delta = "You are speaking a little slow, try to speed down slightly.",delta_color='normal')
        st.markdown('According to the National Center for Voice and Speech, the average rate for English speakers in the US is about 150 words per minute. Aim to be between the 120 - 160 WPM range for a standard speaking rate')
        st.markdown('**_Quick tips:_** ')
        st.markdown('1. **Be more efficient with your pauses** . See if you are taking pauses that are too frequent or lengthy as that may lose the audience.')
        st.markdown('2. **Practice getting to the point directly** . Use a stopwatch to time yourself')
        st.markdown('3.  **Record your talks** . Analyze areas which you can increase speed and practice these portions')

    elif words_per_minute > 160:
        st.metric(label="You were speaking at ", value= str(words_per_minute) + ' words per minute', delta = "You are speaking a little fast, try to slow down slightly.",delta_color='inverse')

        st.markdown('According to the National Center for Voice and Speech, the average rate for English speakers in the US is about *150* words per minute. Aim to be between the *120 - 160* WPM range for a standard speaking rate')
        st.markdown('**_Quick tips:_** ')
        st.markdown('1. **Plan out your presentation** and stick to the times you planned for each section')
        st.markdown('2. Focus on proper **breathing and breath control**')
        st.markdown('3. Use **silence** to strategically to build anticipation, to highlight a key point, or to draw attention and emphasis to a particular idea.')

    else:
        st.metric(label="You were speaking at ", value= str(words_per_minute) + ' words per minute ✅')
        st.markdown('You are in the ideal range for speaking speed! The ideal speaking range is between: 120 - 160 words per minute.')
        st.markdown('According to the National Center for Voice and Speech, the average rate for English speakers in the US is about *150* words per minute. Aim to be between the *120 - 160* WPM range for a standard speaking rate')
        st.markdown('**_General tips:_** ')
        st.markdown('1. **Plan out your presentation** and stick to the times you planned for each section')
        st.markdown('2. Focus on proper **breathing and breath control**')
        st.markdown('3.  **Record your talks** . Analyze areas which you are not fully comfortable with and practice these portions')

    
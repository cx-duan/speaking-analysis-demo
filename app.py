import json
import streamlit as st
from pytube import YouTube
from PIL import Image

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
st.video("https://www.youtube.com/watch?v=AkcwNwPy7RI")

#set 2 columns
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"# Transcript: ")
    st.markdown(f'{transcript_data["text"]}')

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
        st.metric(label="You were speaking at ", value= str(words_per_minute) + ' words per minutes', delta = "-You are speaking a little slow, try to speed down slightly.",delta_color='inverse')
        st.markdown('According to the National Center for Voice and Speech, the average rate for English speakers in the US is about 150 words per minute. Aim to be between the 120 - 160 WPM range for a standard speaking rate')
        st.markdown('**_Quick tips:_** ')

    elif words_per_minute > 160:
        st.metric(label="You were speaking at ", value= str(words_per_minute) + ' words per minutes', delta = "You are speaking a little fast, try to slow down slightly.",delta_color='inverse')
        st.markdown('According to the National Center for Voice and Speech, the average rate for English speakers in the US is about *150* words per minute. Aim to be between the *120 - 160* WPM range for a standard speaking rate')
        st.markdown('**_Quick tips:_** ')
        st.markdown('1. **Plan out your presentation** and stick to the times you planned for each section')
        st.markdown('2. Focus on proper **breathing and breath control**')
        st.markdown('3. Use **silence** to strategically to build anticipation, to highlight a key point, or to draw attention and emphasis to a particular idea.')



    else:
        st.metric(label="You were speaking at ", value= str(words_per_minute) + ' words per minutes', delta = "number+delta+gauge")
        st.markdown('You are in the ideal range for speaking speed! The ideal speaking range is between: 120 - 150 words per minute.')
    
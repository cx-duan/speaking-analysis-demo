# Demo - Speaking Analysis

## Description:
This demo was put together to showcase possible applications of AssemblyAI's API. Processing any YouTube URL, a user can display an analysis of the speaker's total talk time, clarity score and speaking speed. There is also recommendations based on the speed of talking by the user.   

Overall this showcases a practical application of AssemblyAI's API for speech anaylsis.

File contains:
- Customizable YouTube video that is the subject of transcription
- Transcript of the video (Speaker by Speaker timestamps)
- Speaker Diarization Analysis (Limited to 2 Speakers)
- Clarity Score (How clear the words were to the AI model out of 100)
- Total talk time
- Words per minute analysis and personalized tips 

Streamlit App:
https://cx-duan-talk-time-speed-demo-app-aisi98.streamlitapp.com/

<img width="1339" alt="image" src="https://user-images.githubusercontent.com/57568318/198558457-9356e36e-ce49-4e31-96a9-819e1bad346c.png">


## To Run:

To run Python file:
```python3 app.py```   

To run app via StreamLit:
```python3 -m streamlit run app.py``` 


## Import Libraries
```pip3 install streamlit```  
```pip3 install pytube```  




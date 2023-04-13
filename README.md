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
https://cx-duan-speaking-analysis-demo-app-wt640w.streamlit.app/  

![image](https://user-images.githubusercontent.com/57568318/229958740-40cb19ce-698f-4841-be4c-66ea25032108.png)

## To Run:

To run Python file:
```python app.py```   

To run app via StreamLit:
```python -m streamlit run app.py``` 


## Import Main Libraries
```pip install streamlit```  
```pip install pytube```  
```pip install pandas```  





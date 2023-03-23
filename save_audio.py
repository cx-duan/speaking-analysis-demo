from pytube import YouTube

def save_audio(link):
    yt = YouTube(link)
    stream = yt.streams.filter(only_audio=True).first()
    save_location = stream.download()
    print('Saved mp3 to', save_location)
    return save_location
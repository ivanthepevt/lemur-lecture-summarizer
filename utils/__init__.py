import streamlit as st
import assemblyai as aai
from yt_dlp import YoutubeDL

YTDLP_FNAME = 'tmp.webm'

# For some reason directly importing the constant did not work
def return_ytdlp_fname():
    return YTDLP_FNAME

def get_transcript(f, ftype):
    config = aai.TranscriptionConfig(
        language_code='vi'
        )
    transcriber = aai.Transcriber(config=config)

    print("entered")
    print(ftype)
    if ftype == 'YouTube link':
        with st.spinner('Đang tải video...'):
            ydl_opts = {'outtmpl': YTDLP_FNAME}
            print("đang tải")
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([f])
                f = YTDLP_FNAME
    print("returning", f)
    with st.spinner('Đang biên dịch ...'):
        transcript = transcriber.transcribe(f)
    if transcript.error:
        raise TranscriptionException(transcript.error)
    return transcript

def ask_question(transcript, question):
    questions = [
        aai.LemurQuestion(question=question,)
    ]

    result = transcript.lemur.question(questions)

    if transcript.error:
        raise QuestionException(result.error)

    return result.response[0].answer


class TranscriptionException(Exception):
    pass

class QuestionException(Exception):
    pass

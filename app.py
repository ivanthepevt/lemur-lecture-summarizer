import os

import streamlit as st
import assemblyai as aai
from dotenv import load_dotenv
load_dotenv()

from utils import get_transcript, ask_question, return_ytdlp_fname

environ_key = "c1b0224fb3c14871964b3b47893df872"
if environ_key is None:
    pass
elif environ_key == "":
    environ_key = None
else:
    aai.settings.api_key = environ_key

# Remove existing temp files in case if improper shutdown
temp_files = [f for f in os.listdir() if f.startswith('tmp')]
for f in temp_files:
    os.remove(f)

# constant
YTDLP_FNAME = return_ytdlp_fname()

# Setting defaults for conditional rendering
input_key = None
f = None
entered = None
summary = None
question_submit = None
answer = ''

# Initializing state variables
state_strings = ['summary', 'entered', 'transcript']
for s in state_strings:
    if s not in st.session_state:
        st.session_state[s] = None

def set_aai_key():
    """ Callback to change set AAI API key when the key is input in the text area """
    aai.settings.api_key = st.session_state.input_aai_key

# MAIN APPLICATION CONTENT

"# NaviAI SumMate"
"Tóm tắt bài thuyết trình/ tiết học/ bài giảng"


if not environ_key:
    "## Không phát hiện API Key"
    """
To get started, paste your AssemblyAI API key in the below box.
If you don't have an API key, you can get one [here](https://www.assemblyai.com/dashboard/signup). You will need to set up billing in order to use this application since it uses [LeMUR](https://www.assemblyai.com/blog/lemur/).

You can copy your API key by pressing the `Copy token` button on the right hand side of your [Dashboard](https://www.assemblyai.com/app).
    """
    input_key = st.text_input(
        "API Key",
        placeholder="Enter your AssemblyAI API key here",
        type="password",
        on_change=set_aai_key,
        key='input_aai_key'
        )

    st.warning("Note: You can avoid this section by setting the `ASSEMBLYAI_API_KEY` environment variable, either through the terminal or the `.env` file.", icon="🗒️")

if input_key or environ_key:
    """
    Chọn video bạn cần tóm tắt, bạn có thể chọn file trên máy, trên Drive hoặc trên YouTube.
    """

    # File type options
    ftype = st.radio("Chọn file", ('Tải lên từ máy', 'Drive', 'YouTube link'))

    if ftype == 'Tải lên từ máy':
        # Store the uploaded file in a temporary file
        f = st.file_uploader("File")
        if f:
            uploaded_ftype = f.name.split('.')[-1]
            temp_fname = f"tmp.{uploaded_ftype}"
            with open(temp_fname, 'wb') as fl:
                fl.write(f.read())
            f = temp_fname
    elif ftype == 'Drive':
        f = st.text_input("Link", 
                          value="https://storage.googleapis.com/aai-web-samples/cs50p-unit-tests.mp3",
                          placeholder="Public link to the file"
                          )
    elif ftype == 'YouTube link':
        f = st.text_input("Link",
                          value="https://www.youtube.com/watch?v=7sDRk_oGRjg",
                          placeholder="YouTube link"
                          )

    value = "" if ftype == "Local file" else "Video thuyết trình về mẫu xe Vinfast VF7"
    placeholder = "Mô tả file để AI hiểu chính xác hơn"
    context = st.text_input("Mô tả", value=value, placeholder=placeholder)
     
if f:
    entered = st.button("Submit")
    if entered:
              
        transcript = get_transcript(f, ftype)
        print(transcript.text)

        if ftype == "Local file":
            os.remove(f)
        elif ftype == "YouTube link":
            os.remove(YTDLP_FNAME)  # remove file bc youtube DL will not work if there already exists file with that name

        st.session_state['transcript'] = transcript


        params = {
            'answer_format': "**<Tóm tắt>**\n<Những ý chính trong video bao gồm>",
            'max_output_size': 4000
        }
        if context: params['context'] = context
        
        with st.spinner("Đang tóm tắt..."):
            try:
                summary = transcript.lemur.summarize(**params)
                st.session_state['summary'] = summary.response.strip().split('\n')
                st.session_state['entered'] = True
                print('session summary: ', st.session_state['summary'])
            except aai.types.LemurError as e:
               st.write(f'Error: {str(e)}')
               st.session_state['entered'] = False

if st.session_state['entered']:
    "## Kết quả"
    
    if st.session_state['summary']:
        for i in st.session_state['summary']:
            st.markdown(i)


if st.session_state['summary']:
    "# Hỏi đáp nâng cao"
    "Nhập câu hỏi về một thông tin cụ thể trong video:"
    
    question = st.text_input("Nhập câu hỏi",
                              placeholder="",
                              )
    
    question_asked = st.button("Submit", key='question_asked')
    if question_asked:
        with st.spinner('Đang tìm kiếm câu trả lời...'):
            answer = ask_question(st.session_state['transcript'], question)
    answer
    

# -*- coding: utf-8 -*-

from testpack import generate_questionnaire
import streamlit as st
from read_files import read_docx, read_pdf, save_txt
sts = st.session_state
          
def callback():
    with st.spinner("문제를 생성 중입니다."):
        sts.questionnaire = generate_questionnaire(sts.model, sts.input_text, sts.language, sts.num_questions)
    sts.current_step = "B"
    
def callback2():
    sts.current_step = "C"    
    
def callback3():
    sts.current_step = "A"
    for key in sts.keys():
        del sts[key]    
    
if "current_step" not in sts:
    sts.current_step = "A"
if "input_text" not in sts:
    sts.input_text = ""

st.title("모의고사 자동제작 서비스")

if sts.current_step == "A":
    format = st.radio("파일 유형 선택", ["직접 입력", ".pdf", ".docx"], index=0, key="format")
    if format == "직접 입력":
        sts.input_text = st.text_area("내용 입력", sts.input_text)
    elif format == ".pdf":
        pdf_loc = st.file_uploader("최대 200MB까지 업로드할 수 있습니다")
        if pdf_loc:
            sts.input_text = read_pdf(pdf_loc)
    elif format == ".docx":
        docx_loc = st.file_uploader("최대 200MB까지 업로드할 수 있습니다")
        if docx_loc:
            sts.input_text = read_docx(docx_loc)
                
    sts.code = st.text_input("참여자번호를 입력하세요. 1번째 사용인 경우 A를, 2번째 사용인 경우 B를 뒤에 붙여주세요 (예: 7A)")
    sts.model = st.radio("모델 선택 (GPT-4를 권장합니다.)", ["GPT-4", "GPT-3.5"], index=0)
    sts.language = st.radio("언어 선택 (영어가 더 정확합니다.)", ["한국어", "English"], index=0)
    sts.num_questions = st.number_input("생성할 문제 수 설정", min_value=1, max_value=20, value=5)
    
    if sts.input_text:
        st.button("모의고사 생성하기", on_click=callback)
        # st.form_submit_button("모의고사 생성하기", on_click=callback)
    else:
        st.button(":red[내용을 입력하거나 파일을 업로드해 주세요.]", disabled=True)
        # st.form_submit_button(":red[내용을 입력하거나 파일을 업로드해 주세요.]", disabled=True)

if sts.current_step == "B":
    with st.form("main_quiz"):            
        for q_no, question in enumerate(sts.questionnaire):
            labels = question["selection"]
            st.radio(question["question"], range(len(labels)), index=0, format_func=labels.__getitem__, key=f"chosen_{q_no}")
        st.form_submit_button("제출하기", on_click=callback2)
            
if sts.current_step == "C":
    score_list = [0] * len(sts.questionnaire)
    for q_no, question in enumerate(sts.questionnaire):
        selection_list = []
        for s_no, sel in enumerate(question["selection"]):                    
            if s_no == sts[f"chosen_{q_no}"]:
                if s_no == question["correct"]:
                    score_list[q_no] = 1
                    selection_list.append(f":green[{sel}]")
                else:
                    selection_list.append(f":red[{sel}]")
            else:
                if s_no == question["correct"]:
                    selection_list.append(f":green[{sel}]")
                else:
                    selection_list.append(sel)
        st.radio(question["question"], selection_list, index=sts[f"chosen_{q_no}"], disabled=True)
        result = "✅" if score_list[q_no] == 1 else "❌"
        st.write(f"{result} {question['explanation']}") 
    st.write(f"{len(sts.questionnaire)}개 중 {sum(score_list)}개 맞추셨습니다.")
    st.write("아래 파일을 다운로드받아 구글 폼에 첨부해주세요.")
    st.download_button("다운로드/처음으로 돌아가기", data=save_txt(sts), file_name=f"results_{sts.code}.txt", on_click=callback3)
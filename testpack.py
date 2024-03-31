# -*- coding: utf-8 -*-
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.chains.openai_functions import create_structured_output_runnable
from typing import List
import random
from pprint import pprint
import streamlit as st

load_dotenv()

class SingleQuestion(BaseModel):
    question: str = Field(description="Multiple choice questions")
    correct: str = Field(description = "The correct answer")
    incorrect: List[str] = Field(description = "List of incorrect answers, up to 4 elements")
    explanation: str = Field(description="Explanation on why the answer is correct for each question")   
    
class Questionmaker(BaseModel):
    questions: List[SingleQuestion] = Field(description="List of questions") 

template = '''
You are a study assistant which must generate unique {num_questions} multiple-choice questions for students.\n
By using [INPUT_DATA], make multiple choice questions in a structured format.\n
You must make one correct answer, and a maximum of four incorrect answers.\n
The language must be in {language}.\n
Tips: You must return {num_questions} questions, not more and not less.

[INPUT_DATA]:\n
{input_data}
'''

def generate_questionnaire(model_name, input_text, language, num_questions):
    if model_name == "GPT-4":
        model_ver = "gpt-4-0125-preview"
    elif model_name == "GPT-3.5":
        model_ver = "gpt-3.5-turbo-0125"
        
    response_list = []
    duplicate = False
    
    while len(response_list) < num_questions:
        model = ChatOpenAI(model=model_ver, temperature=1, max_tokens=None)
        prompt = PromptTemplate.from_template(template)
        chain = create_structured_output_runnable(Questionmaker, model, prompt)
        response = chain.invoke({"input_data": input_text, "language": language, "num_questions": num_questions - len(response_list)})
        response_list.extend(response.questions)
        if len(response_list) > num_questions:
            response_list = response_list[:num_questions]
        if len(response_list) < num_questions and not duplicate:
            st.write("인공지능의 한계로 동일/비슷한 문제가 여러 개 생성되었습니다.")
            st.write("언어를 영어로 변경하거나, GPT-4를 사용하시면 보다 다양한 문제를 푸실 수 있습니다.")
            duplicate = True        
    
    random.shuffle(response_list)
    questionnaire = list()
    for question in response_list:        
        q_dict = dict()
        q_dict["question"] = question.question
        total_selections = 1 + len(question.incorrect)
        correct_index = random.randint(0, total_selections -1)
        q_dict["selection"] = question.incorrect
        q_dict["selection"].insert(correct_index, question.correct)
        q_dict["correct"] = correct_index
        q_dict["explanation"] = question.explanation
        questionnaire.append(q_dict)    
    return questionnaire

'''
with open("sample.txt",encoding='utf-8') as f:
    sample = f.read()
'''

if __name__ == "__main__":
    pprint(generate_questionnaire("GPT-3.5", "", "English", 20))

        

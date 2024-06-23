import google.generativeai as genai
from langchain_community.llms import GooglePalm 
from langchain.prompts import PromptTemplate
from langchain_community.chains import llm_requests 
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

llm = genai.GenerativeModel('gemini-1.0-pro-latest')

def analyze_syllabus(syllabus_text, credentials):
    """Analyzes the syllabus and returns structured information."""

    prompt_template = PromptTemplate(
        input_variables=["syllabus"],
        template="""
        You are a helpful AI study assistant. Here is the syllabus for a course: 
        ```
        {syllabus}
        ```
        Please analyze the syllabus and provide the following information in a JSON format:
        - course_name: 
        - course_objectives: 
        - main_topics: 
        - grading_breakdown: 
        """
    )
    chain = llm_requests(llm=llm, prompt=prompt_template)
    response = chain.run(syllabus=syllabus_text)

    # Parse the JSON response
    try:
        response = json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response from LLM: {e}, Raw response: {response}") from e
    return response

def generate_roadmap(syllabus_analysis, course_content, credentials):
    """Generates a study roadmap based on syllabus and content."""
    llm = genai.GenerativeModel('gemini-1.0-pro-latest') 
    prompt_template = PromptTemplate(
        input_variables=["analysis", "content"],
        template="""
        You are a helpful AI study assistant.
        Given this course syllabus analysis: 
        ```json
        {analysis}
        ```
        and the course content:
        ```
        {content}
        ```
        Please create a detailed study roadmap to help students succeed in the course. 
        The roadmap should include:
        - A week-by-week or topic-by-topic breakdown of material.
        - Suggestions for readings, practice problems, and other resources.
        - Tips for effective studying and time management.
        """
    )
    chain = llm_requests(llm=llm, prompt=prompt_template) 
    response = chain.run(analysis=syllabus_analysis, content=course_content)
    return response

def get_answer_and_explanation(user_question, all_text, credentials):
    """Gets an answer to a user's question from the provided context."""
    llm = genai.GenerativeModel('gemini-1.0-pro-latest')
    prompt_template = PromptTemplate(
        input_variables=["question", "context"],
        template="""
        You are a helpful AI study assistant. Answer the question based on the context provided. 
        If the answer cannot be found in the context, say "I'm not sure, please provide more information."
        
        Context:
        {context}
        Question: {question}
        Answer:
        """
    )
    chain = llm_requests(llm=llm, prompt=prompt_template) 
    response = chain.run(question=user_question, context=all_text)
    return response
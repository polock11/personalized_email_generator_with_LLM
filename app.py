import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.document_loaders import PyPDFLoader
import os
import tempfile 
import time

# Load environment variables
load_dotenv()

MODEL_NAME_LIST = [
    "llama-3.3-70b-versatile",
    "gemma2-9b-it",
    "llama3-8b-8192",
    "llama3-70b-8192",
]

# Helper function to remove extra whitespace
def remove_extra_whitespace(sentence):
    return ' '.join(sentence.split())

# Streamlit App UI
st.title("Personalized Email Generator")
st.write("Please provide the job description URL and upload your CV in the sidebar to generate a personalized email.")

# Initialize session state for generated content
if "cv" not in st.session_state:
    st.session_state.cv = None
if "jd" not in st.session_state:
    st.session_state.jd = None
if "email" not in st.session_state:
    st.session_state.email = None

# Input fields
# url = st.text_input("Enter the job description URL")
# uploaded_cv = st.file_uploader("Upload your CV (PDF)", type=["pdf"])


# Sidebar for Input Fields
with st.sidebar:
    st.header("Provide Job URL and CV")
    url = st.text_input("URL")
    uploaded_cv = st.file_uploader("Upload your CV (PDF)", type=["pdf"])

    st.header("Select Model")
    selected_model = st.selectbox("Choose a model for the task:", MODEL_NAME_LIST, index=0)


# Initialize the LLM
MODEL_NAME = "llama-3.3-70b-versatile"

llm = ChatGroq(
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name= MODEL_NAME if selected_model is None else selected_model
)
if st.button("Generate Email"):
    if url and uploaded_cv:
        # Save the uploaded CV temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_cv.read())
            temp_file_path = temp_file.name

        # Load job description
        loader = WebBaseLoader(url)
        jd_page_content = loader.load()[-1]
        
        # Prompt for extracting job information
        prompt = PromptTemplate.from_template(
            """
            Your role here is to extract some key information from this job description
            and return them in plain JSON format.(this is very important. do not change the format)
            information to extract: [`overview`,`company_name`,`role_name`, `responsibilities`,`experience`, `hard_skills`,`soft_skills`, `application_deadline`, `contact_person`]

            Some helpful tips:
            if you get multiple values, separate them with a comma and put them in a list.
            if you are not able to extract any information, you assign "n/a" to that field. No preamble is needed. Do not include any other information oe verbose output.
            Be concise and to the point.
            overview is a short summary of the job. in 2/3 sentences.
            hard skills: any skills that is tool or technology related.
            soft skills: any skills that is not related hard skills.
            responsibilities: job specific responsibilities.
            casing of character should be standard each time.

            example output: [add curly braces]

                "overview": "This is a job overview",
                "company_name": "Company Name",
                "role_name": "Data Analyst",
                "experience": "2 years",
                "hard_skills": ["Python", "SQL"],
                "soft_skills": ["Teamwork", "Communication"],
                "responsibilities": "This is a responsibility",
                "application_deadline": "01/01/2022",
                "contact_person": [name, email, phone]
            
            This is a job description for a job.
            {page_content}
            """
        )

        chain = prompt | llm
        jd_info = chain.invoke(input={'page_content': jd_page_content})
        jd_json_parser = JsonOutputParser()
        jd_json = jd_json_parser.parse(jd_info.content)
        st.session_state.jd = jd_json

        # Load CV using PyPDFLoader
        pdf_loader = PyPDFLoader(temp_file_path)
        cv_pages = pdf_loader.load_and_split()
        clean_pages = [remove_extra_whitespace(page.page_content) for page in cv_pages]
        cv_content = "\n".join(clean_pages)
        st.session_state.cv = cv_content

        # Prompt for email generation
        find_relevancy = PromptTemplate.from_template(
            """ 
            Your task is to find the relevancy of the provided CV with the job information provided.
            Here is the cv: {CV}
            Here is the job information: {jd_info}

            and then write an email to the hiring mamager to express your interest in the job.
            and also mention the relevancy of your CV with the job description. 
            The email should be in a formal tone and should be concise and to the point.

            The email should be in English and have a professional formal tone.
            the email should have the following things :

            1. Greetings
            2. breif introduction of from the cv (for this keep it relevent to the job description)
            3. mention where the candidate can offer help to the company according to the job descriotion.
            4. express interest in the job.
            5. Questions about the job or the company.(add an appropriate question that you might have about the job or the company)
            6. closing remarks and thank you.

            Note that is is human to human communication. So, keep it professional and formal and humanly.
            """
        )

        chain = find_relevancy | llm
        email = chain.invoke(input={'CV': cv_content, 'jd_info': jd_json})
        st.session_state.email = email.content

    else:
        st.warning("Please provide both the job URL and upload your CV.")

# Display generated email
if st.session_state.email:
    st.header("Generated Email")
    st.text_area("Generated Email", st.session_state.email, height=300, key="email_display")
    if st.button("Copy to Clipboard"):
        st.code(st.session_state.email, language="text")
        st.success("Email copied to clipboard!")

st.title("Chat with the Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if user_input := st.chat_input("Ask about your CV, Job Description, Generated Email or anything in general!! "):
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    assistant_prompt = PromptTemplate.from_template(
        """
        User has provided the following information:
        - Email: {email}
        - CV: {cv}
        - Job Description: {jd}

        User Question: {question}

        Respond to the user's query based on the provided information.
        """
    )
    chain = assistant_prompt | llm
    response = chain.invoke(input={
        "email": st.session_state.email or "No email generated yet.",
        "cv": st.session_state.cv or "No CV uploaded yet.",
        "jd": st.session_state.jd or "No job description provided yet.",
        "question": user_input
    }).content

    # Character-by-character response display
    placeholder = st.empty()
    displayed_response = ""
    for char in response:
        displayed_response += char
        placeholder.markdown(displayed_response)
        time.sleep(0.03)  # Adjust speed as needed

    st.session_state.messages.append({"role": "assistant", "content": response})
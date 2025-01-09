# Personalized Email Generator with LLM feedback

This project is an AI-powered tool designed to generate personalized emails for job applications based on a given job description and a user's CV.

### Key Features
- Accepts a job description URL and a CV PDF to generate tailored emails.
- Extracts relevant information from job descriptions, such as company name, role, and responsibilities.
- Analyzes the user's CV for relevance to the job description.
- Generates professional, formal emails with clear structure and human-like tone.
- Includes an interactive chat assistant to answer queries based on the input provided.

### Tools Used
- **Streamlit**: For building the interactive and user-friendly web interface.
- **LangChain**: To create and manage conversational AI pipelines.
- **Python**: The core programming language for implementing functionality.
- **Groq Cloud**: For accessing LLMs

#### Screenshot
![Screenshot](ss.png)


## How to Use  

### Prerequisites  
1. Install [Docker](https://docs.docker.com/get-docker/).  
2. Ensure your system has an active internet connection.  

### Steps to Run the Application  

1. **Pull the Docker Image**  
   Run the following command to pull the Docker image from Docker Hub:  
   ```bash  
   docker pull shakib2022/streamlit-app:latest  

2. **Run the Docker Container**  
   - Use the command below to start the application:  
     ```bash  
     docker run -p 8501:8501 shakib2022/streamlit-app:latest  
     ```  
   - This command maps the container's port `8501` to your local machine.  

3. **Access the Application**  
   - Open your web browser.  
   - Navigate to `http://localhost:8501`.  
   - The application interface should load.  

4. **Upload a PDF**  
   - Click on the upload button to upload a PDF document.  
   - The app will process the document and prepare it for querying.  

5. **Query the Information**  
   - Use the chat interface to ask questions about the uploaded document.  
   - The system will provide responses based on the document's content.  
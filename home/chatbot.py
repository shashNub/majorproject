import google.generativeai as genai
from django.conf import settings

# Configure the Gemini API
genai.configure(api_key='AIzaSyCkSmzAt5ujn9Fji_cQ3KfXQVF8S7b0ZoE')

# Set up the model
model = genai.GenerativeModel('gemini-2.0-flash')

def get_gemini_response(prompt):
    context = """You are a helpful assistant specializing in Indian government jobs.
    For each job posting, provide a clear roadmap with these sections:
    
    1. Position Overview
    2. Important Dates & Deadlines
    3. Step-by-Step Application Process
    4. Required Documents
    5. Selection Process
    6. Tips for Success
    
    Use markdown formatting for clear presentation.
    Only include information that's available in the job details."""
    
    if any(key in prompt for key in ["Post Date:", "Name:", "Post Name:"]):
        job_specific_prompt = f"""Create a detailed roadmap for the following job opportunity:

        {prompt}

        Format your response as:
        
        **🎯 Position Overview**
        * Organization and role
        * Key responsibilities
        
        **🛣️ Application Roadmap**
        1. Initial Steps
        2. Document Preparation
        3. Application Submission
        4. Next Steps
        
        **📋 Required Documents**
        * List of essential documents
        * Additional requirements
        
        **🎯 Selection Process**
        * Stages of selection
        * Important tips
        
        Keep it concise and actionable."""
        
        full_prompt = f"{context}\n\n{job_specific_prompt}"
    else:
        full_prompt = f"{context}\n\nUser Question: {prompt}"

    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables (for OpenAI API key)
load_dotenv()

def get_chatbot_response(prompt):
    """Get a response from the chatbot using OpenAI API"""
    try:
        # Initialize the client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Create the chat completion
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful music teacher assistant. Provide concise, accurate information about music theory, instruments, and practice techniques."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        
        # Access the response content
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting response: {str(e)}"
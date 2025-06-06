import os
import tempfile
import librosa
import numpy as np
from midi2audio import FluidSynth
import pretty_midi
import openai
from dotenv import load_dotenv
import uuid
import logging
import json
from datetime import datetime
import time
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load environment variables (for OpenAI API key)
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chatbot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("music_chatbot")

# RAG Chatbot Functions
def initialize_rag_chatbot():
    """Initialize the RAG chatbot by loading the FAISS index and setting up the RAG chain."""
    logger.info("Initializing music education RAG chatbot")
    
    try:
        # Load the saved FAISS index
        logger.info("Loading FAISS index from disk")
        embeddings = OpenAIEmbeddings()
        db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        logger.info("FAISS index loaded successfully")
        
        # Set up retriever
        retriever = db.as_retriever(
            search_kwargs={"k": 3}  # Retrieve top 3 most relevant chunks
        )
        
        # Initialize LLM
        logger.info("Initializing ChatOpenAI model")
        llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
        logger.info("ChatOpenAI model initialized successfully")
        
        # Create custom prompt template
        template = """
        You are an AI assistant helping with music education questions.
        
        Use the following pieces of context to answer the question at the end.
        Include the page numbers from the source material in your response.
        
        {context}
        
        Question: {question}
        
        Answer (include page references in parentheses):
        """
        
        PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create RAG chain
        logger.info("Creating RetrievalQA chain")
        rag_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT}
        )
        logger.info("RetrievalQA chain created successfully")
        return rag_chain
    
    except Exception as e:
        logger.error(f"Error initializing RAG chatbot: {e}")
        return None

def get_rag_chatbot_response(prompt):
    """Get a response from the RAG chatbot using LangChain"""
    try:
        # Initialize RAG chain
        rag_chain = initialize_rag_chatbot()
        if rag_chain is None:
            return "Sorry, I couldn't initialize the advanced music knowledge system. Falling back to basic mode."
        
        # Get response from RAG chain
        start_time = time.time()
        logger.info(f"Processing query: '{prompt}'")
        
        response = rag_chain.invoke(prompt)
        
        # Extract the answer
        if isinstance(response, dict) and "result" in response:
            answer = response["result"]
        else:
            answer = str(response)
        
        # Log completion
        end_time = time.time()
        logger.info(f"Query processed in {end_time - start_time:.2f} seconds")
        
        return answer
    
    except Exception as e:
        logger.error(f"Error getting RAG response: {e}")
        return f"Error getting response: {str(e)}"

def get_chatbot_response(prompt):
    """Get a response from the chatbot using OpenAI API"""
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful music teacher assistant. Provide concise, accurate information about music theory, instruments, and practice techniques."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting response: {str(e)}"

# Import your existing conversion functions
from audio_to_midi import convert_audio_to_midi
from sheet_music import generate_sheet_music

# Flask implementation
from flask import Flask, render_template, request, jsonify
import os
import tempfile
from werkzeug.utils import secure_filename

# Make sure this is after the Flask app is created
app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file and file.filename.endswith('.mp3'):
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            file.save(tmp_file.name)
            audio_path = tmp_file.name
        
        try:
            # Convert audio to MIDI using your existing function
            midi_path = convert_audio_to_midi(audio_path)
            
            # Generate sheet music
            xml_path, _ = generate_sheet_music(midi_path)
            
            # Get relative paths for the frontend
            midi_filename = os.path.basename(midi_path)
            xml_filename = os.path.basename(xml_path)
            
            return jsonify({
                'success': True,
                'midi_path': f'/static/midi/{midi_filename}',
                'xml_path': f'/static/xml/{xml_filename}'
            })
        except Exception as e:
            return jsonify({'error': str(e)})
        finally:
            # Clean up the temporary file
            os.unlink(audio_path)
    
    return jsonify({'error': 'Invalid file format'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    use_rag = data.get('use_rag', True)
    
    if not message:
        return jsonify({'error': 'No message provided'})
    
    try:
        # Get response based on selected mode
        if use_rag:
            response = get_rag_chatbot_response(message)
        else:
            response = get_chatbot_response(message)
        
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    data = request.json
    
    # Extract form data
    instrument = data.get('instrument', '')
    experience_level = data.get('experience_level', '')
    practice_time = data.get('practice_time', 30)
    goals = data.get('goals', [])
    
    try:
        # Generate learning plan using OpenAI
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Create prompt for learning plan
        prompt = f"""Create a personalized 4-week music learning plan for a student with the following profile:
        - Instrument: {instrument}
        - Experience Level: {experience_level}
        - Available Practice Time: {practice_time} minutes per day
        - Learning Goals: {', '.join(goals)}
        
        The plan should include:
        1. Weekly focus areas
        2. Daily practice routine with time allocation
        3. Recommended pieces or exercises
        4. Specific techniques to practice
        5. Progress tracking metrics
        
        Format the response in HTML with appropriate headings, lists, and sections.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional music teacher creating personalized learning plans. Format your response in HTML that can be directly inserted into a webpage."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500
        )
        
        plan_html = response.choices[0].message.content
        return jsonify({'plan': plan_html})
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=False)

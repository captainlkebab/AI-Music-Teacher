import logging
import time
import os
import uuid
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

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

def initialize_chatbot():
    """Initialize the chatbot by loading the FAISS index and setting up the RAG chain."""
    logger.info("Initializing music education chatbot")
    
    # Load environment variables
    logger.info("Loading environment variables")
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY not found in environment variables")
        raise ValueError("OPENAI_API_KEY not found. Please check your .env file.")
    
    # Load the saved FAISS index
    logger.info("Loading FAISS index from disk")
    # In the initialize_chatbot function:
    try:
        embeddings = OpenAIEmbeddings()
        db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        logger.info("FAISS index loaded successfully")
    except Exception as e:
        logger.error(f"Error loading FAISS index: {e}")
        raise
    
    # Set up retriever
    logger.info("Setting up retriever")
    retriever = db.as_retriever(
        search_kwargs={"k": 3}  # Retrieve top 3 most relevant chunks
    )
    
    # Initialize LLM
    logger.info("Initializing ChatOpenAI model")
    try:
        llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
        logger.info("ChatOpenAI model initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing ChatOpenAI model: {e}")
        raise
    
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
    try:
        rag_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT}
        )
        logger.info("RetrievalQA chain created successfully")
        return rag_chain
    except Exception as e:
        logger.error(f"Error creating RetrievalQA chain: {e}")
        raise

def save_user_question(user_id, question, answer=None):
    """Save user question with unique ID to a file."""
    # Create directory if it doesn't exist
    questions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_questions")
    if not os.path.exists(questions_dir):
        os.makedirs(questions_dir)
        logger.info(f"Created user questions directory: {questions_dir}")
    
    # Create a unique question ID
    question_id = str(uuid.uuid4())
    
    # Prepare question data
    question_data = {
        "question_id": question_id,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer
    }
    
    # Save to JSON file
    try:
        # Append to the user's questions file
        user_file = os.path.join(questions_dir, f"user_{user_id}.json")
        
        # Check if file exists and load existing data
        if os.path.exists(user_file):
            with open(user_file, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    # If file is corrupted, start fresh
                    existing_data = {"questions": []}
        else:
            existing_data = {"questions": []}
        
        # Add new question
        existing_data["questions"].append(question_data)
        
        # Write back to file
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved question with ID {question_id} for user {user_id}")
        return question_id
    
    except Exception as e:
        logger.error(f"Error saving user question: {e}")
        return None

def chat_loop(rag_chain):
    """Run an interactive chat loop with the user."""
    print("\n=== Music Education Assistant ===")
    print("Ask questions about music education or type 'exit' to quit.\n")
    
    # Generate a unique user ID for this session
    user_id = str(uuid.uuid4())
    logger.info(f"Starting new chat session with user ID: {user_id}")
    print(f"Your session ID: {user_id}")
    
    while True:
        # Get user input
        user_query = input("Your question: ")
        
        # Check for exit command
        if user_query.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye!")
            break
        
        # Skip empty queries
        if not user_query.strip():
            continue
        
        # Process the query
        start_time = time.time()
        logger.info(f"Processing query: '{user_query}'")
        
        try:
            # Get response from RAG chain
            response = rag_chain.invoke(user_query)
            
            # Extract the answer
            if isinstance(response, dict) and "result" in response:
                answer = response["result"]
            else:
                answer = str(response)
            
            # Save the user question and answer
            question_id = save_user_question(user_id, user_query, answer)
            
            # Print the answer
            print("\nAnswer:")
            print(answer)
            print(f"\nQuestion ID: {question_id}")
            print()
            
            # Log completion
            end_time = time.time()
            logger.info(f"Query processed in {end_time - start_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print(f"Sorry, I encountered an error: {e}")
            
            # Still save the question even if there was an error
            save_user_question(user_id, user_query, f"Error: {str(e)}")

if __name__ == "__main__":
    try:
        # Initialize the chatbot
        rag_chain = initialize_chatbot()
        
        # Start the chat loop
        chat_loop(rag_chain)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Error: {e}")
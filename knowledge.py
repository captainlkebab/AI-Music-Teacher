import fitz  # PyMuPDF
import logging
import time
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("knowledge_processing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("knowledge_processor")

# Start timing the process
start_time = time.time()
logger.info("Starting knowledge processing script")

# Load environment variables
logger.info("Loading environment variables")
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.error("OPENAI_API_KEY not found in environment variables")
    raise ValueError("OPENAI_API_KEY not found. Please check your .env file.")
logger.info("Environment variables loaded successfully")

# Open and read the PDF
pdf_path = "Books/music-theory.pdf"
logger.info(f"Opening PDF file: {pdf_path}")
try:
    doc = fitz.open(pdf_path)
    logger.info(f"PDF opened successfully. Document has {len(doc)} pages")
    
    logger.info("Extracting text from PDF")
    # Extract text with page numbers
    text_with_pages = []
    for page_num, page in enumerate(doc):
        page_text = page.get_text()
        # Add page reference to each chunk
        text_with_pages.append(f"[Page {page_num + 1}] {page_text}")
    
    text = "\n".join(text_with_pages)
    logger.info(f"Text extraction complete. Extracted {len(text)} characters")
except Exception as e:
    logger.error(f"Error opening or reading PDF: {e}")
    raise

# Split text into chunks
logger.info("Splitting text into chunks")
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_text(text)
logger.info(f"Text split into {len(chunks)} chunks")

# Create embeddings
logger.info("Initializing OpenAI embeddings")
try:
    embeddings = OpenAIEmbeddings()
    logger.info("OpenAI embeddings initialized successfully")
except Exception as e:
    logger.error(f"Error initializing OpenAI embeddings: {e}")
    raise

# Create vector store
logger.info("Creating FAISS vector store from text chunks")
try:
    db = FAISS.from_texts(chunks, embedding=embeddings)
    logger.info("FAISS vector store created successfully")
except Exception as e:
    logger.error(f"Error creating FAISS vector store: {e}")
    raise

# Save the vector store
logger.info("Saving FAISS index to disk")
try:
    db.save_local("faiss_index")
    logger.info("FAISS index saved successfully")
except Exception as e:
    logger.error(f"Error saving FAISS index: {e}")
    raise

# Set up retriever and LLM
logger.info("Setting up retriever from vector store")
retriever = db.as_retriever(
    search_kwargs={"k": 3}  # Retrieve top 3 most relevant chunks
)
logger.info("Retriever set up successfully")

logger.info("Initializing ChatOpenAI model")
try:
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    logger.info("ChatOpenAI model initialized successfully")
except Exception as e:
    logger.error(f"Error initializing ChatOpenAI model: {e}")
    raise

# Create RAG chain with custom prompt
logger.info("Creating RetrievalQA chain")
try:
    from langchain.prompts import PromptTemplate
    
    # Custom prompt that asks for source references
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
    
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    logger.info("RetrievalQA chain created successfully")
except Exception as e:
    logger.error(f"Error creating RetrievalQA chain: {e}")
    raise

# Run query
query = "How do I position my hands when starting to play?"
logger.info(f"Running query: '{query}'")
try:
    response = rag_chain.invoke(query)
    logger.info("Query completed successfully")
    logger.info(f"Response length: {len(str(response))} characters")
    
    # Extract the answer from the response
    if isinstance(response, dict) and "result" in response:
        answer = response["result"]
    else:
        answer = str(response)
    
    logger.info(f"Answer: {answer}")
except Exception as e:
    logger.error(f"Error running query: {e}")
    raise

# Print response
print(answer)

# Log execution time
end_time = time.time()
execution_time = end_time - start_time
logger.info(f"Script completed in {execution_time:.2f} seconds")

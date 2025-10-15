# run.py

import os
from dotenv import load_dotenv
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import chromadb

# =========== Load environment & Gemini ===========
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not set in .env")
genai.configure(api_key=api_key)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# =========== Settings ===========
CHROMA_DB_PATH = "./chroma_db_placement"
COLLECTION_NAME = "placement_documents"

# =========== Load embedding model ===========
print("🔄 Loading embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# =========== Load ChromaDB ===========
# =========== Load ChromaDB ===========
print("🔄 Loading ChromaDB...")
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

collection = None # Initialize collection to None
try:
    collection = client.get_collection(name=COLLECTION_NAME)
    print(f"✅ Loaded collection: {COLLECTION_NAME}")
    print(f"📊 Total chunks in database: {collection.count()}")
except Exception as e:
    print(f"❌ Error loading collection: {e}")
    print("⚠️ Please run preprocess.py first!")
    # We don't exit here anymore to allow the app to run and show the error message in the UI
    
# =========== Add this function! ===========
def get_database_status():
    """Checks the status of the ChromaDB connection and collection."""
    try:
        # The 'collection' variable is now accessible from the global scope
        if collection:
            return {
                "status": "ready",
                "total_chunks": collection.count(),
                "collection_name": COLLECTION_NAME
            }
        else:
            return {
                "status": "not_initialized",
                "total_chunks": 0,
                "collection_name": COLLECTION_NAME
            }
    except Exception as e:
        print(f"Error getting database status: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
# ============================================

# =========== Retrieve relevant documents ===========
def retrieve_documents(query, k=4):
    """Retrieve top k relevant documents from ChromaDB"""
    
    # Create embedding for query
    query_embedding = embedding_model.encode([query])[0].tolist()
    
    # Query ChromaDB - Increased k to 4 for better coverage of interview rounds
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )
    
    # Extract documents
    documents = results['documents'][0] if results['documents'] else []
    
    print(f"\n🔍 Retrieved {len(documents)} relevant chunks")
    
    return documents

# =========== Answer with Gemini ===========
def answer_with_gemini(query):
    """Retrieve context and generate answer using Gemini"""
    
    # Retrieve relevant documents (k=4 to cover multiple rounds)
    relevant_docs = retrieve_documents(query, k=4)
    print(relevant_docs)
    if not relevant_docs:
        print("\n⚠️ No relevant information found in the database.")
        print("💡 Answering based on general knowledge...\n")
        context = "No specific context available."
    else:
        context = "\n\n".join(relevant_docs)
    
    # Create prompt for Gemini
    prompt = f"""You are a helpful and professional placement assistance chatbot. Your role is to provide clear, accurate, and synthesized information about company placements, based only on the provided context.

Primary Directive: Present Variations
If the context provides multiple experiences or slightly different processes for the same company, your main goal is to clearly present the different possibilities mentioned.

Example: If one source mentions 3 interview rounds (Aptitude, Technical, HR) and another mentions 4 (Aptitude, Coding, Technical, HR), you should outline both potential paths. You might say, "The interview process can vary. It may consist of 4 rounds including an aptitude test, a coding round, a technical interview, and a final HR interview. In other cases, it might be 3 rounds including a coding round, a technical interview, and a final HR interview ."

Crucially, do not present these as conflicting experiences from different candidates. Simply state them as the possible variations in the company's process.

Core Instructions:

Answer from Context Only: Your knowledge is strictly limited to the information within the "Context from Placement Documents" section below.

Maintain Anonymity and Persona:

Do NOT mention the names of any individuals (e.g., candidates, students).

Do NOT mention that you are answering based on documents, context, or write-ups. Act as a knowledgeable placement assistant, not a document reader.

Provide Specific Details: When the information is available, provide specific details like company names, job roles, salary packages, and eligibility criteria.

Use Clear Formatting:

Use bullet points (•) for lists (like eligibility criteria or companies).

Use numbered lists for processes or sequential steps (like interview rounds).

Keep paragraphs short and easy to read.

Use bold text for emphasis on key terms like company names.

Handle Insufficient Information:

If the context does NOT contain the information needed to answer the question, you must clearly state: "I don't have sufficient information in the placement documents to answer this question."

Do NOT use external knowledge, make assumptions, or invent information.

Context from Placement Documents:
{context}

User Question:
{query}

Answer:
"""

    # Generate response
    response = model.generate_content(prompt)
    
    print("\n💡 Answer:\n")
    print(response.text)
    print("\n" + "="*60)
    return response.text
# =========== Main loop ===========
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 Placement Information Chatbot")
    print("="*60)
    print("Ask questions about placements, companies, eligibility, etc.")
    print("Type 'exit' to quit\n")
    
    while True:
        question = input("❓ Your question: ").strip()
        
        if question.lower() in ['exit', 'quit', 'q']:
            print("\n👋 Thanks for using the Placement Chatbot!")
            break
        
        if not question:
            print("⚠️ Please enter a question.\n")
            continue
        
        try:
            answer_with_gemini(question)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again with a different question.\n")
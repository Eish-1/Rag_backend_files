import os
from PyPDF2 import PdfReader
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import EmbeddingRetriever, PreProcessor
from haystack.pipelines import Pipeline
from flask import Flask, request, jsonify
import nltk

# Ensure NLTK data is downloaded
nltk.download("punkt")
nltk.download("punkt_tab")

# 1. Define paths and settings
PDF_ROOT_DIR = "./data"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

# 2. Extract text from PDFs
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

# 3. Process all PDFs
def process_pdfs(root_dir):
    documents = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                print(f"Processing: {pdf_path}")
                text = extract_text_from_pdf(pdf_path)
                documents.append({"content": text, "meta": {"source": pdf_path}})

    return documents

# 4. Simplified text splitting
def split_into_chunks(documents):
    processor = PreProcessor(
        clean_empty_lines=True,
        split_by="word",
        split_length=CHUNK_SIZE,
        split_overlap=CHUNK_OVERLAP,
        split_respect_sentence_boundary=False,  # Disable sentence splitting
    )
    return processor.process(documents)

# 5. Initialize FAISS Document Store
def get_clean_document_store():
    import time
    max_attempts = 3
    
    # Create directory if it doesn't exist
    os.makedirs("./faiss_data", exist_ok=True)
    db_path = "./faiss_data/faiss_document_store.db"
    
    for attempt in range(max_attempts):
        try:
            # Only try to remove files if they exist
            for file_path in [db_path, "./faiss_data/faiss_index", "./faiss_data/faiss_index.json"]:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"Successfully removed {file_path}")
                    except PermissionError:
                        print(f"Warning: Could not remove {file_path}. File might be in use.")
            
            # Create a fresh document store with the new path
            return FAISSDocumentStore(
                sql_url=f"sqlite:///{db_path}",
                embedding_dim=768,
                faiss_index_factory_str="HNSW32",
                return_embedding=True  # Important: Ensure embeddings are returned
            )
        except Exception as e:
            if attempt == max_attempts - 1:  # Last attempt
                print(f"Failed to initialize document store after {max_attempts} attempts. Error: {str(e)}")
                raise
            time.sleep(2)  # Wait before retrying
            
    raise Exception("Could not initialize document store after multiple attempts")

def cleanup_document_store(document_store):
    if document_store is not None:
        try:
            print("\nCleaning up document store...")
            document_store.save("./faiss_data/faiss_index")  # Save one last time
            document_store.session.close()
            print("Cleanup successful")
        except Exception as e:
            print(f"Error during cleanup: {e}")

# 7. Build the Pipeline
def build_rag_pipeline():
    if retriever is None:
        raise ValueError("Retriever not initialized")
    pipeline = Pipeline()
    pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
    return pipeline

# 8. Flask API
app = Flask(__name__)

@app.route("/query", methods=["POST"])
def query_documents():
    query = request.json.get("query", "")
    pipeline = build_rag_pipeline()
    results = pipeline.run(query=query, params={"Retriever": {"top_k": 3}})
    
    response = []
    for doc in results["documents"]:
        response.append({
            "text": doc.content,
            "source": doc.meta["source"],
            "score": doc.score
        })
    
    return jsonify({"results": response})

# 9. Run
if __name__ == "__main__":
        
    document_store = None
    retriever = None

    # Check if FAISS index already exists
    # First, modify the document store loading code:
    if os.path.exists("./faiss_data/faiss_document_store.db") and os.path.exists("./faiss_data/faiss_index"):  # Note: changed from faiss_index.json
        
        print("\n OLDER DOCUMENTS EXIST \n")

        # Add this before loading:
        print("\n")
        print("Checking files:")
        print(f"DB exists: {os.path.exists('./faiss_data/faiss_document_store.db')}")
        print(f"FAISS index exists: {os.path.exists('./faiss_data/faiss_index')}")
        print(f"JSON config exists: {os.path.exists('./faiss_data/faiss_index.json')}")
        print("\n")

        print("Loading existing FAISS index...")
        try:

            document_store = FAISSDocumentStore.load(
                index_path="./faiss_data/faiss_index",
                config_path="./faiss_data/faiss_index.json"  # if you saved a custom config
            )

            
            if document_store.get_embedding_count() == 0:
                print("No embeddings found, updating now...")
                document_store.update_embeddings(retriever)
            else:
                print(f"Embeddings already exist: {document_store.get_embedding_count()}")

            
            # Verify the number of documents and embeddings match
            num_docs = len(document_store.get_all_documents())
            print(f"Number of documents in store: {num_docs}")

            # Initialize retriever with loaded store
            retriever = EmbeddingRetriever(
                document_store=document_store,
                embedding_model=EMBEDDING_MODEL,
                model_format="sentence_transformers",
            )
            print("Successfully loaded existing index")

        except Exception as e:
            print(f"Error loading existing index: {e}")
            print("Will create new index...")
            document_store = None
    
    # Only create new embeddings if we couldn't load existing ones
    if document_store is None:
        try:

            print("Processing documents and creating new embeddings...")
            # Process PDFs
            raw_docs = process_pdfs(PDF_ROOT_DIR)
            chunks = split_into_chunks(raw_docs)
            
            # Initialize new document store
            document_store = get_clean_document_store()
            
            # Initialize retriever
            retriever = EmbeddingRetriever(
                document_store=document_store,
                embedding_model=EMBEDDING_MODEL,
                model_format="sentence_transformers",
            )
            
            # Write and update documents
            print("Writing documents...")
            document_store.write_documents(chunks)

            # After writing documents:
            print("\n")
            print(f"Documents written: {len(document_store.get_all_documents())}")
            print("\n")
            
            print("Creating embeddings...")
            document_store.update_embeddings(retriever)
            # document_store.save("faiss_document_store.db")

            print("\n")
            print(f"Documents with embeddings: {document_store.get_embedding_count()}")
            print("\n")
            
            # Save both the document store and the FAISS index
            print("Saving index...")
            os.makedirs("./faiss_data", exist_ok=True)

            # Save the FAISS index and DO NOT OVERRIDE SQL database together
            document_store.save(index_path="./faiss_data/faiss_index")

            # Add after saving:
            print("\n")
            print(f"Files in faiss_data directory:")
            print(os.listdir('./faiss_data'))
            print("\n")
            
        except Exception as e:
            print(f"Error during initialization: {e}")
            raise

    # Start the Flask server
    try:
        print("Starting Flask server...")
        app.run(port=5000, debug=False)  # Set debug=False to prevent reloading
    finally:
        cleanup_document_store(document_store)
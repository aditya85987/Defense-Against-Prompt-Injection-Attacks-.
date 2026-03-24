import os
import chromadb
from sentence_transformers import SentenceTransformer

def ingest():
    print("Loading medical guidelines...")
    file_path = os.path.join(os.getcwd(), "medical_guidelines.txt")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by double newlines into distinct protocols
    chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
    print(f"Loaded {len(chunks)} clinical protocols.")

    # Initialize ChromaDB Persistent Client
    db_path = os.path.join(os.getcwd(), "chroma_db")
    print(f"Initializing ChromaDB at {db_path}...")
    client = chromadb.PersistentClient(path=db_path)

    # Create collection
    collection = client.get_or_create_collection(name="clinical_protocols")

    # Load embedding model
    print("Loading sentence-transformers/all-MiniLM-L6-v2...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Embedding chunks...")
    embeddings = model.encode(chunks)

    # Prepare IDs
    ids = [f"protocol_{i}" for i in range(len(chunks))]

    print("Upserting to ChromaDB collection...")
    # Convert ndarray to list of lists for Chroma
    embeddings_list = embeddings.tolist()
    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings_list
    )

    print("Ingestion complete! Database ready at ./chroma_db")

if __name__ == "__main__":
    ingest()

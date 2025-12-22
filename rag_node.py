import os
from pathlib import Path
from dotenv import load_dotenv

# LangChain imports - these help us work with AI and documents
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings  # Updated import


# Load API keys from .env file
load_dotenv()


class SimpleRAG:

    def __init__(self, docs_folder="./docs"):
        """
        Initialize the RAG system

        Args:
            docs_folder: Folder containing your PDF files
        """
        self.docs_folder = Path(docs_folder)
        self.vector_store = None  # This will store our searchable documents

    def setup(self, verbose=True):
        
        if verbose:
            print("\n" + "="*60)
            print("STEP 1: Loading PDF Documents")
            print("="*60)

        # Check if folder exists
        if not self.docs_folder.exists():
            raise ValueError(f"Folder '{self.docs_folder}' not found!")

        # Find all PDF files
        pdf_files = list(self.docs_folder.glob("*.pdf"))

        if not pdf_files:
            raise ValueError(f"No PDF files found in '{self.docs_folder}'")

        if verbose:
            print(f"Found {len(pdf_files)} PDF files:")
            for pdf in pdf_files:
                print(f"  - {pdf.name}")

        # Load all PDFs
        all_pages = []
        for pdf_file in pdf_files:
            loader = PyPDFLoader(str(pdf_file))
            pages = loader.load()

            # Add filename to each page so we know where it came from
            for page in pages:
                page.metadata["source"] = pdf_file.name

            all_pages.extend(pages)

        if verbose:
            print(f"✓ Loaded {len(all_pages)} pages total")

            # STEP 2: Split documents into smaller chunks
            print("\n" + "="*60)
            print("STEP 2: Splitting into Chunks")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,      
            chunk_overlap=100,   
        )

        chunks = text_splitter.split_documents(all_pages)

        if verbose:
            print(f"✓ Created {len(chunks)} chunks")

            # STEP 3: Create embeddings and vector store
            print("\n" + "="*60)
            print("STEP 3: Creating Embeddings & Vector Store")
            print("="*60)
            print("Embeddings = Converting text to numbers that capture meaning")
            print("Vector Store = Database optimized for similarity search")
            print("\nThis may take a minute...")

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Create FAISS vector store - this makes searching super fast
        self.vector_store = FAISS.from_documents(
            documents=chunks,
            embedding=embeddings
        )

        if verbose:
            print(f" Vector store created with {len(chunks)} searchable chunks")
            print("\n" + "="*60)
            print("Setup Complete! Ready to answer questions.")
            print("="*60)

    def search(self, question, num_results=3):
        """
        Search for relevant document chunks
        
        Args:
            question: Your question
            num_results: How many relevant chunks to find
            
        Returns:
            List of relevant text chunks with their sources
        """
        if not self.vector_store:
            raise ValueError("Please run setup() first!")
        
        # Search for similar chunks
        results = self.vector_store.similarity_search(question, k=num_results)
        
        # Format results nicely
        formatted_results = []
        for i, doc in enumerate(results, 1):
            formatted_results.append({
                "rank": i,
                "content": doc.page_content,
                "source": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", "Unknown")
            })
        
        return formatted_results
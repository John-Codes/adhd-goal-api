import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

class MicroRAG:
    def __init__(self):
        self.index = None
    
    def read_cwd(self):
        """Find text files in current folder"""
        return [f for f in os.listdir('.') if f.endswith(('.txt', '.md', '.py')) and os.path.isfile(f)]
    
    def add_file(self, file_path):
        """Add single file to RAG"""
        docs = SimpleDirectoryReader(input_files=[file_path]).load_data()
        
        if self.index is None:
            self.index = VectorStoreIndex.from_documents(docs)
        else:
            for doc in docs:
                self.index.insert(doc)
        
        print(f"Added: {os.path.basename(file_path)}")
    
    def update_files(self, file_paths):
        """Update multiple files in RAG - only updates, no adds"""
        for file_path in file_paths:
            if os.path.exists(file_path):
                # Remove old content
                docs = SimpleDirectoryReader(input_files=[file_path]).load_data()
                for doc in docs:
                    self.index.delete_ref_doc(doc.doc_id)
                
                # Insert updated content
                for doc in docs:
                    self.index.insert(doc)
                
                print(f"Updated: {os.path.basename(file_path)}")

# Usage
rag = MicroRAG()

# Add files initially
for file in rag.read_cwd():
    rag.add_file(file)

# Update modified files
rag.update_files(["file1.txt", "file2.py"])
import PyPDF2

def read_pdf_in_chunks(pdf_path, chunk_size=500):
    """
    Reads a PDF, splits text into chunks for AI processing.
    chunk_size = approximate number of words per chunk
    """
    chunks = []
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + " "
    
    words = text.split()
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    
    return chunks

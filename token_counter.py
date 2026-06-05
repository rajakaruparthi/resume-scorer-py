import tiktoken
import PyPDF2
import os
from pathlib import Path


def convert_pdf_to_markdown(pdf_path: str) -> str:
    """
    Convert a PDF file to markdown text.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Markdown formatted text from the PDF
    """
    markdown_text = ""
    
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            markdown_text += f"## Page {page_num + 1}\n\n{text}\n\n"
    
    return markdown_text


def read_file_content(file_path: str) -> str:
    """
    Read file content and convert to text if PDF.
    
    Args:
        file_path: Path to the file (PDF or text-based)
        
    Returns:
        Text content of the file
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file type is not supported
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_extension = Path(file_path).suffix.lower()
    
    if file_extension == '.pdf':
        print(f"Converting PDF to markdown: {file_path}")
        content = convert_pdf_to_markdown(file_path)
    elif file_extension in ['.txt', '.md', '.markdown']:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    return content


def count_tokens(text: str) -> int:
    """
    Count the number of tokens in the given text using GPT-3.5 tokenizer.
    
    Args:
        text: The text to count tokens for
        
    Returns:
        Total number of tokens
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    return len(tokens)


def get_file_token_count(file_path: str) -> dict:
    """
    Get the total token count for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file info and token count
    """
    content = read_file_content(file_path)
    token_count = count_tokens(content)
    
    return {
        "file_path": file_path,
        "file_name": os.path.basename(file_path),
        "token_count": token_count,
        "content_preview": content[:200] + "..." if len(content) > 200 else content,
        "content": content
    }


def save_markdown_file(content: str, output_path: str = None) -> str:
    """
    Save markdown content to a file.
    
    Args:
        content: The markdown content to save
        output_path: Path where to save the file. If None, creates in current directory.
        
    Returns:
        Path to the created markdown file
    """
    if output_path is None:
        output_path = "output.md"
    
    # Create directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as md_file:
        md_file.write(content)
    
    print(f"Markdown file created: {output_path}")
    return output_path


if __name__ == "__main__":
    # Example usage
    import sys

    file_path = "/Users/rajakaruparthi/Desktop/raja_k.pdf"
    result = get_file_token_count(file_path)
    
    print(f"\n{'='*50}")
    print(f"File: {result['file_name']}")
    print(f"Total Tokens: {result['token_count']}")
    print(f"{'='*50}")
    print(f"Preview:\n{result['content_preview']}")
    print(f"{'='*50}\n")
    
    # Save markdown file
    output_md_path = "resume_output.md"
    save_markdown_file(result['content'], output_md_path)


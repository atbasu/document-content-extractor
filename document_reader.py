import email
import fitz
import docx


def read_document(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()

    if file_path.endswith('.pdf'):
        pdf_reader = fitz.open(stream=content)
        num_pages = pdf_reader.page_count
        text = ''
        for i in range(num_pages):
            page = pdf_reader[i]
            text += page.get_text()
        return text
    elif file_path.endswith('.txt'):
        return content.decode('utf-8')
    elif file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return text
    elif file_path.endswith('.eml'):
        msg = email.message_from_bytes(content)
        text = ''
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                text += part.get_payload()
        return text
    else:
        raise ValueError('Unsupported file type')
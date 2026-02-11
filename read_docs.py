#!/usr/bin/env python3
import os
from pathlib import Path

def read_docx_content(file_path):
    """读取DOCX文件内容"""
    try:
        import docx
        doc = docx.Document(file_path)
        content = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                content.append(paragraph.text)
        return '\n'.join(content)
    except Exception as e:
        return f"读取DOCX文件失败: {str(e)}"

def read_pdf_content(file_path):
    """读取PDF文件内容"""
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            content = []
            for page in pdf_reader.pages:
                content.append(page.extract_text())
            return '\n'.join(content)
    except Exception as e:
        return f"读取PDF文件失败: {str(e)}"

def main():
    doc_dir = Path("/Users/jialei/code/voice-translation-web/doc")
    
    print("=== 文档内容分析 ===\n")
    
    # 读取DOCX文件
    docx_file = doc_dir / "语音对话Web应用开发.docx"
    if docx_file.exists():
        print(f"📄 {docx_file.name}:")
        content = read_docx_content(docx_file)
        print(content[:1000] + "..." if len(content) > 1000 else content)
        print("\n" + "="*50 + "\n")
    
    # 读取PDF文件
    pdf_files = [
        "Makawai 实时语音翻译服务API-2.pdf",
        "实时语音翻译｜TEXT-Real-Time Voice Translation API-2.pdf"
    ]
    
    for pdf_file in pdf_files:
        pdf_path = doc_dir / pdf_file
        if pdf_path.exists():
            print(f"📄 {pdf_file}:")
            content = read_pdf_content(pdf_path)
            print(content[:1000] + "..." if len(content) > 1000 else content)
            print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader, PdfWriter
from docx import Document
from PyPDF2 import PdfWriter, PdfReader
from docx import Document

# Инициализация приложения
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}

# Проверка расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Главная страница
@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

# Загрузка файла
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('index'))
    else:
        return "Invalid file type. Only PDF and DOCX are allowed."


# Отображение файла
@app.route('/view/<filename>')
def view_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Подписание документов
@app.route('/sign/<filename>', methods=['POST'])
def sign_file(filename):
    if '.' in filename:
        ext = filename.rsplit('.', 1)[1].lower()
    else:
        return "Invalid file: no extension found"

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    signature = "Admin Signature"

    if ext == 'pdf':
        signed_file = sign_pdf(file_path, signature)
    elif ext == 'docx':
        signed_file = sign_docx(file_path, signature)
    else:
        return "Unsupported file type"
    
    return redirect(url_for('index'))

# Подпись PDF
def sign_pdf(file_path, signature):
    reader = PdfReader(file_path)
    writer = PdfWriter()

    for page in reader.pages:
        page.add_text_annotation(50, 50, 200, 100, signature)
        writer.add_page(page)

    output_path = file_path.replace('.pdf', '_signed.pdf')
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)

    return output_path

# Подпись DOCX
def sign_docx(file_path, signature):
    doc = Document(file_path)
    doc.add_paragraph(signature)

    output_path = file_path.replace('.docx', '_signed.docx')
    doc.save(output_path)
    return output_path

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return redirect(url_for('index'))
    else:
        return f"File {filename} not found", 404


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

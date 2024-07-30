from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.conf import settings
from django.core.files import File
from PIL import Image
import pytesseract
from docx import Document

def convert_image_to_doc(image_path, output_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='por')
    doc = Document()
    doc.add_paragraph(text)
    doc.save(output_path)

def Image_to_doc(request):
    if request.method == 'POST' and request.FILES['image']:
        uploaded_image = request.FILES['image']
        fs = FileSystemStorage()
        image_path = fs.save(uploaded_image.name, uploaded_image)

        # Define o caminho de saída para o documento .docx
        output_path = settings.MEDIA_ROOT / 'output.docx'

        # Chama a função para converter a imagem em um documento .docx
        convert_image_to_doc(image_path, output_path)

        # Retorna o documento .docx para o usuário
        with open(output_path, 'rb') as docx_file:
            response = HttpResponse(File(docx_file), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename="{output_path.name}"'
            return response

    return render(request, 'Escola/inicio.html', {'conteudo_page':  "imagem-docx"})

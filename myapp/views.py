from django.shortcuts import render

# Create your views here.
from http.client import HTTPResponse
import zipfile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.core.files.storage import default_storage

import PyPDF2
import os

from File_Compressor_Project import settings

# Create your views here.
@csrf_exempt
def home(request):
    return HttpResponse("Hello")

# Function to split the PDF
def split_pdf(pdf_path, output_folder):
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            split_files = []
            for i in range(len(reader.pages)):
                writer = PyPDF2.PdfWriter()
                writer.add_page(reader.pages[i])

                # Save each page as a separate PDF
                output_filename = os.path.join(output_folder, f"page_{i + 1}.pdf")
                with open(output_filename, 'wb') as output_pdf:
                    writer.write(output_pdf)
                split_files.append(output_filename)
        return split_files

@csrf_exempt
def splitPDF(request):
        # Access the uploaded file
        if request.method == 'POST':
            uploaded_file = request.FILES.get('file')

            if not uploaded_file:
                return JsonResponse({"error": "No file provided"}, status=400)

            temp_pdf_path = default_storage.save(uploaded_file.name, uploaded_file)
            temp_pdf_full_path = default_storage.path(temp_pdf_path)
            output_folder = os.path.join(settings.MEDIA_ROOT, "split_pdfs")
            os.makedirs(output_folder, exist_ok=True)

            split_files = split_pdf(temp_pdf_full_path, output_folder)
            zip_filename = "split_pdfs.zip"
            zip_filepath = os.path.join(output_folder, zip_filename)
            with zipfile.ZipFile(zip_filepath, 'w') as zipf:
                for file in split_files:
                    zipf.write(file, os.path.basename(file))
            for file in split_files:
                os.remove(file)

            # Return the zip file as a response
            try:
                with open(zip_filepath, 'rb') as zipf:
                    response = HttpResponse(zipf.read(), content_type='application/zip')
                    response['Content-Disposition'] = f'attachment; filename={zip_filename}'
                    return response
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def merge_pdfs(pdf_files):
        # Initialize PdfMerger
        merger = PyPDF2.PdfMerger()

        # Append each uploaded PDF file
        for pdf in pdf_files:
            merger.append(pdf)

        # Create the merged PDF in memory
        output_filename = 'merged_output.pdf'
        output_path = default_storage.path(output_filename)
        with open(output_path, 'wb') as output_pdf:
            merger.write(output_pdf)

        return output_path

@csrf_exempt
def mergePDF(request):
    if request.method == 'POST':
        pdf_files = request.FILES.getlist('files')
        if not pdf_files:
            return JsonResponse({"error": "No files provided"}, status=400)

            # Merge the PDF files
        try:
            merged_pdf_path = merge_pdfs(pdf_files)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

            # Return the merged PDF as a downloadable response
        with open(merged_pdf_path, 'rb') as merged_pdf:
            response = HttpResponse(merged_pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="merged_output.pdf"'
            return response

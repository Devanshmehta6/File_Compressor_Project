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

# Define the path to your PDF file and output folder
        # pdf_path = '/content/sample_data/page_2.pdf'  # Ensure this file is uploaded in the same directory
        # output_folder = '/content/sample_data/Test'  # Folder where you want to save the split pages

        # # Ensure the output folder exists
        # if not os.path.exists(output_folder):
        #     os.makedirs(output_folder)

        # # Split the PDF file
        # split_pdf(pdf_path, output_folder)

        # # Check if the files are created
        # print("Split PDFs:")
        # print(os.listdir(output_folder))  # List files in the output folder

        # # List of split PDFs to merge from the output folder
        # pdf_list = [f"{output_folder}/page_{i}.pdf" for i in range(1, len(os.listdir(output_folder)) + 1)]

        # # Define the name of the output merged file
        # output_filename = 'merged_output.pdf'

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
            with open(zip_filepath, 'rb') as zipf:
                response = HttpResponse(zipf.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename={zip_filename}'
            return response


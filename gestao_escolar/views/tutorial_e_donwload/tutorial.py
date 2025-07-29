from django.http import FileResponse
import os


def abri_tutorial (request):
    file_tutorial = os.path.join('media/tutorial', 'admin.pdf')
    return FileResponse(open(file_tutorial, 'rb'), content_type = 'application/pdf')
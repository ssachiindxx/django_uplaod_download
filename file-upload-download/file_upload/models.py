from django.db import models
import os
import uuid


def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
    return os.path.join("files", filename)


class File(models.Model):
    
    file = models.FileField(upload_to=user_directory_path, null=True)

class CsvFile(models.Model):
    
    file = models.FileField(upload_to='csv/', null=True)
    year = models.CharField(max_length=20)
    value = models.CharField(max_length=20)
    search_value = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)


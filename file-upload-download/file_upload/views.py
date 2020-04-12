from django.shortcuts import render, redirect
from .models import File, CsvFile
from .forms import FileUploadForm, CsvUploadForm
import os
import uuid
import re
import pdfplumber
import pandas as pd
from collections import namedtuple
import csv


# Show file list
def file_list(request):
    files = CsvFile.objects.all().order_by("id").last()
    context = {'files': files.file, 'year': files.year, 'value': files.value, 'search_value': files.search_value}
    return render(request, 'file_upload/file_list.html', context)


def file_upload(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # get cleaned data
            raw_file = form.cleaned_data.get("file")
            year = form.cleaned_data.get("year")
            value = form.cleaned_data.get("value")
            new_file = File()
            new_file.file = handle_uploaded_file(raw_file)           
            new_file.save()
            file_url = convert_to_csv_upload(year, value)
            csv_file_object = CsvFile.objects.create(file = file_url[0], year = year, value = value, search_value = file_url[1])
            csv_file_object.save()
            return redirect("/file/")
    else:
        form = FileUploadForm()

    return render(request, 'file_upload/upload_form.html', {'form': form,
                                                            'heading': 'Data Parsing'})


def handle_uploaded_file(file):
    ext = file.name.split('.')[-1]
    file_name = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
    file_path = os.path.join('files', file_name)
    absolute_file_path = os.path.join('media', 'files', file_name)
    
    directory = os.path.dirname(absolute_file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(absolute_file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return file_path

def convert_to_csv_upload(year, value):
    search_value = None
    pdf = File.objects.latest('id')
    Inv = namedtuple('Inv', 'Particulars part_2015 part_2016 Particulars_next_col next_col_2015 next_col_2016')
    #regex to match pattern  
    rgx=re.compile(r'^(\D+)?.*?(\d{0,6}\.\d{2}).*?(\d{0,6}\.\d{2}).*?(\D+\.*?)?.*?(\d{0,8}\.\d{2})?\s*(\d{0,8}\.\d{2})?.*?')
    lines = []
    with pdfplumber.open(pdf.file.path) as pdf:
        pages = pdf.pages
        for page in pdf.pages:
            text = page.extract_text()
            for line in text.split('\n'):
                comp  = rgx.search(line)           
                if comp and 'Trading' not in line:   
                    lines.append(Inv(comp.group(1), comp.group(2), comp.group(3), comp.group(4), comp.group(5) , comp.group(6)))  
    file_name = 'BalSheet.csv'
    file_path = os.path.join('csv', 'BalSheet.csv')

    absolute_file_path = os.path.join('media', 'csv', file_name)
    directory = os.path.dirname(absolute_file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    df = pd.DataFrame(lines)

    df1 = df.loc[:,'Particulars': 'part_2016']
    df2 = df.loc[:,'Particulars_next_col': 'next_col_2016']
    
    df1_list = [x.strip(' ') for x in df1.Particulars.values]
    df2_list = [x.strip(' ') for x in df2.Particulars_next_col.values]
    year_for_df1 = 'part_'+year
    year_for_df2 = 'next_col_'+year 

    if value in df1_list and year_for_df1 in df1.columns:      
        search_value = df1.loc[df1['Particulars'].str.contains(value), year_for_df1].values[0]
    
    elif value in df2_list and year_for_df2 in df2.columns:
        search_value = df2.loc[df2['Particulars_next_col'].str.contains(value), year_for_df2].values[0]

    df.rename(columns={'part_2015': '2015', 'part_2016': '2016','Particulars_next_col': 'Particulars', 'next_col_2015': '2015', 'next_col_2016': '2016'}, inplace=True)   
    df.to_csv(absolute_file_path,index = False)
    return file_path, search_value

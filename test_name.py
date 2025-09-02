import io
from urllib.request import Request, urlopen
from pyresparser import ResumeParser

def get_remote_data(url):
    try:
        print(f'Extracting data from: {url}')
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        _file = io.BytesIO(webpage)
        _file.name = url.split('/')[-1]
        return ResumeParser(_file).get_extracted_data()
    except Exception as e:
        return f'Error fetching file: {e}'

def get_local_data(file_path):
    return ResumeParser(file_path).get_extracted_data()

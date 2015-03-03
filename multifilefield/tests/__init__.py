import os, shutil, tempfile
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from multifilefield.models import UploadedFile



TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), 'files')
TEMP_FILES_DIR = tempfile.mkdtemp(dir=os.path.dirname(__file__))



class TestStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        super(TestStorage, self).__init__(*args, **kwargs)

        self.location = TEMP_FILES_DIR
        self.base_url = '/files/'



def make_files():
    if not os.access(TEMP_FILES_DIR, os.F_OK):
        os.makedirs(TEMP_FILES_DIR)

    for filename in os.listdir(TEST_FILES_DIR):
        src = os.path.join(TEST_FILES_DIR, filename)
        dest = os.path.join(TEMP_FILES_DIR, filename)
        shutil.copyfile(src, dest)

    tmp_files = [os.path.join(TEMP_FILES_DIR, filename) for filename in os.listdir(TEMP_FILES_DIR)]
    bulk = [UploadedFile(upload=tmp_file) for tmp_file in tmp_files]
    UploadedFile.objects.bulk_create(bulk)



def get_files():
    files = []
    for filename in os.listdir(TEMP_FILES_DIR):
        pth = os.path.join(TEMP_FILES_DIR, filename)
        with open(pth) as f:
            files.append(File(f))

    return files



def remove_files():
    shutil.rmtree(TEMP_FILES_DIR)

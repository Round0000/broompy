import os
import math
import time
import datetime
import shutil
from pathlib import Path
import cv2
import textract
from pypdf import PdfReader as pdf


extensions = {
    "image": [".jpg", '.JPG', ".jpeg", '.JPEG', ".png", ".gif", ".bmp", ".tiff",".webp",".ico",".raw",".heif",".bat",".indd"],
    "document": [".doc", ".docx", ".pdf", ".txt", ".rtf", ".odt", ".xls",".xlsx", ".ppt", ".pptx", ".csv", ".pages", ".key", ".numbers", ".txt", ".md", ".html", ".epub"],
    "audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".wma", ".m4a", ".aiff",".alac",".ape",".dsd",".dff",".dsf",".mp2",".amr",".au",".ra",".wv"],
    "video": [".mp4", ".mkv", ".avi", ".flv", ".wmv", ".mov", ".mpg", ".mpeg", ".3gp", ".m4v", ".webm", ".ogg", ".m2ts",".ts",".mts",".hevc",".vp9",".vp8",".asf",".rm",".swf",".drc",".gifv",".m2v",".mxf",".roq",".nsv"],
    "archive": [".zip", ".rar", ".7z", ".tar", ".gz", ".tgz", ".bz2",".xz",".lzma",".arj",".cab",".chm",".deb",".dmg",".iso",".lzh",".msi",".rpm",".udf",".wim",".xar"]
}

icons = {
    "image": "📸 - ",
    "document": "📄 - ",
    "audio": "🎵 - ",
    "video": "🎬 - ",
    "archive": "📚 - ",
    "folder": "📂 - ",
    "undefined": "🔹 - "
}

to_ignore = ['_to_be_kept', '_to_be_deleted', '.vscode', 'main.py', 'broom.py']

def manage(file):
    # Check file extension
    ext = Path(file).suffix
    type = 'undefined'
    if ext in extensions["image"]:
        type = 'image'
    elif ext in extensions["document"]:
        type = 'document'
    elif ext in extensions["audio"]:
        type = 'audio'
    elif ext in extensions["video"]:
        type = 'video'
    elif ext in extensions["archive"]:
        type = 'archive'
    elif os.path.isdir(file):
        type = 'folder'
    
    # Print file details
    size = os.path.getsize(file)
    if size < 999999:
        size = f"{math.ceil(size / 1000)} Ko"
    else:
        size = f"{math.ceil(size / 1000000)} Mo"


    date = time.ctime(os.path.getmtime(file))
    date = datetime.datetime.strptime(date, "%a %b %d %H:%M:%S %Y")
    date = date.strftime('%Y-%m-%d')
    
    print(f"\n{icons[type]} \033[93m\033[1m{file}\033[0m ~ {size} ({date})")

    # Actions
    def take_action(file):
        action = input('❔ \033[94mDelete, Look, Open, Keep, or Enter to skip :\033[0m    ')
        if action == 'd':
            shutil.move(file, '_to_be_deleted/' + file)
        elif action == 'k':
            shutil.move(file, '_to_be_kept/' + file)
        elif action == 'o':
            os.startfile(file)
            take_action(file)
        elif action == 'l':
            if type == 'folder':
                print('     folder contents: ', os.listdir(file))
            elif type == 'image' and ext != '.gif':
                shutil.copy(file, '_temp_image_file')
                img = cv2.imread('_temp_image_file', cv2.IMREAD_ANYCOLOR)
                display = True
                while display:
                    cv2.imshow('- Broom -', img)
                    cv2.setWindowProperty('- Broom -', cv2.WND_PROP_TOPMOST, 1)
                    cv2.waitKey(1500)
                    cv2.destroyAllWindows()
                    display = False
                    os.remove('_temp_image_file')
            elif type == 'document':
                if ext in ['.txt', '.xlsx', '.doc', '.docx', '.htm', '.html', '.csv']:
                    doc = textract.process(file)
                    string = doc.decode('utf8')
                    string = string.replace('\n\n', '\n')
                    print(string[:128], '[...]')
                elif ext == '.pdf':
                    doc = pdf(file)
                    string = doc.pages[0].extract_text()
                    print(string[:128], '[...]')
                else:
                    print('No preview available...')
            take_action(file)
    take_action(file)


# Main broom function
def broom():
    # Prepare temp folder and file list
    dir_files = os.listdir()

    if not "_to_be_deleted" in dir_files:
        os.mkdir("_to_be_deleted")

    if not "_to_be_kept" in dir_files:
        os.mkdir("_to_be_kept")

    for file in to_ignore:
        if file in dir_files:
            dir_files.remove(file)

    # Start brooming
    print('--- Starting brooming ---')

    for file in dir_files:
        manage(file)
            
    # Final actions
    print('\n           🧹 FOLDER HAS BEEN BROOMED 🧹')
    destroy = input('           ❗ Would you like to destroy broomed files ? y/n  ')
    if destroy == 'y':
        shutil.rmtree(os.path.join('_to_be_deleted'))

        print('\n           🧹 BROOMED FILES WERE DELETED 🧹')
    rebroom = input('           ❔ Would you like to Rebroom the folder ? y/n  ')
    if rebroom == 'y':
        broom()
        

# Initial function call
broom()


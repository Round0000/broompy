import os
import time
import datetime
import shutil
from pathlib import Path
import cv2
import textract
import csv
import pandas as pd
from pypdf import PdfReader as pdf
from tabulate import tabulate
from decimal import Decimal


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
    "misc": "🔹 - "
}

to_ignore = ['_to_be_kept', '_to_be_deleted', '.vscode', 'main.py', 'broom.py', '.git']

# UTILITIES
def get_formatted_size(size):
    if size == 0:
        return '-'
    mo = Decimal(size/(1024**2)).quantize(Decimal('0.0'))
    if mo > 999:
        return f"{Decimal(size/(1024**3)).quantize(Decimal('0.0'))} Go"
    elif mo < 1:
        return f"{Decimal(size/(1024)).quantize(Decimal('0.0'))} Ko"
    return f"{mo} Mo"


def get_folder_size(folder_path):
    total = 0
    with os.scandir(folder_path) as folder:
        for entry in folder:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_folder_size(entry.path)
    return total

# MAIN FUNCTIONS
def look_image(file):
    shutil.copy(file, '_temp_image_file')
    cv2.namedWindow('- Broom -', cv2.WINDOW_NORMAL)
    img = cv2.imread('_temp_image_file', cv2.IMREAD_ANYCOLOR)
    display = True
    while display:
        cv2.imshow('- Broom -', img)
        cv2.setWindowProperty('- Broom -', cv2.WND_PROP_TOPMOST, 1)
        cv2.waitKey(1500)
        cv2.destroyAllWindows()
        display = False
        os.remove('_temp_image_file')

def look_csv(file):
    with open(file, newline='', encoding="utf-8") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        table = []
        for i, row in enumerate(spamreader):
            if i < 6:
                table.append(row)
        print(tabulate(table))
        print('...\n')

def look_doc(file):
    doc = textract.process(file)
    string = doc.decode('utf8')
    string = string.replace('\n\n', '\n')
    print(string[:256], '[...]')

def look_pdf(file):
    doc = pdf(file)
    string = doc.pages[0].extract_text()
    print(string[:256], '[...]')

def manage(file):
    # Check file extension
    ext = Path(file).suffix
    type = 'misc'
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
    size = get_folder_size(file) if os.path.isdir(file) else os.path.getsize(file)
    formatted_size = get_formatted_size(size)
    date = time.ctime(os.path.getmtime(file))
    date = datetime.datetime.strptime(date, "%a %b %d %H:%M:%S %Y")
    date = date.strftime('%Y-%m-%d')
    
    print(f"\n{icons[type]} \033[93m\033[1m{file}\033[0m ~ {formatted_size} ({date})")

    # Actions
    def take_action(file):
        action = input('   ❔ \033[94m[Delete], [Look], [Open], [Keep], other key to skip :\033[0m    ')
        if action == 'd':
            shutil.move(file, '_to_be_deleted/' + file)
        elif action == 'k':
            shutil.move(file, '_to_be_kept/' + file)
        elif action == 'o':
            os.startfile(file)
            take_action(file)
        elif action == 'l':
            if type == 'folder':
                print('\033[95mfolder contents:\033[0m ', os.listdir(file))
            elif type == 'image' and ext != '.gif':
                look_image(file)
            elif type == 'document':
                if ext == '.csv':
                    look_csv(file)
                elif ext in ['.txt', '.xlsx', '.xls', '.doc', '.docx', '.htm', '.html']:
                    look_doc(file)
                elif ext == '.pdf':
                    look_pdf(file)
                else:
                    print('No preview available...')
            take_action(file)
    take_action(file)


# MAIN BROOMING PROCESS
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

    # Get folder stats
    folder_stats = { "image": 0, "document": 0, "audio": 0, "video": 0, "archive": 0, "folder": 0, "misc": 0 }
    total_size = 0
    for file in dir_files:
        file_size = os.path.getsize(file)
        ext = Path(file).suffix
        file_type = "misc"
        for type in extensions.keys():
            if ext in extensions[type]:
                file_type = type
        if os.path.isdir(file):
            file_type = "folder"
            file_size = get_folder_size(file)
        
        folder_stats[file_type] += file_size
        total_size += file_size
    sorted_stats = sorted(folder_stats.items(), key=lambda x:x[1], reverse = True)
    table = []
    for item in sorted_stats:
        type = item[0]
        table.append(['\033[93m' + type, get_formatted_size(item[1]) + '\033[0m'])
            
    print('\nTotal size in current folder:', get_formatted_size(total_size))
    print(tabulate(table))

    # Start brooming
    print(f"\n▶  Walking through files ({len(dir_files)} elements)...")

    for file in dir_files:
        manage(file)
            
    # Final actions
    print("\n    🧹 FOLDER HAS BEEN BROOMED 🧹")
    to_be_deleted_size = get_folder_size('_to_be_deleted')
    if to_be_deleted_size > 0:
        destroy = input(f"        ❗ Would you like to destroy broomed files {get_formatted_size(to_be_deleted_size)} ? y/n  ")
        if destroy == 'y':
            shutil.rmtree(os.path.join('_to_be_deleted'))
            print('\n           🧹 BROOMED FILES WERE DELETED 🧹')
    else:
        print("       No deleted files.")
    rebroom = input('\n        ❔ Would you like to Rebroom the folder ? y/n  ')
    if rebroom == 'y':
        broom()
        

# Initial function call
broom()


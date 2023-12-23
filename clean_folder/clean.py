import os
import sys
import shutil
from pathlib import Path

# dict file_types, key = file type, value = list of known extensions
file_types = {
    'audio': ['MP3', 'OGG', 'WAV', 'AMR'],
    'archives': ['ZIP', 'GZ', 'TAR'],
    'documents': ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
    'images': ['JPEG', 'PNG', 'JPG', 'SVG'],
    'video': ['AVI', 'MP4', 'MOV', 'MKV'],
    'others': []
}

transliterate_map = {
    # lowercase letters
    ord('а'): 'a', ord('б'): 'b', ord('в'): 'v', ord('г'): 'g', ord('д'): 'd',
    ord('е'): 'e', ord('ё'): 'e', ord('ж'): 'zh', ord('з'): 'z', ord('и'): 'i',
    ord('й'): 'y', ord('к'): 'k', ord('л'): 'l', ord('м'): 'm', ord('н'): 'n',
    ord('о'): 'o', ord('п'): 'p', ord('р'): 'r', ord('с'): 's', ord('т'): 't',
    ord('у'): 'u', ord('ф'): 'f', ord('х'): 'kh', ord('ц'): 'ts', ord('ч'): 'ch',
    ord('ш'): 'sh', ord('щ'): 'sch', ord('ъ'): '', ord('ы'): 'y',
    ord('ь'): '', ord('э'): 'e', ord('ю'): 'yu', ord('я'): 'ya',
    # uppercase letters
    ord('А'): 'A', ord('Б'): 'B', ord('В'): 'V', ord('Г'): 'G', ord('Д'): 'D',
    ord('Е'): 'E', ord('Ё'): 'E', ord('Ж'): 'Zh', ord('З'): 'Z', ord('И'): 'I',
    ord('Й'): 'Y', ord('К'): 'K', ord('Л'): 'L', ord('М'): 'M', ord('Н'): 'N',
    ord('О'): 'O', ord('П'): 'P', ord('Р'): 'R', ord('С'): 'S', ord('Т'): 'T',
    ord('У'): 'U', ord('Ф'): 'F', ord('Х'): 'Kh', ord('Ц'): 'Ts', ord('Ч'): 'Ch',
    ord('Ш'): 'Sh', ord('Щ'): 'Sch', ord('Ъ'): '', ord('Ы'): 'Y', ord('Ь'): '',
     ord('Э'): 'E', ord('Ю'): 'Yu', ord('Я'): 'Ya',
    # additional Ukrainian lowercase letters
    ord('ґ'): 'g', ord('є'): 'ye', ord('ї'): 'yi', ord('і'): 'i',
    # additional Ukrainian uppercase letters
    ord('Ґ'): 'G', ord('Є'): 'Ye', ord('Ї'): 'Yi', ord('І'): 'I',
}

# variables for collect results
files_by_type = {}
known_extensions = set()
unknown_extensions = set()

def check_directory_exist_and_permissions(path: str) -> tuple:
    '''
    Function for check path existence and read/write permissions 

    :param path: Path to folder
    :type path: string
    :return: boolean of check and comment if false
    :rtype: tuple
    '''
    if not os.path.exists(path):
        return False, f'Directory "{path}" not exist!'
    if not os.access(path, os.R_OK):
        return False, f"Script don't have permission to read from directory: {path}"
    if not os.access(path, os.W_OK):
        return False, f"Script don't have permission to write to directory: {path}"
    return True, None

def find_file_type(file: Path) -> str:
    '''
    Function to search for a file type 
    based on specified conditions from 
    the dictionary (file_types)

    :param file: Path object
    :type path: string
    :return: recognized file type or 'others'
    :rtype: string
    '''
    extension = file.name if file.name.startswith('.') else file.suffix[1:]
    finded_file_type = None

    for file_type, extensions in file_types.items():
        if extension.upper() in extensions:
            finded_file_type = file_type
            known_extensions.add(extension.upper())

    if finded_file_type is None:
        finded_file_type = 'others'
        if extension:
            unknown_extensions.add(extension.upper())

    if finded_file_type not in files_by_type:
        files_by_type.setdefault(finded_file_type, set()).add(normalize(file))
    else:
        files_by_type[finded_file_type].add(normalize(file))

    return finded_file_type

def normalize(file: Path, with_ext: bool = True) -> str:
    '''
    Function for transiliterate filename.
    - Cyrillic characters are converted. 
    - The Latin alphabet and numbers remain as is. 
    - The remaining characters are replaced with _
    - File extension does not change

    :param file: Path object
    :type path: Path object
    :param with_ext: default True - function return filename with extension
    :type with_ext: bool
    :return: Transliterated in latin string 
    :rtype: string
    '''
    # in Linux/Unix OS hidden files have name are startswith dot
    if file.name.startswith('.'):
        return file.name

    normalized_filename = ''
    filename = file.stem

    for char in filename:
        ord_char = ord(char)
        # english letters and digits added as is
        # english uppercase letters Unicode codes 65-90
        # english lowercase letters Unicode codes 97-122
        if char.isdigit() or \
            (65 <= ord_char <= 90) or \
            (97 <= ord_char <= 122):
            normalized_filename += char
        else:
            normalized_filename += transliterate_map.get(ord_char, '_')

    return normalized_filename if not with_ext else str(normalized_filename + file.suffix)

def sort(path: Path, target_dir: Path):
    '''
    Recursive function for sorting files 
    - File names are transliterated by function 'normalize'
    - Files are transferred to folders according to file type
    - Archives are unpacked into a folder 'archives' into the same name folder without extension
    - Broken archives are deleted

    :param path: directory for sort
    :type path: Path object
    '''

    for item in path.iterdir():
        if item.is_file():
            item_file_type = find_file_type(item)
            path_to_replace = target_dir.joinpath(item_file_type)
            path_to_replace.mkdir(exist_ok=True)
            if item_file_type == 'archives':
                try:
                    shutil.unpack_archive(
                        item.absolute(), target_dir.joinpath(
                            path_to_replace, normalize(item, with_ext=False)
                            ).as_posix()
                        )
                except shutil.ReadError:
                    print(f'Archive is broken: {item.absolute()}')
                finally:
                    item.unlink()
            else:
                item.replace(target_dir.joinpath(path_to_replace, normalize(item)))

        elif item.is_dir():
            # if that is work folder of script
            if item.name in file_types:
                continue
            sort(item, target_dir)

    if not any(path.iterdir()):
        path.rmdir()

def main():
    # Checking for right numbers of argument
    if len(sys.argv) == 2:
        path_to_dir = sys.argv[1]

        while True:
            valid, comment = check_directory_exist_and_permissions(path_to_dir)

            if valid:
                work_dir_path = Path(path_to_dir).absolute()
                sort(work_dir_path, work_dir_path)

                print(f'\nResult of sort directory: {work_dir_path}', end='\n\n')
                print(f'Known extensions: {", ".join(sorted(known_extensions))}', end='\n\n')
                print(f'Unknown extensions: {", ".join(sorted(unknown_extensions))}', end='\n\n')

                print('Files by type in target directory:')
                for file_category, files in files_by_type.items():
                    print(f'[{file_category}]:\n{", ".join(sorted(files))}', end='\n\n')

                break

            else:
                if path_to_dir == 'n':
                    sys.exit(0)
                else:
                    print('\n' + comment, end='\n\n')
                    path_to_dir = input('Enter the correct folder path or "n" to cancel: ')

    else:
        print('Please try again with correct syntax: "clean-folder path/to/dir"')
        # Exit code - incorrect inline arguments
        sys.exit(2)

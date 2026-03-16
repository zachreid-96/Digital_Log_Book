import os
import glob
import shutil

from datetime import datetime
from configs.config import convert_month_str, DirectoryManager

"""
Description: 
    wrapper for file move and rename processes
    checks if data and serial number are valid
    if valid
        calls move_file_success 
    if not valid
        calls move_file_warning
Args:
    file: file to be moved
    serial_number: None if not found || Valid serial number
    date: None if not found || Valid date
    brand: 'Inventory_Pages', 'Kyocera', 'HP', 'Canon'
"""

def file_manager_wrapper(file, serial_number, date, brand, manual_sort_list=None, flagged=False):

    if serial_number is not None and date is not None:
        move_file_success(file, serial_number, date, brand, manual_sort_list, flagged=False)

    elif brand == "Inventory" and date is not None:
        move_file_success(file, serial_number, date, brand, manual_sort_list, flagged=False)

    elif date is None or serial_number is None:

        move_file_warning(file, serial_number, date, brand, manual_sort_list, multiple=True)


"""
Description: 
    gets all files within the given folder that is passed
Args:
    path: path of folder that houses files that need processed
Returns:
    list of files
"""

def populate_files(path):
    files = []
    for file in glob.glob(f"{path}\\*.pdf"):
        files.append(file)

    return files


"""
Description: 
    moves and renames a file into a specific destination
    multiple is set to DEFAULT value
    will check if file_name already exists and renames to file_name_x (x=1,2,3,etc) and rechecks
    logs operation of move to destination and deletion of file in 'temp_path' and 'unsorted_path'
    if operation fails, calls move_file_warning
Args:
    file: file to be moved
    serial_number: None if not found || Valid serial number
    date: None if not found || Valid date
    brand: 'Inventory_Pages', 'Kyocera', 'HP', 'Canon'
    multiple=True: defaulted to True, not recommended to be changed
    manual_sort_list=None: multiprocess shared list for data collection on failed files
"""


def move_file_success(file, serial_number, date, brand, multiple=True, manual_sort_list=None, flagged=False):
    path_manager = DirectoryManager()
    logbook_path = path_manager.get_logbook_dir()
    inventory_page_path = path_manager.get_inventory_dir()
    unsorted_path = path_manager.get_unsorted_dir()
    logger = path_manager.get_logger()

    destination_folder = None
    new_filename = None

    if serial_number is not None and date is not None:
        destination_folder = rf"{logbook_path}\{brand}\{date.year}\{convert_month_str(date.month)}"
        os.makedirs(destination_folder, exist_ok=True)

        new_filename = f"{date.month}-{date.day}-{date.year}_{serial_number}"

    elif brand == "Inventory" and date is not None:
        destination_folder = rf"{inventory_page_path}\{date.year}\{convert_month_str(date.month)}"
        os.makedirs(destination_folder, exist_ok=True)

        new_filename = f"{date.month}-{date.day}-{date.year}_Inventory"

    if destination_folder is None and new_filename is None:
        move_file_warning(file, serial_number, date, brand, manual_sort_list, multiple=True)

    logged_filename = ''

    try:
        if multiple:
            if not os.path.exists(os.path.join(destination_folder, f"{new_filename}.pdf")):
                shutil.move(file, os.path.join(destination_folder, f"{new_filename}.pdf"))

                message = f"""RENAMED {file.split("\\")[-1]} to {new_filename}.pdf
                        \t MOVED {new_filename}.pdf to {destination_folder}
                        \t DELETED {file.split("\\")[-1]} in {unsorted_path}"""

                logger.info(message)
                logged_filename = os.path.join(destination_folder, f"{new_filename}.pdf")
            else:
                count = 1
                while True:
                    if not os.path.exists(os.path.join(destination_folder, f"{new_filename}_{count}.pdf")):
                        shutil.move(file, os.path.join(destination_folder, f"{new_filename}_{count}.pdf"))

                        message = f"""RENAMED {file.split("\\")[-1]} to {new_filename}_{count}.pdf
                                            \t MOVED {new_filename}.pdf_{count} to {destination_folder}
                                            \t DELETED {file.split("\\")[-1]} in {unsorted_path}"""

                        logger.info(message)
                        logged_filename = os.path.join(destination_folder, f"{new_filename}_{count}.pdf")
                        break
                    count += 1
        if not multiple:
            if not os.path.exists(os.path.join(destination_folder, f"{new_filename}.pdf")):
                shutil.move(file, os.path.join(destination_folder, f"{new_filename}.pdf"))

                message = f"""RENAMED {file.split("\\")[-1]} to {new_filename}.pdf
                        \t MOVED {new_filename}.pdf to {destination_folder}
                        \t DELETED {file.split("\\")[-1]} in {unsorted_path}"""

                logger.info(message)
                logged_filename = os.path.join(destination_folder, f"{new_filename}.pdf")

        if flagged:
            manual_sort_list.append({
                'file': logged_filename,
                'serial_num': serial_number,
                'date': date.strftime('%Y/%m/%d') if date else None,
                'brand': brand
            })

    except Exception as e:
        logger.warning(e)
        move_file_warning(file, serial_number, date, brand, manual_sort_list, multiple=True)


"""
Description: 
    moves and renames a file into a specific destination
    multiple is set to DEFAULT value
    will check if file_name already exists and renames to file_name_x (x=1,2,3,etc) and rechecks
    logs operation of move to destination and deletion of file in 'temp_path' and 'unsorted_path'
Args:
    file: file to be moved
    serial_number: None if not found || Valid serial number
    date: None if not found || Valid date
    brand: 'Inventory_Pages', 'Kyocera', 'HP', 'Canon'
    multiple=True: defaulted to True, not recommended to be changed
    manual_sort_list=None: multiprocess shared list for data collection on failed files 
"""


def move_file_warning(file, serial_number, date, brand, manual_sort_list, multiple=True):
    path_manager = DirectoryManager()
    unsorted_path = path_manager.get_unsorted_dir()
    manual_sort_path = path_manager.get_manual_sort_dir()
    logger = path_manager.get_logger()

    logged_filename = ''

    original_filename = file.split("\\")[-1][:-4]
    if multiple:
        if not os.path.exists(os.path.join(manual_sort_path, f"{original_filename}.pdf")):
            shutil.move(file, os.path.join(manual_sort_path, f"{original_filename}.pdf"))

            message = f"""UNABLE to parse DATE in document
                        \t MOVED {original_filename}.pdf to {manual_sort_path}
                        \t DELETED {file.split("\\")[-1]} in {unsorted_path}"""
            logger.error(message)
            logged_filename = os.path.join(manual_sort_path, f"{original_filename}.pdf")
        else:
            count = 1
            while True:
                if not os.path.exists(os.path.join(manual_sort_path, f"{original_filename}_{count}.pdf")):
                    shutil.move(file, os.path.join(manual_sort_path, f"{original_filename}_{count}.pdf"))

                    message = f"""UNABLE to parse DATE in document
                                \t MOVED {original_filename}.pdf to {manual_sort_path}
                                \t DELETED {file.split("\\")[-1]} in {unsorted_path}"""

                    logger.error(message)
                    break
                count += 1
                logged_filename = os.path.join(manual_sort_path, f"{original_filename}_{count}.pdf")
    if not multiple:
        if not os.path.exists(os.path.join(manual_sort_path, f"{original_filename}.pdf")):
            shutil.move(file, os.path.join(manual_sort_path, f"{original_filename}.pdf"))

            message = f"""UNABLE to parse DATE in document
                        \t MOVED {original_filename}.pdf to {manual_sort_path}
                        \t DELETED {file.split("\\")[-1]} in {unsorted_path}"""

            logger.error(message)
            logged_filename = os.path.join(manual_sort_path, f"{original_filename}.pdf")

    manual_sort_list.append({
        'file': logged_filename,
        'serial_num': serial_number,
        'date': date.strftime('%Y/%m/%d') if date else None,
        'brand': brand
    })

def format_submitted_date(old_date):

    try:
        date = datetime.strptime(old_date, '%Y/%m/%d')
        return date
    except ValueError:
        pass
    try:
        date = datetime.strptime(old_date, '%Y-%m-%d')
        return date
    except ValueError:
        pass
    try:
        date = datetime.strptime(old_date, '%m/%d/%Y')
        return date
    except ValueError:
        pass
    try:
        date = datetime.strptime(old_date, '%m-%d-%Y')
        return date
    except ValueError:
        pass

def move_file_manual_sort(dict_obj, multiple=True):

    path_manager = DirectoryManager()
    logbook_path = path_manager.get_logbook_dir()
    inventory_page_path = path_manager.get_inventory_dir()
    unsorted_path = path_manager.get_unsorted_dir()
    logger = path_manager.get_logger()

    serial_number = dict_obj['serial_num']
    date = format_submitted_date(dict_obj['date'])
    brand = dict_obj['brand']
    file = dict_obj['file']

    destination_folder = None
    new_filename = None

    if serial_number is not None and date is not None:
        destination_folder = rf"{logbook_path}\{brand}\{date.year}\{convert_month_str(date.month)}"
        os.makedirs(destination_folder, exist_ok=True)

        new_filename = f"{date.month}-{date.day}-{date.year}_{serial_number}"

    elif brand == "Inventory" and date is not None:
        destination_folder = rf"{inventory_page_path}\{date.year}\{convert_month_str(date.month)}"
        os.makedirs(destination_folder, exist_ok=True)

        new_filename = f"{date.month}-{date.day}-{date.year}_Inventory"

    if multiple:
        if not os.path.exists(os.path.join(destination_folder, f"{new_filename}.pdf")):
            shutil.move(file, os.path.join(destination_folder, f"{new_filename}.pdf"))

            message = f"""RENAMED {file.split("\\")[-1]} to {new_filename}.pdf
                    \t MOVED {new_filename}.pdf to {destination_folder}
                    \t DELETED {file.split("\\")[-1]} in {unsorted_path}"""

            dict_obj['new_file'] = os.path.join(destination_folder, f"{new_filename}.pdf")
            logger.info(message)
        else:
            count = 1
            while True:
                if not os.path.exists(os.path.join(destination_folder, f"{new_filename}_{count}.pdf")):
                    shutil.move(file, os.path.join(destination_folder, f"{new_filename}_{count}.pdf"))

                    message = f"""RENAMED {file.split("\\")[-1]} to {new_filename}_{count}.pdf
                                        \t MOVED {new_filename}.pdf_{count} to {destination_folder}
                                        \t DELETED {file.split("\\")[-1]} in {unsorted_path}"""

                    dict_obj['new_file'] = os.path.join(destination_folder, f"{new_filename}_{count}.pdf")
                    logger.info(message)
                    break
                count += 1
    if not multiple:
        if not os.path.exists(os.path.join(destination_folder, f"{new_filename}.pdf")):
            shutil.move(file, os.path.join(destination_folder, f"{new_filename}.pdf"))

            message = f"""RENAMED {file.split("\\")[-1]} to {new_filename}.pdf
                    \t MOVED {new_filename}.pdf to {destination_folder}
                    \t DELETED {file.split("\\")[-1]} in {unsorted_path}"""

            logger.info(message)

            dict_obj['new_file'] = os.path.join(destination_folder, f"{new_filename}.pdf")

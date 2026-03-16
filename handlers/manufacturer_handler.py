import re

from rapidfuzz import fuzz
from datetime import datetime
from ocr_processor import ocr_file
from file_manager import file_manager_wrapper

def clean_ocr_date_string(raw_str):
    return re.sub(r'(?<=\d)7(?=\d)', '/', raw_str)

def normalize_date(date_str):

    date_str = clean_ocr_date_string(date_str)
    match = re.match(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', date_str)
    if match:
        m, d, y = match.groups()
        return f"{int(m):02d}/{int(d):02d}/{y}"

    match_year_first = re.match(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_str)
    if match_year_first:
        y, m, d = match_year_first.groups()
        return f"{int(m):02d}/{int(d):02d}/{y}"

    match_short_year = re.match(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})', date_str)
    if match_short_year:
        m, d, y = match_short_year.groups()
        return f"{int(m):02d}/{int(d):02d}/20{y}"

    return None

def normalize_kyocera_serials(serial):

    removable_chars = ['¥']
    serial_arr = [char for char in serial if char not in removable_chars]

    if serial[:2] == "19":
        serial_arr[2] = "Z"

    normalized_serial = "".join(serial_arr)

    return normalized_serial

def fuzzy_subset(subset, data, threshold=80):

    match_count = 0
    confidence_target = len(subset) // 2
    for item, val in subset.items():
        if match_count > confidence_target:
            break
        for data_item in data:
            if fuzz.ratio(item.lower(), data_item.lower()) >= threshold:
                match_count += val
                break

    #with open('testing.txt', 'a', encoding="utf-8", errors="replace") as f:
    #    f.write(f"{match_count} || {(len(subset) // 2)}")
    return match_count > (len(subset) // 2)


def manufacturer_multi(files, manual_sort_list):
    for file in files:
        data = ocr_file(file)
        manufacturer_wrapper(file, data, manual_sort_list)

"""
Description: 
    a wrapper function for the currently programmed manufacturers
    Currently handles Kyocera pages, HP pages, and Inventory Re-Stock pages
Args:
    file: passed file that is ready to be processed and renamed
"""


def manufacturer_wrapper(file, data, manual_sort_list=None):
    inventory_subset = {
        "SERVICE": 1, "INVENTORY": 4, "PICKING": 4, "LIST": 1,
        "PRINTED": 1, "STOCK": 4, "SIGNATURE": 6, "PACKING": 4}
    kyocera_subset = {"KYOCERA": 7, "STATUS": 2, "KPDL": 7, "FIRMWARE": 2, "VERSION": 2, "KIR": 7}
    hp_subset = {"HP": 7, "USAGE": 6, "PAGE": 1, "INFORMATION": 2, "CONFIGURATION": 3, "LaserJet": 4}
    canon_subset = {"COUNTER": 2, "REPORT": 2, "DEVICE": 1, "INSTALLATION": 4, "DATE": 1}
    konica_subset = {"METER": 2, "NO.": 5, "TC:": 5, "SERIAL": 2}

    match_threshhold = 90

    if data is None:
        file_manager_wrapper(file=file, serial_number=None, date=None, brand=None, manual_sort_list=manual_sort_list)

    if fuzzy_subset(inventory_subset, data, match_threshhold):
        parse_inventory(file, data, manual_sort_list)
    elif fuzzy_subset(kyocera_subset, data, match_threshhold):
        parse_kyocera(file, data, manual_sort_list)
    elif fuzzy_subset(hp_subset, data, match_threshhold):
        parse_hp(file, data, manual_sort_list)
    elif fuzzy_subset(canon_subset, data, match_threshhold):
        parse_canon(file, data, manual_sort_list)
    elif fuzzy_subset(konica_subset, data, match_threshhold):
        parse_konica(file, data, manual_sort_list)
    else:
        file_manager_wrapper(file=file, serial_number=None, date=None, brand=None, manual_sort_list=manual_sort_list)


"""
Description: 
    called from manufacturer_wrapper for every inventory restock page found
    finds date in file and checks if it is a valid date
    then calls file_manager_wrapper to rename and move the file to destination
Args:
    file: inventory restock page
    data: data from file (saves an additional I/O operation to read data)
"""


def parse_inventory(file, data, manual_sort_list=None):
    date = None

    for temp in data:
        if date is not None:
            break
        elif date is None:
            try:
                date = datetime.strptime(normalize_date(temp), '%m/%d/%Y')
            except Exception:
                pass

    file_manager_wrapper(file=file, serial_number=None, date=date,
                         brand='Inventory', manual_sort_list=manual_sort_list)


"""
Description: 
    called from manufacturer_wrapper for every kyocera page found
    finds date in file and checks if it is a valid date
    finds serial number and checks if it matches a specific set of requirements
    then calls file_manager_wrapper to rename and move the file to destination
Args:
    file: inventory restock page
    data: data from file (saves an additional I/O operation to read data)
"""


def parse_kyocera(file, data, manual_sort_list=None):
    date = None
    serial_number = None

    excluded_chars = "-_[].,;:()#/?<>|\\\'\"“"
    excluded_phrase = ("dpi", "dpl", "dp1")

    lower = 'abcdefghijklmnopqrstuvwxyz-_[].,;:()#/?<>|'
    bad_serial_flag = False

    for entry in data:
        temp = entry.strip()
        if len(temp) >= 10:

            temp_normalized = normalize_kyocera_serials(temp)

            if (any(char.isdigit() for char in temp_normalized)
                    and any(char.isalpha() for char in temp_normalized)
                    and not any(char in excluded_chars for char in temp_normalized)):

                if not temp_normalized[:3].isnumeric() and serial_number is None:
                    serial_number = temp_normalized
                    if any(char in lower for char in temp):
                        bad_serial_flag = True

        if date is None:
            try:
                date = datetime.strptime(normalize_date(temp), '%m/%d/%Y')
                if date.year > datetime.now().year:
                    date = None
            except Exception:
                pass

        if date is not None and serial_number is not None:
            break

    file_manager_wrapper(file=file, serial_number=serial_number, date=date,
                         brand='Kyocera', manual_sort_list=manual_sort_list, flagged=bad_serial_flag)


"""
Description: 
    called from manufacturer_wrapper for every hp page found
    finds date in file and checks if it is a valid date
    finds serial number based on specific regex pattern
    then calls file_manager_wrapper to rename and move the file to destination
Args:
    file: inventory restock page
    data: data from file (saves an additional I/O operation to read data)
"""


def parse_hp(file, data, manual_sort_list=None):
    date = None
    serial_number = None
    serial_number_pattern = re.compile(r'\b[a-z0-9]{10}\b', re.IGNORECASE)

    excluded_chars = "-_[].,;:()#/?<>|\\\'\"“"
    excluded_phrase = ("dpi", "dpl", "dp1")

    lower = 'abcdefghijklmnopqrstuvwxyz-_[].,;:()#/?<>|'
    bad_serial_flag = False

    for entry in data:
        temp = entry.strip()
        if (any(char.isdigit() for char in temp)
                and any(char.isalpha() for char in temp)
                and not any(char in excluded_chars for char in temp)
                and len(temp) == 10 and not temp.endswith(excluded_phrase)):
            serial_number = temp
            if any(char in lower for char in temp):
                bad_serial_flag = True
        if date is None:
            try:
                date = datetime.strptime(normalize_date(temp), '%m/%d/%Y')
                if date.year > datetime.now().year:
                    date = None
            except Exception:
                pass

        if date is not None and serial_number is not None:
            break

    file_manager_wrapper(file=file, serial_number=serial_number, date=date,
                         brand='HP', manual_sort_list=manual_sort_list, flagged=bad_serial_flag)


def parse_canon(file, data, manual_sort_list=None):
    date = None
    serial_number = None

    lower = 'abcdefghijklmnopqrstuvwxyz-_[].,;:()#/?<>|'
    bad_serial_flag = False

    for entry in data:
        temp = entry.strip()
        if (serial_number is None and any(char.isdigit() for char in temp)
                and any(char.isalpha() for char in temp) and len(temp) == 8):
            serial_number = temp
            if any(char in lower for char in temp):
                bad_serial_flag = True
        if date is None:
            try:
                date = datetime.strptime(normalize_date(temp), '%m/%d/%Y')
                if date.year > datetime.now().year:
                    date = None
            except Exception:
                pass

        if date is not None and serial_number is not None:
            break

    file_manager_wrapper(file=file, serial_number=serial_number, date=date,
                         brand='Canon', manual_sort_list=manual_sort_list, flagged=bad_serial_flag)


def parse_konica(file, data, manual_sort_list=None):
    date = None
    serial_number = None

    lower = 'abcdefghijklmnopqrstuvwxyz-_[].,;:()#/?<>|'
    bad_serial_flag = False

    for entry in data:
        temp = entry.strip()
        if (serial_number is None and any(char.isdigit() for char in temp)
                and any(char.isalpha() for char in temp) and len(temp) >= 12):
            serial_number = temp
            if any(char in lower for char in temp):
                bad_serial_flag = True
        if date is None:
            try:
                date = datetime.strptime(normalize_date(temp), '%m/%d/%Y')
                if date.year > datetime.now().year:
                    date = None
            except Exception:
                pass

        if date is not None and serial_number is not None:
            break

    file_manager_wrapper(file=file, serial_number=serial_number, date=date,
                         brand='Canon', manual_sort_list=manual_sort_list, flagged=bad_serial_flag)

import os
import csv
import json
import logging
import sqlite3

from pathlib import Path
from datetime import datetime

"""
Description: 
    Creates a logger instance for the run duration
    will used a specified log output path to store the log file once completed
"""

def setup_logger():
    path_manager = DirectoryManager()
    log_path = path_manager.get_runlog_dir()

    log_filename = datetime.now().strftime(rf"{log_path}\%Y-%m-%d_runtime.log")

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename)
        ]
    )
    return logging.getLogger()


"""
Description: 
    used to convert 2 in 2/15/2024 to 2-February while utilizing a dictionary
    used to name folders in the folder structure
Args:
    int_month: integer representation of the month
Returns:
    returns 2-February for 2 in 2/15/2024
"""

def convert_month_str(int_month):
    months = {1: "January",
              2: "February",
              3: "March",
              4: "April",
              5: "May",
              6: "June",
              7: "July",
              8: "August",
              9: "September",
              10: "October",
              11: "November",
              12: "December"}

    return f"{int_month}-{months.get(int_month)}"


"""
Description:     
    Acts as a shared Singleton object, sharing pathing, common vars, logging, ect

"""

class DirectoryManager:
    _instance = None
    CONFIG_FILE = "config.json"
    INVENTORY_FILE = "inventory.csv"
    DATABASE_FILE = "parts_logger.db"
    MANUAL_SORT_JSON = "manual_sort.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.unsorted_dir = ""
            cls._instance.runlog_dir = ""
            cls._instance.manual_sort_dir = ""
            cls._instance.logbook_dir = ""
            cls._instance.inventory_dir = ""
            cls._instance.reports_dir = ""
            cls._instance.multi_cores = 0
            cls._instance.restock_days = 3
            cls._instance.last_inventory = None
            cls._instance.appearance = 'System'
            cls._instance.logger = None
            cls._instance.cursor = None
            cls._instance.connection = None
            cls._instance.database_total = 0
            cls._instance.database_processed = 0
            cls._instance.setup = 0
            cls._instance.longest_dir_pixel = 0
            cls._instance.menu_tips = True
            cls._instance.version = '2.1.0'
            cls._instance.running = False
            cls._instance.load_directories_from_file()
        return cls._instance

    def load_directories_from_file(self, recursive=False):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r") as file:
                    data = json.load(file)
                    self.unsorted_dir = data.get("unsorted_dir")
                    self.runlog_dir = data.get("runlog_dir")
                    self.manual_sort_dir = data.get("manual_sort_dir")
                    self.logbook_dir = data.get("logbook_dir")
                    self.inventory_dir = data.get("inventory_dir")
                    self.reports_dir = data.get("reports_dir")
                    self.multi_cores = data.get("multi_cores", 0)
                    self.restock_days = int(data.get("restock_days", 3))
                    self.last_inventory = data.get("last_inventory", None)
                    self.appearance = data.get("appearance", 'System')
                    self.menu_tips = data.get("menu_tips", True)

                if any(filepath is None for filepath in [self.unsorted_dir, self.runlog_dir, self.manual_sort_dir,
                                                       self.logbook_dir, self.inventory_dir, self.reports_dir]):
                    self.setup = 1
                else:
                    self.setup = 0

                self.logger = self.get_logger()
                self.cursor = None
                self.connection = None

                for temp_str in [self.unsorted_dir, self.runlog_dir, self.manual_sort_dir, self.logbook_dir,
                                 self.inventory_dir]:
                    if len(temp_str) * 8 > self.longest_dir_pixel:
                        self.longest_dir_pixel = len(temp_str) * 8

            except json.JSONDecodeError:
                if self.logger is not None:
                    self.logger.error("Failed to populate Singleton")
                else:
                    self.setup = 1
                    pass
        else:
            if not recursive:
                with open(self.CONFIG_FILE, "w") as file:
                    pass
                self.load_directories_from_file(True)

        for file in [self.CONFIG_FILE, self.INVENTORY_FILE, self.DATABASE_FILE, self.MANUAL_SORT_JSON]:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    pass

    def setup_database(self):
        connection = sqlite3.connect(self.DATABASE_FILE)
        cursor = connection.cursor()

        machines = """CREATE TABLE MACHINES(
                            ENTRY_ID INTEGER PRIMARY KEY AUTOINCREMENT, 
                            BRAND TEXT, 
                            SERIAL_NUM TEXT, 
                            DATE DATE);"""

        parts_used = """CREATE TABLE PARTS_USED(
                            ENTRY_ID INTEGER,
                            PART_USED TEXT, 
                            QUANTITY INTEGER,
                            FOREIGN KEY (ENTRY_ID) REFERENCES MACHINES(ENTRY_ID));"""

        file_hash = """CREATE TABLE FILE_HASH(
                            STEM TEXT PRIMARY KEY,
                            FILE_PATH TEXT,
                            ENTRY_ID INTEGER,
                            FOREIGN KEY (ENTRY_ID) REFERENCES MACHINES(ENTRY_ID));"""

        try:
            cursor.execute(machines)
        except Exception as e:
            self.logger.warning(e)

        try:
            cursor.execute(parts_used)
        except Exception as e:
            self.logger.warning(e)

        try:
            cursor.execute(file_hash)
        except Exception as e:
            self.logger.warning(e)

        connection.commit()
        connection.close()

    def get_database(self):
        if self.logger is None:
            # print('logger is setup')
            self.create_logger()

        self.setup_database()
        self.connection = sqlite3.connect(self.DATABASE_FILE)
        self.cursor = self.connection.cursor()
        return self.cursor, self.connection

    def create_logger(self):
        self.logger = setup_logger()

    def get_unsorted_dir(self):
        return self.unsorted_dir

    def get_runlog_dir(self):
        return self.runlog_dir

    def get_manual_sort_dir(self):
        return self.manual_sort_dir

    def get_logbook_dir(self):
        return self.logbook_dir

    def get_inventory_dir(self):
        return self.inventory_dir

    def get_database_dir(self):
        return Path(self.DATABASE_FILE).resolve()

    def get_reports_dir(self):
        return self.reports_dir

    def get_manual_json(self):
        return Path(self.MANUAL_SORT_JSON).resolve()

    def get_logger(self):

        if self.logger is None:
            self.logger = setup_logger()

        return self.logger

    def is_setup(self):

        if self.setup == 0:
            return True
        return False

    def write_config_file(self, path_dict):

        if not os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'w') as f:
                pass

        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(path_dict, f, indent=4, sort_keys=True)

        self.load_directories_from_file()

    def write_inventory_file(self, parts_dict):

        if not os.path.exists(self.INVENTORY_FILE):
            with open(self.INVENTORY_FILE, 'w') as f:
                pass

        with open(self.INVENTORY_FILE, 'w', newline='', encoding='utf-8') as f:
            headers = parts_dict[0].keys()
            writer = csv.DictWriter(f, headers)

            writer.writeheader()
            writer.writerows(parts_dict)

    def load_inventory(self):

        if not os.path.exists(self.INVENTORY_FILE):
            return []

        inventory = []
        with open(self.INVENTORY_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            inventory = [row for row in reader]

        return inventory

    def write_settings(self, settings=None, directories=None):

        if settings:
            self.multi_cores = settings.get('selected_cores')
            self.restock_days = settings.get('selected_restocks')
            self.last_inventory = settings.get('selected_inventory')
            self.appearance = settings.get('selected_appearance')

        if directories:
            self.unsorted_dir = directories.get('unsorted_dir')
            self.runlog_dir = directories.get('runlog_dir')
            self.manual_sort_dir = directories.get('manual_sort_dir')
            self.logbook_dir = directories.get('logbook_dir')
            self.inventory_dir = directories.get('inventory_dir')
            self.reports_dir = directories.get('reports_dir')

        config_dict = {
            'unsorted_dir': self.unsorted_dir,
            'runlog_dir': self.runlog_dir,
            'manual_sort_dir': self.manual_sort_dir,
            'logbook_dir': self.logbook_dir,
            'inventory_dir': self.inventory_dir,
            'reports_dir': self.reports_dir,
            'multi_cores': self.multi_cores,
            'restock_days': self.restock_days,
            'last_inventory': self.last_inventory,
            'appearance': self.appearance,
            'menu_tips': self.menu_tips
        }

        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config_dict, f, indent=4, sort_keys=True)

        pass

    def get_inventory_file(self):
        return self.INVENTORY_FILE

    def set_running_status(self, case):
        self.running = case

    def is_running(self):
        return self.running

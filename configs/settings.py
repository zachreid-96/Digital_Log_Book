import os
import csv
import json
import logging
import sqlite3
import platform

from pathlib import Path
from datetime import datetime

def convert_month_str(int_month) -> str:
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


def _get_platform_pathing() -> Path | None:
    os_name = platform.system()

    if os_name == 'Windows':
        pathing = Path(os.environ['USERPROFILE'], 'Parts Logger')
    elif os_name == 'Linux':
        pathing = Path(os.environ['HOME'], 'Parts Logger')
    elif os_name == 'Darwin':
        pathing = Path(os.environ['HOME'], 'Library/Application Support')
    else:
        pathing = None

    if pathing:
        pathing.mkdir(parents=True, exist_ok=True)

    return pathing


class Settings:

    _instance = None
    _initialized = False

    unsorted_dir = Path("")
    runlog_dir = Path("")
    manual_sort_dir = Path("")
    logbook_dir = Path("")
    inventory_dir = Path("")
    reports_dir = Path("")
    configs_dir = Path("")

    multi_cores = 0
    restock_days = 3
    database_total = 0
    database_processed = 0
    longest_dir_pixel = 0

    version = '2.2.0'
    appearance = 'System'

    config_file = Path("")
    inventory_file = Path("")
    database_file = Path("")
    manual_sort_json = Path("")

    last_inventory = None

    setup = False
    menu_tips = False
    running = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.__setup()
            cls._instance._initialized = True
        return cls._instance

    def __setup(self):
        if self._initialized:
            return

        pathing = _get_platform_pathing()

        manual_sort = Path(pathing, 'Manual Sorting Required')
        runtime_logs = Path(pathing, 'Runtime Logs')
        ready_sort = Path(pathing, 'Ready to Sort Pages')
        inventory_pages = Path(pathing, 'Inventory Pages')
        used_parts = Path(pathing, 'Used Parts Logs')
        reports = Path(pathing, 'Reports')
        configs = Path(pathing, 'Configs')
        
        for folder in [manual_sort, runtime_logs, ready_sort, inventory_pages, used_parts, reports, configs]:
            folder.mkdir(parents=True, exist_ok=True)

        json_dict = {
            'unsorted_dir': str(ready_sort),
            'runlog_dir': str(runtime_logs),
            'manual_sort_dir': str(manual_sort),
            'logbook_dir': str(used_parts),
            'inventory_dir': str(inventory_pages),
            'reports_dir': str(reports),
            'configs_dir': str(configs),
            'multi_cores': 0,
            'restock_days': 3,
            'last_inventory': None,
            'appearance': 'System'
        }

        self.config_file = Path(configs, "config.json")
        self.inventory_file = Path(configs, "inventory.csv")
        self.database_file = Path(configs, "parts_logger.db")
        self.manual_sort_json = Path(configs, "manual_sort.json")

        for f in [self.config_file, self.inventory_file, self.database_file, self.manual_sort_json]:
            f.touch(exist_ok=True)

        self.multi_cores = 0
        self.restock_days = 3
        self.last_inventory = None
        self.appearance = 'System'
        self.database_total = 0
        self.database_processed = 0
        self.setup = True
        self.longest_dir_pixel = 0
        self.menu_tips = False
        self.version = '2.1.0'
        self.running = False
        
        self.write_config_file(json_dict)

    def _load_directories_from_file(self) -> None:
        if not os.path.exists(self.config_file):
            raise Warning("Configuration file not found")

        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)

            self.unsorted_dir = Path(data.get("unsorted_dir"))
            self.runlog_dir = Path(data.get("runlog_dir"))
            self.manual_sort_dir = Path(data.get("manual_sort_dir"))
            self.logbook_dir = Path(data.get("logbook_dir"))
            self.inventory_dir = Path(data.get("inventory_dir"))
            self.reports_dir = Path(data.get("reports_dir"))
            self.configs_dir = Path(data.get("configs_dir"))
            self.multi_cores = data.get("multi_cores", 0)
            self.restock_days = int(data.get("restock_days", 3))
            self.last_inventory = data.get("last_inventory", None)
            self.appearance = data.get("appearance", 'System')
            self.menu_tips = data.get("menu_tips", True)

            if any(filepath is None for filepath in [self.unsorted_dir, self.runlog_dir, self.manual_sort_dir,
                                                     self.logbook_dir, self.inventory_dir, self.reports_dir]):
                self.setup = False
            else:
                self.setup = True

            for temp_str in [self.unsorted_dir, self.runlog_dir, self.manual_sort_dir, self.logbook_dir,
                             self.inventory_dir]:
                if len(str(temp_str)) * 8 > self.longest_dir_pixel:
                    self.longest_dir_pixel = len(str(temp_str)) * 8

        except json.JSONDecodeError:
            self.setup = False

    def get_unsorted_dir(self) -> Path:
        return self.unsorted_dir

    def get_runlog_dir(self) -> Path:
        return self.runlog_dir

    def get_manual_sort_dir(self) -> Path:
        return self.manual_sort_dir

    def get_logbook_dir(self) -> Path:
        return self.logbook_dir

    def get_inventory_dir(self) -> Path:
        return self.inventory_dir

    def get_database_dir(self) -> Path:
        return Path(self.database_file).resolve()

    def get_reports_dir(self) -> Path:
        return self.reports_dir

    def get_manual_json(self) -> Path:
        return Path(self.manual_sort_json).resolve()

    def is_setup(self):

        if self.setup == 0:
            return True
        return False

    def write_config_file(self, path_dict):

        if not os.path.exists(self.config_file):
            file_path = Path(self.config_file)
            file_path.touch(exist_ok=True)

        if os.path.getsize(self.config_file) == 0:
            with open(self.config_file, 'w') as f:
                json.dump(path_dict, f, indent=4, sort_keys=True)

        self._load_directories_from_file()

    def write_inventory_file(self, parts_dict):

        if not os.path.exists(self.inventory_file):
            file_path = Path(self.inventory_file)
            file_path.mkdir(parents=True, exist_ok=True)

        with open(self.inventory_file, 'w', newline='', encoding='utf-8') as f:
            headers = parts_dict[0].keys()
            writer = csv.DictWriter(f, headers)

            writer.writeheader()
            writer.writerows(parts_dict)

    def load_inventory(self) -> list:

        if not os.path.exists(self.inventory_file):
            return []

        inventory = []
        with open(self.inventory_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            inventory = list(reader)

        return inventory

    def write_settings(self, settings=None, directories=None) -> None:

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
            self.configs_dir = directories.get("configs_dir")

        config_dict = {
            'unsorted_dir': str(self.unsorted_dir),
            'runlog_dir': str(self.runlog_dir),
            'manual_sort_dir': str(self.manual_sort_dir),
            'logbook_dir': str(self.logbook_dir),
            'inventory_dir': str(self.inventory_dir),
            'reports_dir': str(self.reports_dir),
            'configs_dir': str(self.configs_dir),
            'multi_cores': self.multi_cores,
            'restock_days': self.restock_days,
            'last_inventory': self.last_inventory,
            'appearance': self.appearance,
            'menu_tips': self.menu_tips
        }

        with open(self.config_file, 'w') as f:
            json.dump(config_dict, f, indent=4, sort_keys=True)

    def get_inventory_file(self) -> Path:
        return self.inventory_file

if __name__ == "__main__":
    settings = Settings()
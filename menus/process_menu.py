import os
import glob
import json
import time
import threading

import tkinter as tk
import customtkinter as ct

from pathlib import Path
from configs.config import DirectoryManager
from handlers.file_manager import populate_files
from handlers.manufacturer_handler import manufacturer_multi
from database.database_handler import database_add_files, barcode_wrapper
from multiprocessing import Pool, Manager, set_start_method, freeze_support

freeze_support()

class ProcessMenu(ct.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.manager = DirectoryManager()
        self.logger = self.manager.get_logger()
        self.manual_json = self.manager.get_manual_json()

        self.unsorted_label = ct.CTkLabel(self, text="Pages Ready to Sort:")
        self.unsorted_label.grid(row=0, column=0, columnspan=3, sticky="e", pady=(40, 10))
        self.unsorted_directory = ct.CTkLabel(self, text=self.manager.get_unsorted_dir())
        self.unsorted_directory.grid(row=0, column=3, columnspan=7, sticky="w", padx=25, pady=(40, 10))

        self.log_label = ct.CTkLabel(self, text="Runtime Logs:")
        self.log_label.grid(row=1, column=0, columnspan=3, sticky="e", pady=10)
        self.log_directory = ct.CTkLabel(self, text=self.manager.get_runlog_dir())
        self.log_directory.grid(row=1, column=3, columnspan=7, sticky="w", padx=25, pady=10)

        self.manual_sort_label = ct.CTkLabel(self, text="Manual Sorting Required:")
        self.manual_sort_label.grid(row=2, column=0, columnspan=3, sticky="e", pady=10)
        self.manual_sort_directory = ct.CTkLabel(self, text=self.manager.get_manual_sort_dir())
        self.manual_sort_directory.grid(row=2, column=3, columnspan=7, sticky="w", padx=25, pady=10)

        self.logbook_label = ct.CTkLabel(self, text="Used Parts:")
        self.logbook_label.grid(row=3, column=0, columnspan=3, sticky="e", pady=10)
        self.logbook_directory = ct.CTkLabel(self, text=self.manager.get_logbook_dir())
        self.logbook_directory.grid(row=3, column=3, columnspan=7, sticky="w", padx=25, pady=10)

        self.inventory_page_label = ct.CTkLabel(self, text="Inventory Pages:")
        self.inventory_page_label.grid(row=4, column=0, columnspan=3, sticky="e", pady=10)
        self.inventory_page_directory = ct.CTkLabel(self, text=self.manager.get_inventory_dir())
        self.inventory_page_directory.grid(row=4, column=3, columnspan=7, sticky="w", padx=25, pady=10)

        self.start_button = ct.CTkButton(self, text="Start Process",
                                         command=self.run_process_multi)
        self.start_button.grid(row=5, column=0, sticky="w", padx=25, pady=10, columnspan=3)
        self.start_button.configure(state="normal")

        self.progress = tk.StringVar(value="Status...")

        self.progress_start_label = ct.CTkLabel(self, textvariable=self.progress, anchor="w", width=35)

        self.progress_start_label.grid(row=5, column=3, columnspan=2, sticky="w", padx=25, pady=10)

        self.reports_menu_help = ct.CTkLabel(self, text="Menu Usage",
                                               font=ct.CTkFont(size=15, weight="bold"))
        self.reports_menu_help.grid(row=6, column=0, padx=20, pady=(20, 0), columnspan=12, sticky='nws')
        self.process_menu_help_1 = ct.CTkLabel(self, text="Load Scanned Documents into 'Ready to Sort' folder. "
                                                        "Then press 'Start Process'.")
        self.process_menu_help_1.grid(row=7, column=0, padx=40, pady=0, columnspan=12, sticky='nws')
        self.process_menu_help_2 = ct.CTkLabel(self, text="This will apply OCR and pull Serial Number, Date of Service, "
                                                          "and any Parts Used from scanned sheets.")
        self.process_menu_help_2.grid(row=8, column=0, padx=40, pady=0, columnspan=12, sticky='nws')
        self.process_menu_help_3 = ct.CTkLabel(self, text="Successful files will be renamed and "
                                        "moved to 'Used Parts Logs' folder and to 'Inventory Pages' folder.")
        self.process_menu_help_3.grid(row=9, column=0, padx=40, pady=0, columnspan=12, sticky='nws')
        self.process_menu_help_4 = ct.CTkLabel(self, text="Failed files will be tagged for "
                                        "Manual Review, where the Serial Number, Date, or Parts Used failed to extract.")
        self.process_menu_help_4.grid(row=10, column=0, padx=40, pady=0, columnspan=12, sticky='nws')

        self.update_fields()

    def update_fields(self):

        if self.manager.menu_tips:
            self.reports_menu_help.configure(text="Menu Usage")
            self.process_menu_help_1.configure(text="Load Scanned Documents into 'Ready to Sort' folder. "
                                                    "Then press 'Start Process'.")
            self.process_menu_help_2.configure(text="This will apply OCR and pull Serial Number, Date of Service, "
                                                    "and any Parts Used from scanned sheets.")
            self.process_menu_help_3.configure(text="Successful files will be renamed and moved to 'Used Parts Logs' "
                                                    "folder and to 'Inventory Pages' folder.")
            self.process_menu_help_4.configure(text="Failed files will be tagged for Manual Review, "
                                                    "where the Serial Number, Date, or Parts Used failed to extract.")
        else:
            self.reports_menu_help.configure(text="")
            self.process_menu_help_1.configure(text="")
            self.process_menu_help_2.configure(text="")
            self.process_menu_help_3.configure(text="")
            self.process_menu_help_4.configure(text="")


    def run_process_multi(self):

        thread = threading.Thread(target=self.thread_multi)
        thread.start()

    def thread_multi(self):

        self.manager.set_running_status(True)
        self.manager.create_logger()
        path = self.manager.unsorted_dir

        barcode_length = 0
        try:

            try:
                set_start_method('spawn', force=True)
            except RuntimeError:
                pass

            with Manager() as manager:

                manual_sort_list = manager.list()

                files = populate_files(path)
                self.progress.set("Status... EXTRACTING DATA FROM LOGS")

                process_start = time.perf_counter()
                #print(f"Start: {process_start}")

                cpu_count = max(1, os.cpu_count() // 2)
                adjusted_cpu_count = min(cpu_count, max(1, len(files) // 25))

                if len(files) > 0:
                    process_chunks = [files[i::adjusted_cpu_count] for i in range(adjusted_cpu_count)]
                    process_args = [(chunk, manual_sort_list) for chunk in process_chunks]
                    with Pool(processes=adjusted_cpu_count) as pool:
                       pool.starmap(manufacturer_multi, process_args)

                process_end = time.perf_counter()
                #print(f"OCR - Execution on {len(files)} files took {process_end - process_start:.2f} seconds.")

                barcode_start = time.perf_counter()

                self.progress.set("Status... EXTRACTING BARCODE DATA")
                self.manager.logger.info("Done processing all copied files in 'Unsorted'...\n")

                # Get files
                cursor, connection = self.manager.get_database()
                cursor.execute('SELECT STEM FROM FILE_HASH')
                processed_stems = [stem for stem, in cursor.fetchall()]

                manual_review_files = []
                with open(self.manual_json, 'r') as manual_files:
                    data = None
                    try:
                        data = json.load(manual_files)
                    except Exception:
                        #print('here')
                        pass
                    if data:
                        manual_review_files = [
                            Path(entry['file']).resolve() for entry in data
                        ]

                for entry in manual_sort_list:
                    manual_review_files.append(entry['file'])

                files = []
                for file in glob.glob(str(Path(self.manager.get_logbook_dir()).resolve() / '**' / '*.pdf'), recursive=True):
                    stem = Path(file).stem
                    if stem in processed_stems:
                        continue
                    if file in manual_review_files:
                        continue
                    files.append(file)

                if len(files) > 0:

                    files_sorted = sorted(files, key=self.sort_key)
                    adjusted_cpu_count = min(cpu_count, max(1, len(files) // 25))

                    barcode_list = manager.list()
                    barcode_chunks = [files_sorted[i::adjusted_cpu_count] for i in range(adjusted_cpu_count)]
                    barcode_args = [(chunk, barcode_list) for chunk in barcode_chunks]

                    with Pool(processes=adjusted_cpu_count) as pool:
                        pool.starmap(barcode_wrapper, barcode_args)

                    barcode_end = time.perf_counter()
                    #print(f"Barcode - Execution on {len(files)} files took {barcode_end - barcode_start:.2f} seconds.")

                    self.progress.set("Status... ADDING DATA TO DATABASE")
                    database_start = time.perf_counter()
                    barcode_length = len(barcode_list)

                    for entry in barcode_list:

                        if not entry['parts_data']:
                            file_name_parts = Path(entry['file']).stem.split('_')

                            brand = None
                            if 'Kyocera' in entry['file']:
                                brand = 'Kyocera'
                            elif 'HP' in entry['file']:
                                brand = 'HP'
                            elif 'Canon' in entry['file']:
                                brand = 'Canon'
                            elif 'Konica' in entry['file']:
                                brand = 'Konica'

                            manual_sort_list.append({
                                'file': entry['file'],
                                'serial_num': file_name_parts[1],
                                'date': file_name_parts[0],
                                'brand': brand,
                                'parts': None
                            })
                        else:
                            database_add_files(entry['file'], entry['parts_data'])
                            #pass

                    with open(self.manual_json, 'r') as local_manual_json:
                        try:
                            data = json.load(local_manual_json)
                        except Exception as e:
                            data = []

                    with open(self.manual_json, 'w') as local_manual_json:
                        for entry in list(manual_sort_list):
                            if entry not in data:
                                data.append(entry)
                        json.dump(data, local_manual_json, indent=4)

                    database_end = time.perf_counter()
                    #print(f"Database - Execution on {barcode_length} files took {database_end - database_start:.2f} seconds.")

            self.progress.set("Status... DONE")
        except Exception as e:
            self.logger.info(f"\n{e}\n")
            self.progress.set("Status... ERROR")
        finally:
            self.manager.set_running_status(False)

    def sort_key(self, file):
        name = Path(file).stem.split('_')

        if len(name) == 3:
            return 1, name
        elif len(name) == 2:
            return 0, name
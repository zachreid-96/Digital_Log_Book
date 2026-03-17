import customtkinter as ct

from pathlib import Path
from tkinter import filedialog
from configs.config import DirectoryManager

class DirectoryMenu(ct.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.manager = DirectoryManager()

        magic_width = self.manager.longest_dir_pixel

        self.directories_label = ct.CTkLabel(self, text="Change Common Directories",
                                              font=ct.CTkFont(size=16, weight="bold"))
        self.directories_label.grid(row=0, column=0, padx=10, pady=(20, 10), columnspan=4, sticky='news')

        self.unsorted_label = ct.CTkLabel(self, text="Pages Ready to Sort:")
        self.unsorted_label.grid(row=1, column=0, columnspan=3, sticky="e", pady=10, padx=10)
        self.unsorted_directory = ct.CTkEntry(self, width=magic_width)
        self.unsorted_directory.grid(row=1, column=3, columnspan=8, sticky="w", padx=25, pady=10)
        self.unsorted_button = ct.CTkButton(self, text="Browse",
                                            command=lambda: self.select_directory("unsorted"))
        self.unsorted_button.grid(row=1, column=8, columnspan=1, sticky="w", padx=25, pady=10)

        self.log_label = ct.CTkLabel(self, text="Runtime Logs:")
        self.log_label.grid(row=2, column=0, columnspan=3, sticky="e", pady=10, padx=10)
        self.log_directory = ct.CTkEntry(self, width=magic_width)
        self.log_directory.grid(row=2, column=3, columnspan=4, sticky="w", padx=25, pady=10)
        self.log_button = ct.CTkButton(self, text="Browse", command=lambda: self.select_directory("log"))
        self.log_button.grid(row=2, column=8, columnspan=1, sticky="w", padx=25, pady=10)

        self.manual_sort_label = ct.CTkLabel(self, text="Manual Sorting Required:")
        self.manual_sort_label.grid(row=3, column=0, columnspan=3, sticky="e", pady=10, padx=10)
        self.manual_sort_directory = ct.CTkEntry(self, width=magic_width)
        self.manual_sort_directory.grid(row=3, column=3, columnspan=4, sticky="w", padx=25, pady=10)
        self.manual_sort_button = ct.CTkButton(self, text="Browse",
                                               command=lambda: self.select_directory("manual_sort"))
        self.manual_sort_button.grid(row=3, column=8, columnspan=1, sticky="w", padx=25, pady=10)

        self.logbook_label = ct.CTkLabel(self, text="Used Parts:")
        self.logbook_label.grid(row=4, column=0, columnspan=3, sticky="e", pady=10, padx=10)
        self.logbook_directory = ct.CTkEntry(self, width=magic_width)
        self.logbook_directory.grid(row=4, column=3, columnspan=4, sticky="w", padx=25, pady=10)
        self.logbook_button = ct.CTkButton(self, text="Browse",
                                           command=lambda: self.select_directory("logbook"))
        self.logbook_button.grid(row=4, column=8, columnspan=1, sticky="w", padx=25, pady=10)

        self.inventory_page_label = ct.CTkLabel(self, text="Inventory Pages:")
        self.inventory_page_label.grid(row=5, column=0, columnspan=3, sticky="e", pady=10, padx=10)
        self.inventory_page_directory = ct.CTkEntry(self, width=magic_width)
        self.inventory_page_directory.grid(row=5, column=3, columnspan=4, sticky="w", padx=25, pady=10)
        self.inventory_page_button = ct.CTkButton(self, text="Browse",
                                                  command=lambda: self.select_directory("inventory_page"))
        self.inventory_page_button.grid(row=5, column=8, columnspan=1, sticky="w", padx=25, pady=10)

        self.reports_label = ct.CTkLabel(self, text="Reports:")
        self.reports_label.grid(row=6, column=0, columnspan=3, sticky="e", pady=10, padx=10)
        self.reports_directory = ct.CTkEntry(self, width=magic_width)
        self.reports_directory.grid(row=6, column=3, columnspan=4, sticky="w", padx=25, pady=10)
        self.reports_button = ct.CTkButton(self, text="Browse",
                                            command=lambda: self.select_directory("reports"))
        self.reports_button.grid(row=6, column=8, columnspan=1, sticky="w", padx=25, pady=10)

        self.populate_directories()

    def populate_directories(self):
        self.unsorted_directory.delete(0, len(self.manager.unsorted_dir))
        self.unsorted_directory.insert(0, self.manager.unsorted_dir)

        self.log_directory.delete(0, len(self.manager.runlog_dir))
        self.log_directory.insert(0, self.manager.runlog_dir)

        self.manual_sort_directory.delete(0, len(self.manager.manual_sort_dir))
        self.manual_sort_directory.insert(0, self.manager.manual_sort_dir)

        self.logbook_directory.delete(0, len(self.manager.logbook_dir))
        self.logbook_directory.insert(0, self.manager.logbook_dir)

        self.inventory_page_directory.delete(0, len(self.manager.inventory_dir))
        self.inventory_page_directory.insert(0, self.manager.inventory_dir)

        self.reports_directory.delete(0, len(self.manager.reports_dir))
        self.reports_directory.insert(0, self.manager.reports_dir)

    def select_directory(self, option):
        directory = filedialog.askdirectory()
        if directory:
            if option == "unsorted":
                self.unsorted_directory.delete(0, len(self.manager.unsorted_dir))
                self.unsorted_directory.insert(0, str(Path(directory)))
            elif option == "log":
                self.log_directory.delete(0, len(self.manager.runlog_dir))
                self.log_directory.insert(0, str(Path(directory)))
            elif option == "manual_sort":
                self.manual_sort_directory.delete(0, len(self.manager.manual_sort_dir))
                self.manual_sort_directory.insert(0, str(Path(directory)))
            elif option == "logbook":
                self.logbook_directory.delete(0, len(self.manager.logbook_dir))
                self.logbook_directory.insert(0, str(Path(directory)))
            elif option == "inventory_page":
                self.inventory_page_directory.delete(0, len(self.manager.inventory_dir))
                self.inventory_page_directory.insert(0, str(Path(directory)))
            elif option == "reports":
                self.reports_directory.delete(0, len(self.manager.reports_dir))
                self.reports_directory.insert(0, str(Path(directory)))
            else:
                pass

    def save_directories_locations(self):

        data = {
            "unsorted_dir": Path(self.unsorted_directory.get()),
            "runlog_dir": Path(self.log_directory.get()),
            "manual_sort_dir": Path(self.manual_sort_directory.get()),
            "logbook_dir": Path(self.logbook_directory.get()),
            "inventory_dir": Path(self.inventory_page_directory.get()),
            "reports_dir": Path(self.reports_directory.get())
        }
        self.manager.write_settings(directories=data)
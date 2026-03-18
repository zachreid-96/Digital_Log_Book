import webbrowser

import customtkinter as ct

from configs.settings import Settings


def open_github_repo(event=None):
    webbrowser.open('https://github.com/zachreid-96/digitial_log_book')

def open_github_releases(event=None):
    webbrowser.open('https://github.com/zachreid-96/digitial_log_book/releases')

def open_github_bugtracker(event=None):
    webbrowser.open('https://github.com/zachreid-96/digitial_log_book/issues')


class AboutMenu(ct.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.manager = Settings()
        self.version = self.manager.version

        self.name_label = ct.CTkLabel(self, text=f"Digital Log Book Tool v{self.version}",
                                      font=ct.CTkFont(size=15, weight='bold'))
        self.name_label.grid(row=0, column=0, padx=20, pady=(20, 10), columnspan=6, sticky='nws')

        self.development = ct.CTkLabel(self, text="Developed/Maintained by Zach")
        self.development.grid(row=1, column=0, padx=20, pady=5, columnspan=6, sticky='nws')

        self.contact = ct.CTkLabel(self, text="Please reach out via email or submit an issue on the Github Page.")
        self.contact.grid(row=2, column=0, padx=20, pady=5, columnspan=6, sticky='nws')

        self.github_repo = ct.CTkLabel(self, text="GitHub Repository", text_color="#40B5AD", cursor="hand2")
        self.github_repo.grid(row=3, column=0, padx=20, pady=0, columnspan=2, sticky='nws')
        self.github_repo.bind("<Button-1>", open_github_repo)

        self.github_releases = ct.CTkLabel(self, text="GitHub Releases", text_color="#40B5AD", cursor="hand2")
        self.github_releases.grid(row=3, column=2, padx=20, pady=0, columnspan=2, sticky='nws')
        self.github_releases.bind("<Button-1>", open_github_releases)

        self.github_bugreport = ct.CTkLabel(self, text="GitHub Issue Tracker", text_color="#40B5AD", cursor="hand2")
        self.github_bugreport.grid(row=3, column=4, padx=20, pady=0, columnspan=2, sticky='nws')
        self.github_bugreport.bind("<Button-1>", open_github_bugtracker)

        self.features_label = ct.CTkLabel(self,
                            text="This tool helps automate the processing of scanned parts usage pages.",
                            font=ct.CTkFont(size=15, weight='bold'))
        self.features_label.grid(row=4, column=0, padx=20, pady=(20, 10), columnspan=6, sticky='nws')
        self.features_brands = ct.CTkLabel(self,
                            text="Currently supports HP, Kyocera, Canon, and Inventory Pick Sheets.")
        self.features_brands.grid(row=5, column=0, padx=40, columnspan=6, sticky='nws')
        self.flavor_1 = ct.CTkLabel(self,
                            text="Extracts Serial Numbers, Dates, and Parts Used via OCR and Barcode Recognition")
        self.flavor_1.grid(row=6, column=0, padx=40, columnspan=6, sticky='nws')
        self.flavor_2 = ct.CTkLabel(self, text="Generates parts usage and inventory reports.")
        self.flavor_2.grid(row=7, column=0, padx=40, columnspan=6, sticky='nws')
        self.flavor_3 = ct.CTkLabel(self, text="Assists with manual verification and inventory tracking.")
        self.flavor_3.grid(row=8, column=0, padx=40, columnspan=6, sticky='nws')

        self.requirements = ct.CTkLabel(self, text="Requirements:",
                            font=ct.CTkFont(size=15, weight='bold'))
        self.requirements.grid(row=9, column=0, padx=20, pady=(20, 10), columnspan=2, sticky='nws')
        self.requirement_1 = ct.CTkLabel(self, text="PDF's must be separated into 1 page documents.")
        self.requirement_1.grid(row=10, column=0, padx=40, columnspan=6, sticky='nws')



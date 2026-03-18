import customtkinter as ct

from configs.settings import Settings

class HelpMenu(ct.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.manager = Settings()

        self.kyocera_scanning_label = ct.CTkLabel(self, text="Scanning Reports on Kyocera",
                                                  font=ct.CTkFont(size=15, weight="bold"))
        self.kyocera_scanning_label.grid(row=0, column=0, padx=20, pady=(20, 5), columnspan=4, sticky='nws')

        self.kyocera_scanning_resolution = ct.CTkLabel(self, text="Scan Resolution > 300x300 DPI")
        self.kyocera_scanning_resolution.grid(row=1, column=0, padx=40, pady=0, columnspan=4, sticky='nws')
        self.kyocera_scanning_image_type = ct.CTkLabel(self, text="Image Type > Text")
        self.kyocera_scanning_image_type.grid(row=2, column=0, padx=40, pady=0, columnspan=4, sticky='nws')
        self.kyocera_scanning_file_type = ct.CTkLabel(self, text="File Type > PDF Compression 4 or 5")
        self.kyocera_scanning_file_type.grid(row=3, column=0, padx=40, pady=0, columnspan=4, sticky='nws')

        self.canon_scanning_label = ct.CTkLabel(self, text="Scanning Reports on Canon",
                                                font=ct.CTkFont(size=15, weight="bold"))
        self.canon_scanning_label.grid(row=4, column=0, padx=20, pady=0, columnspan=4, sticky='nws')

        self.canon_scanning_resolution = ct.CTkLabel(self, text="Scan Resolution > 300x300 DPI")
        self.canon_scanning_resolution.grid(row=5, column=0, padx=40, pady=0, columnspan=4, sticky='nws')
        self.canon_scanning_image_type = ct.CTkLabel(self, text="Image Type > Text")
        self.canon_scanning_image_type.grid(row=6, column=0, padx=40, pady=0, columnspan=4, sticky='nws')
        self.canon_scanning_file_type = ct.CTkLabel(self, text="File Type > PDF Uncompressed")
        self.canon_scanning_file_type.grid(row=7, column=0, padx=40, pady=0, columnspan=4, sticky='nws')

        self.help_menu_label = ct.CTkLabel(self, text="Get to know the Program",
                                            font=ct.CTkFont(size=15, weight='bold'))
        self.help_menu_label.grid(row=0, column=4, padx=20, pady=(20, 5), columnspan=4, sticky='nws')

        self.help_menu_label_1 = ct.CTkLabel(self, text="Scanned PDF's must be individual files (1 page per document).")
        self.help_menu_label_1.grid(row=1, column=4, padx=40, pady=0, columnspan=8, sticky='nws')
        self.help_menu_label_2 = ct.CTkLabel(self, text="Can use PDF24 or another PDF tool to separate PDF's.")
        self.help_menu_label_2.grid(row=2, column=4, padx=40, pady=0, columnspan=8, sticky='nws')
        self.help_menu_label_3 = ct.CTkLabel(self, text="Program is not 100% accurate. There will be mistakes.")
        self.help_menu_label_3.grid(row=3, column=4, padx=40, pady=0, columnspan=8, sticky='nws')
        self.help_menu_label_4 = ct.CTkLabel(self, text="Files flagged for Manual Review can be viewed in 'Manual Review' Menu.")
        self.help_menu_label_4.grid(row=4, column=4, padx=40, pady=0, columnspan=8, sticky='nws')
        self.help_menu_label_5 = ct.CTkLabel(self, text="'Manual Review' Menu does have build in PDF viewer for ease of review.")
        self.help_menu_label_5.grid(row=5, column=4, padx=40, pady=0, columnspan=8, sticky='nws')
        self.help_menu_label_6 = ct.CTkLabel(self, text="Utilizes multiprocessing (multiple CPU cores) to offload and")
        self.help_menu_label_6.grid(row=6, column=4, padx=40, pady=0, columnspan=8, sticky='nws')
        self.help_menu_label_7 = ct.CTkLabel(self, text="speed up processing times for OCR operations and Barcode Recognition.")
        self.help_menu_label_7.grid(row=7, column=4, padx=50, pady=0, columnspan=8, sticky='nws')

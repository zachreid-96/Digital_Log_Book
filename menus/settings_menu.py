import customtkinter as ct

from os import cpu_count
from datetime import datetime
from configs.settings import Settings
from customtkinter import ThemeManager


def change_appearance_mode_event(new_appearance_mode: str):
    ct.set_appearance_mode(new_appearance_mode)


def change_scaling_event(new_scaling: str):
    new_scaling_float = int(new_scaling.replace("%", "")) / 100
    ct.set_widget_scaling(new_scaling_float)

class SettingsMenu(ct.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.bind("<Button-1>", self.remove_focus)
        self.entries = []

        self.manager = Settings()

        self.cpu_core_usage_label = ct.CTkLabel(self, text="Multiprocessing CPU Core Usage",
                                                font=ct.CTkFont(size=16, weight='bold'))
        self.cpu_core_usage_label.grid(row=0, column=0, padx=20, pady=(10,0), columnspan=4, sticky='w')

        self.cpu_cores = cpu_count()
        self.used_cores = self.cpu_cores // 2
        self.cpu_counter = ct.CTkSegmentedButton(self, values=["-", self.used_cores, "+"],
                                             command=self.change_core_count)
        self.cpu_counter.grid(row=1, column=1, padx=(0, 20), pady=(10, 5), columnspan=3)
        self.cpu_recommendation = ct.CTkLabel(self,
                                              text=f'Min: 1\tRecommended: {self.cpu_cores // 2}\tMax: {self.cpu_cores}')
        self.cpu_recommendation.grid(row=2, column=1, padx=(0, 20), pady=(5, 10), columnspan=3)

        self.stock_day_label = ct.CTkLabel(self, text="Desired Days Between Restocks",
                                                font=ct.CTkFont(size=16, weight='bold'))
        self.stock_day_label.grid(row=5, column=0, padx=20, pady=(10, 5), columnspan=4, sticky='w')

        self.current_restock_goal = 3
        self.restock_recommendation = ct.CTkSegmentedButton(self, values=["-", self.current_restock_goal, "+"],
                                             command=self.change_restock_days)
        self.restock_recommendation.grid(row=6, column=1, padx=(0, 20), pady=(5, 10), columnspan=3)

        self.last_inventory_label = ct.CTkLabel(self, text="Date of Last Inventory",
                                                font=ct.CTkFont(size=16, weight='bold'))
        self.last_inventory_label.grid(row=7, column=0, padx=20, pady=(10, 5), columnspan=4, sticky='w')
        self.last_inventory_date = ct.CTkEntry(self, placeholder_text='MM/DD/YYYY')
        self.last_inventory_date.grid(row=8, column=1, padx=(0, 20), pady=(5, 10), columnspan=3)
        self.entries.append(self.last_inventory_date)

        self.appearance_mode_label = ct.CTkLabel(self, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=11, column=1, padx=20, pady=(10, 0), columnspan=2)
        self.appearance_mode_optionemenu = ct.CTkOptionMenu(self,
                                                            values=["Light", "Dark", "System"],
                                                            command=change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=12, column=1, padx=20, pady=(10, 10), columnspan=2)
        self.appearance_mode_optionemenu.set("System")

        self.load_options()

    def load_options(self):
        self.master.update_idletasks()

        if self.manager.multi_cores != 0:
            self.cpu_counter.configure(values=["-", self.manager.multi_cores, "+"])
            self.cpu_counter.set('')

        self.restock_recommendation.configure(values=["-", self.manager.restock_days, "+"])
        self.restock_recommendation.set('')

        if self.manager.last_inventory is None:
            self.last_inventory_date.configure(placeholder_text='MM/DD/YYYY')
        else:
            self.last_inventory_date.insert(0, self.manager.last_inventory)
        self.appearance_mode_optionemenu.set(self.manager.appearance)

    def change_restock_days(self, value):

        if value == '-' and self.current_restock_goal > 1:
            self.current_restock_goal -= 1
        if value == '+':
            self.current_restock_goal += 1

        self.restock_recommendation.configure(values=["-", self.current_restock_goal, "+"])
        self.restock_recommendation.set('')

    def change_core_count(self, value):

        if value == '-' and self.used_cores > 1:
            self.used_cores -= 1
        if value == '+' and self.used_cores < self.cpu_cores:
            self.used_cores += 1

        self.cpu_counter.configure(values=["-", self.used_cores, "+"])
        self.cpu_counter.set('')

    def remove_focus(self, event):
        for entry in self.entries:
            if not entry.winfo_containing(event.x_root, event.y_root) == entry:
                self.focus()

        self.save_selections()

    def is_valid_date(self, date_check):
        try:
            datetime.strptime(date_check, "%m/%d/%Y")
            return True
        except ValueError:
            return False

    def save_selections(self):

        if self.is_valid_date(self.last_inventory_date.get()):
            self.last_inventory_date.configure(fg_color=ThemeManager.theme['CTkEntry']['fg_color'])
            inventory_date = self.last_inventory_date.get()
        else:
            self.last_inventory_date.configure(fg_color='#cd6155')
            inventory_date = None

        settings = {
            'selected_cores': self.cpu_counter.cget('values')[1],
            'selected_restocks': self.restock_recommendation.cget('values')[1],
            'selected_inventory': inventory_date,
            'selected_appearance': self.appearance_mode_optionemenu.get()
        }
        self.manager.write_settings(settings=settings)

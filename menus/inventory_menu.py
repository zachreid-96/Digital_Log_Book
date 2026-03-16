import os
import csv

import customtkinter as ct

from math import ceil
from configs.config import DirectoryManager
from datetime import datetime, timedelta
from tkinter import filedialog, StringVar
from dateutil.relativedelta import relativedelta


def count_weekdays(start, end):

    day_count = 0
    current_date = start
    while current_date < end:
        if current_date.weekday() < 5:
            day_count += 1
        current_date += timedelta(days=1)

    return day_count


def normalize_description(desc):

    new_desc = [s for s in desc.split(' ')
                if s.strip()]

    return ' '.join(new_desc)


class InventoryMenu(ct.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.manager = DirectoryManager()

        self.inventory = self.manager.load_inventory()
        self.parts_list_display = []

        self.selected_part = StringVar()
        self.part_nums = []

        self.parts_list = ct.CTkTextbox(self, width=375, height=450, wrap='none',
                                        font=ct.CTkFont(family="Consolas", size=12))
        self.parts_list.grid(row=0, column=0, columnspan=6, padx=(20, 10), pady=20, rowspan=20)
        self.parts_list.configure(state='disabled')
        self.part_line = 0

        self.import_csv = ct.CTkButton(self, text="Import Inventory CSV",
                                       command=self.import_inventory_csv)
        self.import_csv.grid(row=0, column=6, padx=(10, 10), pady=(20,10), columnspan=2)

        self.update_inventory_label = ct.CTkButton(self, text="Edit Inventory",
                                                   command=self.open_inventory_csv)
        self.update_inventory_label.grid(row=1, column=6, padx=(10, 10), pady=(0,10), columnspan=2)

        self.update_inventory_label = ct.CTkButton(self, text="Refresh Inventory",
                                                   command=self.refresh_inventory)
        self.update_inventory_label.grid(row=1, column=8, padx=(10, 10), pady=(0,10), columnspan=2)

        self.parts_report_label = ct.CTkLabel(self, text="Generate Inventory Usage Reports",
                                              font=ct.CTkFont(size=15, weight="bold"))
        self.parts_report_label.grid(row=2, column=6, padx=(10, 10), pady=(0,10), columnspan=4, sticky='news')

        self.parts_report_month_1 = ct.CTkButton(self, text="1 Month Report",
                                                 command=lambda: self.generate_inventory_report(1))
        self.parts_report_month_1.grid(row=3, column=6, padx=(10, 10), pady=(0,10), columnspan=2)

        self.parts_report_month_3 = ct.CTkButton(self, text="3 Month Report",
                                                 command=lambda: self.generate_inventory_report(3))
        self.parts_report_month_3.grid(row=3, column=8, padx=(10, 10), pady=(0,10), columnspan=2)

        self.parts_report_month_6 = ct.CTkButton(self, text="6 Month Report",
                                                 command=lambda: self.generate_inventory_report(6))
        self.parts_report_month_6.grid(row=4, column=6, padx=(10, 10), pady=(0,10), columnspan=2)

        self.parts_report_month_9 = ct.CTkButton(self, text="9 Month Report",
                                                 command=lambda: self.generate_inventory_report(9))
        self.parts_report_month_9.grid(row=4, column=8, padx=(10, 10), pady=(0,10), columnspan=2)

        self.parts_report_month_12 = ct.CTkButton(self, text="12 Month Report",
                                                  command=lambda: self.generate_inventory_report(12))
        self.parts_report_month_12.grid(row=5, column=6, padx=(10, 10), pady=(0, 10), columnspan=2)

        self.parts_report_last_inventory = ct.CTkButton(self, text="Last Inventory",
                                                        command=lambda: self.generate_inventory_report("last_inventory"))
        self.parts_report_last_inventory.grid(row=5, column=8, padx=(10, 10), pady=(0, 10), columnspan=2)

        self.open_reports = ct.CTkButton(self, text="Open Reports",
                                         command=self.open_report_folder)
        self.open_reports.grid(row=0, column=8, padx=(10, 5), pady=(20, 10), columnspan=2)

        self.inventory_help_menu = ct.CTkLabel(self, text="Menu Usage",
                                              font=ct.CTkFont(size=15, weight="bold"))
        self.inventory_help_menu.grid(row=6, column=6, padx=(10, 5), pady=(10, 0), columnspan=5, sticky='nws')
        self.inventory_help_menu_1 = ct.CTkLabel(self, text="Import Inventory CSV (See Scott).")
        self.inventory_help_menu_1.grid(row=7, column=6, padx=(20, 5), pady=0, columnspan=5, sticky='nws')
        self.inventory_help_menu_2 = ct.CTkLabel(self, text="Use 'Edit Inventory' to Open and Edit Inventory CSV.")
        self.inventory_help_menu_2.grid(row=8, column=6, padx=(20, 5), pady=0, columnspan=5, sticky='nws')
        self.inventory_help_menu_3 = ct.CTkLabel(self, text="Hit 'Refresh Inventory' aftering editing.")
        self.inventory_help_menu_3.grid(row=9, column=6, padx=(20, 5), pady=0, columnspan=5, sticky='nws')
        self.inventory_help_menu_4 = ct.CTkLabel(self, text="Generate Inventory Reports -> Will spit out CSV with")
        self.inventory_help_menu_4.grid(row=10, column=6, padx=(20, 5), pady=0, columnspan=5, sticky='nws')
        self.inventory_help_menu_5 = ct.CTkLabel(self, text="Part #, QTY Used, Weekly/Daily AVG, Current/Suggested Stock")
        self.inventory_help_menu_5.grid(row=11, column=6, padx=(20, 5), pady=0, columnspan=5, sticky='nws')
        self.update_fields()

    def open_report_folder(self):
        os.startfile(self.manager.get_reports_dir())

    def open_inventory_csv(self):
        os.startfile(self.manager.get_inventory_file())

    def refresh_inventory(self):
        self.inventory = self.manager.load_inventory()
        self.update_fields()

    def generate_inventory_report(self, time_frame):

        cursor, connection = self.manager.get_database()
        restock_days = self.manager.restock_days

        current_date = datetime.now()
        report_time = None
        report_name = None
        format_date = None

        if time_frame == 1:
            report_name = f"inventory_1_month_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
            format_date = datetime.now() - relativedelta(months=time_frame)
            report_time = format_date.strftime('%Y-%m-%d')
        elif time_frame == 3:
            report_name = f"inventory_3_month_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
            format_date = datetime.now() - relativedelta(months=time_frame)
            report_time = format_date.strftime('%Y-%m-%d')
        elif time_frame == 6:
            report_name = f"inventory_6_month_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
            format_date = datetime.now() - relativedelta(months=time_frame)
            report_time = format_date.strftime('%Y-%m-%d')
        elif time_frame == 9:
            report_name = f"inventory_9_month_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
            format_date = datetime.now() - relativedelta(months=time_frame)
            report_time = format_date.strftime('%Y-%m-%d')
        elif time_frame == 12:
            report_name = f"inventory_12_month_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
            format_date = datetime.now() - relativedelta(months=time_frame)
            report_time = format_date.strftime('%Y-%m-%d')
        elif time_frame == "last_inventory":
            report_name = f"inventory_last_inventory_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
            format_date = datetime.strptime(self.manager.last_inventory, '%m/%d/%Y')
            report_time = format_date.strftime('%Y-%m-%d')

        if report_time and report_name:
            command = f"""
                SELECT
                    p.PART_USED,
                    p.QUANTITY
                FROM MACHINES m
                LEFT JOIN PARTS_USED p ON m.ENTRY_ID = p.ENTRY_ID
                WHERE m.DATE >= '{report_time}';"""

            cursor.execute(command)
            results = cursor.fetchall()

            parts_summary = {}

            for part_number, part_quantity in results:
                if part_number in parts_summary:
                    parts_summary[part_number] += part_quantity
                else:
                    parts_summary[part_number] = part_quantity

            inventory_keys = [part['part_number'] for part in self.inventory]
            non_inventory_parts = [part for part in parts_summary.keys() if part not in inventory_keys]

            report_path = os.path.join(self.manager.get_reports_dir(), report_name)

            with open(report_path, 'w', newline='', encoding='utf-8') as report_csv:
                writer = csv.writer(report_csv)
                writer.writerow(['Inventory Usage Report'])
                writer.writerow(['Report Range', f'{report_time} to {current_date.year}-{current_date.month}-{current_date.day}'])
                writer.writerow([])

                writer.writerow(['Part Number', 'Quantity Used', 'Weekly Average',
                                 'Daily Average', 'Stock', 'Suggested Stock', 'Delta', 'Stale'])

                #report_time_difference = self.count_weekdays(format_date, current_date)
                report_days = count_weekdays(format_date, current_date)
                report_weeks = report_days // 7

                for item in self.inventory:
                    qty_used = parts_summary.get(item['part_number'], 0)
                    daily_average = round(qty_used / report_days, 2)
                    weekly_average = round(qty_used / report_weeks, 2)
                    suggested_stock = max(0, ceil(daily_average * restock_days))
                    delta = 'Increase' if daily_average > int(item['quantity']) else 'Decrease'
                    delta = '' if daily_average == int(item['quantity']) else delta
                    stale = True if qty_used == 0 else False
                    writer.writerow([item['part_number'], qty_used, weekly_average, daily_average, item['quantity'],
                                     suggested_stock, delta, stale])

                #print(non_inventory_parts)
                for item in non_inventory_parts:
                    qty_used = parts_summary.get(item, 0)
                    daily_average = round(qty_used / report_days, 2)
                    weekly_average = round(qty_used / report_weeks, 2)
                    suggested_stock = max(0, ceil(daily_average * restock_days))
                    delta = 'Increase' if daily_average > 0 else 'Decrease'
                    delta = '' if daily_average == 0 else delta
                    stale = True if qty_used == 0 else False
                    writer.writerow([item, qty_used, weekly_average, daily_average,
                                     0, suggested_stock, delta, stale])

        return

    def update_fields(self):

        self.parts_list_display = []
        self.format_inventory()

        self.parts_list.configure(state='normal')
        self.parts_list.delete('0.0', 'end')
        self.parts_list.insert('0.0', '\n'.join(self.parts_list_display))
        self.parts_list.configure(state='disabled')

        if self.manager.menu_tips:
            self.inventory_help_menu.configure(text="Menu Usage")
            self.inventory_help_menu_1.configure(text="Import Inventory CSV (See Scott).")
            self.inventory_help_menu_2.configure(text="Use 'Edit Inventory' to Open and Edit Inventory CSV.")
            self.inventory_help_menu_3.configure(text="Hit 'Refresh Inventory' aftering editing.")
            self.inventory_help_menu_4.configure(text="Generate Inventory Reports -> Will spit out CSV with")
            self.inventory_help_menu_5.configure(text="Part #, QTY Used, Weekly/Daily AVG, Current/Suggested Stock")
        else:
            self.inventory_help_menu.configure(text="")
            self.inventory_help_menu_1.configure(text="")
            self.inventory_help_menu_2.configure(text="")
            self.inventory_help_menu_3.configure(text="")
            self.inventory_help_menu_4.configure(text="")
            self.inventory_help_menu_5.configure(text="")

    def import_inventory_csv(self):

        file_obj = filedialog.askopenfile(defaultextension='.csv', filetypes=[('CSV files', '.csv')])

        if file_obj:
            file_path = file_obj.__getattribute__('name')

            lines = []

            with open(file_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f, delimiter=',')

                for row in reader:
                    useless_cols = 0
                    for entry in row:
                        if entry == "MAIN":
                            useless_cols += 3
                            lines.append([
                                entry for entry in row[useless_cols:]
                                if entry != ""
                            ])
                            break
                        if entry != "MAIN":
                            useless_cols += 1

            parts_dict = []

            for line in lines:
                parts_dict.append({
                    'part_number': line[0].strip(),
                    'description': normalize_description(line[1].strip()),
                    'quantity': int(line[2].strip('.00').strip()),
                    'part_price': float(line[3].strip('$').strip())
                })

            sorted_parts_dict = sorted(parts_dict, key=lambda part: part['part_number'], reverse=True)

            for entry in sorted_parts_dict:
                self.parts_list_display.append(f"{entry['part_number']} x {entry['quantity']}")

            self.parts_list.configure(state='normal')
            self.parts_list.insert('0.0', '\n'.join(self.parts_list_display))
            self.parts_list.configure(state='disabled')

            self.manager.write_inventory_file(parts_dict=sorted_parts_dict)

    def format_inventory(self):

        longest_part_num = 0
        for part in self.inventory:
            if len(part['part_number']) > longest_part_num:
                longest_part_num = len(part['part_number'])

        for entry in self.inventory:
            self.parts_list_display.append(f"{entry['part_number']:<{longest_part_num}} "
                                           f" x {entry['quantity']}  |  {entry['description']}")


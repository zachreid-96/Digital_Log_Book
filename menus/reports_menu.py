import os
import csv, platform
import sys, subprocess

import customtkinter as ct

from math import ceil
from configs.settings import Settings
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def count_weekdays(start, end):

    day_count = 0
    current_date = start
    while current_date < end:
        if current_date.weekday() < 5:
            day_count += 1
        current_date += timedelta(days=1)

    return day_count


class ReportsMenu(ct.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.manager = Settings()

        self.full_report_label = ct.CTkLabel(self, text="Generate Full Usage Reports",
                                             font=ct.CTkFont(size=15, weight="bold"))
        self.full_report_label.grid(row=0, column=0, padx=20, pady=(20, 10), columnspan=4, sticky='news')

        self.open_reports = ct.CTkButton(self, text="Open Reports",
                                         command=self.open_report_folder)
        self.open_reports.grid(row=0, column=6, padx=(20, 20), pady=(20, 0), columnspan=2)

        self.full_report_month_1 = ct.CTkButton(self, text="1 Month Report",
                                                command=lambda: self.generate_full_report(1))
        self.full_report_month_1.grid(row=1, column=0, padx=20, pady=10, columnspan=2, sticky='news')

        self.full_report_month_3 = ct.CTkButton(self, text="3 Month Report",
                                                command=lambda: self.generate_full_report(3))
        self.full_report_month_3.grid(row=1, column=2, padx=20, pady=10, columnspan=2, sticky='news')

        self.full_report_month_6 = ct.CTkButton(self, text="6 Month Report",
                                                command=lambda: self.generate_full_report(6))
        self.full_report_month_6.grid(row=1, column=4, padx=20, pady=10, columnspan=2, sticky='news')

        self.full_report_month_9 = ct.CTkButton(self, text="9 Month Report",
                                                command=lambda: self.generate_full_report(9))
        self.full_report_month_9.grid(row=2, column=0, padx=20, pady=10, columnspan=2, sticky='news')

        self.full_report_month_12 = ct.CTkButton(self, text="12 Month Report",
                                                 command=lambda: self.generate_full_report(12))
        self.full_report_month_12.grid(row=2, column=2, padx=20, pady=10, columnspan=2, sticky='news')

        self.full_report_last_inventory = ct.CTkButton(self, text="Last Inventory",
                                                       command=lambda: self.generate_full_report("last_inventory"))
        self.full_report_last_inventory.grid(row=2, column=4, padx=20, pady=10, columnspan=2, sticky='news')

        # Parts Reporting

        self.parts_report_label = ct.CTkLabel(self, text="Generate Parts Usage Reports",
                                             font=ct.CTkFont(size=15, weight="bold"))
        self.parts_report_label.grid(row=3, column=0, padx=20, pady=(20, 10), columnspan=4, sticky='news')

        self.parts_report_month_1 = ct.CTkButton(self, text="1 Month Report",
                                                command=lambda: self.generate_parts_report(1))
        self.parts_report_month_1.grid(row=4, column=0, padx=20, pady=10, columnspan=2, sticky='news')

        self.parts_report_month_3 = ct.CTkButton(self, text="3 Month Report",
                                                command=lambda: self.generate_parts_report(3))
        self.parts_report_month_3.grid(row=4, column=2, padx=20, pady=10, columnspan=2, sticky='news')

        self.parts_report_month_6 = ct.CTkButton(self, text="6 Month Report",
                                                command=lambda: self.generate_parts_report(6))
        self.parts_report_month_6.grid(row=4, column=4, padx=20, pady=10, columnspan=2, sticky='news')

        self.parts_report_month_9 = ct.CTkButton(self, text="9 Month Report",
                                                command=lambda: self.generate_parts_report(9))
        self.parts_report_month_9.grid(row=5, column=0, padx=20, pady=10, columnspan=2, sticky='news')

        self.parts_report_month_12 = ct.CTkButton(self, text="12 Month Report",
                                                 command=lambda: self.generate_parts_report(12))
        self.parts_report_month_12.grid(row=5, column=2, padx=20, pady=10, columnspan=2, sticky='news')

        self.parts_report_last_inventory = ct.CTkButton(self, text="Last Inventory",
                                                       command=lambda: self.generate_parts_report("last_inventory"))
        self.parts_report_last_inventory.grid(row=5, column=4, padx=20, pady=10, columnspan=2, sticky='news')

        self.reports_menu_help = ct.CTkLabel(self, text="Menu Usage",
                                               font=ct.CTkFont(size=15, weight="bold"))
        self.reports_menu_help.grid(row=6, column=0, padx=20, pady=(20, 0), columnspan=9, sticky='nws')
        self.reports_menu_help_1 = ct.CTkLabel(self, text="Generate Full Usage Reports -> Will spit out CSV with "
                                                        "Date, Serial Number, Parts Used, and File for time frame.")
        self.reports_menu_help_1.grid(row=7, column=0, padx=40, pady=0, columnspan=9, sticky='nws')
        self.reports_menu_help_2 = ct.CTkLabel(self, text="Generate Parts Usage Reports -> Will spit out CSV with "
                                                          "Part Number, Quantity Used, Weekly/Daily Average, and Suggested Stock.")
        self.reports_menu_help_2.grid(row=8, column=0, padx=40, pady=0, columnspan=9, sticky='nws')
        self.reports_menu_help_3 = ct.CTkLabel(self, text="Generated reports will appear in the 'Reports' folder.")
        self.reports_menu_help_3.grid(row=9, column=0, padx=40, pady=0, columnspan=9, sticky='nws')
        self.reports_menu_help_4 = ct.CTkLabel(self, text="Use 'Open Reports' button to open that folder.")
        self.reports_menu_help_4.grid(row=10, column=0, padx=40, pady=0, columnspan=9, sticky='nws')

        self.update_fields()


    def update_fields(self):
        if self.manager.menu_tips:
            self.reports_menu_help.configure(text="Menu Usage")
            self.reports_menu_help_1.configure(text="Generate Full Usage Reports -> Will spit out CSV with "
                                            "Date, Serial Number, Parts Used, and File for time frame.")
            self.reports_menu_help_2.configure(text="Generate Parts Usage Reports -> Will spit out CSV with "
                                            "Part Number, Quantity Used, Weekly/Daily Average, and Suggested Stock.")
            self.reports_menu_help_3.configure(text="Generated reports will appear in the 'Reports' folder.")
            self.reports_menu_help_4.configure(text="Use 'Open Reports' button to open that folder.")
        else:
            self.reports_menu_help.configure(text="")
            self.reports_menu_help_1.configure(text="")
            self.reports_menu_help_2.configure(text="")
            self.reports_menu_help_3.configure(text="")
            self.reports_menu_help_4.configure(text="")

    def open_report_folder(self):

        os_name = platform.system()

        if os_name == 'Windows':
            os.startfile(self.manager.get_reports_dir())
        elif os_name == 'Darwin':
            subprocess.call(('open', self.manager.get_reports_dir()))
        elif os_name == 'Linux':
            subprocess.call(('xdg-open', self.manager.get_reports_dir()))
        else:
            raise Warning(f"Unsupported OS: {os_name}")

    def generate_full_report(self, time_frame):

        cursor, connection = self.manager.get_database()

        current_date = datetime.now()
        report_time = None
        report_name = None

        if time_frame == 1:
            report_name = f"full_1_month_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
            format_date = datetime.now() - relativedelta(months=1)
            report_time = format_date.strftime('%Y-%m-%d')
        elif time_frame == 3:
            report_name = f"full_3_month_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
            format_date = datetime.now() - relativedelta(months=3)
            report_time = format_date.strftime('%Y-%m-%d')
        elif time_frame == 6:
            report_name = f"full_6_month_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
            format_date = datetime.now() - relativedelta(months=6)
            report_time = format_date.strftime('%Y-%m-%d')
        elif time_frame == 9:
            report_name = f"full_9_month_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
            format_date = datetime.now() - relativedelta(months=9)
            report_time = format_date.strftime('%Y-%m-%d')
        elif time_frame == 12:
            report_name = f"full_12_month_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
            format_date = datetime.now() - relativedelta(months=12)
            report_time = format_date.strftime('%Y-%m-%d')
        elif time_frame == "last_inventory":
            report_name = f"full_last_inventory_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
            format_date = datetime.strptime(self.manager.last_inventory, '%m/%d/%Y')
            report_time = format_date.strftime('%Y-%m-%d')

        if report_time and report_name:
            command = f"""SELECT 
                                m.DATE,
                                m.SERIAL_NUM,
                                GROUP_CONCAT(p.PART_USED || ' x' || p.QUANTITY, ',') AS Parts_List,
                                f.FILE_PATH
                            FROM MACHINES m
                            LEFT JOIN PARTS_USED p ON m.ENTRY_ID = p.ENTRY_ID
                            LEFT JOIN FILE_HASH f ON m.ENTRY_ID = f.ENTRY_ID
                            WHERE m.DATE >= '{report_time}'
                            GROUP BY m.ENTRY_ID
                            ORDER BY m.DATE DESC;"""

            cursor.execute(command)
            rows = cursor.fetchall()

            headers = [description[0] for description in cursor.description]

            report_path = os.path.join(self.manager.get_reports_dir(), report_name)

            with open(report_path, 'w', newline='', encoding='utf-8') as report_csv:
                writer = csv.writer(report_csv)
                writer.writerow(headers)
                writer.writerows(rows)

    def generate_parts_report(self, time_frame):

        cursor, connection = self.manager.get_database()
        self.restock = self.manager.restock_days

        current_date = datetime.now()
        report_time = None
        report_name = None
        format_date = None

        if time_frame == 1:
            report_name = f"parts_1_month_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
            format_date = datetime.now() - relativedelta(months=time_frame)
            report_time = format_date.strftime('%Y-%m-%d')
        elif time_frame == 3:
            report_name = f"parts_3_month_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
            format_date = datetime.now() - relativedelta(months=time_frame)
            report_time = format_date.strftime('%Y-%m-%d')
        elif time_frame == 6:
            report_name = f"parts_6_month_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
            format_date = datetime.now() - relativedelta(months=time_frame)
            report_time = format_date.strftime('%Y-%m-%d')
        elif time_frame == 9:
            report_name = f"parts_9_month_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
            format_date = datetime.now() - relativedelta(months=time_frame)
            report_time = format_date.strftime('%Y-%m-%d')
        elif time_frame == 12:
            report_name = f"parts_12_month_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
            format_date = datetime.now() - relativedelta(months=time_frame)
            report_time = format_date.strftime('%Y-%m-%d')
        elif time_frame == "last_inventory":
            report_name = f"parts_last_inventory_report_{current_date.month}-{current_date.day}-{current_date.year}.csv"
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

            report_path = os.path.join(self.manager.get_reports_dir(), report_name)

            with open(report_path, 'w', newline='', encoding='utf-8') as report_csv:
                writer = csv.writer(report_csv)
                writer.writerow(['Parts Usage Report'])
                writer.writerow(['Report Range', f'{report_time} to {current_date.year}-{current_date.month}-{current_date.day}'])
                writer.writerow([])

                writer.writerow(['Part Number', 'Quantity Used', 'Weekly Average', 'Daily Average', 'Suggested Stock'])

                #report_time_difference = self.count_weekdays(format_date, current_date)
                report_days = count_weekdays(format_date, current_date)
                report_weeks = report_days // 7

                for part, qty in sorted(parts_summary.items(), key=lambda x: x[1], reverse=True):
                    daily_average = round(qty / report_days, 2)
                    weekly_average = round(qty / report_weeks, 2)
                    suggested_stock = max(1, ceil(daily_average * self.restock))
                    writer.writerow([part, qty, weekly_average, daily_average, suggested_stock])

        return


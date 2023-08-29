from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from RPA.Robocorp.WorkItems import WorkItems
from RPA.Excel.Files import Files
import os

class ExportExcel:

    def __init__(self):
        config_dict = {
            "url_website": "https://www.nytimes.com/search?query=$TERM&sort=newest",
            "default_search_attribute": "data-testid",
            "xpath_close_cookies_button": "expanded-dock-btn-selector",
            "innertext_accept_terms_button": "continue",
            "xpath_cards": "search-results",
            "xpath_show_more_button": "search-show-more-button",
            "xpath_cards_date": "todays-date",
            "xpath_sections_button": "search-multiselect-button",
            "xpath_sections_boxes": "multi-select-dropdown-list",
            "xpath_date": "todays-date",
            "regex_money_bool": "\\$\\d+\\,?\\d*\\.?\\d*|\\d+\\s?dollars|\\d+\\s?USD"
        }

        wi = WorkItems()
        wi.get_input_work_item()
        variables = wi.get_work_item_variables()
        self.number_months = variables("number_months")
        self.number_months = int(self.number_months)
        self.df_output = {}

    def get_month_date_criteria(self):
        if self.number_months == 0 or self.number_months == 1:
            return date(datetime.now().year, datetime.now().month, 1)
        else:
            return date(datetime.now().year, datetime.now().month, 1)-relativedelta(months=
                                                         self.number_months-1)
        
    def export_excel_file(self, list_registers, filename):
        date_criteria = self.get_month_date_criteria()
        list_registers = [dict(t) for t in {tuple(d.items()) for d in list_registers}]
        print(list_registers[0]["datetime"])
        list_registers = [d for d in list_registers if d['datetime'] >= date_criteria]
        for key in list_registers[0].keys():
            self.df_output[key] = [d[key] for d in list_registers]

        print(f'Creating output.xlsx file')
        workbook = Files()
        workbook.create_workbook(path=filename, sheet_name="data_collected")
        workbook.save_workbook()

        lib = Files()
        lib.open_workbook(path=filename)
        lib.read_worksheet("data_collected")
        lib.append_rows_to_worksheet(self.df_output, header=True)
        lib.save_workbook()
        lib.close_workbook()
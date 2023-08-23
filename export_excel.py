from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from RPA.JSON import JSON
from RPA.Excel.Files import Files

class ExportExcel:

    def __init__(self):
        json_file = JSON().load_json_from_file("resources\config.json")
        self.number_months = json_file["number_months"]
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
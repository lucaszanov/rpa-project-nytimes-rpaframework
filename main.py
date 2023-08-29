from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP
from RPA.Robocorp.WorkItems import WorkItems
import os
from get_attributes import GetAttributes
from export_excel import ExportExcel

class Main:

    def __init__(self):

        config_dict = {
          "url_website" : "https://www.nytimes.com/search?query=$TERM&sort=newest",
          "default_search_attribute" : "data-testid",
          "xpath_close_cookies_button" : "expanded-dock-btn-selector",
          "innertext_accept_terms_button" : "continue",
          "xpath_cards" : "search-results",
          "xpath_show_more_button" : "search-show-more-button",
          "xpath_cards_date" : "todays-date",
          "xpath_sections_button" : "search-multiselect-button",
          "xpath_sections_boxes" : "multi-select-dropdown-list",
          "xpath_date" : "todays-date",
          "regex_money_bool" :  "\\$\\d+\\,?\\d*\\.?\\d*|\\d+\\s?dollars|\\d+\\s?USD"
        }

        wi = WorkItems()
        wi.get_input_work_item()
        self.search_phrase = wi.get_work_item_variables("search_phrase")
        self.news_sections = wi.get_work_item_variables("news_sections")
        self.number_months = wi.get_work_item_variables("number_months")

        self.default_search_attribute = config_dict["default_search_attribute"]
        self.xpath_close_cookies_button = config_dict["xpath_close_cookies_button"]
        self.url_website = config_dict["url_website"]
        self.xpath_sections_button = config_dict["xpath_sections_button"]
        self.xpath_sections_boxes = config_dict["xpath_sections_boxes"]

    def clear_output_folder(self):
        print(f'Cleaning output folder')
        if not os.path.exists(os.path.join(os.getcwd(),"output")):
            os.mkdir(os.path.join(os.getcwd(),"output"))

        for file in os.listdir(os.path.join(os.getcwd(),"output")):
            os.remove(os.path.join(os.getcwd(),"output",file))

    def validate_inputs(self):
        print(f'Validating number_months')
        try:
            self.number_months = int(self.number_months)
            print(f'Valid number_months: {str(self.number_months)}')
        except Exception as error:
            print(f'Invalid number_months: {error}')
            return ["error", f"Error validating number_months. Msg: {error}"]
        try:
            self.news_sections = self.news_sections.replace("[", "").replace("]", "").replace(
                " ", "")
            self.news_sections = self.news_sections.split(",")
            print(f'Valid news_section: {str(self.news_sections)}')
        except Exception as error:
            print(f"Error validating news_section. Msg: {error}")
            return ["error", f"Error validating news_section. Msg: {error}"]
        print(f"Inputs validated")
        return ["success",""]

    def get_driver(self):
        self.driver = Selenium()
        self.driver.open_available_browser(self.url_website.replace(
            "$TERM",self.search_phrase.replace(" ","+")))

    def accept_terms(self):
        flag_accept_terms = False
        while not flag_accept_terms:
            elements = self.driver.find_elements("tag:button")
            for element in elements:
                if element.text.lower() == "continue":
                    element.click()
                    print(f'Button {element} clicked')
                    flag_accept_terms = True

    def close_cookies(self):
        flag_accept_cookies = False
        while not flag_accept_cookies:
            try:
                elements = self.driver.find_elements(f"xpath://button"
                                      f"[@{self.default_search_attribute}="
                                      f"'{self.xpath_close_cookies_button}']")
                elements[0].click()
                print(f'Button {elements[0]} clicked')
                flag_accept_cookies=True
            except:
                print(f'Accept cookies button not found yet')

    def download_pics(self, url, filename):
        if '.jpg' in filename.lower():
            try:
                HTTP().download(url=url, target_file=filename, overwrite=True)
            except Exception as error:
                print(f'Not possible to download pic {filename} from url {url}. Msg: {error}')
        else:
            try:
                HTTP().download(url=url, target_file=filename+".jpg", overwrite=True)
            except Exception as error:
                print(f'Not possible to download pic {filename} from url {url}. Msg: {error}')

    def filter_sections(self):
        print(f'Filtering sections: {self.news_sections}')
        flag_filter_sections_button = False
        while not flag_filter_sections_button:
            try:
                sections_button = self.driver.find_elements(f"xpath://button"
                     f"[@{self.default_search_attribute}='{self.xpath_sections_button}']")
                sections_button[0].click()
                flag_filter_sections_button = True
            except Exception as error:
                msg = f'Error filtering sections: {error}'
                print(msg)
                return ["error", msg]
        try:
            search_result_elements = self.driver.find_elements(f"xpath://ul"
                       f"[@{self.default_search_attribute}='{self.xpath_sections_boxes}']/li")
        except Exception as error:
            msg = f'Error filtering sections: {error}'
            print(msg)
            return ["error", msg]
        if search_result_elements==[]:
            return ["error", f"No sections available. No results"]
        for element in search_result_elements:
            try:
                section = element.text
                section = ''.join((x for x in section if not x.isdigit()))
                if section.lower() in [x.lower() for x in self.news_sections]:
                    print(f'Selecting {section}')
                    element.click()
                else:
                    print(f'Section {section} available but not selected')
            except Exception as error:
                msg = f'Error filtering sections. Msg: {error}'
                print(msg)
                return ["error", msg]
        print('-'*50)
        return ["success", f""]

    def main(self):
        print(f'\n============================= Execution Initialized =============================\n')
        self.clear_output_folder()
        validate_inputs_ = self.validate_inputs()
        if validate_inputs_[0] != "success":
            print(f"Error: {validate_inputs_[1]}")
            return f"Error: {validate_inputs_[1]}"
        self.get_driver()
        print(f'Accepting terms')
        self.accept_terms()
        print('Accepting cookies')
        self.close_cookies()
        print(f'Search phrase: {self.search_phrase}')
        filter_sections_ = self.filter_sections()
        if filter_sections_[0] != "success":
            print(f"Error: {filter_sections_[1]}")
            return f"Error: {filter_sections_[1]}"
        list_data = GetAttributes(self.driver).main()
        date_criteria = ExportExcel().get_month_date_criteria()
        for data in list_data:
            if f'{data["datetime"].year}-{data["datetime"].month}-{data["datetime"].day}'>=\
             f'{date_criteria.year}-{date_criteria.month}-{date_criteria.day}':
                print(f'Collected data: {data}')
                print(f'Downloading pic: {data["pic_file_name"]}')
                self.download_pics(data["pic_url"],os.path.join(
                    os.getcwd(),'output',f'{data["pic_file_name"]}'))
        print(f'Exporting results to Excel file: output.xlsx')
        ExportExcel().export_excel_file(list_data, os.path.join(
            os.getcwd(),"output","output.xlsx"))
        print(f'\n============================= Execution Finalized =============================\n')

if __name__ == "__main__":
    Main().main()
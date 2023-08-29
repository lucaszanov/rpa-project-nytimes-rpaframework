from RPA.Robocorp.WorkItems import WorkItems
from datetime import datetime, date
import re
from dateutil.relativedelta import relativedelta
import os

class GetAttributes:

    def __init__(self, driver):
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

        workitems = WorkItems()
        workitems.get_input_work_item()
        variables = workitems.get_work_item_variables()

        self.search_phrase = variables["search_phrase"]
        self.news_sections = variables["news_sections"]
        self.number_months = variables["number_months"]

        self.driver = driver
        self.regex_money_bool = config_dict["regex_money_bool"]
        self.number_months = int(self.number_months)
        self.default_search_attribute = config_dict["default_search_attribute"]
        self.xpath_cards = config_dict["xpath_cards"]
        self.xpath_show_more_button = config_dict["xpath_show_more_button"]
        self.xpath_date = config_dict["xpath_date"]

        self.list_data = []
        self.dict_month = {
            "Jan.": 1,
            "Feb.": 2,
            "March": 3,
            "April": 4,
            "May": 5,
            "June": 6,
            "July": 7,
            "Aug.": 8,
            "Sept.": 9,
            "Oct.": 10,
            "Nov.": 11,
            "Dec.": 12
        }

    def get_month_date_criteria(self):
        if self.number_months == 0 or self.number_months == 1:
            return date(datetime.now().year, datetime.now().month, 1)
        else:
            return date(datetime.now().year, datetime.now().month, 1)-relativedelta(months=
                                                         self.number_months-1)

    def get_last_date_available(self):
        flag_elements_cards = False
        search_result_elements = []
        while not flag_elements_cards and len(search_result_elements) == 0:
            try:
                search_result_elements = self.driver.find_elements(f"xpath://ol"
                          f"[@{self.default_search_attribute}='{self.xpath_cards}']/li")
                flag_elements_cards = True
            except Exception as error:
                print(f'Error getting last date available: {error}')
        date_ = ""
        for index in range(len(search_result_elements)-1, -1, -1):
            if date_ == "":
                try:
                    date_ = self.driver.find_elements("tag:span", search_result_elements[index])[0].text
                    try:
                        if "ago" in date_:
                            month = datetime.now().month
                            day = datetime.now().day
                            year = datetime.now().year
                            date_ = date(year, month, day)
                        else:
                            data_split = date_.split(" ")
                            if len(data_split) == 2:
                                day = int(data_split[1])
                                month = self.dict_month[data_split[0]]
                                year = datetime.now().year
                                date_ = date(year, month, day)
                            else:
                                day = int(data_split[1])
                                month = self.dict_month[data_split[0]]
                                year = int(data_split[2])
                                date_ = date(year, month, day)
                        return date_
                    except Exception as error:
                        print(f'Error getting last date available: {error}')
                except Exception as error:
                    print(f'Error getting last date available: {error}')

    def preparing_cards_to_extract(self):
        date_criteria = self.get_month_date_criteria()
        last_date_available = self.get_last_date_available()
        while type(last_date_available) == type(None):
            last_date_available = self.get_last_date_available()

        while date_criteria <= last_date_available:
            click_show_more_results_ = self.click_show_more_results()
            if click_show_more_results_[0] == "error":
                return ["success", f""]
            last_date_available = self.get_last_date_available()
        return ["success", f""]

    def get_dates(self):
        print('Getting dates')
        for data in self.list_data:
            try:
                if "ago" in data["date"]:
                    data["month"] = datetime.now().month
                    data["day"] = datetime.now().day
                    data["year"] = datetime.now().year
                    data["datetime"] = date(data["year"], data["month"], data["day"])
                else:
                    data_split = data["date"].split(" ")
                    if len(data_split) == 2:
                        data["day"] = int(data_split[1])
                        data["month"] = self.dict_month[data_split[0]]
                        data["year"] = datetime.now().year
                        data["datetime"] = date(data["year"], data["month"], data["day"])
                    else:
                        data["day"] = int(data_split[1])
                        data["month"] = self.dict_month[data_split[0]]
                        data["year"] = int(data_split[2])
                        data["datetime"] = date(data["year"], data["month"], data["day"])
            except Exception as error:
                print(f'Error getting dates: {error}')

    def click_show_more_results(self):
        print('Click in show more results')
        try:
            show_more_button = self.driver.find_elements(f"xpath://button"
                        f"[@{self.default_search_attribute}='{self.xpath_show_more_button}']")
            show_more_button[0].click()
            return ["success", f""]
        except Exception as error:
            print(f"No button available. Msg: {error}")
            return ["error", f"No button available. Msg: {error}"]

    def get_info_card(self):
        print('Getting info from cards')
        search_result_elements = self.driver.find_elements(f"xpath://ol"
                f"[@{self.default_search_attribute}='{self.xpath_cards}']/li")
        for element in search_result_elements:
            try:
                title = self.driver.find_elements("tag:h4", element)[0].text
                description = self.driver.find_elements("tag:p", element)[1].text
                pic_url = self.driver.find_elements("tag:img", element)[0].get_attribute("src")
                pic_file_name = self.driver.find_elements("tag:img", element)[0].get_attribute("srcset")
                pic_file_name = pic_file_name.split(' ')[0].split('/')[-1]
                date = self.driver.find_elements("tag:span", element)[0].text
                self.list_data.append(
                    {"title": title,
                     "description": description,
                     "date": date,
                     "pic_url": pic_url,
                     "pic_file_name": pic_file_name,
                     "day": "",
                     "month": "",
                     "year": "",
                     "money_bool": False,
                     "count_search_phrase": 0
                }
                )
                print(f'Collected info from card: {self.list_data[-1]}')
            except Exception as error:
                msg = f'Error extracting info from card. Msg: {error}'
                print(msg)
        self.get_dates()
        self.get_money_bool()
        self.get_count_sf_title_description()
        return self.list_data

    def get_count_sf_title_description(self):
        print('Counting search phrases in title or description')
        for data in self.list_data:
            try:
                data["count_search_phrase"] = \
                    len(re.findall(fr"\b{self.search_phrase.lower()}\b", data["description"].lower())) + \
                    len(re.findall(fr"\b{self.search_phrase.lower()}\b", data["title"].lower()))
            except Exception as error:
                print(f'Error getting search phrase counting: {error}')

    def get_money_bool(self):
        '''
        Possible formats:
        $11.1 | $111,111.11 | 11 dollars | 11 USD"
        :return:
        '''
        print('Getting bool for money occurences in title and description')
        for data in self.list_data:
            try:
                if len(re.findall(fr"{self.regex_money_bool}", data["description"]))+ \
                        len(re.findall(fr"{self.regex_money_bool}", data["title"])) > 0:
                    data["money_bool"]=True
            except Exception as error:
                print(f'Error getting money occurences (bool): {error}')

    def main(self):
        self.preparing_cards_to_extract()
        return self.get_info_card()
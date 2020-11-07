import scrapy

from scrapy.selector import Selector

from selenium.webdriver.common.keys import Keys

from scrapy_selenium import SeleniumRequest

from time import sleep, time


class TrendspainSpider(scrapy.Spider):
    name = 'trendSpain'

    regions = {
        'Galicia': 'GA',
        'Navarre': 'NC',
        'Community of Madrid': 'MD',
        'Castile-La Mancha': 'CM',
        'La Rioja': 'RI',
        'Castile and León': 'CL',
        'Region of Murcia': 'MC',
        'Valencian Community': 'VC',
        'Extremadura': 'EX',
        'Asturias': 'AS',
        'Aragon': 'AR',
        'Andalusia': 'AN',
        'Cantabria': 'CB',
        'Basque Country': 'PV',
        'Catalonia': 'CT',
        'Balearic Islands': 'IB',
        'Canary Islands': 'CN'
    }

    keywords = {
        'ES': {},
        'GA': {},
        'NC': {},
        'MD': {},
        'CM': {},
        'RI': {},
        'CL': {},
        'MC': {},
        'VC': {},
        'EX': {},
        'AS': {},
        'AR': {},
        'AN': {},
        'CB': {},
        'PV': {},
        'CT': {},
        'IB': {},
        'CN': {}}

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'

    def start_requests(self):
        yield SeleniumRequest(url='https://trends.google.com/trends/?geo=ES',
                              wait_time=1,
                              callback=self.parse,
                              dont_filter=True,
                              headers={'User-Agent': self.user_agent})

    def parse(self, response):
        driver = response.meta['driver']
        driver.set_window_position(0, 0)
        driver.set_window_size(1920, 1080)

        # search for a specific keyword
        self.search_keyword(driver, 'Vetusta Morla')

        # change time range to 2004-present
        self.change_time_range(driver)

        # extract for spain
        self.keywords['ES'] = self.parse_page(driver)

        page = 1
        for i in range(1, 18):
            print('-----{}-----'.format(i))
            r = i % 5
            for _ in range(1, page):
                while True:
                    try:
                        print(
                            '-----------------------no next region--------------------')
                        print(page)
                        driver.find_element_by_xpath(
                            '//div[@class="widget-container flex-100"]//button[@aria-label="Next"]').click()
                        break
                    except:
                        pass
                sleep(1)

            if(r == 0):
                page += 1
                r = 5
            driver.find_element_by_xpath(
                '(//div[@class="fe-atoms-generic-content-container"])[2]/div[{}]'.format(r)).click()
            sleep(3)
            region_code = driver.current_url.split('-')[1].split('&')[0]
            p = self.parse_page(driver)
            print('----------{}-----------'.format(region_code))
            print(p)
            sleep(10)
            self.keywords[region_code] = p
            driver.execute_script("window.history.go(-1)")
            sleep(3)

        yield self.keywords

    def parse_page(self, driver):
        topic_error_xpath = '//div[@class="widget-container flex-50"][1]//div[@class="widget-error"]'
        topic_text_xpath = '//div[@class="widget-container flex-50"][1]//div[@class="item"]//span/text()'
        topic_next_btn_xpath = '//div[@class="widget-container flex-50"][1]//button[@aria-label="Next"]'

        queries_error_xpath = '//div[@class="widget-container flex-50"][2]//div[@class="widget-error"]'
        queries_text_xpath = '//div[@class="widget-container flex-50"][2]//div[@class="item"]//span/text()'
        queries_next_btn_xpath = '//div[@class="widget-container flex-50"][2]//button[@aria-label="Next"]'

        topic_type_btn = '(//div[@class="widget-container flex-50"][1]//ng-include)[2]'
        queries_type_btn = '(//div[@class="widget-container flex-50"][2]//ng-include)[2]'

        # TOPIC
        topics = self.extract_keywords(
            driver, topic_text_xpath, topic_error_xpath, topic_next_btn_xpath)

        # QUERIES
        queries = self.extract_keywords(
            driver, queries_text_xpath, queries_error_xpath, queries_next_btn_xpath)

        # Raising Topics
        # raising_topics = self.extract_keywords(
        #     driver, topic_text_xpath, topic_error_xpath, topic_next_btn_xpath)

        # # Change to top topics
        # self.change_type(driver, topic_type_btn)

        # # Top Topics
        # top_topics = self.extract_keywords(
        #     driver, topic_text_xpath, topic_error_xpath, topic_next_btn_xpath)

        # Raising Queries
        # raising_queries = self.extract_keywords(
        #     driver, queries_text_xpath, queries_error_xpath, queries_next_btn_xpath)

        # Change to top queries
        # self.change_type(driver, queries_type_btn)

        # Top Queries
        # top_queries = self.extract_keywords(
        #     driver, queries_text_xpath, queries_error_xpath, queries_next_btn_xpath)

        return {
            'topic': topics,
            'queries': queries
            # 'raising_topics': raising_topics,
            # 'top_topics': top_topics,
            # 'raising_queries': raising_queries,
            # 'top_queries': top_queries
        }

    def search_keyword(self, driver, keyword):
        input_xpath = '(//autocomplete)[2]//input'
        search_input = driver.find_element_by_xpath(input_xpath)
        search_input.send_keys(keyword)
        search_input.send_keys(Keys.ENTER)
        sleep(6)

    def last_menu(self, driver):
        menu_len = len(driver.find_elements_by_xpath('//md-select-menu'))

        return '(//md-select-menu)[{}]'.format(menu_len)

    def change_time_range(self, driver):
        time_range_selector_xpath = '//custom-date-picker//md-select'
        y2004_present_xpath = '/md-content/md-option[9]'

        driver.find_element_by_xpath(time_range_selector_xpath).click()
        sleep(1)

        full_y2004_present_xpath = self.last_menu(driver) + y2004_present_xpath

        driver.find_element_by_xpath(full_y2004_present_xpath).click()
        sleep(5)

    def extract_keywords(self, driver, keyword_xpath, error_xpath, next_btn_xpath):
        keywords = []

        while True:
            try:
                res_obj = Selector(text=driver.page_source)
                if(res_obj.xpath(error_xpath)):
                    break

                keywords += res_obj.xpath(keyword_xpath).getall()

                while True:
                    try:
                        next_btn = driver.find_element_by_xpath(next_btn_xpath)

                        if(next_btn.get_attribute('disabled')):
                            break

                        next_btn.click()
                        sleep(1)

                        res_obj = Selector(text=driver.page_source)
                        keywords += res_obj.xpath(keyword_xpath).getall()
                    except:
                        break
                break
            except:
                pass
        return keywords

    def change_type(self, driver, keyword_type_btn_xpath, t="top"):
        raising_btn = self.last_menu(driver) + '/md-content/md-option[1]'
        top_btn = self.last_menu(driver) + '/md-content/md-option[2]'

        if(t == 'raising'):
            type_btn_xpath = raising_btn

        type_btn_xpath = top_btn
        try:
            keyword_type_btn = driver.find_element_by_xpath(
                keyword_type_btn_xpath)
            keyword_type_btn.click()
            sleep(1)

            type_btn = driver.find_element_by_xpath(type_btn_xpath)
            if(type_btn.get_attribute('disabled') == 'disabled'):
                return False
            type_btn.click()
            sleep(1)
        except:
            pass

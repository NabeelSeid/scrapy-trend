import os

import scrapy

import pandas as pd

from scrapy.selector import Selector

from selenium.webdriver.common.keys import Keys

from scrapy_selenium import SeleniumRequest

from time import sleep, time


class TimelinesSpider(scrapy.Spider):
    name = 'timelines'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
    # user_agent = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'

    def start_requests(self):
        yield SeleniumRequest(url='https://trends.google.com/trends/?geo=ES',
                              wait_time=1,
                              callback=self.parse,
                              dont_filter=True,
                              headers={'User-Agent': self.user_agent})

    def parse(self, response):

        d1 = [120, 201]
        d2 = [221, 301]
        d3 = [403, 501]
        d4 = [309, 401]

        d = d1

        keywords = pd.read_excel(
            '/home/ns/Desktop/timelines/Keywords Music.xlsx')['Band'][d[0]:d[1]]

        driver = response.meta['driver']
        driver.set_window_position(0, 0)
        driver.set_window_size(1920, 1080)

        keyword = 'gogo'

        sleep(4)

        # search for a specific keyword
        self.search_keyword(driver, keyword)

        # change time range to 2004-present
        self.change_time_range(driver)

        for keyword in keywords:
            print('======================={}======================'.format(keyword))
            self.wait_page_load(driver)

            search_input = driver.find_element_by_xpath(
                '(//input[@type="search"])[1]')
            search_input.click()
            search_input.send_keys(Keys.SHIFT, Keys.END, Keys.BACK_SPACE)
            search_input.send_keys(keyword)
            search_input.send_keys(Keys.ENTER)

            self.wait_page_load(driver)

            self.download_csv(driver, keyword, 'ES')

            # class name chaged if region exced 5
            paged_region = ' mobile-container-height'

            try:
                pag_text = driver.find_element_by_xpath(
                    '(//div[@class="widget-container flex-100"]//span)[10]').text
                regions = int(pag_text.split()[-2])
                paged_region = ''
            except:
                res_obj = Selector(text=driver.page_source)
                regions = len(res_obj.xpath(
                    '//div[@class="widget-container flex-100"]//span/text()').getall())

            region_page = 1
            for region_i in range(1, regions):
                print('-----{}-----'.format(region_i))
                print('======================={}======================'.format(keyword))
                self.wait_region_load(driver)
                print('---------end region load-----------')
                region_i = region_i % 5

                self.next_regions(driver, region_page)
                print('---------next region end-----------')

                if(region_i == 0):
                    region_page += 1
                    region_i = 5

                driver.find_element_by_xpath(
                    '//div[@class="widget-container flex-100"]//div[@class="fe-related-queries fe-atoms-generic-container"]//div[@class="fe-atoms-generic-content-container{}"]/div[{}]'.format(paged_region, region_i)).click()
                self.wait_page_load(driver)
                code = driver.current_url.split('-')[1].split('&')[0]
                self.download_csv(driver, keyword, code)

                driver.execute_script("window.history.go(-1)")

    def wait_page_load(self, driver):
        sleep(1)
        download_btns = len(driver.find_elements_by_xpath(
            '//div[@class="widget-container flex-100"]//button[@class="widget-actions-item export"]'))

        while download_btns < 2:
            sleep(0.5)
            download_btns = len(driver.find_elements_by_xpath(
                '//div[@class="widget-container flex-100"]//button[@class="widget-actions-item export"]'))

    def wait_region_load(self, driver):
        while True:
            try:
                sleep(0.5)
                region_div = len(driver.find_elements_by_xpath(
                    '//div[@class="widget-container flex-100"]//div[@class="fe-related-queries fe-atoms-generic-container"]'))
                if(region_div > 0):
                    break
            except:
                pass

    def download_csv(self, driver, keyword, code):
        # download
        driver.find_element_by_xpath(
            '(//div[@class="widget-container flex-100"]//button[@class="widget-actions-item export"])[1]').click()

        d_3 = '/home/ns/Downloads/'      # 3
        d_1 = '/home/ns/Desktop/two_th/'  # 1
        d_2 = '/home/ns/Desktop/thr_th/'  # 2
        d_4 = '/home/ns/Desktop/for_th/'  # 4

        d = d_1

        while not os.path.exists('{}multiTimeline.csv'.format(d)):
            sleep(0.5)

        # rename
        newfilename = '/home/ns/Desktop/multiTimelines/' + \
            keyword.replace('/', '') + '_{}.csv'.format(code)

        os.rename('{}multiTimeline.csv'.format(d), newfilename)

    def next_regions(self, driver, region_page):
        for _ in range(1, region_page):
            while True:
                try:
                    print(
                        '-----------------------no next region--------------------')
                    print(region_page)
                    driver.find_element_by_xpath(
                        '//div[@class="widget-container flex-100"]//button[@aria-label="Next"]').click()
                    break
                except:
                    pass
            sleep(0.5)

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

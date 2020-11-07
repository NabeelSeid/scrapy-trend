import scrapy

from scrapy.selector import Selector

from selenium.webdriver.common.keys import Keys

from scrapy_selenium import SeleniumRequest

from time import sleep, time


class ProductsSpider(scrapy.Spider):
    name = 'products'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'

    def start_requests(self):
        begin = time()

        for page in range(1, 65):
            print(page)
            print('---------------------------------')
            yield SeleniumRequest(url='https://certificates.vontobel.com/SE/EN/Products/Find_Products/Leverage_products/',
                                  wait_time=1,
                                  callback=self.parse,
                                  meta={'page': page},
                                  dont_filter=True,
                                  headers={'User-Agent': self.user_agent})

        end = time()
        print(f"Total runtime of the program is {end - begin}")

    def parse(self, response):
        page = response.meta['page']
        driver = response.meta['driver']

        while page == 1:
            print('accept btn {}'.format(page))
            sleep(1)
            try:
                btn_accept = driver.find_element_by_xpath(
                    '//a[@id="ctl00_DisclaimerManager_ctl00_ctl00_Accept"]')
                btn_accept.click()
                break
            except:
                pass

        # progress_indicator = driver.find_element_by_xpath(
        #     '//div[@id="ctl00_ctl20_ctl04_ctl21"]')

        # while progress_indicator.is_displayed():
        #     sleep(1)

        init_pages = response.xpath(
            '(//span[@class="title"])[2]/text()').get().strip()
        first_isin = response.xpath('(//tbody//a)[4]/text()').get().strip()

        while page==1:
            print('100 btn {}'.format(page))
            sleep(1)
            try:
                btn_100 = driver.find_element_by_xpath(
                    '//div[@id="ctl00_ctl20_ctl04_PageSizeChooser"]/ul/li[3]/a')
                btn_100.click()
                break
            except:
                pass

        res_obj = Selector(text=driver.page_source)
        pages_100 = res_obj.xpath(
            '(//span[@class="title"])[2]/text()').get().strip()

        while init_pages == pages_100:
            sleep(1)
            res_obj = Selector(text=driver.page_source)
            pages_100 = res_obj.xpath(
                '(//span[@class="title"])[2]/text()').get().strip()

        if page > 1:
            while True:
                print('input btn {}'.format(page))
                sleep(1)
                try:
                    page_input = driver.find_element_by_xpath(
                        '//input[@id="ctl00_ctl20_ctl04_Grid_TopPaging_CurrentPage"]')
                    page_input.clear()
                    page_input.send_keys(page)

                    page_input.send_keys(Keys.ENTER)
                    break
                except:
                    pass

            res_obj = Selector(text=driver.page_source)
            post_isin = res_obj.xpath('(//tbody//a)[4]/text()').get().strip()
            # print(first_isin)
            # print(post_isin)
            while first_isin == post_isin:
                sleep(1)
                res_obj = Selector(text=driver.page_source)
                post_isin = res_obj.xpath(
                    '(//tbody//a)[4]/text()').get().strip()

        # while True:
        #     print('body btn {}'.format(page))
        #     try:
        #         res_obj = Selector(text=driver.page_source)
        #         products = res_obj.xpath('//tbody/tr')
        #         if(len(products) == 100):
        #             break
        #     except:
        #         pass

        products = res_obj.xpath('//tbody/tr')

        for product in products:
            product_desc = product.xpath('./td')
            symbol = product_desc[1].xpath('./a/text()').get().strip()
            isin = product_desc[3].xpath('./a/text()').get().strip()
            iri = product_desc[4].xpath('./a/text()').get().strip()
            factor = product_desc[5].xpath('./a/text()').get().strip()
            p_type = product_desc[6].xpath('./a/text()').get().strip()
            cur = product_desc[7].xpath('./a/text()').get().strip()
            # .xpath('./a/span/span/text()').get().strip()
            bid = self.extract_bid_ask(product_desc[8])
            # .xpath('./a/span/span/text()').get().strip()
            ask = self.extract_bid_ask(product_desc[9])

            yield {
                'symbol': symbol,
                'isin': isin,
                'iri': iri,
                'factor': factor,
                'type': p_type,
                'cur': cur,
                'bid': bid,
                'ask': ask}

        # btn_next = driver.find_element_by_xpath('(//a[@class="next"])[1]')
        # btn_next.click()

        # sleep(4)

        # res_obj = Selector(text=driver.page_source)

        # products = res_obj.xpath('//tbody/tr').getall()
        # print(len(products))

    def extract_bid_ask(self, product_desc):
        value = product_desc.xpath('./a/span/span/text()').get()
        if(value):
            return value.strip()
        else:
            return None

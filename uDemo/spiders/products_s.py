import scrapy

from scrapy.selector import Selector

from selenium.webdriver.common.keys import Keys

from scrapy_selenium import SeleniumRequest

from time import sleep, time


class ProductsSpider(scrapy.Spider):
    name = 'products_s'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'

    def start_requests(self):
        yield SeleniumRequest(url='https://certificates.vontobel.com/SE/EN/Products/Find_Products/Leverage_products/',
                              wait_time=1,
                              callback=self.parse,
                              dont_filter=True,
                              headers={'User-Agent': self.user_agent})

    def parse(self, response):
        driver = response.meta['driver']

        # !Accept Button
        btn_accept = driver.find_element_by_xpath(
            '//a[@id="ctl00_DisclaimerManager_ctl00_ctl00_Accept"]')
        btn_accept.click()

        # !page number before 100
        init_pages = response.xpath(
            '(//span[@class="title"])[2]/text()').get().strip()

        # !100 per page button
        btn_100 = driver.find_element_by_xpath(
            '//div[@id="ctl00_ctl20_ctl04_PageSizeChooser"]/ul/li[3]/a')
        btn_100.click()

        # !Check if page has loaded 100 products
        res_obj = Selector(text=driver.page_source)
        pages_100 = res_obj.xpath(
            '(//span[@class="title"])[2]/text()').get().strip()

        while init_pages == pages_100:
            sleep(1)
            res_obj = Selector(text=driver.page_source)
            pages_100 = res_obj.xpath(
                '(//span[@class="title"])[2]/text()').get().strip()

        # pages = int(pages_100.split()[-1]) + 1

        while True:
            try:
                res_obj = Selector(text=driver.page_source)

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

                current_page = res_obj.xpath(
                    '//input[@id="ctl00_ctl20_ctl04_Grid_TopPaging_CurrentPage"]/@value').get().strip()

                next_btn = driver.find_element_by_xpath(
                    '//span[@id="ctl00_ctl20_ctl04_Grid_TopPaging"]//a[@class="next"]')
                next_btn.click()

                res_obj = Selector(text=driver.page_source)
                next_page = res_obj.xpath(
                    '//input[@id="ctl00_ctl20_ctl04_Grid_TopPaging_CurrentPage"]/@value').get().strip()
                while current_page == next_page:
                    print("{} == {}".format(current_page, next_page))
                    sleep(1)
                    res_obj = Selector(text=driver.page_source)
                    next_page = res_obj.xpath(
                        '//input[@id="ctl00_ctl20_ctl04_Grid_TopPaging_CurrentPage"]/@value').get().strip()
            except:
                break

        # for page in range(2, pages):
        #     res_obj = Selector(text=driver.page_source)
        #     first_isin = res_obj.xpath('(//tbody//a)[2]/text()').get().strip()

        #     # !page input box
        #     page_input = driver.find_element_by_xpath(
        #         '//input[@id="ctl00_ctl20_ctl04_Grid_TopPaging_CurrentPage"]')
        #     page_input.clear()
        #     page_input.send_keys(page)

        #     page_input.send_keys(Keys.ENTER)

        #     # !chick if new page has finished loading
        #     res_obj = Selector(text=driver.page_source)
        #     post_isin = res_obj.xpath('(//tbody//a)[2]/text()').get().strip()

        #     while first_isin == post_isin:
        #         print("{} == {}, {}".format(first_isin, post_isin, page))
        #         sleep(1)
        #         res_obj = Selector(text=driver.page_source)
        #         post_isin = res_obj.xpath(
        #             '(//tbody//a)[2]/text()').get().strip()

            # products = res_obj.xpath('//tbody/tr')

            # for product in products:
            #     product_desc = product.xpath('./td')
            #     symbol = product_desc[1].xpath('./a/text()').get().strip()
            #     isin = product_desc[3].xpath('./a/text()').get().strip()
            #     iri = product_desc[4].xpath('./a/text()').get().strip()
            #     factor = product_desc[5].xpath('./a/text()').get().strip()
            #     p_type = product_desc[6].xpath('./a/text()').get().strip()
            #     cur = product_desc[7].xpath('./a/text()').get().strip()
            #     # .xpath('./a/span/span/text()').get().strip()
            #     bid = self.extract_bid_ask(product_desc[8])
            #     # .xpath('./a/span/span/text()').get().strip()
            #     ask = self.extract_bid_ask(product_desc[9])

            #     yield {
            #         'symbol': symbol,
            #         'isin': isin,
            #         'iri': iri,
            #         'factor': factor,
            #         'type': p_type,
            #         'cur': cur,
            #         'bid': bid,
            #         'ask': ask}

    def extract_bid_ask(self, product_desc):
        value = product_desc.xpath('./a/span/span/text()').get()
        if(value):
            return value.strip()
        else:
            return None

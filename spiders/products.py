import scrapy
import json
import time
from shutil import which
from selenium import webdriver
from scrapy.selector import Selector
from scrapy.shell import inspect_response
from selenium.webdriver.chrome.options import Options


with open('flatCategory-2.json') as f:
    categories = json.load(f)


class ProductsSpider(scrapy.Spider):
    name = 'products'
    allowed_domains = ['www.woolworths.com.au']
    start_urls = ['https://www.woolworths.com.au']

    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_path = which("chromedriver")
        self.driver = webdriver.Chrome(
            executable_path=chrome_path, options=chrome_options)
        self.driver.set_window_size(1920, 1080)
        self.driver.get("https://www.woolworths.com.au")
        self.html = self.driver.page_source

    def parse(self, response):
        inspect_response(response, self)
        for category in categories:
            self.driver.get(
                f"https://www.woolworths.com.au/shop/browse{category}")
            time.sleep(7)
            html = self.driver.page_source
            response_obj = Selector(text=html)
            cate, subcat, sub_subcat = category[1:].split("/")
            while True:
                for product in response_obj.xpath("//section[@class='shelfProductTile tile']"):
                    yield {
                        "Category": cate,
                        "Sub Category": subcat,
                        "Sub Sub-Category": sub_subcat or "None",
                        "Product Name": product.xpath(".//a[@class='shelfProductTile-descriptionLink']/text()").get(),
                        "Price": product.xpath(".//span[@class='price-dollars']/text()").get() + '.' + product.xpath(".//span[@class='price-cents']/text()").get(),
                        "Image": product.xpath(".//img[@class='shelfProductTile-image']/@src").get()
                    }
                try:
                    next_page = self.driver.find_element_by_xpath(
                        "//a[@class='paging-next ng-star-inserted']")
                    next_page.click()
                    time.sleep(8)
                except:
                    break

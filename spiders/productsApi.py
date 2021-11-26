import scrapy
import json
import math
from scrapy.shell import inspect_response

with open('flatCategory-4.json') as f:
    categories = json.load(f)


class ProductsapiSpider(scrapy.Spider):
    name = 'productsApi'
    handle_httpstatus_list = [400]
    allowed_domains = ['www.woolworths.com.au']
    start_urls = [
        'https://www.woolworths.com.au/apis/ui/PiesCategoriesWithSpecials']

    def parse(self, response):
        # jsonData = json.loads(response.body)
        # categories = jsonData.get('Categories')
        for category in categories:
            body_data = {
                "categoryId": categories[category],
                "filters": [],
                "formatObject": '{"name": ' + "\""+categories[category] + "\"" + '}',
                "isBundle": 'False',
                "isMobile": 'False',
                "isSpecial": 'False',
                "location": category,
                "pageNumber": '1',
                "pageSize": '36',
                "sortType": "TraderRelevance",
                "token": "",
                "url": category
            }
            cate, subcat, sub_subcat = category[1:].split("/")
            yield scrapy.FormRequest(
                url='https://www.woolworths.com.au/apis/ui/browse/category',
                formdata=body_data,
                callback=self.products,
                meta={"Category": cate, "Sub Category": subcat,
                      "Sub Sub-Category": sub_subcat or "None", "Id": categories[category], "url": category},
                dont_filter=True
            )

    def products(self, response):
        # inspect_response(response, self)
        resp = json.loads(response.body)
        category = response.request.meta['Category']
        sub_category = response.request.meta['Sub Category']
        sub_sub_category = response.request.meta['Sub Sub-Category']
        Id = response.request.meta['Id']
        url = response.request.meta['url']

        try:
            page_no = response.request.meta['page_no']
        except:
            page_no = 1

        body_data = {
            "categoryId": Id,
            "filters": [],
            "formatObject": '{"name": ' + "\"" + Id + "\"" + '}',
            "isBundle": 'False',
            "isMobile": 'False',
            "isSpecial": 'False',
            "location": url,
            "pageNumber": str(page_no+1),
            "pageSize": '36',
            "sortType": "TraderRelevance",
            "token": "",
            "url": url
        }
        bundle = resp.get('Bundles')
        for product in bundle:
            products = product.get('Products') or None
            if products:
                for prod in products:
                    yield {
                        'Category': category,
                        'Sub Category': sub_category,
                        'Sub Sub-Category': sub_sub_category,
                        'Name': prod.get('Name'),
                        'Price': prod.get('Price'),
                        'Discount_Price': float(prod.get('WasPrice')) - float(prod.get('Price')) if float(prod.get('WasPrice')) > 0.0 else 0.0,
                        'Ingredients': prod.get('AdditionalAttributes').get('ingredients'),
                        'Product_Details': prod.get('RichDescription'),
                        'Weight': prod.get('PackageSize'),
                        'Image': prod.get('DetailsImagePaths')
                    }
        total_item = resp.get('TotalRecordCount')
        print(total_item)
        total_page = math.floor((total_item + 35) / 36)
        print(total_page)
        if total_item > 36:
            if page_no < total_page:
                yield scrapy.FormRequest(
                    url='https://www.woolworths.com.au/apis/ui/browse/category',
                    formdata=body_data,
                    callback=self.products,
                    meta={"page_no": page_no+1,
                          "Category": category, "Sub Category": sub_category,
                          "Sub Sub-Category": sub_sub_category or "None", "Id": Id, "url": url
                          },
                    dont_filter=True,
                )
                print(page_no)


# {
# "categoryId": "1_2BE5A2D",
# "filters": [],
# "formatObject": "{\"name\":\"Healthier Frozen Meals\"}",
# "isBundle": false,
# "isMobile": false,
# "isSpecial": false,
# "location": "/shop/browse/freezer/frozen-meals/healthier-frozen-meals",
# "pageNumber": 1,
# "pageSize": 36,
# "sortType": "TraderRelevance",
# "token": "",
# "url": "/shop/browse/freezer/frozen-meals/healthier-frozen-meals"
# }
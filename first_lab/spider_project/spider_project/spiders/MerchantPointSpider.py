import scrapy
from ..items import MerchantPointItem

class MerchantPointSpider(scrapy.Spider):
    name = "merchantpoint"
    start_urls = ['https://merchantpoint.ru/brands/']


    def parse(self, response):
        self.logger.info("Spider stated his job. Wait for a while)")
        brands_tab_url = response.xpath('//a[@class="nav-link"][contains(text(),"Бренды")]/@href').get()

        yield response.follow(brands_tab_url, self.parse_brands_tab)


    def parse_brands_tab(self, response):
        brand_urls = response.xpath('//tbody/tr/td[2]/a/@href').getall()
        for brand_url in brand_urls:
            if brand_url:
                yield response.follow(brand_url, callback=self.parse_brand)

        next_page_url = response.xpath('//a[@class="page-link"][contains(text(),"Вперед")]/@href').get()
        if next_page_url:
            yield response.follow(next_page_url, callback=self.parse_brands_tab)

    def parse_brand(self, response : scrapy.http.Response):
        org_name = response.xpath('//h1[@class="h2"]/text()').get()
        org_description = response.xpath('//div[@id="home"]/div/div/div/div/div/div/p[2]/text()').get()

        merchant_points_urls = response.xpath('//*[@id="terminals"]/div/div/div/div/div/div/table/tbody/tr/td[2]/a/@href').extract()
        for point_url in merchant_points_urls:
            if point_url:
                yield response.follow(url=point_url,
                                      callback=self.parse_merchant_point,
                                      cb_kwargs={'org_name': org_name, 'org_description': org_description})


    def parse_merchant_point(self, response: scrapy.http.Response, org_name, org_description):
        item = MerchantPointItem()
        item['merchant_name'] = self.prepare_string(response.xpath('//div[@id="home"]/div/div/div/div/div[2]/p[2]/text()').get())
        item['mcc'] = response.xpath('//div[@id="home"]/div/div/div/div/div[2]/p[4]/a/text()').get()
        item['address'] = self.prepare_string(response.xpath('//div[@id="home"]/div/div/div/div/div[2]/p[7]/text()').get())
        item['geo_coordinates'] = response.xpath('//div[@id="home"]/div/div/div/div/div[2]/p[8]/text()').get()
        item['org_name'] = org_name
        item['org_description'] = org_description
        item['source_url'] = response.url

        if not self.validate_required_fields(item):
            return

        yield item


    def prepare_string(self, string: str) -> str:
        return None if not string else string.replace('—', '').replace('-', '').strip()


    def validate_required_fields(self, item: MerchantPointItem) -> bool:
        if not item['merchant_name'] or \
                not item['mcc'] or \
                not item['org_name'] or \
                not item['org_description'] or \
                not item['source_url']:
            return False

        return True
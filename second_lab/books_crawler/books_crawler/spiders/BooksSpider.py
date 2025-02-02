import logging

import scrapy

from scrapy.spiders import SitemapSpider
from ..items import BookItem


class BooksSpider(SitemapSpider):
    name = 'books'
    sitemap_urls = ['https://www.chitai-gorod.ru/sitemap.xml']
    sitemap_follow = ['authors']
    sitemap_rules = [
        ('/author/', 'parse_author_page')
    ]


    def parse_author_page(self, response: scrapy.http.Response):
        author = self.strip_safely(response.xpath('//h1[@class="app-catalog-page__title"]/text()').get())
        books_urls = set(response.xpath('//a[contains(@href, "/product/")]/@href').getall())
        rating_count = None
        rating_value = None
        for book_url in books_urls:
            yield response.follow(
                book_url,
                callback=self.parse_book_page,
                cb_kwargs={'author': author, 'rating_count': rating_count, 'rating_value': rating_value})

        next_page_url = response.xpath('//a[contains(@class, "pagination__button--icon")]/@href').get()
        if next_page_url:
            yield response.follow(next_page_url, callback=self.parse_author_page)


    def parse_book_page(self, response, author, rating_count, rating_value):
        item = BookItem()

        logging.info('PARSEBOOK')

        # Пример XPath выражений (нужно будет адаптировать под реальную структуру страницы)
        item['title'] = self.strip_safely(response.xpath('//h1[@class="detail-product__header-title"]/text()').get())  # +
        item['author'] = author
        item['description'] = self.strip_safely(response.xpath('//div[@class="product-description-short__text"]/text()').get())
        item['price_amount'] = self.get_price_amount(response.xpath('//span[@class="price-val"]/text()').get())
        item['price_currency'] = response.xpath('//meta[@itemprop="priceCurrency"]/@content').get()
        item['rating_value'] = rating_value
        item['rating_count'] = rating_count
        item['publication_year'] = self.strip_safely(response.xpath('//span[@itemprop="datePublished"]/text()').get())  # +
        item['isbn'] = self.strip_safely(response.xpath('//span[@itemprop="isbn"]/text()').get())  # +
        item['pages_cnt'] = self.strip_safely(response.xpath('//span[@itemprop="numberOfPages"]/text()').get())  # +
        item['publisher'] = self.strip_safely(response.xpath('//a[@itemprop="publisher"]/text()').get())
        item['book_cover'] = self.strip_safely(response.xpath('//img[@class="product-info-gallery__poster"]/@src').get())
        item['source_url'] = response.url

        logging.info('VALIDATE: %s', item)
        if not self.validate_required_fields(item):
            logging.info('INVALID BOOK')
            return
        logging.info('SAVE: %s', item)


        yield item


    def validate_required_fields(self, item: BookItem):
        if not item['title'] \
            or not item['publication_year'] \
            or not item['isbn'] \
            or not item['pages_cnt'] \
            or not item['source_url']:
            return False
        return True

    def strip_safely(self, string):
        return None if not string else string.strip()

    def get_price_amount(self, string):
        return None if not string else string[0:-2]

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bankwithlnb.items import Article


class BankwithlnbSpider(scrapy.Spider):
    name = 'bankwithlnb'
    start_urls = ['https://www.bankwithlnb.com/tools-tech/articles']

    def parse(self, response):
        links = response.xpath('//a[@class="button-2 no-margin right"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@title="Go to next page"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//main//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="header-5 xtra-thin-margin-bottom"]/text()').get()
        if date:
            date = " ".join(date.split()[2:])

        content = response.xpath('//div[@class="body field"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()

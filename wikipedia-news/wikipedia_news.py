import scrapy
from scrapy.crawler import CrawlerProcess

class WikiSpider(scrapy.Spider):
    name = 'wikispider'

    start_urls = [ 'https://en.wikipedia.org/wiki/Main_Page' ]
    found_events = []

    def parse(self, response):
        for index, li in enumerate(response.xpath('/html/body/div[3]/div[3]/div[5]/div[1]/table/tbody/tr/td[3]/div[1]/ul/li'), start=1):
            news_blurb = li.xpath('string(.)').get()[0]

            self.found_events.append(f"{index}. {news_blurb.replace('(pictured)', '')}")

if __name__ == "__main__":
    process = CrawlerProcess({ 'LOG_LEVEL': 'ERROR' })
    process.crawl(WikiSpider)
    spider = next(iter(process.crawlers)).spider
    process.start()

    for event in spider.found_events: print(event)
# -*- coding: utf-8 -*-
import scrapy
import json
import requests


class EngadgetnewsSpider(scrapy.Spider):
    name = 'EngadgetNews'

    def get_num_pages(self):
        url = "https://www.engadget.com/a/search?filters[page][type][]=articles&sort_field[page]=published_at"
        response = requests.get(url)
        return json.loads(response.text)["info"]["page"]["num_pages"]

    def clean_output_file(self):
        open('articles.json', 'w').close()

    def create_page_url(self, page):
        return f"https://www.engadget.com/a/search?filters[page][type][]=articles&sort_field[page]=published_at&page={page}"

    def get_articles_for_page(self, page):
        response = requests.get(self.create_page_url(page))
        return json.loads(response.text)["records"]["page"]

    def extract_text(self, response):
        return " ".join(response.css('.article-text > p *::text').getall())

    def get_article_urls(self, pages):
        for page in range(1, pages + 1):
            for article in self.get_articles_for_page(page):
                yield article['url']

    def start_requests(self):
        self.clean_output_file()
        total_num_pages = self.get_num_pages()

        for url in self.get_article_urls(total_num_pages):
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        yield {
            'text': self.extract_text(response)
        }

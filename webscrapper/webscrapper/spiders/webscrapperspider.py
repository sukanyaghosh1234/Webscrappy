import json
import scrapy
import os


class webscrapperspider(scrapy.Spider):
    name = "webscrapper"
    start_urls = ["https://www.uvp-verbund.de/freitextsuche?rstart=0&currentSelectorPage=1"]

    main = 1
    def parse(self, response):
        pageNo = response.url.split("/")[-1].split("=")[-1]
        filename = "Page-" + pageNo + '.html'

        self.dir1 = f"Germany{self.main}"
        os.makedirs(self.dir1, exist_ok=True)

        with open(f"{self.dir1}/Germany{self.main}.html", 'wb') as f:
            f.write(response.body)

        self.count = 1

        for link in response.xpath("//div[@class='teaser-data search']/a/@href"):
            yield response.follow(link.get(), callback=self.parse_subpage)

        self.main += 1

        next_page_url = response.css('a.icon.small-button')[-2].attrib['href']
        if next_page_url is not None:
            yield response.follow(next_page_url, callback=self.parse)

    def parse_subpage(self, response):

        project_folder = f"{self.dir1}/Subpage{self.count}"
        self.count += 1
        os.makedirs(project_folder, exist_ok=True)

        jsonDict = {
            'title': response.css('div.banner-noimage h1::text').get().strip(),
            'date': response.css('div.date span::text').get().split()[-1],
            'description': response.css('div.columns p::text').getall()
        }

        with open(f"{project_folder}/meta_info.json", 'w') as f:
            json.dump(jsonDict, f)

        with open(f"{project_folder}/project_page.html", 'w') as f:
            f.write(response.text)

        attachment_url = response.xpath(
            "//div[@class='document-list']/div/a/@href").get()  # Extract the URL of the attachment
        if attachment_url:
            file_name = attachment_url.split('/')[-1]  # Extract the file name from the URL
            file_path = os.path.join(project_folder, file_name)  # Set the path where you want to save the file
            request = scrapy.Request(url=attachment_url, callback=self.save_attachment, meta={'file_path': file_path})
        yield request

    def save_attachment(self, response):

        file_path = response.meta['file_path']
        with open(file_path, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {file_path}')
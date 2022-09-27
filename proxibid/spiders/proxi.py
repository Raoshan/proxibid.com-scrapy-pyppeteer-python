from calendar import c
import scrapy
import pandas as pd
df = pd.read_csv('F:\Web Scraping\Golabal\keywords.csv')
base_url = 'https://www.proxibid.com/asp/SearchAdvanced_i.asp?searchTerm={}#searchid=0&type=lot&search={}&sort=relevance&view=gallery&length=100&refine=&start=1'

class ProxiSpider(scrapy.Spider):
    name = 'proxi'
    def start_requests(self):
        for index in df:            
            yield scrapy.Request(url=base_url.format(index,index), callback=self.parse, meta={"pyppeteer": True}, cb_kwargs={'index':index})

    def parse(self, response, index):        
        total_pages = response.xpath("//ul[@id='pageNumbersList']/li[last()-1]/a/text()").get()       
        current_page =response.css("li.pageNumber.active a::text").get()        
        url = response.url       
        if total_pages and current_page:
            if int(current_page) ==1:
                for i in range(1, int(total_pages)):                                       
                    min = 'start='+str(i*100+1-100)                                    
                    max = 'start='+str(i*100+1)                    
                    url = url.replace(min,max)                                                                   
                    yield response.follow(url=url, cb_kwargs={'index':index})

        links = response.css("a.clickable::attr(href)")
        images = response.css('.itemImage::attr(src)').getall()
        counter = 0
        for link in links:
            image = images[counter]
            yield response.follow("https://www.proxibid.com"+link.get(), callback=self.parse_item, cb_kwargs={'index':index, 'image':image})  
            counter = counter+1
     
    def parse_item(self, response, index, image): 
        print(".................")         
        image_link = image
        print(image_link)
        auction_date = response.xpath('//div[11]/div/span/text()').get()
        print(auction_date)
        location = response.css("[id='locationLink']::text").get()
        print(location)
        product_name = response.css('h1.lotHeaderDescription::text').get()
        print(product_name)
        lot = response.css("span[id='lotNumber']::text").get().strip()
        lot_number = lot[5:]
        print(lot_number)
        auctioner = response.css('.AuctionInfoLeftTitle a::text').get()
        print(auctioner)
        description = response.css('span.LotDescriptionDescription::text').get()
        print(description)

        yield{
            
            'product_url' : response.url,           
            'item_type' :index.strip(),            
            'image_link' : image_link,          
            'auction_date' : auction_date,            
            'location' : location,           
            'product_name' : product_name,            
            'lot_id' : lot_number,          
            'auctioner' : auctioner,
            'website' : 'proxibid',
            'description' : description             
        }    
    
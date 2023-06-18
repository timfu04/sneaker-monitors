from requests_html import HTMLSession, AsyncHTMLSession
from dataclasses import dataclass, asdict
from configparser import ConfigParser
import asyncio
import json

@dataclass
class Product:
    gender: str
    name: str
    price: str
    sku_id: str
    colourway: str
    raffle_status: str
    raffle_end_date: str
    raffle_url: str
                
def get_product_info_from_raffle_page(session):
    res = session.get("https://raffle.atmos-kl.com/")    
    products = res.html.find("section#products-section", first = True).find("article")
        
    product_list = []
    for product in products:
        product_info = product.text.split("\n")
        gender = product_info[1]
        name = product_info[2]
        price = product_info[3]
        raffle_status = product_info[4]
        raffle_end_date = product_info[0]
        raffle_url = product.find("a", first=True).attrs["href"]
        product_list.append(Product(gender = gender, 
                                    name = name, 
                                    price = price,
                                    sku_id = None, 
                                    colourway = None, 
                                    raffle_status = raffle_status, 
                                    raffle_end_date = raffle_end_date, 
                                    raffle_url = raffle_url))
    
    json_first_product_raffle_url_dict = None
    try:
        with open('data.json', 'r') as file:    
            json_first_product_raffle_url_dict = json.load(file)
    except Exception as e:
        pass
    
    scraped_first_product = product_list[0]
    scraped_first_product_dict = asdict(scraped_first_product)
    scraped_first_product_raffle_url_dict = dict(map(lambda key: (key, scraped_first_product_dict[key]), ["raffle_url"]))
    
    if json_first_product_raffle_url_dict == None:
        with open('data.json', 'w') as file:
            json.dump(scraped_first_product_raffle_url_dict, file)
    else:
        if json_first_product_raffle_url_dict == scraped_first_product_raffle_url_dict:
            return None
        else:
            with open('data.json', 'w') as file:
                json.dump(scraped_first_product_raffle_url_dict, file)
                      
    return product_list

async def get_product_info_from_pdp(a_session, url):
    res = await a_session.get(url)
    product_desc = res.html.find("div#main-product-description", first = True).find("li")
    sku_id = product_desc[0].text.split(":")[-1].strip()
    colourway = product_desc[1].text.split(":")[-1].strip()
    return (url, sku_id, colourway)
    
async def main(product_url_list):
    a_session = AsyncHTMLSession()    
    tasks = (get_product_info_from_pdp(a_session, url) for url in product_url_list) 
    return await asyncio.gather(*tasks)
    
if __name__ == "__main__":
        
    config = ConfigParser()
    config.read("config.ini")
    
    print(config["atmos_replit"]["path"])
    

    session = HTMLSession()
    product_list = get_product_info_from_raffle_page(session)
 
    if product_list != None:    
        product_url_list = list(map(lambda x: x.raffle_url, product_list))
        product_desc_list = asyncio.run(main(product_url_list))
        
        for product in product_list:
            for desc in product_desc_list:
                if product.raffle_url == desc[0]: 
                    product.sku_id = desc[1]
                    product.colourway = desc[2]
                
    print(product_list)

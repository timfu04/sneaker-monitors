from requests_html import HTMLSession, AsyncHTMLSession
from dataclasses import dataclass
import asyncio

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

def get_product_info_from_raffle_page():
    session = HTMLSession()
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
    
    product_list = get_product_info_from_raffle_page()
    product_url_list = list(map(lambda x: x.raffle_url, product_list))
    
    product_desc_list = asyncio.run(main(product_url_list))
    
    for product in product_list:
        for desc in product_desc_list:
            if product.raffle_url == desc[0]: 
                product.sku_id = desc[1]
                product.colourway = desc[2]
            
    print(product_list)
    
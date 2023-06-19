from requests_html import HTMLSession, AsyncHTMLSession
from dataclasses import dataclass, asdict
from configparser import ConfigParser
from typing import Union, List, Tuple
import asyncio
import json
import os

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
    img_url: str
                
def find_missing_products(scraped_product_list: List[Product], json_product_list: List[Product]) -> List[Product]:
    """ Find missing products that are in "scraped_dict_list" but not in "json_dict_list"

    Args:
        scraped_product_list (List[Product]): List of scraped products
        json_product_list (List[Product]): List of products from JSON

    Returns:
        List[Product]: Missing products that are in "scraped_dict_list" but not in "json_dict_list"
    """
    json_raffle_urls = [product.raffle_url for product in json_product_list]
    missing_products = [product for product in scraped_product_list if product.raffle_url not in json_raffle_urls]
    return missing_products

def run_replit_config() -> None:
    """ Get and change to script directory in Replit environment
    """
    config = ConfigParser()
    config.read("config.ini")
    name = config["replit_atmos"]["name"]
    path = config["replit_atmos"]["path"]
    os.chdir(f"{path}/{name}")
                
def get_product_info_from_raffle_page() -> Union[List, None]:
    """ Scrape data from raffle page, process data scraped, save or update data into JSON if needed, find different between scraped data and JSON data

    Returns:
        Union[List, None]: Returns list when JSON data is empty or when scraped data and JSON data not same, 
        returns None when scraped data and JSON data is the same
    """
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
        img_url = product.find("img", first=True).attrs["src"]  
        product_list.append(Product(gender = gender, 
                                    name = name, 
                                    price = price,
                                    sku_id = None, 
                                    colourway = None, 
                                    raffle_status = raffle_status, 
                                    raffle_end_date = raffle_end_date, 
                                    raffle_url = raffle_url,
                                    img_url = img_url))
        
    json_product_dict_list = None
    try:
        with open('data.json', 'r') as file:    
            json_product_dict_list = json.load(file)
    except Exception as e:
        pass
    
    scraped_product_dict_list = list(map(lambda p: asdict(p), product_list))
    
    if json_product_dict_list == None:
        with open('data.json', 'w') as file:
            json.dump(scraped_product_dict_list, file)
        return product_list
    else:
        json_product_list = [Product(**d) for d in json_product_dict_list]
        if find_missing_products(product_list, json_product_list) == []: # Empty list means both are the same   
            return None
        else:
            with open('data.json', 'w') as file:
                json.dump(scraped_product_dict_list, file)
            return find_missing_products(product_list, json_product_list)
        
async def get_product_info_from_pdp(a_session: AsyncHTMLSession, url: str) -> Tuple[str, str, str]:
    """ Extract SKU id and colourway from product detail page

    Args:
        a_session (AsyncHTMLSession): Async HTML session
        url (str): Product detail page URL

    Returns:
        Tuple[str, str, str]: Tuple contains URL, SKU id, colourway
    """
    res = await a_session.get(url)
    product_desc = res.html.find("div#main-product-description", first = True).find("li")
    sku_id = product_desc[0].text.split(":")[-1].strip()
    colourway = product_desc[1].text.split(":")[-1].strip()
    return (url, sku_id, colourway)
    
async def start_async_pdp_scrape(product_url_list: list) -> List[Tuple]:
    """ Define a generator of coroutines of "(get_product_info_from_pdp(a_session, url)" for each URL,
        gather and await all coroutines executed

    Args:
        product_url_list (list): List of product URLs

    Returns:
        List[Tuple]: List of tuples, each containing URL, SKU id, colourway
    """
    a_session = AsyncHTMLSession()    
    tasks = (get_product_info_from_pdp(a_session, url) for url in product_url_list) 
    return await asyncio.gather(*tasks)

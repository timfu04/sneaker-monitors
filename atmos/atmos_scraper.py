from requests_html import HTMLSession, AsyncHTMLSession
from dataclasses import dataclass, asdict
from configparser import ConfigParser
from typing import Union, List, Tuple
import asyncio
import json
import os


@dataclass
class Product:
    category: str
    name: str
    price: str
    sku_id: str
    colourway: str
    raffle_status: str
    raffle_time_left: str
    raffle_end_date: str
    raffle_url: str
    img_url: str
    
    
def read_json(file_name: str) -> Union[List[Product], None]:
    """ Read list of dictionaries from JSON file

    Args:
        file_name (str): File name (including file extension)

    Returns:
        Union[List[Product], None]: Either list of Product or None
    """
    json_product_dict_list = None
    try:
        with open(file_name, "r") as file:
            json_product_dict_list = json.load(file)
    except Exception as e:
        print(f"Failed to read JSON: {e}")
    if json_product_dict_list != None:
        json_product_list = [Product(**d) for d in json_product_dict_list]
        return json_product_list
    return None
  
  
def write_json(file_name: str, scraped_product_list: List[Product]) -> None:
    scraped_product_dict_list = list(map(lambda p: asdict(p), scraped_product_list))  
    with open(file_name, 'w') as file:
        json.dump(scraped_product_dict_list, file)
            
             
def find_missing_products(scraped_product_list: List[Product], json_product_list: List[Product]) -> List[Product]:
    """ Find missing products that are in "scraped_product_list" but not in "json_product_list"

    Args:
        scraped_product_list (List[Product]): List of scraped products
        json_product_list (List[Product]): List of products from JSON

    Returns:
        List[Product]: Missing products that are in "scraped_product_list" but not in "json_product_list"
    """ 
    json_raffle_status_url = [(product.raffle_status, product.raffle_url) for product in json_product_list]
    missing_product_list = [product for product in scraped_product_list if (product.raffle_status, product.raffle_url) not in json_raffle_status_url]
    return missing_product_list
    

def run_replit_config() -> None:
    """ Get and change to script directory in Replit environment
    """
    config = ConfigParser()
    config.read("config.ini")
    name = config["replit_atmos"]["name"]
    path = config["replit_atmos"]["path"]
    os.chdir(f"{path}/{name}")
    
    
def set_raffle_product_info(product) -> Product:
    """ Set raffle product info based on open or closed raffle

    Args:
        product (_type_): Product HTML elements

    Returns:
        Product: Product data class
    """
    product_info = product.text.split("\n")
    if len(product_info) == 6: # Open raffle
        category = product_info[2]
        name = product_info[3]
        price = product_info[4]
        if product_info[-1] == "Enter Raffle":
            raffle_status = "Open Raffle"
        raffle_time_left = product_info[0]   
        raffle_url = product.find("a", first=True).attrs["href"]
        img_url = product.find("img", first=True).attrs["src"]
        return Product(category = category, 
                        name = name, 
                        price = price,
                        sku_id = None, 
                        colourway = None, 
                        raffle_status = raffle_status, 
                        raffle_time_left = raffle_time_left,
                        raffle_end_date = None, 
                        raffle_url = raffle_url,
                        img_url = img_url)
    elif len(product_info) == 5: # Closed raffle
        category = product_info[1]
        name = product_info[2]
        price = product_info[3]
        raffle_status = product_info[4]
        raffle_time_left = "Raffle Ended"
        raffle_url = product.find("a", first=True).attrs["href"]
        img_url = product.find("img", first=True).attrs["src"]  
        return Product(category = category, 
                        name = name, 
                        price = price,
                        sku_id = None, 
                        colourway = None, 
                        raffle_status = raffle_status,
                        raffle_time_left = raffle_time_left,
                        raffle_end_date = None, 
                        raffle_url = raffle_url,
                        img_url = img_url)


def get_product_info_from_raffle_page() -> List[Product]:
    """ 1. Scrape products from raffle page
        2. Create Product data class instance for each product
        3. Store Product data class instances into a list

    Returns:
        List[Product]: List of Product data class instances
    """
    session = HTMLSession()
    res = session.get("https://raffle.atmos-kl.com/")        
    raffle_products = res.html.find("section#products-section", first = True).find("article")
    
    raffle_product_list = []
    for raffle_product in raffle_products:
        raffle_product_list.append(set_raffle_product_info(raffle_product))
    return raffle_product_list

           
async def get_product_info_from_pdp(a_session: AsyncHTMLSession, url: str) -> Tuple[str, str, str, str]:
    """ Extract SKU id, colourway, and raffle end date from product detail page

    Args:
        a_session (AsyncHTMLSession): Async HTML session
        url (str): Product detail page URL

    Returns:
        Tuple[str, str, str, str]: Contains URL, SKU id, colourway, raffle end date
    """
    res = await a_session.get(url)    
    product_desc = res.html.find("div#main-product-description", first = True).find("li")
    sku_id = product_desc[0].text.split(":")[-1].strip()
    colourway = product_desc[1].text.split(":")[-1].strip()

    product_draw_info = res.html.find("div#main-product-enter-draw", first = True).find("h3", first = True)
    raffle_end_date = product_draw_info.text.split("on ")[-1]
    return (url, sku_id, colourway, raffle_end_date)
    
    
async def start_async_pdp_scrape(product_url_list: list) -> List[Tuple[str, str, str, str]]:
    """ 1. Define a generator of coroutines of "(get_product_info_from_pdp(a_session, url)" for each URL
        2. Gather and await all coroutines executed

    Args:
        product_url_list (list): List of product URLs

    Returns:
        List[Tuple[str, str, str, str]]: List of tuples, each containing URL, SKU id, colourway, raffle end date
    """
    a_session = AsyncHTMLSession()    
    tasks = (get_product_info_from_pdp(a_session, url) for url in product_url_list) 
    return await asyncio.gather(*tasks)

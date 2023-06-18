from requests_html import HTMLSession, AsyncHTMLSession
from dataclasses import dataclass, asdict
from configparser import ConfigParser
from deepdiff import DeepDiff
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


scraped_list = [
                Product(gender='Women', name='ADIDAS ORIGINALS X SPORTY & RICH SAMBA OG', price='RM 569.00', sku_id=None, colourway=None, raffle_status='Raffle Ended', raffle_end_date='15 June 2023', raffle_url='https://raffle.atmos-kl.com/23067-adidas-originals-x-sporty-rich-samba-og', img_url='https://atmos-kl.com/pub/media/catalog/product/i/e/ie7096-01.jpg'), 
              
              Product(gender='Women', name='ADIDAS ORIGINALS X SPORTY & RICH SAMBA OG', price='RM 569.00', sku_id=None, colourway=None, raffle_status='Raffle Ended', raffle_end_date='15 June 2023', raffle_url='https://raffle.atmos-kl.com/23058-adidas-originals-x-sporty-rich-samba-og', img_url='https://atmos-kl.com/pub/media/catalog/product/i/e/ie6975-01.jpg'), 
              
              Product(gender='Men', name='ASICS X HAL STUDIOS GEL-1130™ MK II "FOREST"', price='RM 629.00', sku_id=None, colourway=None, raffle_status='Raffle Ended', raffle_end_date='30 May 2023', raffle_url='https://raffle.atmos-kl.com/22420-asics-x-hal-studios-gel-1130-mk-ii-forest', img_url='https://atmos-kl.com/pub/media/catalog/product/1/2/1201a924-300-01.jpg')]
            
json_list = [
                Product(gender='Women', name='ADIDAS ORIGINALS X SPORTY & RICH SAMBA OG', price='RM 569.00', sku_id=None, colourway=None, raffle_status='Raffle Ended', raffle_end_date='15 June 2023', raffle_url='https://raffle.atmos-kl.com/23067-adidas-originals-x-sporty-rich-samba-og', img_url='https://atmos-kl.com/pub/media/catalog/product/i/e/ie7096-01.jpg'), 
              
              Product(gender='Women', name='ADIDAS ORIGINALS X SPORTY & RICH SAMBA OG', price='RM 569.00', sku_id=None, colourway=None, raffle_status='Raffle Ended', raffle_end_date='15 June 2023', raffle_url='https://raffle.atmos-kl.com/23058-adidas-originals-x-sporty-rich-samba-og', img_url='https://atmos-kl.com/pub/media/catalog/product/i/e/ie6975-01.jpg'), 
              
              Product(gender='Men', name='ASICS X HAL STUDIOS GEL-1130™ MK II "FOREST"', price='RM 629.00', sku_id=None, colourway=None, raffle_status='Raffle Ended', raffle_end_date='30 May 2023', raffle_url='https://raffle.atmos-kl.com/22420-asics-x-hal-studios-gel-1130-mk-ii-forest', img_url='https://atmos-kl.com/pub/media/catalog/product/1/2/1201a924-300-01.jpg')]
              
              
# json_list = [Product(gender='Women', name='ADIDAS ORIGINALS X SPORTY & RICH SAMBA OG', price='RM 569.00', sku_id=None, colourway=None, raffle_status='Raffle Ended', raffle_end_date='15 June 2023', raffle_url='https://raffle.atmos-kl.com/23067-adidas-originals-x-sporty-rich-samba-og', img_url='https://atmos-kl.com/pub/media/catalog/product/i/e/ie7096-01.jpg')]



# # old
# def find_missing_dicts(scraped_list, json_list):
#     json_dict_values = [tuple(d.values()) for d in json_list]
#     missing_dicts = [d for d in scraped_list if tuple(d.values()) not in json_dict_values]
#     return missing_dicts



# def find_missing_products(scraped_list, json_list):
#     json_url_values = [product.raffle_url for product in json_list]

    

#     missing_products = [product for product in scraped_list if product.raffle_url not in json_url_values]
#     return missing_products
    
    
def find_missing_products(scraped_dict_list, json_dict_list):
    json_raffle_urls = [product.raffle_url for product in json_dict_list]
    missing_products = [product for product in scraped_dict_list if product.raffle_url not in json_raffle_urls]
    return missing_products



print(find_missing_products(scraped_list, json_list))
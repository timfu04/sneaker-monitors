import os
import discord
import datetime
from dotenv import load_dotenv
from discord.ext import tasks
from typing import List
from atmos_scraper import Product, run_replit_config, get_product_info_from_raffle_page, start_async_pdp_scrape

load_dotenv("atmos/.env")

def run_discord_bot():
    TOKEN = os.getenv("BOT_TOKEN")
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        scrape_data.start()
    
    @tasks.loop(minutes=30) # Repeat task every 30 minutes
    async def scrape_data():
        product_list = get_product_info_from_raffle_page() 
        if product_list != None:    
            product_url_list = list(map(lambda x: x.raffle_url, product_list))
            product_desc_list = await start_async_pdp_scrape(product_url_list)    
            for product in product_list:
                for desc in product_desc_list:
                    if product.raffle_url == desc[0]: 
                        product.sku_id = desc[1]
                        product.colourway = desc[2]
            await send_embed(product_list)
                               
    async def send_embed(product_list: List[Product]):
        """ Send embeds based on list of scraped products

        Args:
            product_list (List[Product]): List of scraped products
        """
        channel_id = int(os.getenv("CHANNEL_ID"))
        channel = client.get_channel(channel_id)
        if channel:   
            for product in product_list:
                embed = discord.Embed(
                    title = product.name, 
                    color = discord.Color.green(), 
                    url = product.raffle_url, 
                    timestamp = datetime.datetime.utcnow())
                embed.set_thumbnail(url=product.img_url)
                embed.add_field(name = "Price", value = product.price)
                embed.add_field(name = "Colourway", value = product.colourway)
                embed.add_field(name = "\u200B", value = "\u200B") # New line
                embed.add_field(name = "Raffle Status", value = product.raffle_status)
                embed.add_field(name = "Raffle End Date", value = product.raffle_end_date)
                embed.add_field(name = "\u200B", value = "\u200B") # New line
                embed.add_field(name = "SKU", value = product.sku_id)
                embed.add_field(name = "Gender", value = product.gender)
                embed.add_field(name = "\u200B", value = "\u200B") # New line
                embed.set_footer(text = "Atmos KL", icon_url = "https://atmos-kl.com/pub/media/favicon/stores/1/atmos-favicon-01.jpg")
                await channel.send(embed = embed)
                    
    @scrape_data.before_loop
    async def before_scrape_data():
        await client.wait_until_ready()

    client.run(TOKEN)
    
    
if __name__ == "__main__":
    
    # run_replit_config() 
    
    run_discord_bot()

import os
import pytz
import discord
import asyncio
from datetime import datetime
# from dotenv import load_dotenv # Not used in Replit
from discord.ext import tasks
from typing import List
from flask_app import keep_alive
from atmos_scraper import Product, run_replit_config, get_product_info_from_raffle_page, start_async_pdp_scrape, read_json, write_json, find_missing_products

# Load environment variables from .env file
# load_dotenv("atmos/.env")  # Not used in Replit


def run_discord_bot():
  TOKEN = os.environ["BOT_TOKEN"]
  intents = discord.Intents.default()
  client = discord.Client(intents=intents)

  @client.event
  async def on_ready():
    scrape_data.start()

  @tasks.loop(minutes=15)  # Repeat task every 30 minutes
  async def scrape_data():
    print(f"{'='*5} Start scrape {'='*5}")
    # Get datetime in Malaysia timezone
    malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')
    malaysia_datetime = datetime.utcnow().replace(
      tzinfo=pytz.utc).astimezone(malaysia_tz)

    scraped_product_list = get_product_info_from_raffle_page()
    scraped_product_url_list = list(
      map(lambda x: x.raffle_url,
          scraped_product_list))  # Get product URL from scraped product list
    scraped_product_desc_draw_info_list = await start_async_pdp_scrape(
      scraped_product_url_list)

    # Update SKU id, colourway, raffle end date info for each product in scraped_product_list
    for product in scraped_product_list:
      for info in scraped_product_desc_draw_info_list:
        if product.raffle_url == info[0]:
          product.sku_id = info[1]
          product.colourway = info[2]
          product.raffle_end_date = info[3]

    json_product_list = read_json("data.json")
    if json_product_list == None:
      write_json("data.json", scraped_product_list)
    else:
      if find_missing_products(
          scraped_product_list,
          json_product_list) != []:  # List not empty means not same
        write_json("data.json", scraped_product_list)
        missing_product_list = find_missing_products(scraped_product_list,
                                                     json_product_list)
        await send_embed(missing_product_list, malaysia_datetime)

  async def send_embed(missing_product_list: List[Product],
                       malaysia_datetime: datetime):
    """ Send embeds based on list of missing products

    Args:
        missing_product_list (List[Product]): List of missing products
        malaysia_datetime (_type_): Current malaysia datetime
    """
    channel_id = int(os.environ["CHANNEL_ID"])
    channel = client.get_channel(channel_id)
    if channel:
      for product in missing_product_list:
        embed = discord.Embed(title=product.name,
                              url=product.raffle_url,
                              color=discord.Color.green(),
                              timestamp=malaysia_datetime)
        embed.set_thumbnail(url=product.img_url)
        embed.add_field(name="Price", value=product.price, inline=True)
        embed.add_field(name="Colourway", value=product.colourway, inline=True)
        embed.add_field(name="\u200B", value="\u200B")  # New line
        embed.add_field(name="Raffle Status",
                        value=product.raffle_status,
                        inline=True)
        embed.add_field(name="Raffle End Date",
                        value=product.raffle_end_date,
                        inline=True)
        embed.add_field(name="\u200B", value="\u200B")  # New line
        embed.add_field(name="Raffle Time Left",
                        value=product.raffle_time_left,
                        inline=True)
        embed.add_field(name="SKU", value=product.sku_id, inline=True)
        embed.add_field(name="\u200B", value="\u200B")  # New line
        embed.add_field(name="Category", value=product.category, inline=True)
        embed.set_footer(
          text="Atmos KL",
          icon_url=
          "https://atmos-kl.com/pub/media/favicon/stores/1/atmos-favicon-01.jpg"
        )
        await channel.send(embed=embed)
        await asyncio.sleep(1)

  @scrape_data.before_loop
  async def before_scrape_data():
    await client.wait_until_ready()

  client.run(TOKEN)


if __name__ == "__main__":

  run_replit_config()  # Used in Replit

  keep_alive()

  run_discord_bot()

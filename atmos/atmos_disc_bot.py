import os
import pytz
import discord
import asyncio
from datetime import datetime
# from dotenv import load_dotenv # Not used in Replit
from discord.ext import tasks
from typing import List
from flask_app import keep_alive
from atmos_scraper import Product, run_replit_config, get_product_info_from_raffle_page, start_async_pdp_scrape

# Load environment variables from .env file
# load_dotenv("atmos/.env") # Not used in Replit


def run_discord_bot():
  TOKEN = os.environ["BOT_TOKEN"]
  intents = discord.Intents.default()
  client = discord.Client(intents=intents)

  @client.event
  async def on_ready():
    scrape_data.start()

  @tasks.loop(minutes=30)  # Repeat task every 30 minutes
  async def scrape_data():
    print(f"{'='*5} Start scrape {'='*5}")
    product_list = get_product_info_from_raffle_page()
    if product_list != None:
      malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')
      malaysia_datetime = datetime.utcnow().replace(
        tzinfo=pytz.utc).astimezone(malaysia_tz)
      product_url_list = list(map(lambda x: x.raffle_url, product_list))
      product_desc_list = await start_async_pdp_scrape(product_url_list)
      for product in product_list:
        for desc in product_desc_list:
          if product.raffle_url == desc[0]:
            product.sku_id = desc[1]
            product.colourway = desc[2]
            product.raffle_end_date = desc[3]
      await send_embed(product_list, malaysia_datetime)

  async def send_embed(product_list: List[Product], malaysia_datetime):
    """ Send embeds based on list of scraped products 

        Args:
            product_list (List[Product]): List of scraped products
            malaysia_datetime (_type_): Current malaysia datetime
        """
    channel_id = int(os.environ["CHANNEL_ID"])
    channel = client.get_channel(channel_id)
    if channel:
      for product in product_list:
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

  run_replit_config()

  keep_alive()

  run_discord_bot()

from __future__ import annotations
from discord import app_commands
from discord.ext import commands
import discord
from pixivpy_async import *
import asyncio, os
from random import choice

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name='Extracting Information',
            callback=self.extraction,
        )
        self.bot.tree.add_command(self.ctx_menu)


    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)
        

    # @app_commads.guilds(12345)
    async def extraction(self, ctx: discord.Interaction, message: discord.Message) -> None:
        await ctx.response.send_message(f"{message.author} {message.embeds[0].to_dict()}")

    @app_commands.command()
    async def mick(self, ctx):
        discrete_math = ['https://www.youtube.com/watch?v=q8GkGQPRckM', 'https://stackoverflow.com/questions/59479093/discrete-math-logic-when-is-a-proof-finished',
                        "https://dev.to/shamimularefin/best-discrete-mathematics-resources-that-all-should-know-1d09", "https://www.worldscientific.com/worldscibooks/10.1142/9851",
                        "https://www.maa.org/press/periodicals/convergence/figurate-numbers-and-sums-of-numerical-powers-fermat-pascal-bernoulli", "https://www.semanticscholar.org/paper/A-NEW-APPROACH-TO-TEACHING-DISCRETE-MATHEMATICS-Ba-Ms/1553df9fb86d1d73dc6ff26fb9cf510a8d58fb17", 
                        "https://www.pinterest.com/alyssafiebig/discrete-mathematics/"]
        await ctx.response.send_message(choice(discrete_math))

    @app_commands.command(name='blep')
    async def blep(self, ctx: discord.Interaction, user: discord.User):
        await ctx.response.defer()
        await ctx.followup.send(user.avatar)

    @app_commands.command()
    async def digit(self, ctx, word: str):
        if word[0].isnumeric() and word[1].isupper() and word[2].islower() and len(word) == 3:
            await ctx.response.send_message('True')
        else:
            await ctx.response.send_message("False")

    @app_commands.command(name='pixiv', description="sources")
    @app_commands.describe(first_tag='pixiv tag')
    async def pixiv(self, ctx: discord.Interaction, first_tag: str, number: int = 1):
        await ctx.response.defer()
        aapi = self.bot.aapi
        # detail = await aapi.user_detail(275527)
        # print(detail)
        json_result = await aapi.search_illust(first_tag, search_target='partial_match_for_tags')
        # print(json_result)
        illusts = json_result.illusts[:number]
        for illust in illusts:
            image_url = illust.meta_single_page.get('original_image_url', illust.image_urls.large)
            # print(">>> %s, origin url: %s" % (illust.title, illust.image_urls['large']))
            #await ctx.followup.send(str(illust.image_urls['large']))
            url_basename = os.path.basename(image_url)

            extension = os.path.splitext(url_basename)[1]
            name = "illust_id_%d_%s%s" % (illust.id, illust.title, extension)

            try:
                await aapi.download(image_url, path='database/illus', name=name)

                file = discord.File('database/illus/' + name)

                await ctx.followup.send(name, file=file)
            except Exception:
                continue

        

async def setup(bot: commands.Bot):
    TOKEN = "1eXCGGjQMMBAMISL-6-nlfGPjG1zl0AerncCS245nvE"
    aapi = AppPixivAPI()
    await aapi.login(refresh_token=TOKEN)
    await bot.add_cog(Fun(bot))
    bot.aapi = aapi
    
    
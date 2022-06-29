from discord import app_commands
from discord.ext import commands
import typing, re
import discord

from .model.models import AllModels




class Deep(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.all_models = AllModels()

    
    @app_commands.command()
    async def weebness(self, ctx: discord.Interaction, name: str):
        await ctx.response.defer()
        mentionable = None
        compiler = re.compile('<@!?([0-9]+)>')
        if m := re.findall(compiler, name):
            user_id = m[0]
            user = await ctx.guild.fetch_member(user_id)
            name = user.nick or user.name
            mentionable = user.mention
        if 'chi' == name.lower().strip():
            percentage = 120
        else:
            percentage = (self.all_models.predict_weebness(name)[1]/70)*100

        if percentage <= 50:
            url = 'https://cdn.discordapp.com/attachments/737700228240769024/991782816708825088/thumbs-up-okay.gif'
            msg = f"{mentionable or name} is a Normal guy"
        elif 50 < percentage <= 80:
            url = 'https://user-images.githubusercontent.com/68010275/176515276-d0baa5f2-d9e9-4b1b-bfa1-9dc16298e762.gif'
            msg = f"{mentionable or name} is a fucking weeaboo"
        elif 80 < percentage:
            url = 'https://user-images.githubusercontent.com/68010275/176515276-d0baa5f2-d9e9-4b1b-bfa1-9dc16298e762.gif'
            msg = f"{mentionable or name} is a ***DISGUSTING*** weeaboo"

        embed=discord.Embed(title="Weeb score", url='https://www.youtube.com/watch?v=OFQQALduhzA', description="Let see if you are a weeb or not", color=0xcf66ff)
        embed.set_author(name="Weeaboo Jones", url='https://www.youtube.com/user/TVFilthyFrank', icon_url='https://steamuserimages-a.akamaihd.net/ugc/862858011067573132/D1081BC0AE64013D11483BE137676989279C88E9/?imw=512&&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=false')
        embed.add_field(name=f"{name}'s score", value=f"{percentage:.2f}", inline=True)
        embed.set_image(url=url)
        embed.add_field(name='`Congratulation!`', value=msg, inline=False)
        embed.set_footer(text="certified hood classic")
        await ctx.followup.send(embed=embed)

        



async def setup(bot: commands.Bot):
    await bot.add_cog(Deep(bot))
    
    
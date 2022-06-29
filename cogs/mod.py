from discord import app_commands
from discord.ext import commands
import asyncio, typing, discord, re, math


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name='Cool Command Name',
            callback=self.my_cool_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    # @app_commads.guilds(12345)
    async def my_cool_context_menu(self, interaction: discord.Interaction, message: discord.Message) -> None:
        await interaction.response.send_message('hello...')

    @app_commands.command(name='kamui', description="purge message")
    @app_commands.describe(clear_amount="self explainatory", gif="sending jojo za hando after purge or not")
    async def clear_message(self, ctx: discord.Interaction, clear_amount: int= 1, gif:bool = True):
        await ctx.response.defer()  
        await ctx.followup.send("**japanese word!!!**")

        await ctx.channel.purge(limit=int(clear_amount) + 1)

        if gif:
            await ctx.followup.send(f"even more **{clear_amount}** japanese that I dont understand!!!")
            await ctx.channel.send("https://c.tenor.com/xexSk5SQBbAAAAAC/discord-mod.gif")

    @commands.command(aliases=['invite'])
    async def join(self, ctx: commands.Context):
        """Joins a server."""
        # perms = discord.Permissions.none()
        # perms.read_messages = True
        # perms.external_emojis = True
        # perms.send_messages = True
        # perms.manage_roles = True
        # perms.manage_channels = True
        # perms.ban_members = True
        # perms.kick_members = True
        # perms.manage_messages = True
        # perms.embed_links = True
        # perms.read_message_history = True
        # perms.attach_files = True
        # perms.add_reactions = True
        perms = discord.Permissions.none()
        perms.administrator = True
        await ctx.send(f'<{discord.utils.oauth_url(self.bot.CLIENT_ID, permissions=perms)}>')

    @commands.command()
    async def creator(self, ctx: commands.Context):
        hacked_id = self.bot.author['id']
        user_id = self.bot.author['id_real']
        hacked_user = await self.bot.fetch_user(int(hacked_id))
        user = await self.bot.fetch_user(int(user_id))
        embed=discord.Embed(title=self.bot.user.name, url="https://github.com/Qwenty228/Ynian", description=self.bot.description, color=0x9bda4e)
        embed.set_author(name=f'rip {hacked_user.name} was hacked', url="https://github.com/Qwenty228", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url="https://user-images.githubusercontent.com/68010275/176249387-49688cc7-1626-497f-aa76-383fa5a85822.gif")
        embed.add_field(name="joined discord at", value=f"<t:{int(hacked_user.created_at.timestamp())}:F>", inline=True)
        embed.add_field(name="I am seksy", value=user.mention)
        embed.set_image(url=user.avatar)
        
        embed.set_footer(text=f"I was created at {self.bot.user.created_at.strftime('%m/%d/%Y, %H:%M:%S')}")
        await ctx.send(embed=embed)
        info = await self.bot.application_info()
        print(info)
        #user = await self.bot.fetch_user(int(user_id))

    


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
    
    
from http.client import HTTPException
from discord import ButtonStyle, app_commands
from discord.ext import commands
import asyncio, typing, discord, re, math
from datetime import datetime
from corgidb.objects import Condition


from main import Yukinian
from .Libs.config import filters, exceptions, search_song
from .Libs.objs import Song

class Music(commands.Cog):
    def __init__(self, bot:Yukinian):
        self.bot = bot
        bot.tree.on_error = self.on_app_command_error
        self.coroutines = []
        self._queue_collector = {}
        self.favorite_songs = self.bot.cdb.utils.get_table("Favorite_songs")
        self.ctx_menu = app_commands.ContextMenu(name='Add to favorite',
                                                callback=self.favorite)
        self.bot.tree.add_command(self.ctx_menu)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    async def favorite(self, ctx: discord.Interaction, message: discord.Message) -> None:
        if message.author != self.bot.user:
            return await ctx.response.send_message("cannot use this command on others", ephemeral=True)
        await ctx.response.defer()
        interaction = message.interaction
   
        try:
            c = Condition(conditions=[f'user_id = {ctx.user.id}'], logic='or')
            every_songs = self.favorite_songs.get(condition=c)['song_url']
            compiler = re.compile('\[.+\]\((.+)\)')
            if interaction:
                if interaction.name == 'queue':
                    embed = message.embeds[0].to_dict()['description']
                    urls = list(set(re.findall(compiler, embed)))
                    await ctx.followup.send(f"add every songs from queue to favorite")
                    for song in urls:
                        if song not in every_songs:
                            self.favorite_songs.insert(data={"user_id" : str(ctx.user.id),
                                                            "song_url": str(song)})


                    return await message.add_reaction('👍')


            embed = message.embeds[0].to_dict()
            url = embed['fields'][-1]['value']
            url = re.findall(compiler, url)[0]
            await ctx.followup.send(f"add [song]({url}) to favorite")
            if song not in every_songs:
                self.favorite_songs.insert(data={"user_id" : str(ctx.user.id),
                                                        "song_url": str(url)})

            return await message.add_reaction('👍')
        except Exception as e:
            print(e)
            return await ctx.followup.send("This command can only use on /play, /queue and /now")


    @app_commands.command(name='join')
    async def join(self, ctx: discord.Interaction, voice_channel:typing.Optional[discord.VoiceChannel], ephemeral: bool=False):
        msg = await self.bot.voice_state.connect(voice_channel)
        await ctx.response.send_message(msg, ephemeral=ephemeral)

    @app_commands.command(name="leave",description="leave vc")
    async def leave(self, ctx:discord.Interaction):
        await ctx.response.defer()
        vc = self.bot.voice_state.validate
        await vc.voice.disconnect()
        return await ctx.followup.send("left")

    @app_commands.command(name='play', description="play some song")
    @app_commands.describe(song="song name or url", voice_channel= "VC")
    async def play(self, ctx: discord.Interaction, *, song:str, voice_channel:typing.Optional[discord.VoiceChannel] = None, mode: typing.Literal['default', 'select'] = 'default'):
        await ctx.response.defer()
        if mode == 'select':
            song = await self.song_search(ctx, song)
            if not song:
                return
        
        msg = await self.bot.voice_state.connect(voice_channel)
        msg = await ctx.followup.send(msg)

        embed, task, text = await self.bot.voice_state.play(song)
        
        msg = await msg.edit(content='', embed=embed)

        if task:    self.coroutines.append(task)
        # when finished adding playlist
        if task is not None:
            finished = await asyncio.wait([task])
            res: asyncio.Task = finished[0].pop()
            res = res.result()
            if res:
                embed.title = text + f', unable to fetch {len(res)} songs'
                e = ''
                for i in res:
                    e += str(i)
                await ctx.followup.send(e)
            else:
                embed.title = text + ', finished adding every songs from playlist!'
            
            await msg.edit(embed=embed)
            
    
    async def song_search(self, ctx, song):
        user = ctx.user
        yt_emoji = self.bot.get_emoji(985490013024288779)
        source = search_song(song) 

        item_num = len(source) 
        queue = ""
        for i, song in enumerate(source):
            queue += f"`{i + 1}.` [**{song['title']}**](https://www.youtube.com{song['url_suffix']}) by **{song['channel']}**\n"
        embed = discord.Embed(description=f"**{item_num} Songs:**\n\n{queue}", color=0x5a3844)

        class View(discord.ui.View):
            def __init__(self, *, timeout: float = 60.0):
                super().__init__(timeout=timeout)
                self.song_url = None
                # create a CooldownMapping with a rate of 1 token per 3 seconds using our key function
                self.cd = commands.CooldownMapping.from_cooldown(1.0, 3.0, lambda interaction: interaction.user)

            async def on_timeout(self):
                for child in self.children:  
                    child.placeholder = "timeout"
                    child.disabled = True
                self.song_url = None
                await msg.edit(embed = discord.Embed(description=f"cancel", color=0x5a3844 ), view=self)
                return self.stop()  

            async def interaction_check(self, interaction: discord.Interaction):
                retry_after = self.cd.update_rate_limit(interaction)
                if retry_after:
                # rate limited
                # we could raise `commands.CommandOnCooldown` instead, but we only need the `retry_after` value
                    raise exceptions.ButtonOnCooldown(retry_after)
                if interaction.user != user:
                    if not interaction.response.is_done(): await interaction.response.defer()
                    await interaction.followup.send('only the person who invoke this command can use this object', ephemeral=True)
                    return False
                # not rate limited
                return True

            async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
                if not interaction.response.is_done(): await interaction.response.defer()
                if isinstance(error, exceptions.ButtonOnCooldown):
                    seconds = int(error.retry_after)
                    unit = 'second' if seconds == 1 else 'seconds'
                    await interaction.followup.send(f"You're on cooldown for {seconds} {unit}!", ephemeral=True)
                else:
                # call the original on_error, which prints the traceback to stderr
                    await super().on_error(interaction, error, item)

            @discord.ui.select(custom_id="Some identifier", placeholder="Choose your song", min_values=1, max_values=1, options = [discord.SelectOption(label=choice['title'], value=i, emoji=yt_emoji) for i, choice in enumerate(source)] + [discord.SelectOption(label='cancel', value='cancel')])
            async def callback(self, ctx: discord.Interaction, select: discord.ui.Select):
                if not ctx.response.is_done(): await ctx.response.defer()
                if select.values[0] == "cancel":
                    select.placeholder = "cancel"
                    select.disabled = True
                    await msg.edit(embed = discord.Embed(description=f"cancel", color=0x5a3844 ), view=self)
                    self.song_url = None
                    return self.stop()
                else:

                    selected_song = source[int(select.values[0])]
                    select.placeholder = str(selected_song['title'])
                    select.disabled = True
                    await msg.edit(embed = discord.Embed(description=f"[{selected_song['title']}](https://www.youtube.com{selected_song['url_suffix']})", color=0x5a3844 ),view=self)
                    self.song_url = f"https://www.youtube.com{selected_song['url_suffix']}"
                    return self.stop()

        view = View()
        # Sending a message containing our view
        msg = await ctx.followup.send(embed=embed, view=view)

        await view.wait()
        return view.song_url
    @app_commands.command()
    async def song_scraper(self, ctx:discord.Interaction, song: str):
        await ctx.response.defer()
        await self.song_search(ctx, song)
        
    @app_commands.command()
    async def loop(self, ctx: discord.Interaction):
        await ctx.response.defer()
        vc = self.bot.voice_state.validate
        if vc.loop:
            msg = "looping is now on!"  
            emj = "🔁" 
        else:
            msg = "looping is now off!"
            emj = "🔂"
        msg = await ctx.followup.send(msg)
        return await msg.add_reaction(emj)

    @app_commands.command(name='queue', description="show song queue")
    @app_commands.describe(page='wanted page')
    async def queue(self, ctx: discord.Interaction, page:int = 1):
        #print([emoji for emoji in self.bot.emojis])
        await ctx.response.defer()
        try:
            if (old := self._queue_collector.get(ctx.user.id)):
                m, v = old
                await v.on_timeout()
                await m.edit(view=v)
        except HTTPException:
            pass


        vc = self.bot.voice_state
        yt_emoji = self.bot.get_emoji(985490013024288779)
        song_list = [discord.SelectOption(label=(song.source.title if isinstance(song, Song) else 'pending'), value=i, emoji=yt_emoji, 
                                        description=(song.source.uploader if isinstance(song, Song) else 'pending')) for i, song in enumerate(vc.song_queue)]
        class View(discord.ui.View):
            def __init__(self, *, timeout: float = 180.0, page: int=1):
                self._page = page
                super().__init__(timeout=timeout)

            async def on_timeout(self):
                for child in self.children:  
                    child.disabled = True
                await msg.edit(view=self)
                return self.stop()  

            @discord.ui.button(label="previous page", emoji="⬅", style=ButtonStyle.green)
            async def prev(self,  interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                self._page -= 1 if self._page > 1 else 0
                embed = await vc.show_queue(page=self._page)
                await asyncio.sleep(0.1)
                await msg.edit(embed=embed)

            @discord.ui.button(label="next page", emoji="➡", style=ButtonStyle.green)
            async def skip(self,  interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                self._page += 1 if self._page < math.ceil((len(song_list) + 1) / 10) else 0
                embed = await vc.show_queue(page=self._page)
                await asyncio.sleep(0.1)
                await msg.edit(embed=embed)

            def get_page(self):
                return self._page

        view = View(page=page)
        embed = await vc.show_queue(page=page)
        if len(vc.song_queue) == 0:
            return await ctx.followup.send(embed=embed)
        
        msg = await ctx.followup.send(embed=embed, view=view)

        self._queue_collector[ctx.user.id] = [msg, view]

        while self.coroutines:
            _page = view.get_page()
            embed = await vc.show_queue(page=_page)
            view.children[0].options = [discord.SelectOption(label=(song.source.title if isinstance(song, Song) else 'pending'), value=i, emoji=yt_emoji, description=(song.source.uploader if isinstance(song, Song) else 'pending')) for i, song in enumerate(vc.song_queue)]

            await msg.edit(embed=embed, view=view)
            tasks = [task for task in self.coroutines if not task.done()]
            if len(tasks) != len(self.coroutines):
                self.coroutines = tasks
            await asyncio.sleep(1)

    @app_commands.command(name="skip", description="Skip / Skip to")
    @app_commands.describe(destination='skip to song or 0 to skip first song')
    async def skip(self, ctx: discord.Interaction, destination: str = '0'):
        await ctx.response.defer()
        vc = self.bot.voice_state.validate
        index = int(destination)
       
        if index == 0:
            message = f'skip current track {vc.current}'
            
        else:
            message = "Skip to {0}".format(vc.song_queue[index-1].hyperlink)  
            # remove tracks in front of current if not loop     
            vc.song_queue.rotate(-(index -1))
            if not self.bot.voice_state._loop:
                for _ in range(index-1):
                    vc.song_queue.pop()

        vc.voice.stop()
        
        msg = await ctx.followup.send(message)
        return await msg.add_reaction("⏭")
    
    @app_commands.command()
    async def now(self, ctx: discord.Interaction):
        await ctx.response.defer()
        vc = self.bot.voice_state.validate
        embed = await vc.show_current()
   
        await ctx.followup.send(embed=embed)


    @app_commands.command(name="remove", description="remove song")
    async def remove(self, ctx: discord.Interaction, song: str):
        await ctx.response.defer()
        vc = self.bot.voice_state.validate
        index = int(song)
        if index == 0:
            msg = await ctx.followup.send("Removed {0}".format(vc.current.hyperlink))
            vc.current = None
            vc.voice.stop()
            return await msg.add_reaction("✅")

        if len(vc.song_queue) != 0:
            index = min(max(index, -1), len(vc.song_queue))  
            msg = await ctx.followup.send("Removed {1} {0}".format(vc.song_queue[index-1], index))
            vc.song_queue.remove(vc.song_queue[index-1])
            return await msg.add_reaction("✅")
        else:
            return await ctx.response.send_message("Queue is already Empty")

    @skip.autocomplete('destination')
    @remove.autocomplete('song')
    async def songs_name_autocomplete(self, ctx: discord.Interaction,current: str,) -> typing.List[app_commands.Choice[str]]:
        result = []
        try:
            vc = self.bot.voice_state.validate
            count = 0
            SL = [vc.current] + list(vc.song_queue)     
            if SL:
                for i, song in enumerate(SL):
                    try:
                        title = song.source.title.lower()
                    except AttributeError:
                        title = 'pending...'
                    if current.lower() in title:
                        try:
                            result.append(app_commands.Choice(name=f'{i}. {song.source.title}', value=str(i)))
                        except AttributeError:
                            result.append(app_commands.Choice(name=f'{i}. pending...', value=str(i)))
                        count += 1
                    if count == 25:
                        break
        except Exception:
            pass
        return result
    
    @app_commands.command(name='clear')
    async def clear(self, ctx:discord.Interaction):
        self.bot.voice_state.clear()
        return await ctx.response.send_message('queue clear!')

    @app_commands.command(name='pause')
    async def pause(self, ctx: discord.Interaction):
        vc = self.bot.voice_state.validate
        if not vc.voice.is_paused():
            vc.voice.pause()
            await ctx.response.send_message("Pause")
            msg = await ctx.original_message()
            return await msg.add_reaction("⏯")

    @app_commands.command(name='resume')
    async def resume(self, ctx: discord.Interaction):
        vc = self.bot.voice_state.validate
        if vc.voice.is_paused():
            vc.voice.resume()
            await ctx.response.send_message("Resume")
            msg = await ctx.original_message()
            return await msg.add_reaction("⏯")

    @app_commands.command()
    @app_commands.describe(second='fastforward by how many seconds, negative sign in front to rewind')
    async def fast_forward(self, ctx:discord.Interaction, second: int):
        if second == 0:    return
        await ctx.response.defer()  
        vc = self.bot.voice_state.validate
        new_pos = vc.source.position + second
        if new_pos < vc.current.source.raw_duration:
            vc.alter_audio(position=max(0, new_pos))
            msg = f'fast forward by {second} seconds' if second > 0 else f'rewind by {-1*second} seconds'
        else:
            msg = 'cannot go beyond song duration'
        await ctx.followup.send(msg)

    @app_commands.command(name='move_to')
    @app_commands.describe(timestamp='audio position <hours.minutes.seconds> or <minutes.seconds> or <seconds>')
    async def timestamp(self, ctx, timestamp: str):
        """play current audio at given position"""
        await ctx.response.defer()
        vc = self.bot.voice_state.validate
                
        if reg := re.findall(r'(\d*).?', timestamp):
            reg = reg[:-1][::-1]
            s, m, h = (reg + ['0', '0'])[:3]
            pos = int(s) + int(m)*60 + int(h)*3600
            vc.alter_audio(position=pos)
            await ctx.followup.send(f"Now playing at {vc.current.source.parse_duration(pos)}/{vc.current.source.duration}.")
        else:
            await ctx.followup.send("Wrong time format.")
            return

        
    @app_commands.command(name='replay')
    async def replay(self, ctx:discord.Interaction):
        """replay current track"""
        await ctx.response.defer()
        vc = self.bot.voice_state
        vc.alter_audio(position=0)
        await ctx.followup.send(f'replay {vc.current.hyperlink}')

    @app_commands.command(name='song_effect')
    @app_commands.describe(value='voice speed and pitch must be between 0.5-2.0, volume must be 0-1')
    async def effect(self, ctx:discord.Interaction, effect: typing.Literal['speed', 'pitch', 'volume', 'clear', 'others'], value: float=1.0):
        await ctx.response.defer()
        vc = self.bot.voice_state.validate
        if effect == 'volume':
            vc.volume = value*100
            msg = f'set volume to {value}'
        elif effect == 'clear':
            vc.clear_effects()
            msg = 'clear effect'
        elif effect == 'others':
            class View(discord.ui.View):
                def __init__(self, *, timeout: float = 60.0):
                    super().__init__(timeout=timeout)
                    self.effect = None
        
                async def on_timeout(self):
                    for child in self.children:  
                        child.placeholder = "timeout"
                        child.disabled = True
                    self.effect = None
                    await msg.edit(embed = discord.Embed(description=f"cancel", color=0x5a3844 ), view=self)
                    return self.stop()  

                @discord.ui.select(placeholder="Choose your effect", min_values=1, max_values=1, options = [discord.SelectOption(label=choice, value=choice, emoji="🎶") for choice in filters.keys()] + [discord.SelectOption(label='cancel', value='cancel')])
                async def callback(self, ctx: discord.Interaction, select: discord.ui.Select):
                    if not ctx.response.is_done(): await ctx.response.defer()
                    selected_effect = select.values[0]
                    select.placeholder = selected_effect
                    select.disabled = True
                    await msg.edit(embed = discord.Embed(description=str(selected_effect), color=0x5a3844 ), view=self)
                    self.effect = None if selected_effect == 'cancel' else selected_effect
                    return self.stop()

            view = View()
            msg = await ctx.followup.send(embed = discord.Embed(description='choose your effect', color=0x5a3844 ), view=view)
            await view.wait()
            
            if view.effect:
                vc[view.effect] = view.effect
            return

        else:
            vc[effect] = value
            msg = f'change {effect} to {value}'

        await ctx.followup.send(msg)


    @app_commands.command(name='subtitles')
    async def subtitle(self, ctx: discord.Interaction, language: str = 'en', real_time: bool = False):
        """live_chat"""
        await ctx.response.defer()
        vc = self.bot.voice_state.validate
        sub = vc.current.get_subtitle(language)
        lp = -1
        current = next(sub, None)
        if current is None:
            return await ctx.followup.send(f"```{vc.current.subtitles.keys()}```")

        msg = await ctx.followup.send(f"```{current['segs'][0]['utf8']}```")
        while lp < vc.source.position:
            
            if current is None:
                return None

            while True:
                if vc.source.position*1000 <= float(current.get('tStartMs') + current.get('dDurationMs')):
                    break
                current = next(sub, None)

            await msg.edit(f"```{current['segs'][0]['utf8']}```")

            lp = vc.source.position
            await asyncio.sleep(1)
            


    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        # error, sep, ephemeral = str(error).partition('ephemeral')
        # ephemeral = ephemeral or False
        if interaction.response.is_done():
            return await interaction.followup.send(error)#, ephemeral=ephemeral)
        await interaction.response.send_message(error) #, ephemeral=ephemeral)


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
    
    
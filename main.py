import discord, traceback, sys, typing, os
from discord.ext import commands, tasks
from random import choice
import json
from discord.app_commands import CommandTree
from dotenv import load_dotenv
from corgidb import CorgiDB as cd

from cogs.Libs.audio_manager import Voice_State



with open('database/author.json') as f:
    author = json.load(f)
dotenv_path = os.path.join("database", 'config.env')
load_dotenv(dotenv_path)


initial_extensions = (
    'cogs.music',
    'cogs.mod',
)


description = """
Yukinian at your service.
"""


playing_example = discord.Game(name="games")
streaming_example = discord.Streaming(name="streams", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
listening_example = discord.Activity(type=discord.ActivityType.listening, name="songs")
competing_example = discord.Activity(type=discord.ActivityType.competing, name="competitions")
watching_example = discord.Activity(type=discord.ActivityType.watching, name="movies")

activities = [playing_example, streaming_example, listening_example, competing_example, watching_example]


class MyTree(CommandTree): 
     def __init__(self, bot, /): 
         """Initialize the ClutterCommandTree class. 
  
         Args: 
             bot (Clutter): The bot to use the command tree in. 
         """ 
         super().__init__(bot) 
         self.bot = bot
        
  
     async def interaction_check(self, ctx: discord.Interaction, /) -> bool: 
         self.bot.voice_state = Voice_State(self.bot, ctx)
         return True 
  

class Yukinian(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or('?/'),
            description=description,
            pm_help=None,
            help_attrs=dict(hidden=True),
            chunk_guilds_at_startup=False,
            heartbeat_timeout=150.0,
            intents=discord.Intents.all(),
            enable_debug_events=True,         
            activity=choice(activities),
            tree_cls=MyTree,
            application_id= os.environ.get('APPLICATION_ID'),
        )
        self.voice_state: Voice_State = None
        self.CLIENT_ID = os.environ.get('CLIENT_ID')
        self.author = author
        self.cdb = cd(database_path='database/db.sqlite')
        try:
            self.cdb.utils.create_table(name="Favorite_songs",
                                        columns=[("user_id"     , str),
                                                ("song_url"      , str)])
        except Exception:
            pass
      
    async def setup_hook(self):
        for extension in initial_extensions:
            try:
                await self.load_extension(extension)
                
            except Exception as e:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()
        fmt = await bot.tree.sync()



    async def on_ready(self):
        await self.my_background_task()
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    @tasks.loop(seconds=60)
    async def my_background_task(self):
        await bot.change_presence(activity=choice(activities))


        

    
if __name__ == "__main__":
    bot = Yukinian()
    bot.run(os.environ.get('TOKEN'))
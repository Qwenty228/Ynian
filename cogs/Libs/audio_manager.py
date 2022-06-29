import math
import time
import yt_dlp as youtube_dl
import asyncio, functools
import discord, re
import urllib
from pytube import Playlist
from discord.ext import commands

from .objs import Song, SongQueue
from .config import filters, exceptions, progress_bar

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ""



#  Option base to avoid pull errors
FFMPEG_OPTION_BASE = (
    "-loglevel panic -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")

# YTDL options for creating sources
YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "extractaudio": True,
    "audioformat": "mp3",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "flatplaylist": False,
    "nocheckcertificate": True,
    "ignoreerrors": False,  # TODO change to false and handle download errors
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
    "subtitleslangs": ["en"],
    "writesubtitles": True,
    "writeautomaticsub": True,
    'subtitle': '--write-sub --sub-lang en'
}

# YTDL info extractor class
YOUTUBE_DL = youtube_dl.YoutubeDL(YTDL_OPTIONS)


class AudioSource(discord.PCMVolumeTransformer):
    """
    Takes a ytdl source and player settings
    and returns a FFmpegPCMAudio source.
    AudioSource(data, volume, position, effect)
    effect: [speed] [pitch] [nightcore] [earrape] [echo] ...
    """
    def __init__(self, ytdl, volume: float = 0.5, position: float = 0.0, **kwargs):
        self.ytdl = ytdl
        self.position = position
        self.rate = speed = kwargs.get("speed", 1)
        pitch = kwargs.get("pitch", 1)

        s_filter = f"atempo=sqrt({speed}/{pitch}),atempo=sqrt({speed}/{pitch})"
        p_filter = f",asetrate=48000*{pitch}" if pitch != 1 else ""

        base = s_filter + p_filter
        effects = "".join([y for x, y in filters.items() if kwargs.get(x)])
        ffmpeg_options = {
            "before_options": FFMPEG_OPTION_BASE + f" -ss {position}",
            "options": f'-vn -af:a "{base + effects}"',
        }

        self.original = discord.FFmpegPCMAudio(ytdl.stream_url, **ffmpeg_options)
        super().__init__(self.original, volume=volume)


class YTDLSource:
    """
    @classmethod functions create a YTDLSource object with video data
    @staticmethod functions return queueable Song objects
    """
    def __init__(self, ctx, data, search):
        self.ctx = ctx
        self.requester = ctx.user 
        self.data = data
        self.id = data.get("id")
        self.uploader = data.get("uploader")
        self.uploader_url = data.get("uploader_url")
        date = data.get("upload_date")
        self.upload_date = date[6:8] + "." + date[4:6] + "." + date[0:4]
        self.title = data.get("title")
        self.thumbnail = data.get("thumbnail")
        self.description = data.get("description")
        self.raw_duration = data.get("duration")
        self.duration = YTDLSource.parse_duration(data.get("duration"))
        self.tags = data.get("tags")
        self.url = data.get("webpage_url")
        self.views = data.get("view_count", 0)
        self.likes = data.get("like_count", 0)
        self.dislikes = data.get("dislike_count", 0)
        self.stream_url = data.get("url")
        sub = data.get('subtitles', {})
        self.subtitles = {}
        self.search = search
        for key, val in sub.items():
            if val:
                self.subtitles[key] = [functools.partial(urllib.request.urlopen, val[0].get('url')), val[0].get('url')]
            
        

    @property
    def hyperlink(self):
        return "[**{0.title}**](<{0.url}>)".format(self)

    def __str__(self):
        return "**{0.title}** by **{0.uploader}**".format(self)    
    
    @staticmethod
    def parse_duration(duration):
        if duration == None:
            value = "LIVE"
        elif duration >= 0:
            minutes, seconds = divmod(duration, 60)
            hours, minutes = divmod(minutes, 60)
            hr = f"{hours}:" if hours> 0 else None
            if hr:
                value = hr +"{}:{}".format(*[str(n).zfill(2) for n in [minutes, seconds]])
            else:
                value = "{}:{}{}".format(minutes, '0' if int(seconds) < 10 else '', int(seconds))
                
        return value


    @classmethod
    async def create_source(cls, ctx: discord.Interaction, search: str, *, loop: asyncio.BaseEventLoop = None, verbose=False):
        """create song (data) source"""
        # get task loop, (dpy bot has its own loop)
        loop = loop or asyncio.get_event_loop()
        if re.search(re.compile(r"[\?|&](list=)"), search) and '&index=' not in search:
            #track, playlist = await cls._playlist_tracks(ctx, url=search, loop=loop)
            if verbose:
                print('playlist')
            track, pl = await cls._get_playlist(ctx, search, loop=loop, verbose=verbose)
            
        else:
            if verbose:
                print('single track')
            track = await cls._get_song(ctx, search, loop=loop, verbose=verbose)
            pl = None

        return track, pl

    @staticmethod
    async def _get_song(ctx: discord.Interaction, search: str, loop: asyncio.BaseEventLoop, verbose): 
        # pattern = r'((?:http(?:s)?:\/\/)?[(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*))'
        # process = False
        # if (reg := re.search(pattern, search)):
        #     search = reg[0]
        #     process = True
        partial = functools.partial(YOUTUBE_DL.extract_info, search, download=False) 

        try:
            s = time.perf_counter()
            info = await loop.run_in_executor(None, partial)
            if verbose:
                print(f'getting data : {search} took: {time.perf_counter() - s} ')
        except Exception as e:
            raise exceptions.YTDLError(f'unable to download due to {e}')

        if 'entries' in info:
            data = None
            s = time.perf_counter()
            while data is None:
                try:
                    if verbose:
                        print('fetching data')
                    data = info["entries"].pop(0)
                except IndexError as e:
                    raise exceptions.YTDLError(f"Unable to retrieve matches for `{info['webpage_url']}`")

            if verbose:
                print(f'getting data from real url: {info["webpage_url"]} took: {time.perf_counter() - s} ')
        else:
            data = info
        if verbose:
            print('returning source')
        return Song(YTDLSource(ctx, data, search))

    @staticmethod
    async def _get_playlist(ctx, search, loop: asyncio.BaseEventLoop, verbose):

        search_key = search

        source = None

        if (playlist := list(Playlist(search))):
            I = 0
            for i, s in enumerate(playlist):
                try:
                    source = await YTDLSource._get_song(ctx, s, loop, verbose=verbose)
                    source.search = search
                    I = i
                    break
                except Exception as e:
                    # if has an error download current song get next one
                    pass

            tasks = []

            async def song_source(search, loop):
                try:
                    sr = await YTDLSource._get_song(ctx=ctx,search=search, loop=loop, verbose=verbose)
                    sr.search = search_key
                    return sr
                except Exception as e:
                    return e
            
            for s in playlist[I+1:]:
                tasks.append(functools.partial(song_source, search=s))
        else:
            tasks = None
            source = await YTDLSource._get_song(ctx, s, loop, verbose=verbose)
    
        return source, tasks


class Voice_State:
    VOICE_STATES = {}

    def __new__(cls, bot, ctx: discord.Interaction):
        if (voice_state := cls.VOICE_STATES.get(ctx.user.guild.id)) is not None:
            voice_state._ctx = ctx
            return voice_state

        voice_state = super().__new__(cls)
        cls.VOICE_STATES[ctx.user.guild.id] = voice_state
        voice_state._init(bot, ctx)
        return voice_state

    def _init(self, bot, ctx):
        self.bot = bot
        self._ctx: discord.Interaction = ctx
        self.server_id = ctx.user.guild.id

        self.source  : AudioSource = None  # Audio source.
        self.current : Song = None  # Current track.
        self.voice   : discord.VoiceClient = None  # Guild voice client.

        self._volume = 0.5  # Volume default.
        self.effects = {}

        self._loop = False

        self.song_queue : SongQueue = SongQueue()

        self.incrementer = bot.loop.create_task(self.increment_position())

    @property
    def loop(self):
        self._loop = not self._loop
        return self._loop

    @property
    def is_playing(self):
        if self.voice:
            if self.voice.is_playing():
                return True
        return False

    @property
    def validate(self):
        if self.is_playing:
            return self
        raise exceptions.InactivePlayer

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        if not 0.0 <= value <= 100.0:
            raise commands.BadArgument("Volume must be between `0.0` and `100.0`")
        self._volume = value
        self.source.volume = value


    def __setitem__(self, key, value):
        if key == "speed":  # Assert valid speed range
            if not 0.5 <= value <= 2.0:
                raise commands.BadArgument("Speed must be between `0.5` and `2.0`")
        if key == "pitch":  # Assert valid pitch range
            if not 0.5 <= value <= 2.0:
                raise commands.BadArgument("Pitch must be between `0.5` and `2.0`")

        self.effects.__setitem__(key, value)
        self.alter_audio()


    def __getitem__(self, key):  # Return false by default
        if key == "speed":  # Speed = 1 by default
            return self.effects.get(key, 1)
        if key == "pitch":  # Pitch = 1 by default
            return self.effects.get(key, 1)

        # Other effects are False by default
        return self.effects.get(key, False)
    
    def clear(self):
        self.incrementer.cancel()
        self.song_queue.clear()
        self.current = None
        self.voice.stop()

    def clear_effects(self):
        self.effects = {}
        self.alter_audio() 
        

    def alter_audio(self, *, position=None):
        if position is None:
            position = self.source.position

        self.voice.pause()  # Pause the audio before altering
        self.source = AudioSource(self.current.source, self.volume, position, **self.effects)
        self.voice.play(self.source, after=lambda x=None: asyncio.run(self.play_next_song()))

    async def increment_position(self):
        """Keeps track of the position in the song"""
        def condition():
            if not self.voice:
                return False
            else:
                if not self.voice.is_playing():
                    return False
            if not self.source:
                return False
            return True

        while True:
            if condition():
                self.source.position += self.source.rate
            await asyncio.sleep(1.0)

    async def connect(self, channel: discord.VoiceChannel = None):
        user_vc = self._ctx.user.voice.channel if self._ctx.user.voice else None
        vc = channel or user_vc
        if not vc:
            raise exceptions.NoVoiceChannel()

        if self.voice:
            if self.voice.channel == vc:
                return 'already in this channel'
            await self.voice.move_to(vc)
            return f'move to {vc}!'

        self.voice = await vc.connect()
        return f'connect to {vc}!'

    async def play(self, song, position=0):
        track, pl = await YTDLSource.create_source(self._ctx, song, loop=self.bot.loop, verbose=False)

        if self.is_playing:
            'enqueue'
            await self.song_queue.add_playlist([track])
            text = 'Enqueue'
        else: 
            self.current = track
            self.source = AudioSource(self.current.source, self._volume, position, **self.effects)
            self.voice.play(self.source, after=lambda x=None: asyncio.run(self.play_next_song()))
            text = "Now Playing!"
        pending = None
        t = text
        if pl:
            t = text + f', adding {len(pl)} songs from playlist!' 
            pending = await self.song_queue.add_playlist(pl)
            
            
        return track.create_embed(words=t), pending, text

    async def play_next_song(self):    
        if self._loop and self.current:
            track, _ = await YTDLSource.create_source(self._ctx, self.current.source.url, verbose=False)
            if self.song_queue._num_shift != 0: # mean queue has been rotated
                self.song_queue.insert(self.song_queue._num_shift, track)
                self.song_queue._num_shift = 0
            else:
                await self.song_queue.add_playlist([track])
        
        if len(self.song_queue) == 0:
            return

        self.current = self.song_queue.popleft()
        self.source = AudioSource(self.current.source, self._volume, 0, **self.effects)
        self.voice.play(self.source, after=lambda x=None: asyncio.run(self.play_next_song()))

    async def show_queue(self, page):
        queue_length =len(self.song_queue)
        items_per_page = 10
        pages = math.ceil((queue_length + 1) / items_per_page)
        page = pages if page == -1 else min(max(1, page), pages)

        start = (page - 1) * items_per_page
        end = start + items_per_page
   
        queue = "{0}{1}\n ------------\n".format(self.current.hyperlink, " <<< Now Playing")

        for i, song in enumerate(list(self.song_queue)[start:end], start=start):    
            if isinstance(song, Song):
                queue += f"`{i+1}.` {song.hyperlink}\n"
            else:
                queue += f"`{i+1}.` fetching data...\n"
        
        amount = queue_length + 1 if self._loop else queue_length
    
        embed = (discord.Embed(description=f"**{amount} Songs in Queue:{'🔁' if self._loop else ''}**\n\n{queue}", color=0x5a3844)
            ).set_footer(text=f"<-- this guy is very proud of this music extension he made    Viewing page {page}/{pages}", icon_url="https://cdn.discordapp.com/avatars/515844352971636736/3fc4dabf653fe3a534be173c02a0dd9e.png?size=1024")

        return embed

    async def show_current(self):
        embed = self.current.create_embed(f"currently playing")
        for e, v in self.effects.items():
            embed.add_field(name=str(e), value=f'`{v}`')

        if (rd := self.current.source.raw_duration):
            total_duration = int(rd)
            ratio = self.source.position/total_duration

            time_url = "&t=" + str(self.source.position)
            embed.add_field(name='time_stamp', value=f'[{self.current.source.parse_duration(int(self.source.position))}]({str(self.current.source.url) + time_url})')
            #file = self.current.create_progress_bar(max([0.01, ratio]))
            #embed.set_image(url="attachment://image.png")
            embed.set_image(url=progress_bar[int(100*ratio)])


        else:
            embed.title = 'currently streaming'
            #ile = self.current.create_progress_bar(1)
            #embed.set_image(url="attachment://image.png")
            embed.set_image(url=progress_bar[100])

        
        return embed

    
    
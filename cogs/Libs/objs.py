import discord, json
import math, io
from PIL import Image
import asyncio, functools
from collections import deque



class Song:
    # preloading arrtributes
    __slots__ = ('source', 'requester', 'search', 'subtitles')

    def __init__(self, source):
        self.source = source
        self.search = source.search
        self.requester = source.requester
        self.subtitles = source.subtitles
        

    def __str__(self) -> str:
        if self.source.uploader:
            return f"**{self.source.title}** by **{self.source.uploader}**"
        return f"**{self.source.title}**"

    def __eq__(self, other):
        if isinstance(other, Song):
            return self.search == other.search and self.source.title == other.source.title
        else:
            return self is other

    def __hash__(self):
        return hash((self.search, self.source.title))

    def __repr__(self) -> str:
        return f"**{self.source.title}**"

    @property
    def hyperlink(self):
        return f"**[{self.source.title}]({self.source.url})**"

    @property
    def has_data(self):
        if self.source.data:
            return True
        return False

    def create_embed(self, words="Now playing"):
        thumbnail = self.source.thumbnail
      
        embed = (discord.Embed(title=words, description='```css\n{0.source.title}\n```**search with**\n{1}'.format(self, str(self.search)), color=0x66ff99)  # discord.Color.blurple())
                .add_field(name='Duration', value=self.source.duration)
                .add_field(name='Requested by', value=self.requester.mention)
                .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                .set_thumbnail(url=thumbnail)
                .set_author(name=self.requester.name, icon_url=self.requester.avatar)
                .set_footer(text="Hi :D", icon_url='https://cdn.discordapp.com/avatars/907501414178258945/72371c48cea3b587d061af09e9bc9d21.png?size=1024'))
                
        return embed
    
    @staticmethod
    def create_progress_bar(ratio, length=800, width=20):
        GRAY = (75,75,75)
        BLUE = (85, 189, 116)
        bar_length = ratio * length
        a = 0
        b = -1
        c = width / 2
        w = (width / 2) + 1

        shell = Image.new("RGB", (length, width), color=GRAY)
        imgsize = (int(bar_length), width)  # The size of the image
        image = Image.new("RGB", imgsize, color=GRAY)  # Create the image

        innerColor = BLUE  # Color at the center
        outerColor = [0, 0, 0]  # Color at the edge

        for y in range(imgsize[1]):
            for x in range(imgsize[0]):
                dist = (a * x + b * y + c) / math.sqrt(a * a + b * b)
                color_coef = abs(dist) / w

                if abs(dist) < w:
                    red = outerColor[0] * color_coef + innerColor[0] * (1 - color_coef)
                    green = outerColor[1] * color_coef + innerColor[1] * (
                        1 - color_coef
                    )
                    blue = outerColor[2] * color_coef + innerColor[2] * (1 - color_coef)

                    image.putpixel((x, y), (int(red), int(green), int(blue)))

        shell.paste(image)
        buffer = io.BytesIO()
        shell.save(buffer, "png")  # 'save' function for PIL
        buffer.seek(0)
        return discord.File(fp=buffer, filename="image.png")

   

    def get_subtitle(self, language):
                
        if (sub := self.subtitles.get(language)) is not None:
            sub, url = sub
            data = json.loads(sub().read()) or {}
        
            data = data.get('events', [])


            # def get_by_time(self, time):
            #     #print(time*1000)
            #     if self.cur == None:
            #         while True:
            #             cur = next(self.data)
            #             if time*1000 <= float(cur['tStartMs'] + cur['dDurationMs']):
            #                 break
            #     else:
            #         cur = self.cur

            #     self.cur = cur
            #     if time*1000 >= float(cur['tStartMs'] + cur['dDurationMs']):
            #         self.cur = None
                    
            #     #print(cur)
            #     return cur['segs'][0]['utf8']
            for event in data:
                yield event
        
    


class SongQueue(deque):
    def __init__(self, iterable=[]):
        super(SongQueue, self).__init__(iterable)
        self._num_shift = 0

    def rotate(self, __n: int = ...) -> None:
        self._num_shift = __n
        return super().rotate(__n)

    async def add_playlist(self, __iterable) -> None:
        self.extend(__iterable)
        errors = []
        async def m():
            loop = asyncio.get_event_loop()
            for current in list(__iterable):
                if isinstance(current, Song):
                    continue
                song = await current(loop=loop)  
                try:
                    if isinstance(current, functools.partial):
                        self[self.index(current)] = song            
                    else:
                        self.remove(current)
                        errors.append(song)
                except IndexError:
                    print('error', self._num_shift)

                await asyncio.sleep(0.1)
            return errors
  
        task = asyncio.create_task(m())
        return task
      

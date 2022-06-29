from discord.ext import commands
# import discord, io
# from PIL import Image
# import pygame as pg
from youtube_search import YoutubeSearch



filters = {  # Mapping of filters to their names
            "nightcore": ",asetrate=48000*1.1",
            "earrape": ",acrusher=.1:1:64:0:log",
            "echo": ",aecho=0.5:0.5:500|50000:1.0|1.0",
            "muffle": ",lowpass=f=300",
            "treble": ",treble=g=15",
            "bass": ",bass=g=15",
            # "backwards": ",areverse",
            "phaser": ",aphaser=type=t:speed=2:decay=0.6",
            "robot": ",afftfilt=real='hypot(re,im)*sin(0)':imag='hypot(re,im)*cos(0)':win_size=512:overlap=0.75",
            "tremolo": ",apulsator=mode=sine:hz=3:width=0.1:offset_r=0",
            "vibrato": ",vibrato=f=10:d=1",
            "whisper": ",afftfilt=real='hypot(re,im)*cos((random(0)*2-1)*2*3.14)':imag='hypot(re,im)*sin((random(1)*2-1)*2*3.14)':win_size=128:overlap=0.8",
        }

progress_bar = {0:'https://cdn.discordapp.com/attachments/455952391381188638/985263432481775626/image.png',
                1:'https://cdn.discordapp.com/attachments/455952391381188638/985263434537009253/image.png',
                2:'https://cdn.discordapp.com/attachments/455952391381188638/985263436936130600/image.png',
                3:'https://cdn.discordapp.com/attachments/455952391381188638/985263439159115806/image.png',
                4:'https://cdn.discordapp.com/attachments/455952391381188638/985263440933290055/image.png',
                5:'https://cdn.discordapp.com/attachments/455952391381188638/985263455114244096/image.png',
                6:'https://cdn.discordapp.com/attachments/455952391381188638/985263457026838638/image.png',
                7:'https://cdn.discordapp.com/attachments/455952391381188638/985263458893299742/image.png',
                8:'https://cdn.discordapp.com/attachments/455952391381188638/985263460759777301/image.png',
                9:'https://cdn.discordapp.com/attachments/455952391381188638/985263462533972068/image.png',
                10:'https://cdn.discordapp.com/attachments/455952391381188638/985263477922881598/image.png',
                11:'https://cdn.discordapp.com/attachments/455952391381188638/985263480225529916/image.png',
                12:'https://cdn.discordapp.com/attachments/455952391381188638/985263482431742032/image.png',
                13:'https://cdn.discordapp.com/attachments/455952391381188638/985263484294017074/image.png',
                14:'https://cdn.discordapp.com/attachments/455952391381188638/985263486152114196/image.png',
                15:'https://cdn.discordapp.com/attachments/455952391381188638/985263501419380746/image.png',
                16:'https://cdn.discordapp.com/attachments/455952391381188638/985263503323561984/image.png',
                17:'https://cdn.discordapp.com/attachments/455952391381188638/985263505412337684/image.png',
                18:'https://cdn.discordapp.com/attachments/455952391381188638/985263507601776740/image.png',
                19:'https://cdn.discordapp.com/attachments/455952391381188638/985263509426274424/image.png',
                20:'https://cdn.discordapp.com/attachments/455952391381188638/985263526052515880/image.png',
                21:'https://cdn.discordapp.com/attachments/455952391381188638/985263528439074836/image.png',
                22:'https://cdn.discordapp.com/attachments/455952391381188638/985263530573959218/image.png',
                23:'https://cdn.discordapp.com/attachments/455952391381188638/985263532507553812/image.png',
                24:'https://cdn.discordapp.com/attachments/455952391381188638/985263534436921444/image.png',
                25:'https://cdn.discordapp.com/attachments/455952391381188638/985263549565771816/image.png',
                26:'https://cdn.discordapp.com/attachments/455952391381188638/985263551809740850/image.png',
                27:'https://cdn.discordapp.com/attachments/455952391381188638/985263555639119922/image.png',
                28:'https://cdn.discordapp.com/attachments/455952391381188638/985263558092800030/image.png',
                29:'https://cdn.discordapp.com/attachments/455952391381188638/985263560026386482/image.png',
                30:'https://cdn.discordapp.com/attachments/455952391381188638/985263572366016632/image.png',
                31:'https://cdn.discordapp.com/attachments/455952391381188638/985263574115045446/image.png',
                32:'https://cdn.discordapp.com/attachments/455952391381188638/985263575897620540/image.png',
                33:'https://cdn.discordapp.com/attachments/455952391381188638/985263577751486494/image.png',
                34:'https://cdn.discordapp.com/attachments/455952391381188638/985263580175814788/image.png',
                35:'https://cdn.discordapp.com/attachments/455952391381188638/985263595560525854/image.png',
                36:'https://cdn.discordapp.com/attachments/455952391381188638/985263598311993354/image.png',
                37:'https://cdn.discordapp.com/attachments/455952391381188638/985263600996323328/image.png',
                38:'https://cdn.discordapp.com/attachments/455952391381188638/985263603231907901/image.png',
                39:'https://cdn.discordapp.com/attachments/455952391381188638/985263605266145280/image.png',
                40:'https://cdn.discordapp.com/attachments/455952391381188638/985263618641776670/image.png',
                41:'https://cdn.discordapp.com/attachments/455952391381188638/985263620650831882/image.png',
                42:'https://cdn.discordapp.com/attachments/455952391381188638/985263623087751178/image.png',
                43:'https://cdn.discordapp.com/attachments/455952391381188638/985263624983572530/image.png',
                44:'https://cdn.discordapp.com/attachments/455952391381188638/985263626837426186/image.png',
                45:'https://cdn.discordapp.com/attachments/455952391381188638/985263641676881950/image.png',
                46:'https://cdn.discordapp.com/attachments/455952391381188638/985263644017320006/image.png',
                47:'https://cdn.discordapp.com/attachments/455952391381188638/985263645812477992/image.png',
                48:'https://cdn.discordapp.com/attachments/455952391381188638/985263647964151838/image.png',
                49:'https://cdn.discordapp.com/attachments/455952391381188638/985263650082283551/image.png',
                50:'https://cdn.discordapp.com/attachments/455952391381188638/985263664472936538/image.png',
                51:'https://cdn.discordapp.com/attachments/455952391381188638/985263666645569596/image.png',
                52:'https://cdn.discordapp.com/attachments/455952391381188638/985263669048901692/image.png',
                53:'https://cdn.discordapp.com/attachments/455952391381188638/985263670810517634/image.png',
                54:'https://cdn.discordapp.com/attachments/455952391381188638/985263672848953474/image.png',
                55:'https://cdn.discordapp.com/attachments/455952391381188638/985263687600316476/image.png',
                56:'https://cdn.discordapp.com/attachments/455952391381188638/985263689735241758/image.png',
                57:'https://cdn.discordapp.com/attachments/455952391381188638/985263691748479027/image.png',
                58:'https://cdn.discordapp.com/attachments/455952391381188638/985263693644329020/image.png',
                59:'https://cdn.discordapp.com/attachments/455952391381188638/985263695632433212/image.png',
                60:'https://cdn.discordapp.com/attachments/455952391381188638/985263710702567474/image.png',
                61:'https://cdn.discordapp.com/attachments/455952391381188638/985263712753569872/image.png',
                62:'https://cdn.discordapp.com/attachments/455952391381188638/985263714640994354/image.png',
                63:'https://cdn.discordapp.com/attachments/455952391381188638/985263717048516669/image.png',
                64:'https://cdn.discordapp.com/attachments/455952391381188638/985263719212793906/image.png',
                65:'https://cdn.discordapp.com/attachments/455952391381188638/985263734769483797/image.png',
                66:'https://cdn.discordapp.com/attachments/455952391381188638/985263737021800508/image.png',
                67:'https://cdn.discordapp.com/attachments/455952391381188638/985263739144110120/image.png',
                68:'https://cdn.discordapp.com/attachments/455952391381188638/985263741002211389/image.png',
                69:'https://cdn.discordapp.com/attachments/455952391381188638/985263743283916890/image.png',
                70:'https://cdn.discordapp.com/attachments/455952391381188638/985263757620035674/image.png',
                71:'https://cdn.discordapp.com/attachments/455952391381188638/985263759507480666/image.png',
                72:'https://cdn.discordapp.com/attachments/455952391381188638/985263762078588978/image.png',
                73:'https://cdn.discordapp.com/attachments/455952391381188638/985263765358526534/image.png',
                74:'https://cdn.discordapp.com/attachments/455952391381188638/985263767602475078/image.png',
                75:'https://cdn.discordapp.com/attachments/455952391381188638/985263780537704548/image.png',
                76:'https://cdn.discordapp.com/attachments/455952391381188638/985263782387388456/image.png',
                77:'https://cdn.discordapp.com/attachments/455952391381188638/985263784396476466/image.png',
                78:'https://cdn.discordapp.com/attachments/455952391381188638/985263786317447218/image.png',
                79:'https://cdn.discordapp.com/attachments/455952391381188638/985263788364271637/image.png',
                80:'https://cdn.discordapp.com/attachments/455952391381188638/985263803728007229/image.png',
                81:'https://cdn.discordapp.com/attachments/455952391381188638/985263807041507398/image.png',
                82:'https://cdn.discordapp.com/attachments/455952391381188638/985263808991862854/image.png',
                83:'https://cdn.discordapp.com/attachments/455952391381188638/985263811210649620/image.png',
                84:'https://cdn.discordapp.com/attachments/455952391381188638/985263813219729518/image.png',
                85:'https://cdn.discordapp.com/attachments/455952391381188638/985263827308408892/image.png',
                86:'https://cdn.discordapp.com/attachments/455952391381188638/985263829766242334/image.png',
                87:'https://cdn.discordapp.com/attachments/455952391381188638/985263831599185920/image.png',
                88:'https://cdn.discordapp.com/attachments/455952391381188638/985263833432092763/image.png',
                89:'https://cdn.discordapp.com/attachments/455952391381188638/985263835176927272/image.png',
                90:'https://cdn.discordapp.com/attachments/455952391381188638/985263849898934292/image.png',
                91:'https://cdn.discordapp.com/attachments/455952391381188638/985263851681505380/image.png',
                92:'https://cdn.discordapp.com/attachments/455952391381188638/985263853455675482/image.png',
                93:'https://cdn.discordapp.com/attachments/455952391381188638/985263855552835654/image.png',
                94:'https://cdn.discordapp.com/attachments/455952391381188638/985263857666773012/image.png',
                95:'https://cdn.discordapp.com/attachments/455952391381188638/985263873114378260/image.png',
                96:'https://cdn.discordapp.com/attachments/455952391381188638/985263875299622952/image.png',
                97:'https://cdn.discordapp.com/attachments/455952391381188638/985263877828784219/image.png',
                98:'https://cdn.discordapp.com/attachments/455952391381188638/985263879607169055/image.png',
                99:'https://cdn.discordapp.com/attachments/455952391381188638/985263881339412630/image.png',
                100:'https://cdn.discordapp.com/attachments/455952391381188638/985263896107581490/image.png'}


class exceptions:
    class InactivePlayer(commands.BadArgument):
        """
        Custom exception to raise when
        the music player is not active.
        """
        def __init__(self, *args):
            msg = "No track is currently being played."
            super().__init__(message=msg, *args)

    class NoVoiceChannel(commands.BadArgument):
        """
        Custom exception to raise when
        tno channel to join
        """
        def __init__(self, *args):
            msg = "Not given specific Channel to join and user is not in any Voice Channel "
            super().__init__(message=msg, *args)


    class FeatureNotSupported(commands.BadArgument):
        """
        Custom exception to raise when the user
        uses on a not yet implemented music feature.
        """
        def __init__(self, message=None, *args):
            msg = "Feature is currently not supported."
            super().__init__(message=message or msg, *args)

    class InvalidMediaType(commands.BadArgument):
        """
        Custom exception to raise when the
        file media type cannot be played.
        """
        def __init__(self, message=None, *args):
            msg = "Invalid media type. Media type must be either audio or video."
            super().__init__(message=message or msg, *args)


    class IsBound(commands.BadArgument):
        """
        Custom exception to raise when the
        bot is bound to a specific text channel.
        """
        def __init__(self, channel, *args):
            msg = f"Music commands cannot be used outside of {channel.mention}."
            super().__init__(message=msg, *args)

    class ButtonOnCooldown(commands.CommandError):
        def __init__(self, retry_after: float):
            self.retry_after = retry_after


    class SpotifyError(Exception):
        pass

    class VoiceError(Exception):
        pass

    class YTDLError(Exception):
        pass

    class InvalidPosition(Exception):
        pass

# def create_progress_bar_2(ratio):
#     def roundcorner(surf, roundness):
#         """make round corner"""
#         size = surf.get_size()
#         rect_image = pg.Surface(size, pg.SRCALPHA)
#         pg.draw.rect(rect_image, (255, 255, 255), (0, 0, *size), border_radius=roundness)
#         image = surf.copy()
#         image.blit(rect_image, (0, 0), None, pg.BLEND_RGBA_MIN) 
#         return image
    
#     def gradientRect( left_colour, right_colour, target_rect ):
#         """ Draw a horizontal-gradient filled rectangle covering <target_rect> """
#         colour_rect = pg.Surface( ( 2, 2 ) )                                   # tiny! 2x2 bitmap
#         pg.draw.line( colour_rect, left_colour,  ( 0,0 ), ( 0,1 ) )            # left colour line
#         pg.draw.line( colour_rect, right_colour, ( 1,0 ), ( 1,1 ) )            # right colour line
#         return pg.transform.smoothscale( colour_rect, ( target_rect.width, target_rect.height ) )  # stretch!
    
    
#     percent = ratio
#     bg = pg.Surface((800, 20), pg.SRCALPHA)
#     f = pg.Surface((800, 12))
#     f.fill((50,50,50))
#     frame = roundcorner(f, 10)

#     pointer = pg.image.load(r"C:\Users\zuto37\OneDrive\Desktop\pics\silver.png")
#     pointer = pg.transform.scale(pointer, (15, 13))

#     bar = roundcorner(gradientRect(0x72f2e5, 0x328c40, pg.Rect(0, 0, int(percent*785/100), 6)), 3)

#     bg.blit(frame, (0, 4))
#     bg.blit(bar, (5, 7))
#     bg.blit(pointer, (783*percent/100, 3))


#     pil_string_image = pg.image.tostring(bg, "RGB", False)
#     pli_image = Image.frombytes('RGB', bg.get_size(), pil_string_image, 'raw')
#     buffer = io.BytesIO()
#     pli_image.save(buffer, format="png")

#     buffer.seek(0)
#     return discord.File(fp=buffer, filename="image.png")


def search_song(arg: str, m=10):
    return YoutubeSearch(arg, max_results=m).to_dict()
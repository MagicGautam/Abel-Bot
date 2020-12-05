import discord
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
import youtube_dl
import random

from random import choice

youtube_dl.utils.bug_reports_message = lambda: ''       #YTDL API CLASS IMPLEMENTATION.

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


weeknd = commands.Bot(command_prefix='!')
queue = []

@weeknd.event 
async def on_ready():
    await weeknd.change_presence(activity=discord.Game('with your feelings'))
    print('\n**********************')
    print('The Weeknd is Summoned')
    print('**********************')
    
@weeknd.command()
async def clear(ctx, amount=6): #To clear the last 6 messages including the !clear one in the chat.
    await ctx.channel.purge(limit=amount)

##############################  KICK-BAN-UNBAN  ##################################################

@weeknd.command()
async def kick(ctx, member: discord.Member, *, reason=None):  #To make the bot kick the user.
    await member.kick(reason=reason)

@weeknd.command()
async def ban(ctx, member: discord.Member, *, reason=None): #To make the bot Ban the banned user.
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention}')

@weeknd.command()
async def unban(ctx, *, member): #To make the bot Unban the banned user.
    banned_users= await ctx.guild.bans()
    member_name, member_discriminator= member.split('#')
    for ban_entry in banned_users:
        user=ban_entry.user
        if(user.name, user.discriminator)== (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {member.mention}')
            return


##############################  Jokes-Funny-questions CONFIG  ####################################
@weeknd.command()
async def joke(ctx): #This Function is used to trigger the Joke saying sequence of the bot when !joke is used in the discord chat.
    jokes= ["What's oragne and sounds like parrot? A Carrot.",
                "What's blue and smells like red paint? Blue Paint",
                "My Grandpa has The heart of a lion, and a lifetime ban from the zoo",
                "My therapist told me ""Time heals all Wounds"", So i stabbed her. Now we wait....",
                "What's similar between a pregnant 14 year old and the fetus inside of her? They are both thinking ""holy shit, my mom is gonna kill me.""",
                "what do you call a blind German… a not see.",
                "Whats The Only Zodiac That Cant Grow Hair?..CANCER",
                "I have a Fish that can breakdance for 20 sec but only once",
                "You know you’re not liked when you get handed the camera every time they make a group photo.",
                "You’re not completely useless. You can always serve as a bad example.",
                "Wow wow wow, calm down, we are just acquaintances",
                "My boss said to me, “You’re the worst train driver ever. How many have you derailed this year?” I said, “I’m not sure; it’s hard to keep track.”",
                "My grandfather says I’m too reliant on technology. I called him a hypocrite and unplugged his life support.",
                "I hope Death is a woman. That way it will never look at me twice.",
                "My elderly relatives liked to tease me at weddings, saying, “You’ll be next!” They soon stopped though, once I started doing the same to them at funerals.",
                "Can orphans eat at a family restaurant?",
                "A woman visits the doctor as she has some abdominal pains and suspects she may be pregnant. After her examination, the doctor comes out to see her: “Well, I hope you like changing diapers”, to which she replies: “Oh my god am I pregnant!?”\nTo which he responds: “No, you’ve got bowel cancer.”"
            ]

    await ctx.send(f'{random.choice(jokes)}')

@weeknd.command(aliases=['weeknd','heyabel','ayoweek','heystarboy'])
async def _heyabel(ctx, *, question): #This Function is used to trigger the question answering sequence of the bot when !weeknd is used in the discord chat.
    answers= ["Can't promise but yeah.",
                "Save your Tears for another day.",
                "Yeah...Could be.",
                "Nah, i ain't in mood to talk",
                "Watch yo back.",
                "I can't talk rn, booty calls ;).",
                "Well yes, but no.",
                "Hell Yeah.",
                "Yeah.",
                "Maybe.",
                "Wow wow wow, calm down, we are just acquaintances",
                "Call me later.",
                "Son, you are not ready for the answer.",
                "Well, Talk to my hand.",
                "Yo that won't work my man.",
                "Well, i afraid that won't happen.",
                "Well, Nigga i don't think so."]           
    await ctx.send(f'{random.choice(answers)}')


##############################  MUSIC BOT CONFIG  ###############################################

@weeknd.command()
async def join(ctx):    #To make the bot join the voice channel.
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel")
        return
    
    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()

@weeknd.command()
async def leave(ctx):   #To make the bot leave the voice channel.   
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

@weeknd.command()
async def queue_(ctx, url): #To make the bot Queue the song.
    global queue

    queue.append(url)
    await ctx.send(f'`{url}` added to queue!')

@weeknd.command()
async def play(ctx): #To make the bot Play the queued song.
    global queue

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(queue[0], loop=weeknd.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**Now playing:** {}'.format(player.title))
    del(queue[0])

@weeknd.command()
async def pause(ctx):#To make the bot Pause the queued song.
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.pause()

@weeknd.command()
async def resume(ctx):#To make the bot Resume the queued song.
    server = ctx.message.guild
    voice_channel = server.voice_client
    
    voice_channel.resume()

@weeknd.command()
async def view(ctx):#To make the bot display the queued song.
    await ctx.send(f'Your queue is now `{queue}!`')

@weeknd.command()
async def stop(ctx):#To make the bot stop the queued song.
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.stop()

weeknd.run('TOKEN')
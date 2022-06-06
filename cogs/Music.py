import os
import nextcord
from nextcord.ext import commands
from nextcord import FFmpegPCMAudio
from youtubesearchpython import VideosSearch
import sys
import os.path
import yt_dlp
import shutil
import config
import settings
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)) + '/Dependencies/')
import Threaded_timer
import dccommands

extensions = config.extension
ydl_opts = {
'format': 'bestaudio/best',
'postprocessors': [{
    'key':'FFmpegExtractAudio',
    'preferredcodec': 'mp3',
    'preferredquality': '192',
}]
}

class Music(commands.Cog):

    def __init__(self, client):
        print("Music Initialized Successfully")
        self.client = client

    @commands.command(pass_context = True)
    async def join(self, ctx):
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if (ctx.author.voice):
            if voice == None:
                pwd = os.path.dirname(os.path.realpath(__file__))
                if os.path.isdir(pwd + '/' + str(ctx.guild.id)):
                    shutil.rmtree(pwd + '/' + str(ctx.guild.id))
                    print('directory ' + str(ctx.guild.id) + ' has been deleted')
                os.mkdir(pwd+ '/' + str(ctx.guild.id))
                print('directory ' + str(ctx.guild.id) + ' has been created')
                settings.queues[ctx.guild.id] = []
                settings.titles[ctx.guild.id] = []
                settings.downloading[ctx.guild.id] = False
                settings.searches[ctx.guild.id] = ''
                channel = ctx.message.author.voice.channel
                voice = await channel.connect()
                await ctx.send('Successfully Joined the ' + str(channel) + ' voice channel')
                print('Successfully Joined the ' + str(channel) + ' voice channel')
                settings.timers[ctx.guild.id] = Threaded_timer.RepeatedTimer(1, queue, ctx)
                settings.timers[ctx.guild.id].stop()
            else:
                await ctx.send("I am already connected")
        else:
            print('User is not in a voice channel')
            await ctx.send("You are not in a voice channel, you must be in a voice channel for me to join")

    @commands.command(pass_context = True)
    async def leave(self, ctx):
        pwd = os.path.dirname(os.path.realpath(__file__))
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if (ctx.voice_client):
            await voice.disconnect()
            await ctx.send("Left the voice channel")
        else:
            await ctx.send("I am not in a voice channel")
        shutil.rmtree(pwd + '/' + str(ctx.guild.id))
        print('directory ' + str(ctx.guild.id) + ' has been deleted')
        settings.timers[ctx.guild.id].stop()
        settings.timers.pop(ctx.guild.id)
        settings.queues.pop(ctx.guild.id)
        settings.searches.pop(ctx.guild.id)
        settings.titles.pop(ctx.guild.id)
        print('Successfully left the voice Channel')

    @commands.command(pass_context = True)
    async def play(self, ctx, *, url:str):
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        pwd = os.path.dirname(os.path.realpath(__file__))
        if (ctx.author.voice):
            print(url)
            if voice == None:
                if os.path.isdir(pwd + '/' + str(ctx.guild.id)):
                    shutil.rmtree(pwd + '/' + str(ctx.guild.id))
                    print('directory ' + str(ctx.guild.id) + ' has been deleted')
                os.mkdir(pwd+ '/' + str(ctx.guild.id))
                print('directory ' + str(ctx.guild.id) + ' has been created')
                settings.queues[ctx.guild.id] = []
                settings.titles[ctx.guild.id] = []
                settings.downloading[ctx.guild.id] = False
                settings.searches[ctx.guild.id] = ''
                channel = ctx.message.author.voice.channel
                voice = await channel.connect()
                await ctx.send('Successfully Joined the ' + str(channel) + ' voice channel')
                print('Successfully Joined the ' + str(channel) + ' voice channel')
                settings.timers[ctx.guild.id] = Threaded_timer.RepeatedTimer(1, queue, ctx, self.client)
                settings.timers[ctx.guild.id].stop()
            if 'https://www.youtube.com' in url or 'https://youtu.be' in url:
                settings.queues[ctx.guild.id].append(url)
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False, process=False)
                    title = info.get('title', None)
                    settings.titles[ctx.guild.id].append(title)
                if voice.is_playing() or voice.is_paused() or settings.downloading[ctx.guild.id] == True:
                    if "playlist" in url:
                        await ctx.send('Playlist ***' + title + '*** has been added to the queue')
                    else:
                        await ctx.send('***' + title + '*** has been added to the queue')
                else:
                    await ctx.send('Retrieving from source')
                    if "playlist" in url:
                        await ctx.send('Now playing playlist:\n***' + title + '***')
                        await ctx.send('Please enjoy this music while the playlist is being retrieved.')
                    else:
                        await ctx.send('Now playing:\n***' + title + '***')
                if settings.downloading[ctx.guild.id] == False:
                    settings.timers[ctx.guild.id].start()
            elif url == '1' or url == '2' or url == '3' or url == '4' or url == '5':
                if settings.searches[ctx.guild.id] == '':
                    await ctx.send('There is currently no searched music, please search for a song and try again.')
                else:
                    print('successfully chose a song')
                    if voice.is_playing() or voice.is_paused() or settings.downloading[ctx.guild.id] == True:
                        await ctx.send('Song number ' + url + ' selected:\n***' + settings.searches[ctx.guild.id]['result'][int(url)-1]['title']+'*** has been added to the queue')
                    else:
                        await ctx.send('Song number ' + url + ' selected:\nNow Playing:\n***' + settings.searches[ctx.guild.id]['result'][int(url)-1]['title']+'***')
                    settings.queues[ctx.guild.id].append(settings.searches[ctx.guild.id]['result'][int(url)-1]['link'])
                    settings.titles[ctx.guild.id].append(settings.searches[ctx.guild.id]['result'][int(url)-1]['title'])
                    settings.searches[ctx.guild.id] = ''
                    if settings.downloading[ctx.guild.id] == False:
                        settings.timers[ctx.guild.id].start()
            else:
                vidsearch = VideosSearch(url, limit = 5)
                settings.searches[ctx.guild.id] = vidsearch.result()
                await ctx.send('Please select a song from the following results:\nSyntax:\n' + extensions + 'play 3\n' + '1: ***' + settings.searches[ctx.guild.id]['result'][0]['title']+'***\n'
                '2: ***' + settings.searches[ctx.guild.id]['result'][1]['title']+'***\n'+
                '3: ***' + settings.searches[ctx.guild.id]['result'][2]['title']+'***\n'+
                '4: ***' + settings.searches[ctx.guild.id]['result'][3]['title']+'***\n'+
                '5: ***' + settings.searches[ctx.guild.id]['result'][4]['title']+'***\n')
        else:
            await ctx.send("You are not in a voice channel, you must be in a voice channel for me to join")

    @play.error
    async def unpause(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
            if voice.is_paused():
                voice.resume()
                await ctx.send("Music is playing")
            else:
                await ctx.send("There is no paused audio in the voice channel.")


    @commands.command(pass_context = True)
    async def pause(self, ctx):
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.pause()
            await ctx.send("Music has been paused")
        else:
            await ctx.send("There is no audio playing in the voice channel.")

    @commands.command(pass_context = True)
    async def stop(self, ctx):
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice.is_playing() or voice.is_paused():
            settings.queues[ctx.guild.id].clear()
            settings.titles[ctx.guild.id].clear()
            voice.stop()
            await ctx.send("Music has been stopped and queue has been cleared")
            print("Music has been stopped and queue has been cleared")
            os.system('rm ' + str(ctx.guild.id) + '/*.mp3')
            os.system('rm ' + str(ctx.guild.id) + '/*.webm')
            settings.timers[ctx.guild.id].stop()
        else:
            await ctx.send("There is no audio to stop.")

    @commands.command(pass_context = True)
    async def skip(self, ctx):
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice.is_playing() or voice.is_paused():
            voice.stop()
            await ctx.send("Song has been skipped")
            print("\nSong has been skipped\n")
            if settings.queues[ctx.guild.id]:
                if "youtube" in settings.queues[ctx.guild.id][0]:
                    title = settings.titles[ctx.guild.id][0]
                    if "playlist" in settings.queues[ctx.guild.id][0]:
                        await ctx.send('Now playing playlist:\n***' + title + '***')
                        await ctx.send('Please enjoy this music while the playlist is being retrieved.')
                    else:
                        await ctx.send('Now playing:\n***' + title + '***')
                elif "song" in settings.queues[ctx.guild.id][0]:
                    await ctx.send('Now playing the next item in your playlist')
            else:
                await ctx.send("Your queue is empty")
        else:
            await ctx.send("There is no music to skip.")

    @commands.command(pass_context = True)
    async def showqueue(self, ctx):
        queued = ''
        counter = 0
        for title in settings.titles[ctx.guild.id]:
            queued = queued + str(counter+1) + ': ***' + settings.titles[ctx.guild.id][counter] + '***\n'
            counter = counter + 1
        if queued == '':
            await ctx.send('There are no songs currently on queue')
        else:
            await ctx.send('Songs currently on queue:\n' + queued)

def setup(client):
    client.add_cog(Music(client))

def queue(ctx, client):
    pwd = os.path.dirname(os.path.realpath(__file__))
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
    if (voice.is_playing() or voice.is_paused()):
        pass
    else:
        settings.timers[ctx.guild.id].stop()
        if settings.queues[ctx.guild.id]:
            if settings.queues[ctx.guild.id][0].startswith('song'):
                source = FFmpegPCMAudio(pwd+'/'+str(ctx.guild.id)+'/'+settings.queues[ctx.guild.id][0])
            else:
                settings.downloading[ctx.guild.id] = True
                if "playlist" in settings.queues[ctx.guild.id][0]:
                    os.system('rm ' + pwd+'/'+str(ctx.guild.id) + '/*.mp3')
                    os.system('rm ' + pwd+'/'+str(ctx.guild.id) + '/*.webm')
                    source = FFmpegPCMAudio(pwd + '/Dependencies/' + 'Elevator_Music.mp3')
                    player = voice.play(source)
                    songlist, title = dccommands.retrievePlaylist(settings.queues[ctx.guild.id][0], (pwd+'/'+str(ctx.guild.id)))
                    voice.stop()
                    settings.queues[ctx.guild.id].pop(0)
                    settings.queues[ctx.guild.id] = songlist+settings.queues[ctx.guild.id]
                    source = FFmpegPCMAudio(pwd+'/'+str(ctx.guild.id)+'/'+settings.queues[ctx.guild.id][0])
                    settings.titles[ctx.guild.id].pop(0)
                else:
                    os.system('rm ' + str(ctx.guild.id) + '/*.mp3')
                    source, title = dccommands.retrieveAudio(settings.queues[ctx.guild.id][0], (pwd+'/'+str(ctx.guild.id)))
                    settings.titles[ctx.guild.id].pop(0)
            player = voice.play(source)
            settings.queues[ctx.guild.id].pop(0)
            settings.timers[ctx.guild.id].start()
            settings.downloading[ctx.guild.id] = False
        else:
            os.system('rm ' + pwd+'/'+str(ctx.guild.id) + '/*.mp3')
            os.system('rm ' + pwd+'/'+str(ctx.guild.id) + '/*.webm')
            print('No queued items')

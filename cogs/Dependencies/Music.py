#cogs.Music runs the Music message commands for Mobot
#This file contains all of the commands associated with the Mobot Music commands
import os
import cogs.Dependencies.dccommands as dccommands
import nextcord
from nextcord import FFmpegPCMAudio
import validators
from validators import ValidationFailure
import os.path
import config
import settings
import random


extensions = config.extension

def checkurl(url_string: str):
    result = validators.url(url_string)

    if isinstance(result, ValidationFailure):
        return False

    return result

#The queue function is what runs the entire music bot.
#This function is used to periodically check if a song is ready to be loaded up into the voice chat for playing
async def queue(ctx, client):

    #First it sets the working directory and checks if the bot is playing a song
    pwd = os.path.dirname(os.path.realpath(__file__))
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
    if (voice.is_playing() or voice.is_paused()):
        pass
    else:

        #It then checks if there is an active queue for an individual server
        if settings.queues[ctx.guild.id]:
            if settings.queues[ctx.guild.id][0].startswith('song'):
                source = FFmpegPCMAudio(pwd+'/'+str(ctx.guild.id)+'/'+settings.queues[ctx.guild.id][0])
            
            #It then sets up everything for the next song to play properly
            #It clears the guild directory and sets downloading to true
            else:
                settings.downloading[ctx.guild.id][0] = True
                os.system('rm ' + str(ctx.guild.id) + '/*.opus')
                os.system('rm ' + str(ctx.guild.id) + '/*.webm')

                #It then checks if shuffle is turned on and grabs the index for the next shuffle
                if settings.downloading[ctx.guild.id][2] and (not settings.indexes[ctx.guild.id]):
                    if len(settings.queues[ctx.guild.id]) > 1:
                        if settings.downloading[ctx.guild.id][1]:
                            index = random.randint(1, (len(settings.queues[ctx.guild.id])-1)) - 1
                        else:
                            index = random.randint(1, len(settings.queues[ctx.guild.id])) - 1
                    else:
                        index = 0
                else:
                    index = 0
                    settings.indexes[ctx.guild.id] = False
                
                #It then checks if the next item is a playlist and retrieves every item in the playlist
                url = settings.queues[ctx.guild.id][index]
                if "playlist" in url and ("youtube" in url or "youtu.be" in url):
                    songlist, title = await dccommands.retrievePlaylist(settings.queues[ctx.guild.id][index], ctx)
                    voice.stop()
                    settings.queues[ctx.guild.id].pop(index)
                    settings.queues[ctx.guild.id] = songlist+settings.queues[ctx.guild.id]
                    settings.titles[ctx.guild.id].pop(index)
                    settings.titles[ctx.guild.id] = title+settings.titles[ctx.guild.id]
                
                #After that it then retrieves the next audio and if it is set to repeating, it places the song back to the end of the queue
                #It then plays the next song and sets downloading to false
                else:
                    if settings.downloading[ctx.guild.id][1]:
                        settings.titles[ctx.guild.id].append(settings.titles[ctx.guild.id][index])
                        settings.queues[ctx.guild.id].append(settings.queues[ctx.guild.id][index])
                    source, title, thumbnail, duration = await dccommands.retrieveAudio(settings.queues[ctx.guild.id][index], (pwd+'/'+str(ctx.guild.id)), ctx, index)
                    textchannel = nextcord.utils.get(settings.channels[ctx.guild.id].guild.channels, id=settings.channels[ctx.guild.id].channel.id)
                    embed = nextcord.Embed(title="Now playing:", description=title)
                    embed.set_footer(text=f"Duration: {duration}")
                    embed.set_thumbnail(url=thumbnail)
                    await textchannel.send(embed=embed)
                    #Reminder, ARRAY POPPING FOR TITLES AND QUEUES IS IN dccommands.py
                    #settings.titles[ctx.guild.id].pop(index)
                    if settings.downloading[ctx.guild.id][3]:
                        #loop = asyncio.get_event_loop()
                        print("normalized")
                        #raw = await loop.run_in_executor(None, AudioSegment.from_file, f"{pwd}/{ctx.guild.id}/song.opus", codec = "opus")
                        #raw = AudioSegment.from_file(f"{pwd}/{ctx.guild.id}/song.opus", codec = "opus")
                        #normalized = effects.normalize(raw, headroom=10)
                        #normalized = await loop.run_in_executor(None, effects.normalize, raw, headroom=10)
                        #os.system('rm ' + str(ctx.guild.id) + '/*.opus')
                        #normalized.export(f"{pwd}/{ctx.guild.id}/song.opus", format="opus")
                        #await loop.run_in_executor(None, normalized.export, f"{pwd}/{ctx.guild.id}/song.opus", format="opus")
                        #source = FFmpegOpusAudio(f"{pwd}/{ctx.guild.id}/song.opus")
                    player = voice.play(source)
                    #settings.queues[ctx.guild.id].pop(index)
            settings.downloading[ctx.guild.id][0] = False
        
        #If there is not an active queue, it cleans up and pauses the timer
        else:
            os.system('rm ' + str(ctx.guild.id) + '/*.opus')
            os.system('rm ' + str(ctx.guild.id) + '/*.webm')
            await settings.timers[ctx.guild.id].pause()
            print('No queued items')

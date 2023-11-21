from credentials import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, DISCORD_TOKEN
from spotify_uri import formatURI, formatOpenURL
import re
import math
import asyncio

import discord
from discord.ext import commands
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix = '&', intents=intents)

import spotipy
from spotipy.oauth2 import SpotifyOAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, scope="user-read-currently-playing user-modify-playback-state", redirect_uri='http://www.google.com/'))


def ms_to_timestamp(ms):
    hrs = 0
    if ms >= 3_600_000:
        hrs = math.floor(ms / 3_600_000)
        ms %= 3_600_000

    min = math.floor(ms / 60_000)
    ms %= 60_000
    sec = math.floor(ms / 1_000)

    if hrs > 0:
        return f'{hrs}:{min:02d}:{sec:02d}'
    else:
        return f'{min}:{sec:02d}'


def get_queue_length():
    count = 0
    while sp.queue()["queue"][count]["uri"] != "spotify:track:198X5Hqdx31ir9V8SJev8k":
        count += 1
        if (count >= 20):
            break
    return count


@client.event
async def on_ready():
    print(f'{client.user.name} is online.')


@client.event
async def on_message(message):
    await client.process_commands(message)


@client.command(aliases=['np'])
async def nowplaying(ctx):
    if (sp.current_user_playing_track()["item"]["uri"] == "spotify:track:198X5Hqdx31ir9V8SJev8k" and not sp.currently_playing()["is_playing"]):
        await ctx.send('❌ **Nothing playing**')
    else:
        embed = discord.Embed(title = "Now Playing", color = discord.Color.from_rgb(0, 86, 191))
        current = sp.current_user_playing_track()["item"]
        overflow_length = 65 - len(current["name"])
        artists = ", ".join([artist["name"] for artist in current["artists"]])
        now_playing = f'**[{current["name"]} - {artists[:overflow_length] + (artists[overflow_length:] and "...")}]({formatOpenURL(current["uri"])})**'

        progress = math.floor(sp.current_user_playing_track()["progress_ms"] / current["duration_ms"] * 30 - 1)
        progress_bar = f'{"▬" * progress}🔘{"▬" * (29 - progress)}'
        timestamp_progress = f'{ms_to_timestamp(sp.current_user_playing_track()["progress_ms"])} / {ms_to_timestamp(current["duration_ms"])}'

        embed.add_field(name="", value=now_playing, inline=False)
        embed.add_field(name = "", value = f'`{progress_bar}`\n\n`{timestamp_progress}`', inline=False)
        embed.set_thumbnail(url=current["album"]["images"][0]["url"])
        await ctx.send(embed=embed)


@client.command()
async def pause(ctx):
    sp.pause_playback()
    await ctx.send('**Paused** ⏸')


@client.command()
async def resume(ctx):
    sp.start_playback()
    await ctx.send('⏯ **Resuming** 👍')


@client.command(aliases=['p'])
async def play(ctx, *, query):
    uri = ""
    query_type = ""
    try:
        uri = formatURI(query)
        query_type = uri.split(':')[1]
    except:
        try:
            uri = sp.search(query)["tracks"]["items"][0]["uri"]
            query_type = uri.split(':')[1]
        except:
            await ctx.send(f'❌ **Cannot play** `{query}`')

    if uri != "":
        if query_type == "track":
            sp.add_to_queue(uri)
            track = sp.track(uri)
            current = sp.currently_playing()

            if current["item"]["uri"] == "spotify:track:198X5Hqdx31ir9V8SJev8k":
                await ctx.send(f'**Playing** 🎶 {track["name"]} - Now!')
                sp.next_track()
            else:
                embed = discord.Embed(title = "Added to queue", color = discord.Color.from_rgb(30, 31, 34))
                embed.add_field(name = "", value = f'**[{", ".join([artist["name"] for artist in track["artists"]])} - {track["name"]}]({formatOpenURL(uri)})**', inline=False)
                embed.add_field(name = "Artist", value = track["artists"][0]["name"], inline=True)
                embed.add_field(name = "Song Duration", value = ms_to_timestamp(track["duration_ms"]), inline=True)

                if current["context"]["external_urls"]["spotify"] == "https://open.spotify.com/playlist/4JqQJIevpZoz10eRFTM7pR" and get_queue_length() < 20:
                    remaining_time = current["item"]["duration_ms"] - current["progress_ms"]
                    for i in range(get_queue_length() - 1):
                        remaining_time += sp.queue()["queue"][i]["duration_ms"]
                    embed.add_field(name = "Estimated time until playing", value = ms_to_timestamp(remaining_time), inline=True)
                    embed.add_field(name = "Position in queue", value = f'{get_queue_length()}', inline=False)
                    
                embed.set_thumbnail(url=track["album"]["images"][0]["url"])
                await ctx.send(embed=embed)

        elif query_type == "playlist" or query_type == "album":
            if query_type == "playlist":
                song_list = sp.playlist(uri)

            elif query_type == "album":
                song_list = sp.album(uri)
                
            embed = discord.Embed(title = "Playlist added to queue", color = discord.Color.from_rgb(30, 31, 34))
            embed.add_field(name="", value=f'**[{song_list["name"]}]({formatOpenURL(uri)})**', inline=False)
            current = sp.currently_playing()
            if current["context"]["external_urls"]["spotify"] == "https://open.spotify.com/playlist/4JqQJIevpZoz10eRFTM7pR" and get_queue_length() < 20:
                if current["item"]["uri"] == "spotify:track:198X5Hqdx31ir9V8SJev8k":
                    embed.add_field(name = "Estimated time until playing", value = "Now", inline=False)
                    embed.add_field(name = "Position in queue", value = "Now", inline=True)
                    sp.next_track()
                else:
                    remaining_time = current["item"]["duration_ms"] - current["progress_ms"]
                    for i in range(get_queue_length() - 1):
                        remaining_time += sp.queue()["queue"][i]["duration_ms"]
                    embed.add_field(name = "Estimated time until playing", value = ms_to_timestamp(remaining_time), inline=False)
                    embed.add_field(name = "Position in queue", value = f'{get_queue_length()}', inline=True)
            
            if query_type == "playlist":
                for song in song_list["tracks"]["items"]:
                    sp.add_to_queue(song["track"]["uri"])
            elif query_type == "album":
                for song in song_list["tracks"]["items"]:
                    sp.add_to_queue(song["uri"])
            embed.add_field(name = "Enqueued", value = f'`{song_list["tracks"]["total"]}` songs', inline=True)
            embed.set_thumbnail(url=song_list["images"][0]["url"])
            await ctx.send(embed=embed)


@client.command()
async def search(ctx, *, query):
    user = ctx.message.author
    embed = discord.Embed(color = discord.Color.from_rgb(30, 31, 34))
    embed.set_author(name=user.name, icon_url=user.avatar)

    search_results = []
    for count, song in enumerate(sp.search(query)["tracks"]["items"]):
        artists = ", ".join([artist["name"] for artist in song["artists"]])
        overflow_length = 55 - len(song["name"])
        search_results.append(f'`{count + 1}.` [{song["name"]} - {artists[:overflow_length] + (artists[overflow_length:] and "...")}]({formatOpenURL(song["uri"])}) | `{ms_to_timestamp(song["duration_ms"])}`\n\n')

    for i in range(10):
        embed.add_field(name="", value=search_results[i], inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="Type a number to make a choice. Type `cancel` to exit", value="", inline=False)
    search_box = await ctx.send(embed=embed)

    def check(author):
        def inner_check(message):
            if isinstance(message, int):
                return message.author == author and int(message.content) >= 1 and int(message.content) <= 10
            else:
                return message.author == author and message.content == "cancel"
        return inner_check
    try:
        msg = await client.wait_for("message", timeout=30.0, check=check)
    except asyncio.TimeoutError:
        return
    else:
        await search_box.delete()
        if msg.content == "cancel":
            await ctx.send('✅')
        elif int(msg.content) < 1 or int(msg.content) > 10:
            await ctx.send('❌ **Timeout!**')
        else:
            song_choice = sp.search(query)["tracks"]["items"][int(msg.content)-1]["uri"]
            await ctx.invoke(client.get_command('play'), query=song_choice)


@client.command()
async def skip(ctx):
    sp.next_track()
    await ctx.send('⏩ ***Skipped*** 👍')


@client.command()
async def previous(ctx):
    sp.previous_track()
    await ctx.send('⏪ ***Skipped back*** 👍')


@client.command()
async def seek(ctx, seek):
    if (re.match(r"\d:\d{2}", seek)):
        seek_ms = (int(seek.split(":")[0]) * 60000) + (int(seek.split(":")[1]) * 1000)
        if (seek_ms < sp.currently_playing()["item"]["duration_ms"]):
            sp.seek_track(seek_ms)
            await ctx.send(f'🎵 **Set position to** `{seek}` ⏩')
        else:
            await ctx.send('Invalid timestamp (timestamp longer than song).')
    else:
        await ctx.send('Invalid timestamp (try &seek X:XX).')


@client.command(aliases=['q'])
async def queue(ctx):
    embed = discord.Embed(title = "Queue", color = discord.Color.from_rgb(75, 51, 30))
    current = sp.current_user_playing_track()["item"]

    if (current["uri"] == "spotify:track:198X5Hqdx31ir9V8SJev8k" and not sp.currently_playing()["is_playing"]):
        now_playing = "Nothing, let's get this party started! 🎉"
    else:
        overflow_length = 60 - len(current["name"])
        artists = ", ".join([artist["name"] for artist in current["artists"]])
        now_playing = f'[{current["name"]} - {artists[:overflow_length] + (artists[overflow_length:] and "...")}]({formatOpenURL(current["uri"])}) | `{ms_to_timestamp(current["duration_ms"])}`'

        up_next = []
        for count, song in enumerate(sp.queue()["queue"]):
            if song["uri"] == "spotify:track:198X5Hqdx31ir9V8SJev8k":
                count -= 1
                break
            artists = ", ".join([artist["name"] for artist in song["artists"]])
            overflow_length = 55 - len(song["name"])
            up_next.append(f'`{count + 1}.` [{song["name"]} - {artists[:overflow_length] + (artists[overflow_length:] and "...")}]({formatOpenURL(song["uri"])}) | `{ms_to_timestamp(song["duration_ms"])}`\n\n')
            if count > 8:
                break

    embed.add_field(name="__Now Playing:__", value=now_playing, inline=False)
    if sp.queue()["queue"][0]["uri"] != "spotify:track:198X5Hqdx31ir9V8SJev8k":
        embed.add_field(name="__Up Next:__", value="", inline=False)
        for i in range(count+1):
            embed.add_field(name="", value=up_next[i], inline=False)

    await ctx.send(embed=embed)


client.run(DISCORD_TOKEN)

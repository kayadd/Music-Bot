# remove the file from the directory.
# noinspection PyUnresolvedReferences
import os

# Import Discord and all its extensions.
if True:
    import discord
    from discord.ext import commands

# Imports the library for downloading the meta-data and the file.
from yDown import *

# Imports the library for getting the lyrics.
from genius_lyrics import *

# Gives the bot all permissions to read, write and speak.
intents = discord.Intents().all()

# Sets the prefix to "§" and sets all permissions.
bot = commands.Bot(command_prefix='§', intents=intents)

# Initiates all global variables.
if True:
    listAuthor = 0
    queue = []
    Playing = False
    paused = False
    looped = False
    current = [0, 0]
    ListQueue = []
    EntryQueue = []


@bot.event
async def on_ready():
    # Declares all variables as global.
    global queue
    global Playing
    global current
    global EntryQueue

    # Ensures, that no mp3-file will be causing any conflict.
    await purgeData()

    print("Data purged")

    await bot.get_channel(1090764939226009630).send("Der Bot ist ready.")

    # checks every second, if the bot is still playing and if the queue is not empty.
    while True:
        print(EntryQueue)
        try:
            # Gets the channel, in which the bot is playing and all its members. If it is not all
            Members = bot.voice_clients[0].channel.members

            # Filter if it's a bot or a user.
            for i in range(len(Members)):
                Members[i] = Members[i].bot

            # Disconnect, if all members have left.
            if Members.count(False) == 0:
                await bot.voice_clients[0].disconnect(force=True)
                Playing = False
        except IndexError:
            pass

        # Displaying the current status of all relevant global variables
        # print(f"Playing: {Playing} \nQueue: {queue} \nCurrent: {current}")

        if (current != [0, 0] or queue) and not Playing:
            # If loop is not active.
            if not looped and queue:
                # Sends a message to the channel to call the bot to play the next song in the queue.
                await bot.get_channel(1090764939226009630).send("§p!lay " + str(queue[0]))
                # Deletes the current song in the queue.
                del queue[0]
                del EntryQueue[0]

            # If loop is activated.
            elif looped:
                await bot.get_channel(1090764939226009630).send("§p!lay " + str(current))
            elif not queue:
                pass
        # Waits a second in the loop.
        await asyncio.sleep(1)


@bot.event
async def on_message(message):
    await asyncio.sleep(0.5)
    """Handles all message-events."""
    # Declares all variables as global.
    global listAuthor
    global looped
    global ListQueue

    # Makes the message also available for comments.
    await bot.process_commands(message)

    # Play songs in queue.
    if "§p!lay" in message.content:
        # Deletes the message, that it send to play the next song.
        await message.delete()
        # Plays the requested song in the queue.
        await p(message, message.content.replace("!", ""))

    # Gets links from playlist.
    if "§list" in message.content:
        # gets the id from the user, who sent the message containing the playlist.
        try:
            listAuthor = message.author.voice.channel.id

            # Sends info about the playlist being downloaded and played.
            await bot.get_channel(1090764939226009630).send("Die Lieder werden der Queue hinzugefügt. "
                                                            "Bitte warte mit neuen Songs, bis der Vorgang"
                                                            " abgeschlossen ist.")

            # Gets the links of the videos contained in the playlist.
            ListQueue = await getPlaylistLinks(message.content.replace("§list", ""))

            await bot.change_presence(activity=discord.Game(name="Lädt die Liste in die Queue..."))

            # Calls the bot to download that song.
            await bot.get_channel(1090764939226009630).send("§ListAdd " + str((ListQueue[0].split("&list="))[0]))

        except AttributeError:
            await bot.get_channel(1090764939226009630).send("Du musst mit einem Kanal verbunden sein.")

    # Adds the song from a list to the queue.
    if "§ListAdd" in message.content:
        try:
            # Gets the remaining links and deletes the message.
            link = (message.content.replace("§ListAdd ", ""))
            await message.delete()
            # Gets the necessary meta-data.
            nlink = await getLink(link)
            # Gets the file and passes on the file name.
            src = await DownloadFile(nlink[0])

            # Appends the song to the queue.
            queue.append([src, nlink[1]])

            # Appends the info to the Song-queue
            EntryQueue.append(nlink[1][-1])

            await bot.get_channel(1090764939226009630).send(f">>> {nlink[1][-1]} ist zur Queue hinzugefügt worden.")

            del ListQueue[0]

            await bot.get_channel(1090764939226009630).send("§ListAdd " + (ListQueue[0].split("&list="))[0])

        # If every song is in queue, declare it and end recursion.
        except IndexError:
            await bot.change_presence(activity=discord.Game(name=""))
            print(ListQueue)
            if not ListQueue:
                await bot.get_channel(1090764939226009630).send("Die Queue wurde aktualisiert. "
                                                                "Du kannst jetzt wieder etwas hinzufügen.")

            else:
                await bot.get_channel(1090764939226009630).send("Beim Herunterladen ist ein Fehler aufgetreten.")

    # Puts the bot in a loop.
    if "§loop" in message.content:
        # Check if the bot is playing.
        if Playing:
            # Sets the state to the opposite and declares it.
            if not looped:
                looped = True
                await bot.get_channel(1090764939226009630).send("Der Loop ist aktiviert.")
            else:
                looped = False
                await bot.get_channel(1090764939226009630).send("Der Loop ist nicht mehr aktiviert")
        else:
            await bot.get_channel(1090764939226009630).send("Der Bot muss einen Song spielen um"
                                                            " ihn in einen Loop zu packen.")


@bot.command()
async def p(ctx, *args):
    """Plays a given song, either by file-name or link."""
    # Declares the variables as global variables.
    global queue
    global Playing
    global listAuthor
    global current
    global EntryQueue

    # Concatenates the arguments to a single string.
    arguments = " ".join(args).replace("&list=", "")

    # Saves the entry
    if "[" not in arguments:
        EntryQueue.append(arguments)

    # Gets the channel, from the author of the message, in which it should join.
    try:
        vc = bot.get_channel(ctx.author.voice.channel.id)
    except AttributeError:
        # If the bot is sending itself a message, he connects to the channel the user is in, who called the bot.
        if bot.get_user(816723854319288361) == ctx.author:
            vc = bot.get_channel(listAuthor)
            listAuthor = 0
        # Sends a message if it is the user, that called the bot, who is not in a channel.
        else:
            vc = None
            await bot.get_channel(1090764939226009630).send("Du musst mit einem Kanal verbunden sein.")

    # If the user is connected to a channel.
    if vc is not None:
        await bot.change_presence(activity=discord.Game(name="Suche den Song..."))

        # If the song is not a mp3-file and already downloaded.
        if "[" not in arguments and "]" not in arguments:
            # Catches a connection error and prints a corresponding message
            try:
                # Gets the meta-data
                link = await getLink(arguments)
                # Gets the file and passes on the file name.
                src = await DownloadFile(link[0])
            except IndexError:
                await bot.get_channel(1090764939226009630).send("Es ist ein Fehler mit der Verbindung aufgetreten. "
                                                                "Bitte versuche es erneut.")
                link = 0
                src = 0

        else:
            # Extracts the file name from the message.
            src = eval((arguments.split(",")[0].replace("[", "")).replace("§play ", ""))
            print(src)
            # Extracts the meta-data from the message
            link = [0, eval(arguments[len(src) + 10:len(arguments) - 1])]

        # Connects the bot to the corresponding channel, if necessary.
        if ctx.guild.voice_client is None and link != 0:
            c = await vc.connect()
        elif link != 0:
            c = ctx.guild.voice_client
        else:
            c = 0

        # Checks if the bot is already playing a song.
        if Playing and link != 0:

            # If the bot is already playing a song, append it to the queue and confirm it in a channel.
            queue.append([src, link[1]])
            await bot.change_presence(activity=discord.Game(name=""))

            await bot.get_channel(1090764939226009630).send(f">>> {link[1][-1]} ist zur Queue hinzugefügt worden.")
        elif link != 0:
            await bot.change_presence(activity=discord.Game(name=""))
            ch = bot.get_channel(1090764939226009630)

            # Plays the file from ffmpeg.
            c.play(discord.FFmpegPCMAudio(src, executable="ffmpeg.exe"))

            # Changing the status of the bot.
            Playing = True
            current = [src, link[1]]

            current[1][-4] = await getFileDuration(src)
            link[1][-4] = current[1][-4]

            # Formats the meta-data and sends them, if the player is not looped.
            if "vor " not in link[1][-3]:
                link[1][-3] = "vor " + link[1][-3]
            if not looped:
                await ch.send(f">>> **Spielt jetzt**: {link[1][-1]} "
                              f"\n**von** {link[1][-2]} "
                              f"**vor** {link[1][-3][3:len(link[1][-3])]} "
                              f"\n**Dauer**: {link[1][-4]} "
                              f"\n**Views**: {link[1][-5]}")

            # Calculates the time, that it has to wait before it can change its status to not playing.
            duration = link[1][-4].replace("Minuten,", "*60 +").replace("Minute,", "*60 +")
            duration = duration.replace("Sekunden", "").replace("Sekunde", "")

            duration = eval(duration)

            # Freezes this particular thread of the bot for time seconds.
            await asyncio.sleep(duration)

            # If a song was skipped, the thread is still active and waiting, because the skip-command
            # does not terminate the thread play but only the ffmpeg-thread. With comparing the current song to the
            # title, if the audio is still being played, change the status to not playing. If the audio is a relict
            # from a skipped title, don't change anything.
            if current[1][-1] == link[1][-1]:
                Playing = False

            # If the song is not in a loop delete the mp3-file.
            if not looped:
                # Try to remove the file, if it is not being accessed by another process
                try:
                    os.remove(src)
                except WindowsError:
                    pass


@bot.command()
async def play(ctx, *args):
    await p(ctx, *args)


@bot.command()
async def skip(ctx):
    """Skip the current song and terminate the thread of ffmpeg"""
    global Playing
    global looped

    # If the bot is playing music, terminate the ffmpeg-thread and set mode to not playing.
    if Playing:
        ctx.guild.voice_client.stop()

        await ctx.send(f"{current[1][-1]} von {current[1][-2]} wurde übersprungen.")
        if looped:
            looped = False

        Playing = False

    # If the bot is not playing music, send a message to the corresponding channel.
    else:
        await ctx.send("Es muss erst etwas gespielt werden um etwas zu überspringen. ")


@bot.command()
async def pause(ctx):
    """Pauses the song."""
    global paused

    # If the bot is playing and not paused, pause the bot, set paused to True and send a message.
    if Playing and not paused:
        ctx.guild.voice_client.pause()
        paused = True
        await ctx.send("Der Musikbot wurde erfolgreich pausiert.")

        await bot.change_presence(activity=discord.Game(name="Pausiert"))

    # If the bot is paused, send a message, that it's paused.
    elif paused:
        await ctx.send("Es wurde bereits pausiert.")


@bot.command()
async def resume(ctx):
    """Resume the song."""
    global paused

    # If the bot is playing and paused, resume the bot, set paused to False and send a message.
    if Playing and paused:
        ctx.guild.voice_client.resume()
        paused = False
        await ctx.send("Der Musikbot wurde erfolgreich entpausiert.")

        await bot.change_presence(activity=discord.Game(name=""))
    # If the bot is not paused, send a message, that it's paused.
    elif not paused:
        await ctx.send("Der Musikbot ist nicht pausiert.")


@bot.command()
async def Lyrics(ctx, *args):
    """Gets the lyrics of a requested song."""

    await bot.change_presence(activity=discord.Game(name="Suche die Lyrics..."))
    # Gets the argument and adds them
    req = " ".join(args)

    temp = req

    # Checks, if the current song is requested or another song is requested
    if ".playing" in req:
        req = EntryQueue[0]

    # Gets the lyrics from genius.

    txt = await getLyrics(req)

    # If the Song is currently playing a song and current is requested, print current lyrics, if not playing
    # but current lyrics are requested, send error message. If the current song is not requested, print lyrics
    if (Playing and ".playing" in temp) or ".playing" not in temp:
        for i in range(len(txt)):
            # Send the lyrics to channel.
            await ctx.send(txt[i])
            await asyncio.sleep(0.5)
    elif not Playing and ".playing" in temp:
        await ctx.send("Es wird gerade kein Song abgespielt.")

    await bot.change_presence(activity=discord.Game(name=""))


@bot.command()
async def qinfo(ctx):
    """Prints all songs, that are in the queue."""
    global queue

    # Checks if the queue is empty
    try:
        if queue:
            # Announce, that it's going to iterate through the queue.
            await ctx.send("In der Queue sind in dieser Reihenfolge diese Songs:")
            await asyncio.sleep(0.5)

            # Iterate through every queue-entry and print the title.
            for i in range(len(queue)):
                await ctx.send(queue[i][1][-1] + " von " + queue[i][1][-2])
                await asyncio.sleep(0.5)
        else:
            await ctx.send("Die Queue ist leer.")
    except IndexError:
        await ctx.send("Es ist ein Fehler aufgetreten. Bitte gib die Queue wieder neu ein.")


@bot.command()
async def qclear(ctx):
    """Clears the song-queue."""
    global queue

    # Announce to clear the queue.
    await ctx.send("Cleare die Queue...")

    # Iterate through all queued songs and delete the file and the queue-entry.
    for i in range(len(queue)):
        # Gets the filename of the next song in the queue.
        filename = queue[0][0]

        # Removes the file from the directory.
        os.remove(filename)

        # Deletes the next entry.
        del queue[0]

    # Announce it's finished.
    await ctx.send("Die Queue ist wieder leer.")


@bot.command()
async def qdelete(ctx, *args):
    """Deletes specific parts of the queue."""
    global queue

    try:
        # Transforms all forms of input into one.

        delIndex = []
        arguments = " ".join(args)

        if "-" in arguments:
            arguments = arguments.split("-")

            for i in range(int(arguments[1]) - int(arguments[0])):
                delIndex.append(eval(f"{arguments[0]} -1 + {i}"))

            delIndex.append(eval(f"{delIndex[-1]}+1"))

        elif "," in arguments:
            arguments = arguments.split(",")

            for i in range(len(arguments)):
                delIndex.append(int(arguments[i])-1)

        else:
            delIndex = [int(arguments)-1]

        tempSong = []
        tempEntry = []

        # Gets all songs, that should be deleted.
        for i in range(len(delIndex)):
            # Adds the song-information.
            tempSong.append(queue[delIndex[i]])
            # Adds the entry-information.
            tempEntry.append(EntryQueue[delIndex[i]+1])

        # Removes them all per Values.
        for i in range(len(tempSong)):
            EntryQueue.remove(tempEntry[i])
            queue.remove(tempSong[i])

            await ctx.send(f"{tempSong[i][1][-1]} von {tempSong[i][1][-2]} wurde aus der Queue entfernt.")
            os.remove(tempSong[i][0])

    except ValueError:
        await ctx.send("Das angegebene Argument ist keine Zahl.")

    except IndexError:
        await ctx.send("So weit reicht die Liste nicht.")


@bot.command()
async def info(ctx):
    """Prints the meta-data of the song, that is currently playing."""
    global current
    global looped

    if looped:
        strLoop = "I"
    else:
        strLoop = "Nicht i"

    # If the bot is playing and current is not empty, send the meta-data in the corresponding channel.
    if Playing and current != [0, 0]:
        await ctx.send(f">>> **Spielt gerade**: {current[1][-1]} "
                       f"\n**von** {current[1][-2]} "
                       f"**vor** {current[1][-3][3:len(current[1][-3])]} "
                       f"\n**Dauer**: {current[1][-4]} "
                       f"\n**Views**: {current[1][-5]}"
                       f"\n**Loop**: {strLoop}m Loop")

    # If the bot is currently not playing anything, send an informing message in the corresponding channel.
    else:
        await ctx.send("Es wird gerade nichts abgespielt.")


@bot.command()
async def commands(ctx):
    """Prints a list of all commands, which are highlighted in the message, to the corresponding discord-channel."""

    # Sends a message with all usable commands to the corresponding channel.
    await ctx.send("Jeder Befehl muss nach einem Prefix folgen: §**{Befehl}** \n"
                   "Spiele einen Song ab: **p {Songtitel oder Youtubelink}** oder "
                   "**play {Songtitel oder Youtubelink}** \n"
                   "Bitte nicht ungeduldig sein. Der Bot braucht beim ersten Starten und in den Channel "
                   "kommen etwas länger. Bitte wartet mit neuen Anfragen bis der Bot im "
                   "Channel ist und Musik spielt.\n"
                   "Dies funktionert auch um Songs in die Queue zu packen. Warte aber bitte die Benachrichtigung"
                   "ab, bevor du mehrere Sachen hintereinander hinzufügst, da der Bot auf keinem leistungsstarkem "
                   "Server mit Nasa-Internet sitzt. Dies kann bei einer Liste auch etwas länger dauern.\n"
                   "Spiele eine Youtube-Playlist:**list {Ein Video in der Playlist}**\n"
                   "Überspringe das Lied, welches gerade abgespielt wird: **skip**\n"
                   "Ein Skip eines Songs im Loop beendet den Loop. \n"
                   "Löscht jedes Lied an der angegebenen Stelle in der Queue: **qdelete {Stelle 1, Stelle 2, ... , "
                   "Stelle 9}** \n"
                   "Löscht jedes Lied zwischen den angegebenen Stellen, inklusive der Grenzen "
                   "in der Queue: **qdelete {Untere Grenze-Obere Grenze}** \n"
                   "Löscht alle Lieder in der Queue: **qclear**\n"
                   "Packt den aktuellen Song in einen Loop oder beendet den Loop: **loop** \n"
                   "Pausiere: **pause**\n"
                   "Entpausiere: **resume**\n"
                   "Gibt den Titel, Dauer, Views, Interpret, Uploaddatum und Loopstatus aus: **info** \n"
                   "Gebe die Lyrics eines Liedes aus: **Lyrics {Songtitel, Interpret}**\n"
                   "Gibt die Lyrics des aktuellen Liedes aus: **Lyrics .playing** \n"
                   "Dabei ist der Interpret optional; es können also Interpret und das Komma weggelassen werden.\n"
                   "Gibt die Titel und die Interpreten der Songs aus, die noch in der Queue sind: **qinfo** \n")
    await ctx.send("Zusatzinformationen: \n"
                   ">>> Der Bot wurde unter Nutzung der Module mutagen, selenium, yt-dlp, asyncio, discord, genius "
                   "und OS in 5 Tagen in Python erstellt und lädt alle Songs oder Videos automatisch herunter und"
                   " speichert sie zwischen. Das gesamte Projekt umfasst 855 Zeilen und 6 Dateien. ")

# Runs bot with token.
bot.run("")

# Import time to wait for the connection to build
import asyncio

# Imports the youtube-download-library
import yt_dlp

# Gets the mp3-duration
from mutagen.mp3 import MP3

# Import Selenium and all its extensions to webscrape
if True:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    import selenium.common

# Import to download the file from the webscraped selenium-link
# Imports to rename the file
import os


async def getLink(Input: str):
    """Returns the link itself or the first link of a youtube-search-query with the search words"""

    # Formats the string into a youtube-search-query
    Temp = Input

    Input = "https://www.youtube.com/results?search_query=" + Input.replace(" ", "+")

    # Initializes the selenium-webdriver
    driver = webdriver.Chrome()

    # downloads the css, html -page
    driver.get(Input)

    # Finds the meta-data of the video
    await asyncio.sleep(1)

    try:
        # Checks for delay in loading and for shorts
        title = driver.find_elements(By.ID, "video-title")

        i = 0
        while title[i].get_attribute("aria-label") is None:
            i += 1

        title = title[i]

    except selenium.common.NoSuchElementException:
        await asyncio.sleep(1)

        # Checks for delay in loading and for shorts
        title = driver.find_elements(By.ID, "video-title")

        i = 0
        while title[i].get_attribute("aria-label") is None:
            i += 1

        title = title[i]

    except IndexError:
        await asyncio.sleep(3)

        # Checks for delay in loading and for shorts
        title = driver.find_elements(By.ID, "video-title")

        i = 0
        while title[i].get_attribute("aria-label") is None:
            i += 1

        title = title[i]

    meta = (title.get_attribute("aria-label"))
    # Formats the meta-data of the first youtube-video

    print(meta)
    if True:
        meta = meta.split(" ")
        # formats the views
        fMeta = [f"{meta[-2]} {meta[-1]}"]

        # formats the watch-time
        watch_time = ""
        i = 0
        try:
            while meta[i] != "vor":
                i += 1

            while 3+i <= len(meta)-3:
                watch_time += meta[3+i]+" "
                i += 1
            fMeta.append(watch_time[0: len(watch_time)-1])
        except IndexError:
            i = 0
            t = ["Minuten,", "Minute,", "Sekunden", "Sekunde"]
            while meta[-(2+i)] in t or meta[-(3+i)] in t:
                watch_time = meta[-(3+i)] + " " + watch_time
                i += 1
            fMeta.append(watch_time[0: len(watch_time)-1])

        # formats time of upload
        upload_time = ""
        i0 = 0
        try:
            while meta[-(1+i0)] != "vor":
                i0 += 1
            for i1 in range(3):
                upload_time += meta[-(1+i0)+i1] + " "
            i1 = 1
        except IndexError:
            i0 = i
            upload_time = "Uploadzeit ist nicht angegeben"
            i1 = 2
        fMeta.append(upload_time)

        # formats the uploader-name
        uploader_name = ""
        while meta[-(i0+i1+1)] != "von":
            uploader_name = meta[-(i0+i1+1)] + " " + uploader_name
            i1 += 1
        fMeta.append(uploader_name[0:len(uploader_name)-1])

        # formats the youtube-title
        fMeta.append(" ".join(meta[0:-(i0+i1+1)]))

        if "www.youtube.com" in Input[45:len(Input)]:
            try:
                driver.get(Temp)
                await asyncio.sleep(2)
                meta = (driver.find_element(By.CLASS_NAME, "style-scope ytd-watch-metadata")).text.split("\n")
                # Formats the title.
                fMeta[-1] = meta[0]

                # Formats the artist
                fMeta[-2] = meta[1]

                tdata = meta[6].split("vor")

                #  Formats the views
                fMeta[-5] = tdata[0]

                # Formats the upload-time
                fMeta[-3] = "vor " + tdata[1]

            except IndexError:
                pass
            return [Input[45:len(Input)], fMeta]

        # filters by all links and returns the first link, that has a "watch"; a video-id, in url
        links = driver.find_elements(By.XPATH, "//a[@href]")

        # Returns the first watchable youtube-link
        for elements in links:
            if "watch" in elements.get_attribute("href"):
                return [elements.get_attribute("href"), fMeta]


async def DownloadFile(Input: str):
    """Downloads the file of a given youtube-link yt-dlp """
    ODir = os.listdir()

    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([Input])

    # returns the file-name of the new file
    NewDir = os.listdir()

    for i in range(len(NewDir)):
        if NewDir[i] not in ODir:
            # Find positions of brackets

            F = NewDir[i].find("[")
            L = NewDir[i].find("]")

            NewName = NewDir[i].replace(NewDir[i][F:L+1], "")
            NewName = NewName.replace(",", " &")

            os.rename(NewDir[i], NewName)
            return NewName


async def purgeData():
    """Removes all unnecessary files from the directory"""
    # Loads all files from this directory
    OldDir = os.listdir()
    # Sets all file-names, that are essential when starting the bot
    St = ["chromedriver.exe", "Discord-Bot.py", "ffmpeg.exe", "LICENSE.chromedriver", "yDown.py", "__pycache__",
          "genius_lyrics.py"]

    # Filters all non-essential files and removes them
    for i in range(len(OldDir)):
        if OldDir[i] not in St:
            os.remove(OldDir[i])


async def getPlaylistLinks(link: str):
    """Gets all links from a youtube-playlist"""
    playList = []
    # Opens the website of the playlist
    driver = webdriver.Chrome()
    driver.get(link)

    # Waits for the page to load
    await asyncio.sleep(1)

    # Find all elements, that are in the playlist
    title = driver.find_elements(By.ID, "wc-endpoint")

    # get all
    for elements in title:
        playList.append(elements.get_attribute("href"))

    # Returns all links of the playlist
    return playList


async def getFileDuration(mFile):
    """Calculates the number of seconds of a file-length in Minutes, Seconds and returns a string"""
    audio = MP3(mFile)
    a = (int(audio.info.length) + 1)

    minutes = int(a / 60)

    seconds = a - 60 * minutes

    if minutes == 1:
        mdDuration = f"{minutes} Minute,"
    else:
        mdDuration = f"{minutes} Minuten,"
    if seconds == 1:
        mdDuration += f" {seconds} Sekunde"
    else:
        mdDuration += f" {seconds} Sekunden"

    return mdDuration

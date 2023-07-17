import lyricsgenius
import requests.exceptions


async def getLyrics(content):
    # Formats the input
    if "," in content:
        content = content.split(",")
    else:
        content = [content, ""]

    # Initiates the Genius-Library
    genius = lyricsgenius.Genius("")
    try:
        song = genius.search_song(title=content[0], artist=content[1])
    except requests.exceptions.Timeout:
        return ["Die Verbindung wurde von Genius geschlossen."]
    try:
        # Gets the song-attributes
        text = song.lyrics
        title = song.title
        artist = song.artist

    except AttributeError:
        return ["Der Song konnte nicht gefunden werden. Bitte gib für eine genauere Suche den Titel manuell ein."]

    # Removes all webscraped errors and the first line

    text = text.split("\n")

    for i in range(len(text)):
        if "[" in text[i]:
            while text[i][0] != "[":
                text[i] = text[i][1:len(text[i])]

    # Removes the contributions in the last line
    text[-1] = (text[-1].replace("KEmbed", "")).replace("Embed", "")

    Er = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]

    while text[-1][-1] in Er:
        text[-1] = text[-1][0:-2]

    text.insert(0, f"{title} von {artist}: \n")

    bits = []
    cText = ""
    for i in range(len(text)):
        if len(cText) + 2 + len(text[i]) <= 2000:
            cText += "\n" + text[i]
        else:
            bits.append(cText)
            cText = text[i]

    if cText != "":
        bits.append(cText)

    return bits

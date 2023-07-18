import os
# The database is:
# User-Stats/ Song-Stats : name, link, count


async def addSong(name: str, link: str, user_id: str, artist: str):
    """Adds the song to the database."""
    user_file = ".//Stats//User-Stats//"+user_id+".txt"

    # Writes to user file.

    path = os.listdir(".//Stats//User-Stats")

    # Creates the file, if not existing.
    if user_id+".txt" not in path:
        wFile = open(user_file, "w")
        wFile.close()

    # Read the file.
    wFile = open(user_file, "r")
    text = wFile.readlines()
    wFile.close()

    changed = False

    for count in range(len(text)):
        text[count] = text[count].replace("\n", "")
        if link in text[count]:
            changed = True
            temp = int(text[count].split(",")[2])+1
            text[count] = f"{name},{link},{temp},{artist}"

    if not changed:
        text.append(f"{name},{link},1,{artist}")

    # Write in that file.
    wFile = open(user_file, "w")

    wFile.write("\n".join(text))
    wFile.close()

    # Read the songs file.
    wFile = open(".//Stats//Songs.txt", "r")
    text = wFile.readlines()

    wFile.close()

    changed = False

    for count in range(len(text)):
        text[count] = text[count].replace("\n", "")
        if link in text[count]:
            changed = True
            temp = int(text[count].split(",")[2]) + 1
            text[count] = f"{name},{link},{temp},{artist}"

    if not changed:
        text.append(f"{name},{link},1,{artist}")

    # Write in that file.
    wFile = open(".//Stats//Songs.txt", "w")

    wFile.write("\n".join(text))
    wFile.close()


async def displayData(user_id: str, name):
    """Returns the all-time list of played songs."""
    if user_id != "0":
        file = ".//Stats//User-Stats//" + user_id + ".txt"
    else:
        file = ".//Stats//Songs.txt"
        name = "Everyone"

    try:
        tfile = open(file, "r")

    except FileNotFoundError:
        return ["Der User hat bisher keinen Song abgespielt."]

    data = tfile.readlines()

    Sorted = []
    GElem = 0

    Sorted = []
    GElem = "a,a,0"

    for i0 in range(len(data)):
        for i1 in range(len(data)):
            if int(data[i0].split(",")[2]) >= int(GElem.split(",")[2]):
                if GElem not in Sorted:
                    print(GElem)
                    GElem = data[i0]

        Sorted.append(GElem)
        GElem = "a,a,0"

    Sorted = data

    if len(data) > 20:
        length = 20
    else:
        length = len(data)

    text = [f"{name} - All time stats:"]

    for i in range(length):
        Sorted[i] = Sorted[i].replace("\n", "")
        song = Sorted[i].split(",")
        text.append(f"{i + 1}: {song[1]} vom {song[3]}- Gespielt: {song[2]}")

    # Reused from genius_lyrics
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

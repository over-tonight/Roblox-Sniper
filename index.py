import requests
import discord
from discord.ext import commands
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="/",intents=discord.Intents.all())


TOKEN = '' # Put your discord bot token here.


# Dont change anything below unless you know what you're doing.
@client.event
async def on_ready():
    print("Started") # TODO make this print the bot username at the end.
    await client.tree.sync()

def snipe(ign: str, placeId: int, cursor: str):
    getRequest = requests.get(
        f"https://games.roblox.com/v1/games/{placeId}/servers/0?sortOrder=2&excludeFullGames=false&limit=100")
    if cursor is not None: # I made this at 3am, please help
        getRequest = requests.get(
            f"https://games.roblox.com/v1/games/{placeId}/servers/0?sortOrder=2&excludeFullGames=false&limit=100&cursor={cursor}")


    userId = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [ign]}).json()["data"][0]["id"]
    thumbnailId = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userId}&size=150x150&format=Webp&isCircular=false").json()["data"][0]["imageUrl"]

    cachedTokens = [] # To help prevent ratelimits.
    json = getRequest.json()
    # Check for ratelimiting - TODO make it use response codes
    if 'Too many requests' in getRequest.text:
        return 'Ratelimited.';
    for server in json["data"]:
        for playerToken in server["playerTokens"]:
            cachedTokens.append({
                "requestId": f"0:{playerToken}:AvatarHeadshot:150x150:webp:regular", "token": playerToken, # I dont know if you need parse most of these but im not checking.
                "type": "AvatarHeadShot", "size": "150x150","format": "webp",
            })
        tokenThumbs = requests.post('https://thumbnails.roblox.com/v1/batch', json=cachedTokens)
        cachedTokens.clear()
        if str(thumbnailId) in str(tokenThumbs.text): # str("TODO idk make this better")
            return str(f"https://fern.wtf/joiner?placeId={placeId}&gameInstanceId={server['id']}");
    if 'nextPageCursor' in getRequest.text and json['nextPageCursor'] is not None: # Crashes because its dumb or whtv..
        snipe(ign, placeId, json['nextPageCursor'])
    return str("Player not found.")

@client.tree.command()
async def snipe(interaction: discord.Interaction, ign: str, gameid: int):
    await interaction.response.send_message('Please wait.') # Cant be bothered to optimise this
    # TODO Make it edit the message instead of sending another
    serverId = snipe(ign, gameid, None)
    if serverId: # Check incase my code fucks up and doesnt return anything !
        await interaction.channel.send(serverId)

client.run(TOKEN)

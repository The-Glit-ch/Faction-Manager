import discord
import json
import os
from discord import file
from discord.colour import Color
from discord.errors import PrivilegedIntentsRequired
from discord.ext import commands
from json.decoder import JSONDecodeError
from discord.user import User

bot = commands.Bot(command_prefix='/')
bot.remove_command('help')

#Vars
TOKEN = "No"

FactionsFolder = "Factions"
JoinedFactionsFolder = "UserData"

#Start Up
@bot.event
async def on_ready():
    print ("------------------------------------")
    print (f"Bot Name: {str(bot.user.name)}")
    print (f"Bot ID: {bot.user.id}")
    print ("------------------------------------")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching ,name="for /help"))

@bot.command()
async def help(ctx):
    Embed = discord.Embed(title="Commands",description = """``/help`` Shows the help board ``Aliases= None``\n``/Factions`` Shows all factions ``Aliases= Factions``\n``/myFaction`` Shows your current faction ``Aliases= myfaction``\n``/newFaction <FactionName>`` Make a new faction ``Aliases= newfaction``\n``/joinFaction <FactionName>`` Join a faction ``Aliases= joinfaction``\n``/leaveFaction`` Leave your current faction ``Aliases= leavefaction``\n""",color = discord.Colour.red())
    await ctx.send(embed=Embed)

@bot.command(aliases=['factions'])
async def Factions(ctx):
       with open("AllFactions.txt","r") as AllFactions:
           Names =AllFactions.readline().replace(",","\n")
           Embed = discord.Embed(title = "All factions", description = Names, color = discord.Color.blue())
           await ctx.send(embed = Embed)
           AllFactions.close()
#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^
#Gets all faction names in the "AllFactions.txt" file
#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^

@bot.command(aliases=['myfaction'])
async def myFaction(ctx):
    ID = str(ctx.author.id)
    try:
        with open(os.path.abspath(__file__).replace("\Bot.py",f"\{JoinedFactionsFolder}\{ID}.json")) as UserJson_File:
            UserData = json.load(UserJson_File)
            Dir = UserData["InFaction"]
            with open(os.path.abspath(__file__).replace("\Bot.py",f"\{FactionsFolder}\{Dir}.json")) as FactionJson_File:
                FJF = json.load(FactionJson_File)
                #Get faction details
                FName = FJF["FactionDetails"]["FName"]
                FOwner = FJF["FactionDetails"]["FOwner"]
                FMembersRaw = str(FJF["FactionDetails"]["FMembers"]).split(",")
                FMembers = await IDtoPing(FMembersRaw) #Convert a list into user pings
                Embed = discord.Embed(title = f"**{FName}**", description = f"Founder: <@{FOwner}>\nMembers:\n{FMembers}", color = discord.Colour.blue()) #Make an embed
                await ctx.send(embed=Embed)
                FactionJson_File.close() #Close the file
                UserJson_File.close() #Close the file
    
    except FileNotFoundError: #Player hasent made a faction err
                await ctx.send(f"It looks like you havent made a faction yet.")
    
    except Exception as err: #Bot messed up err
                await ctx.send(f"Uh oh. It looks like soething went wrong on my end. Error: **{err}**")
#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^#
#Shows faction details for said user
#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^#

@bot.command(aliases=['newfaction'])
async def newFaction(ctx, *args):
    ID = str(ctx.author.id)
    FName = ' '.join(args) #Joins the faction name text
    
    if FName == "": #We dont want an empty faction name
        await ctx.send("You have to give your faction a name")
    
    else:
        if os.path.exists(os.path.abspath(__file__).replace("\Bot.py",f"\{JoinedFactionsFolder}\{ID}.json")): #We dont want the same user to make another faction
            FName = json.load(open(os.path.abspath(__file__).replace("\Bot.py",f"\{JoinedFactionsFolder}\{ID}.json")))
            FName["InFaction"]
            await ctx.send(f"<@{ID}> It appears that you are already in a faction named **{FName}**")
        
        else:
            if os.path.exists(os.path.abspath(__file__).replace("\Bot.py",f"\{FactionsFolder}\{FName}.json")): #We dont want the same faction names
                await ctx.send(f"<@{ID}> It appears that the name is taken ")
                open("AllFactions.txt","r").close()
            
            else:
                with open(os.path.abspath(__file__).replace("\Bot.py",f"\{JoinedFactionsFolder}\{ID}.json"),"a") as UserJson_File:
                    with open(os.path.abspath(__file__).replace("\Bot.py",f"\{FactionsFolder}\{FName}.json"),"a") as FactionJson_File:
                        with open("AllFactions.txt","a") as AllFactions:
                            FactionData = {
                                "FactionDetails" : {
                                    "FName" : FName,
                                    "FOwner" : ID,
                                    "FMembers" : "$"
                                }
                            }
                            UserData = {
                                "InFaction" : FName
                            }
                            json.dump(FactionData,FactionJson_File) #Write Json Data
                            json.dump(UserData,UserJson_File) #Write Json Data
                            AllFactions.write(f"{FName},")
                            AllFactions.close() #Close file
                            FactionJson_File.close() #Close file
                            UserJson_File.close() #Close file
                            await ctx.send(f"Your faction **{FName}** has been created")
#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^#
#Makes a faction
#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^#

@bot.command(aliases=['joinfaction'])
async def joinFaction(ctx, *args):
    ID = str(ctx.author.id)
    FName = ' '.join(args)
    if os.path.exists(os.path.abspath(__file__).replace("\Bot.py",f"\{JoinedFactionsFolder}\{ID}.json")):
        File = open(os.path.abspath(__file__).replace("\Bot.py",f"\{JoinedFactionsFolder}\{ID}.json"),"r")
        Data = json.load(File)
        T_FName = Data["InFaction"]
        await ctx.send(f"Your already in a faction called **{T_FName}**")
    else:
        try:
            with open(os.path.abspath(__file__).replace("\Bot.py",f"\{JoinedFactionsFolder}\{ID}.json"),"a") as UserJson_File:
                with open(os.path.abspath(__file__).replace("\Bot.py",f"\{FactionsFolder}\{FName}.json"),"r") as FactionJson_File:
                    FactionData = json.load(FactionJson_File)
                    Temp = open(os.path.abspath(__file__).replace("\Bot.py",f"\{FactionsFolder}\{FName}.json"),"w")
                    
                    UserData = {
                        "InFaction" : FName
                    }
                    RawStrData = str(FactionData).replace("$",f"{ID},$")
                    NewFactionData = dict(eval(RawStrData))

                    json.dump(UserData,UserJson_File)
                    json.dump(NewFactionData,Temp)

                    UserJson_File.close()
                    FactionJson_File.close()
                    
                    await ctx.send(f"You have now joined the **{FName}** faction")
        except FileNotFoundError:
            await ctx.send(f"<@{ID}> That faction dosent exist")

#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^#
#Join a faction
#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^#^^^^^^^^^#       

@bot.command(aliases=['leavefaction'])
async def leaveFaction(ctx):
    try:
        ID = str(ctx.author.id)
        with open(os.path.abspath(__file__).replace("\Bot.py",f"\{JoinedFactionsFolder}\{ID}.json"),"r") as UserJson_File:
            UJF = json.load(UserJson_File)
            FName = UJF["InFaction"]
            with open(os.path.abspath(__file__).replace("\Bot.py",f"\{FactionsFolder}\{FName}.json"),"r") as FactionJson_File:
                FJF = json.load(FactionJson_File)
                JID = FJF["FactionDetails"]["FOwner"]
                
                if JID == ID:
                    FMembersRaw = str(FJF["FactionDetails"]["FMembers"]).split(",")
                    FMembers = await IDtoFile(FMembersRaw) #Convert a list into File dirs
                    
                    FactionFile = open("AllFactions.txt","r").read().replace(f"{FName},","")
                    F = open("AllFactions.txt","w")
                    F.write(FactionFile)
                    F.close()
                    
                    #^^^^^^^^^^^^^^^^^^^^
                    #Update the current factions
                    #^^^^^^^^^^^^^^^^^^^^
                    
                    FactionJson_File.close()
                    UserJson_File.close()
                    

                    try:
                        for i in FMembers:
                            os.remove(os.path.abspath(__file__).replace("\Bot.py",f"\{JoinedFactionsFolder}\{i}.json"))
                    except:
                        pass
                    

                    os.remove(os.path.abspath(__file__).replace("\Bot.py",f"\{FactionsFolder}\{FName}.json"))
                    os.remove(os.path.abspath(__file__).replace("\Bot.py",f"\{JoinedFactionsFolder}\{ID}.json"))
                    await ctx.send(f"You have disband the **{FName}** Faction")
                else:
                    FactionJson_File.close()
                    UserJson_File.close()
                    
                    os.remove(os.path.abspath(__file__).replace("\Bot.py",f"\{JoinedFactionsFolder}\{ID}.json"))
                    await ctx.send(f"You have now left the **{FName}** Faction")
    except FileNotFoundError:
        await ctx.send(f"It looks like your not in a faction")
    except Exception as err:
        await ctx.send(f"Uh oh. It looks like soething went wrong on my end. Error: **{err}**")



#Custom Functions
async def IDtoPing(List):
    A = ['$']
    if List == A: #If the list is empty return no members, else return members
        return "None :("
    else:
        ReturnStr = []
        for i in List:
            if i == "$":
                pass
            else:
                ReturnStr.append(f"<@{i}>")
        return str(ReturnStr).replace("[","").replace("]","").replace("'","").replace(",","\n").replace("$","")

async def IDtoFile(List):
    A = ['$']
    if List == A: #If the list is empty return no members, else return members
        pass
    else:
        ReturnArry = []
        for i in List:
            if i == "$":
                pass
            else:
                ReturnArry.append(f"{i}")
        return ReturnArry

bot.run(TOKEN)

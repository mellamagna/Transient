# bot.py
import os
from os import path

import discord
from discord.utils import get
from dotenv import load_dotenv

import json
import re
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
discordclient = client

#####config

version = "1.2"
prefix = "!transient"
shortprefix = "!tr"

channelfile = "channeltimes.json"
defaultchanneltime = 1800

def refresh_channeltimes():
	if path.isfile(channelfile):
		with open(channelfile) as json_file:
			c = json.load(json_file)
		return c
	else:
		return {}

channeltimes = refresh_channeltimes()

def write_times():
	with open(channelfile, 'w', encoding='utf-8') as f:
		json.dump(channeltimes, f, ensure_ascii=False, indent=4)

#####discord actions

def helpmsg():
	output = ""
	output += "```"
	output += "GENERAL USE:\n\n"
	output += "Prefix any message with the following to mark it for automatic deletion.\n"
	output += "!!(two exclamation marks) - message deletes in 5 minutes\n"
	output += "!!!(three exclamation marks) - message deletes in 2 minutes\n"
	output += "!!!!(four or more) - message deletes in 10 seconds\n"
	output += "\n"
	output += "Please note that editing a message will not retroactively apply the deletion tag."
	output += "\n\n"
	output += "MISC COMMANDS (prefix !transient or !tr):\n\n"
	output += "!transient markchannel [n] - marks channel for auto-delete with optional time interval in seconds\n"
	output += "!transient unmarkchannel - unmarks channel for auto-delete\n"
	output += "\n"
	output += "!transient about - displays general info about this bot\n"
	output += "!transient changelog - displays changes from last version\n"
	output += "!transient help - displays this message\n"
	output += "```"
	return output

def aboutmsg():
	output = ""
	output += "```"
	output += "Transient (v"
	output += version
	output += ")\n"
	output += "Snapchat for Discord - your messages, lost to the sands of time.\n"
	output += "Written by Mel Lamagna\n"
	output += "```"
	return output

def changelog():
	output = ""
	output += "```"
	output += "v"
	output += version
	output += ":\n"
	output += "\t - added channel-wide monitoring\n"
	output += "```"
	return output

def invinput():
	output = "Invalid command, please see `!transient help` for a list of available commands"
	return output

#####core functionality

def markchannel(channel, time):
	channeltimes[str(channel)] = time
	write_times()

def unmarkchannel(channel):
	del(channeltimes[str(channel)])
	write_times()

async def markfordelete(message, time):
	print(str(message.id) + " marked for deletion in " + str(time) + " seconds")
	await asyncio.sleep(time)
	await message.delete()
	print(str(message.id) + " deleted")

#####custom actions

def checkprefix(text):
	t = text.lower()
	if re.search("^!!", t):
		return True
	else:
		return False

def checkprefixlv2(text):
	t = text.lower()
	if re.search("^!!!", t):
		return True
	else:
		return False

def checkprefixlv3(text):
	t = text.lower()
	if re.search("^!!!!", t):
		return True
	else:
		return False

#####emoji arrays

def emojiarrayninja():
	emojis = []
	emojis.append('\U0001F977')
	return emojis

#####client events

@client.event
async def on_ready():
	await client.change_presence(activity=discord.Game('!transient help'))
	for guild in client.guilds:
		if guild.name == GUILD:
			break
	print(
        f'{client.user} is connected to the following guild:\n'
    	f'{guild.name}(id: {guild.id})'
    )
	print(str(len(channeltimes)) + " channel(s) loaded from file.")

async def add_reaction_array(message, arr):
	for emoji in arr:
		await message.add_reaction(emoji)

@client.event
async def on_message(message):
	if message.author == client.user:
		return
	elif message.content.startswith(prefix) or message.content.startswith(shortprefix):
		try:
			if message.content.startswith(prefix):
				args = message.content[len(prefix):len(message.content)].strip().split()
			else:
				args = message.content[len(shortprefix):len(message.content)].strip().split()
			command = args[0]
			args = args[1:len(args)]
			try:
				if command == "help":
					await message.channel.send(helpmsg())
				elif command == "about":
					await message.channel.send(aboutmsg())
				elif command == "changelog":
					await message.channel.send(changelog())
				elif command == "markchannel":
					time = defaultchanneltime
					try:
						if args[0].isnumeric():
							time = int(args[0])
					except ValueError:
						time = defaultchanneltime
					except IndexError:
						time = defaultchanneltime
					markchannel(message.channel.id, time)
					await message.channel.send("This channel has been marked for message auto-delete with time interval set to " + str(time) + " seconds.")
				elif command == "unmarkchannel":
					unmarkchannel(message.channel.id)
					await message.channel.send("This channel has been unmarked for message auto-delete.")
				else:
					await message.channel.send(invinput())
			except ValueError:
				await message.channel.send(invinput())
			except IndexError:
				await message.channel.send(invinput())
		except IndexError:
			await message.channel.send(invinput())
	elif checkprefix(message.content):
		print("Prefix regex match")
		await add_reaction_array(message, emojiarrayninja())
		if checkprefixlv3(message.content):
			time = 10
		elif checkprefixlv2(message.content):
			time = 120
		else:
			time = 300
		await markfordelete(message, time)
	elif str(message.channel.id) in channeltimes:
		print("Message sent in marked channel")
		# await add_reaction_array(message, emojiarrayninja())
		await markfordelete(message, channeltimes[str(message.channel.id)])

client.run(TOKEN)
from secrets import Token, bot_channel_ID
from predictor import *
import discord
from discord.ext import commands
from datetime import datetime
import requests
import asyncio

# from keep_alive import keep_alive

bot = commands.Bot(command_prefix='$')


@bot.event
async def on_ready(ctx):
    await bot.change_presence(activity=discord.Game("Predicting btc"))
    

@bot.command()
async def working(ctx):
    """ Checks if bot is online or not"""
    await ctx.send("Yes I'm working")


@bot.command()
async def predict(ctx):
    """ Predicts btc close price of current 15 min candle"""
    [openTime, predictedClose, openPrice] = predictClose()
    numberOfShares = 100/openPrice
    Profit = abs((100/openPrice)*predictedClose[0] - 100)
    embed = discord.Embed(title="15 min Close prediction", color=discord.Color.blue())
    embed.add_field(name="Open Time", value=openTime, inline=False)
    embed.add_field(name="Predicted Close Price in usdt", value=predictedClose[0], inline=False)
    embed.add_field(name="Open Price in usdt", value=openPrice, inline=False)
    embed.add_field(name="Predicted Percentage change", value=str(Profit) + "%", inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def pdata(ctx):
    """ Display data of previous 15 min btc candle"""
    data = previousData()
    embed = discord.Embed(title="Previous 15 min BTC Candle statistics",
                          description="all prices in usdt", color=discord.Color.blue())
    embed.add_field(name="Open Time", value=data[0], inline=False)
    embed.add_field(name="Open Price", value=data[1], inline=False)
    embed.add_field(name="High", value=data[2], inline=False)
    embed.add_field(name="Low", value=data[3], inline=False)
    embed.add_field(name="Close", value=data[4], inline=False)
    embed.add_field(name="Predicted Close", value=data[5], inline=False)
    embed.add_field(name="Percentage Profit",
                    value=str(data[6])+"%", inline=False)
    await ctx.send(embed = embed)


@bot.command()
async def lastProfits(ctx):
    """" Display profit earned through predictions in last N candles based on threshold profit margin as per user"""
    N=0
    minProfitPerTrade = 0
    embedVar = discord.Embed(
        title="Enter number(between 1 to 980) of candles to track profit", description="", color=0x00ff00)
    await ctx.send(embed=embedVar)

    try:
        message = await bot.wait_for('message', timeout=60, check=lambda message: message.author == ctx.author)
        N = int(message.content)
    except asyncio.TimeoutError:
        embedVar = discord.Embed(
            title="timeup you did not respond, please try again if you wish to", description="", color=0x00ff00)
        await ctx.send(embed=embedVar)
        return

    embedVar = discord.Embed(
        title="Enter minimun profit percentage required for you to enter a trade", description="", color=0x00ff00)
    await ctx.send(embed=embedVar)

    try:
        message = await bot.wait_for('message', timeout=60, check=lambda message: message.author == ctx.author)
        minProfitPerTrade = int(message.content)
    except asyncio.TimeoutError:
        embedVar = discord.Embed(
            title="timeup you did not respond, please try again if you wish to", description="", color=0x00ff00)
        await ctx.send(embed=embedVar)
        return
    if(N>980 or N<1):
        embedVar = discord.Embed(
            title="Please enter a valid N, try again if you wish to", description="", color=0x00ff00)
        await ctx.send(embed=embedVar)
        return 
    
    [netProfit, numberOfTrades] = profitInLastNcandles(N, minProfitPerTrade)
    embed = discord.Embed(title="Statistics of last "+str(N)+" candles", color=discord.Color.blue())
    embed.add_field(name="Net Profit earned", value=str(netProfit), inline=False)
    embed.add_field(name="Number of Trades entered",
                    value=str(numberOfTrades), inline=False)
    embed.add_field(name="Avg. profit per trade",
                    value=str(netProfit/numberOfTrades), inline=False)
    await ctx.send(embed=embed)

@bot.event
async def on_disconnect(ctx):
    await ctx.send('Logging off!')

# keep_alive()

bot.run(Token)

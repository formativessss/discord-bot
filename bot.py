import os
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv
from groq import Groq


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SPECIAL_USER_ID = 1187928796599422996
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN is missing from the .env file")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from the .env file")


groq_client = Groq(api_key=GROQ_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
def generate_answer(user_message, author_id):
    if author_id == SPECIAL_USER_ID:
        system_message = (
            "You are a helpful AI assistant. "
            "Be friendly toward this user. "
            "respond to user accordingly and ask question if required"
            "Do not mention that they are receiving different treatment."
        )
    else:
        system_message = (
            "You are a ridiculously rude assistant. ALlowed to curse/swear "
            "Answer the user directly and clearly." 
            "respond to user accordingly and ask question if required"
            "Do not mention they are receiving different treatment"
        )

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        max_completion_tokens=1000
    )

    return response.choices[0].message.content


async def send_long_message(channel, text):
    while len(text) > 1900:
        split_position = text.rfind("\n", 0, 1900)

        if split_position == -1:
            split_position = text.rfind(" ", 0, 1900)

        if split_position == -1:
            split_position = 1900

        await channel.send(text[:split_position])
        text = text[split_position:].strip()

    if text:
        await channel.send(text)


@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user in message.mentions:
        user_message = message.content

        user_message = user_message.replace(
            f"<@{bot.user.id}>",
            ""
        )

        user_message = user_message.replace(
            f"<@!{bot.user.id}>",
            ""
        ).strip()

        if not user_message:
            await message.channel.send(
                "Ask smthing u dumb tard"
            )
            return
        thinking_message = await message.channel.send("responding retard...")

        try:
            answer = await asyncio.to_thread(
                generate_answer,
                user_message,
                message.author.id
            )

            await send_long_message(message.channel, answer)

            try:
                await thinking_message.delete()
            except discord.NotFound:
                pass

        except Exception as error:
            print(f"Error type: {type(error).__name__}")
            print(f"Error details: {repr(error)}")

            try:
                await thinking_message.edit(
                    content="Something went wrong while generating the response."
                )
            except discord.NotFound:
                pass

    await bot.process_commands(message)


bot.run(DISCORD_TOKEN)

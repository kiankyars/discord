import os, asyncio
from pathlib import Path

import discord
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path.home() / ".env")

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
GROK = "/Users/kian/.grok/bin/grok"
GROK_ENV = {
    **os.environ,
    "PATH": "/Users/kian/.grok/bin:/opt/homebrew/bin:/usr/bin:/bin",
    "HOME": "/Users/kian",
}

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(m: discord.Message):
    if m.author.bot or (m.guild and bot.user not in m.mentions):
        return

    prompt = m.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
    if not prompt:
        return

    async with m.channel.typing():
        proc = await asyncio.create_subprocess_exec(
            GROK, "--sandbox", "workspace", "--model", "grok-composer-2.5-fast",
            "-p", prompt, "--always-approve",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=GROK_ENV,
        )
        out, err = await proc.communicate()
        text = out.decode(errors="replace").strip()
        stderr = err.decode(errors="replace")[-800:]
        reply = text or f"(no response) rc={proc.returncode} stderr={stderr}"

    for i in range(0, len(reply), 1900):
        await m.channel.send(reply[i:i+1900])

bot.run(DISCORD_TOKEN)

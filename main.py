import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}!')

async def send_gear_message(ctx, title, lines, emoji_keys):
    message = await ctx.send(f"**▬▬▬▬▬▬ {title} ▬▬▬▬▬▬**\n\n" + "\n".join(lines))

    for key in ['vagtsword'] + emoji_keys:
        emoji = EMOJIS.get(key)
        if emoji:
            try:
                await message.add_reaction(emoji)
            except discord.HTTPException:
                print(f"❌ Kunne ikke tilføje emoji: {key}")

    bot_gear_messages.add(message.id)

#
# Emoji-oversigt
#

EMOJIS = {
    'vagtsword': discord.PartialEmoji(name='vagtsword', id=1104397646837317743),
    '3pieces': discord.PartialEmoji(name='3pieces', id=1303475209722134538),
    '2pieces': discord.PartialEmoji(name='2pieces', id=1303475253875445901),
    '3piece_p4': discord.PartialEmoji(name='3piece_p4', id=1356993957288214694),
    'leggear': discord.PartialEmoji(name='leggear', id=1303475306320887849),
    'irongear': discord.PartialEmoji(name='irongear', id=1303475378614046871)
}

bot_gear_messages = set()

#
# !GEAR HERUNDER
# 

@bot.command()
async def geara(ctx):
    lines = [
        "**Vagtsværd: <:vagtsword:1104397646837317743>**",
        "**3 Pieces P5 Vagtgear: <:3pieces:1303475209722134538>**",
        "**2 Pieces P5 Vagtgear: <:2pieces:1303475253875445901>**",
        "**P4 Vagtgear: <:3piece_p4:1356993957288214694>**",
        "**Leggear: <:leggear:1303475306320887849>**"
    ]
    await send_gear_message(ctx, "Gear React i A", lines, ['3pieces', '2pieces', '3piece_p4', 'leggear'])

@bot.command()
async def gearb(ctx):
    lines = [
        "**Vagtsværd: <:vagtsword:1104397646837317743>**",
        "**3 Pieces P4 Vagtgear: <:3pieces:1303475209722134538>**",
        "**2 Pieces P4 Vagtgear (eller 3 pieces uden leg hat): <:2pieces:1303475253875445901>**",
        "**Leggear: <:leggear:1303475306320887849>**"
    ]
    await send_gear_message(ctx, "Gear React i B", lines, ['3pieces', '2pieces', 'leggear'])

@bot.command()
async def gearc(ctx):
    lines = [
        "**Vagtsværd: <:vagtsword:1104397646837317743>**",
        "**3 Pieces P5 Vagtgear: <:3pieces:1303475209722134538>**",
        "**2 Pieces P5 Vagtgear: <:2pieces:1303475253875445901>**",
        "**P4 Vagtgear: <:3piece_p4:1356993957288214694>**",
        "**Iron gear: <:irongear:1303475378614046871>**"
    ]
    await send_gear_message(ctx, "Gear React i C", lines, ['3pieces', '2pieces', '3piece_p4', 'irongear'])

#
# !REACT HERUNDER
# 

@bot.command()
async def react(ctx, message_id: int):
    # ID på det stemmeopkald vi checker imod
    voice_channel_id = 1370831612882849972

    # Hent kanalen og beskeden
    try:
        channel = ctx.channel
        message = await channel.fetch_message(message_id)
    except Exception as e:
        await ctx.send(f"❌ Kunne ikke hente beskeden: {e}")
        return

    # Hent alle brugere der HAR reageret (uanset emoji)
    reacted_users = set()
    for reaction in message.reactions:
        async for user in reaction.users():
            reacted_users.add(user)

    # Hent brugere i opkaldet
    voice_channel = ctx.guild.get_channel(voice_channel_id)
    if not voice_channel or not isinstance(voice_channel, discord.VoiceChannel):
        await ctx.send("❌ Opkaldet blev ikke fundet.")
        return

    in_call = [member for member in voice_channel.members if not member.bot]

    missing = [member.mention for member in in_call if member not in reacted_users]

    if missing:
        await ctx.send(f"🙋 Følgende personer i opkaldet har IKKE reactet:\n" + "\n".join(missing))
    else:
        await ctx.send("✅ Alle i opkaldet har reactet.")

#
# FJERN REAKTION HERUNDER
# 

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return  # Ignorer andre botter

    message = reaction.message
    if message.id not in bot_gear_messages:
        return

    # Find den emoji som brugeren lige har tilføjet
    emoji_added = reaction.emoji

    for bot_reaction in message.reactions:
        # Vi sammenligner emoji ID (for custom emojis)
        if hasattr(bot_reaction.emoji, "id") and hasattr(emoji_added, "id"):
            same = bot_reaction.emoji.id == emoji_added.id
        else:
            # Fallback til unicode emojis
            same = bot_reaction.emoji == emoji_added

        if same:
            async for u in bot_reaction.users():
                if u == message.guild.me:  # Botten selv
                    try:
                        await message.remove_reaction(bot_reaction.emoji, u)
                        print(f"✅ Fjernede bot-reaktion: {bot_reaction.emoji}")
                    except discord.HTTPException:
                        print(f"❌ Kunne ikke fjerne bot-reaktion: {bot_reaction.emoji}")
                    break

#
# REAKTION LOGS
#

REACTION_LOG_CHANNEL_ID = 1371178740767391776
MONITORED_CHANNEL_ID = 1104306243482431562

async def log_reaction_event(event_type, reaction, user):
    if reaction.message.channel.id != MONITORED_CHANNEL_ID:
        return  # Kun log i specifik kanal

    log_channel = reaction.message.guild.get_channel(REACTION_LOG_CHANNEL_ID)
    if not log_channel:
        return

    action = "tilføjede" if event_type == "add" else "fjernede"
    await log_channel.send(f"🔁 {user.display_name} {action} reaktion {reaction.emoji} på besked `{reaction.message.id}`")

@bot.event
async def on_reaction_add(reaction, user):
    if not user.bot:
        await log_reaction_event("add", reaction, user)
    # Din eksisterende kode til at fjerne bot-reaktion...
    # (den kan stå her også)

@bot.event
async def on_reaction_remove(reaction, user):
    if not user.bot:
        await log_reaction_event("remove", reaction, user)

#
# OPKALD LOGS
#

VC_LOG_CHANNEL_ID = 1104306242849091711  # Logkanal til alle opkald

@bot.event
async def on_voice_state_update(member, before, after):
    log_channel = member.guild.get_channel(VC_LOG_CHANNEL_ID)
    if not log_channel:
        return

    if before.channel != after.channel:
        if before.channel and not after.channel:
            # Brugeren forlod et opkald
            await log_channel.send(f"🔇 {member.display_name} forlod **{before.channel.name}**")
        elif after.channel and not before.channel:
            # Brugeren tilsluttede et opkald
            await log_channel.send(f"🔊 {member.display_name} tilsluttede **{after.channel.name}**")
        elif before.channel and after.channel and before.channel != after.channel:
            # Brugeren skiftede mellem opkald
            await log_channel.send(f"🔁 {member.display_name} flyttede fra **{before.channel.name}** til **{after.channel.name}**")

#
# KØR BOTTEN
#

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
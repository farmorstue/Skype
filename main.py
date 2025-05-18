import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

# Indlæs token
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Emoji-oversigt
EMOJIS = {
    'vagtsword': discord.PartialEmoji(name='vagtsword', id=1104397646837317743),
    '3pieces': discord.PartialEmoji(name='3pieces', id=1303475209722134538),
    '2pieces': discord.PartialEmoji(name='2pieces', id=1303475253875445901),
    '3piece_p4': discord.PartialEmoji(name='3piece_p4', id=1356993957288214694),
    'leggear': discord.PartialEmoji(name='leggear', id=1303475306320887849),
    'irongear': discord.PartialEmoji(name='irongear', id=1303475378614046871)
}

bot_gear_messages = set()

# Logkanaler
REACTION_LOG_CHANNEL_ID = 1371178740767391776
MONITORED_CHANNEL_ID = 1104306243482431562
VC_LOG_CHANNEL_ID = 1104306242849091711
VC_CHECK_CHANNEL_ID = 1370831612882849972

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

# Gear-kommandoer
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

# REACT-kommando (tjek hvem i opkald der mangler reaktion)
@bot.command()
async def react(ctx, message_id: int):
    try:
        message = await ctx.channel.fetch_message(message_id)
    except Exception as e:
        await ctx.send(f"❌ Kunne ikke hente beskeden: {e}")
        return

    reacted_users = set()
    for reaction in message.reactions:
        async for user in reaction.users():
            reacted_users.add(user)

    voice_channel = ctx.guild.get_channel(VC_CHECK_CHANNEL_ID)
    if not voice_channel or not isinstance(voice_channel, discord.VoiceChannel):
        await ctx.send("❌ Opkaldet blev ikke fundet.")
        return

    in_call = [member for member in voice_channel.members if not member.bot]
    missing = [member.mention for member in in_call if member not in reacted_users]

    if missing:
        await ctx.send(f"🙋 Følgende personer i opkaldet har IKKE reactet:\n" + "\n".join(missing))
    else:
        await ctx.send("✅ Alle i opkaldet har reactet.")

# Fælles event: log + fjern bot-reaktion
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    message = reaction.message

    # Log reaktionen i overvåget kanal
    if message.channel.id == MONITORED_CHANNEL_ID:
        log_channel = message.guild.get_channel(REACTION_LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"🔁 {user.display_name} tilføjede reaktion {reaction.emoji} på besked `{message.id}`")

    # Fjern bot-reaktion hvis relevant gearbesked
    if message.id in bot_gear_messages:
        emoji_added = reaction.emoji
        for bot_reaction in message.reactions:
            same = (
                hasattr(bot_reaction.emoji, "id") and hasattr(emoji_added, "id")
                and bot_reaction.emoji.id == emoji_added.id
            ) or bot_reaction.emoji == emoji_added

            if same:
                async for u in bot_reaction.users():
                    if u == message.guild.me:
                        try:
                            await message.remove_reaction(bot_reaction.emoji, u)
                            print(f"✅ Fjernede bot-reaktion: {bot_reaction.emoji}")
                        except discord.HTTPException:
                            print(f"❌ Kunne ikke fjerne bot-reaktion: {bot_reaction.emoji}")
                        break

@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return

    if reaction.message.channel.id == MONITORED_CHANNEL_ID:
        log_channel = reaction.message.guild.get_channel(REACTION_LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"🔁 {user.display_name} fjernede reaktion {reaction.emoji} på besked `{reaction.message.id}`")

# Opkalds-logs
@bot.event
async def on_voice_state_update(member, before, after):
    log_channel = member.guild.get_channel(VC_LOG_CHANNEL_ID)
    if not log_channel:
        return

    if before.channel != after.channel:
        if before.channel and not after.channel:
            await log_channel.send(f"🔇 {member.display_name} forlod **{before.channel.name}**")
        elif after.channel and not before.channel:
            await log_channel.send(f"🔊 {member.display_name} tilsluttede **{after.channel.name}**")
        elif before.channel and after.channel:
            await log_channel.send(f"🔁 {member.display_name} flyttede fra **{before.channel.name}** til **{after.channel.name}**")

@bot.command()
async def gearroll(ctx, message_id: int):
    try:
        message = await ctx.channel.fetch_message(message_id)
    except Exception as e:
        await ctx.send(f"❌ Kunne ikke hente beskeden: {e}")
        return

    # Emoji prioritet: højeste først
    slot_emojis = {
        '3pieces': 4,
        '2pieces': 3,
        '3piece_p4': 2,
        'leggear': 1  # kræver også vagtsword
    }

    # Brugers reaktioner
    user_to_emojis = {}
    vagtsword_users = set()

    # Saml hvem der har reageret med hvad
    for reaction in message.reactions:
        emoji = reaction.emoji
        emoji_key = None

        for key, partial in EMOJIS.items():
            if hasattr(emoji, "id") and emoji.id == partial.id:
                emoji_key = key
                break

        if not emoji_key:
            continue

        async for user in reaction.users():
            if user.bot:
                continue

            if emoji_key == "vagtsword":
                vagtsword_users.add(user)
            else:
                if user not in user_to_emojis:
                    user_to_emojis[user] = set()
                user_to_emojis[user].add(emoji_key)

    # Beregn højeste slot for hver bruger
    final_list = []

    for user, emojis in user_to_emojis.items():
        for key in slot_emojis:  #_

# Start botten
bot.run(token, log_handler=handler, log_level=logging.DEBUG)

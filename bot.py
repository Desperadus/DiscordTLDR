import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime, timedelta
import shlex

# Load environment variables from .env file
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

SUMMARY_PROMPT = (
    "Provide a concise summary of the following Discord conversation. "
    "Include what the discussion was about, users' opinions, experiences, etc. "
    "When needed, highlight important information in bold. "
    "Respond in the language the conversation took place in."
)

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN is not set in the environment variables.")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in the environment variables.")

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# Set up Discord intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Required to read message content

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")


@bot.command(name="tldr")
async def tldr(ctx, *, arg_string: str = None):
    """
    TLDR command to summarize Discord conversations.

    Usage:
    !tldr -h [hours] [-p] [-c "Your custom prompt"]
    !tldr -m [messages] [-p] [-c "Your custom prompt"]
    !tldr --help
    """
    if arg_string is None:
        await send_help(ctx)
        return

    try:
        parsed_args = shlex.split(arg_string)
    except ValueError as e:
        await ctx.send(f"❌ Error parsing arguments: {str(e)}")
        return

    # Initialize flags
    flags = {
        "-h": None,
        "-m": None,
        "-c": None,
        "-p": False
    }

    if "--help" in parsed_args:
        await send_help(ctx)
        return

    # Parsing logic
    i = 0
    while i < len(parsed_args):
        arg = parsed_args[i]
        if arg == "-h":
            if i + 1 < len(parsed_args):
                flags["-h"] = parsed_args[i + 1]
                i += 2
            else:
                await ctx.send("❌ The `-h` flag requires a numerical value for hours.")
                return
        elif arg == "-m":
            if i + 1 < len(parsed_args):
                flags["-m"] = parsed_args[i + 1]
                i += 2
            else:
                await ctx.send("❌ The `-m` flag requires a numerical value for messages.")
                return
        elif arg == "-c":
            if i + 1 < len(parsed_args):
                flags["-c"] = parsed_args[i + 1]
                i += 2
            else:
                await ctx.send("❌ The `-c` flag requires a custom prompt.")
                return
        elif arg == "-p":
            flags["-p"] = True
            i += 1
        elif arg == "--help":
            await send_help(ctx)
            return
        else:
            await ctx.send(f"❌ Unrecognized flag `{arg}`.")
            return

    # Validate flags
    if flags["-h"] and flags["-m"]:
        await ctx.send("❌ Please use either `-h` (hours) or `-m` (messages), not both.")
        return
    if not flags["-h"] and not flags["-m"]:
        await ctx.send("❌ You must specify either `-h [hours]` or `-m [messages]`.")
        return

    # Fetch messages based on flags
    try:
        if flags["-h"]:
            hours = float(flags["-h"])
            since = datetime.utcnow() - timedelta(hours=hours)
            messages = []
            async for message in ctx.channel.history(after=since, limit=None, oldest_first=True):
                # Skip bot messages to avoid recursion
                if message.author == bot.user:
                    continue
                messages.append(f"{message.author}: {message.content}")
        elif flags["-m"]:
            limit = int(flags["-m"])
            messages = []
            async for message in ctx.channel.history(limit=limit, oldest_first=False):
                if message.author == bot.user:
                    continue
                messages.append(f"{message.author}: {message.content}")
            messages.reverse()
    except ValueError:
        await ctx.send("❌ Invalid number format for hours or messages.")
        return
    except Exception as e:
        print(e)
        await ctx.send("❌ An unexpected error occurred while fetching messages.")
        return

    if not messages:
        await ctx.send("ℹ️ No messages found for the specified criteria.")
        return

    # Prepare the prompt for the Gemini API
    prompt = "\n".join(messages)
    if flags["-c"]:
        summary_prompt = f"{SUMMARY_PROMPT}\n\nAdditionaly: {flags['-c']}\n\nConversation: {prompt}"
    else:
        summary_prompt = f"{SUMMARY_PROMPT}\n\n{prompt}"

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        generation_config = {
            "temperature": 0.5,
            "max_output_tokens": 4096,
        }

        response = model.generate_content(
            summary_prompt,
            generation_config=generation_config
        )
        summary = response.text.strip()
    except Exception as e:
        print(e)
        await ctx.send("❌ Failed to generate summary using Gemini API.")
        return

    if flags["-p"]:
        # Post the summary in the channel
        embed = discord.Embed(
            title="📄 TLDR Summary",
            description=summary,
            color=discord.Color.blue(),
            timestamp=datetime.utcnow(),
        )
        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
        )
        await ctx.send(embed=embed)
    else:
        # Send the summary as a DM to the user
        try:
            embed = discord.Embed(
                title="📄 TLDR Summary",
                description=summary,
                color=discord.Color.green(),
                timestamp=datetime.utcnow(),
            )
            embed.set_footer(
                text=f"Requested on {ctx.guild.name}",
                icon_url=ctx.guild.icon.url if ctx.guild.icon else None,
            )
            await ctx.author.send(embed=embed)
            # await ctx.send("✅ I've sent you a DM with the summary!")
        except discord.Forbidden:
            await ctx.send(
                "❌ I couldn't send you a DM. Please check your privacy settings."
            )


@tldr.error
async def tldr_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "❌ Missing arguments. Use `!tldr -h [hours]` or `!tldr -m [messages]`."
        )
    else:
        await ctx.send("❌ An error occurred while processing your request.")


@bot.command(name="help")
async def help_command(ctx):
    help_message = (
        "📄 **TLDR Bot Help** 📄\n\n"
        "**Commands:**\n"
        "`!tldr -h [hours]` - Get a summary of the last [hours] hours of the chat as a DM.\n"
        "`!tldr -m [messages]` - Get a summary of the last [messages] messages as a DM.\n"
        "`-c \"Your custom prompt\"` - Add a custom prompt to ask specific questions about the conversation.\n"
        "`-p` flag can be added to post the summary in the channel instead of DM.\n"
        "`!tldr --help` - Display this help message.\n\n"
        "**Examples:**\n"
        "`!tldr -h 2` - Summarize the last 2 hours of conversation privately.\n"
        "`!tldr -m 50 -p` - Summarize the last 50 messages publicly in the channel.\n"
        "`!tldr -h 1 -c \"What were the main decisions made during this discussion?\"` - Summarize the last 1 hour of conversation with a specific focus."
    )
    await ctx.send(help_message)


async def send_help(ctx):
    help_message = (
        "📄 **TLDR Bot Help** 📄\n\n"
        "**Commands:**\n"
        "`!tldr -h [hours]` - Get a summary of the last [hours] hours of the chat as a DM.\n"
        "`!tldr -m [messages]` - Get a summary of the last [messages] messages as a DM.\n"
        "`-c \"Your custom prompt\"` - Add a custom prompt to ask specific questions about the conversation.\n"
        "`-p` flag can be added to post the summary in the channel instead of DM.\n"
        "`!tldr --help` - Display this help message.\n\n"
        "**Examples:**\n"
        "`!tldr -h 2` - Summarize the last 2 hours of conversation privately.\n"
        "`!tldr -m 50 -p` - Summarize the last 50 messages publicly in the channel.\n"
        "`!tldr -h 1 -c \"What were the main decisions made during this discussion?\"` - Summarize the last 1 hour of conversation with a specific focus."
    )
    await ctx.send(help_message)


# Run the bot
bot.run(DISCORD_TOKEN)
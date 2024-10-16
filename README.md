# Discord TLDR Bot

A Discord bot that uses the Google Gemini API to generate TLDR (Too Long; Didn't Read) summaries of Discord conversations. The bot can summarize based on a number of messages, a time window, or even answer specific custom questions about the conversation.

## Features

- **Summarize by Time**: Get a summary of the conversation from the last _n_ hours.
- **Summarize by Message Count**: Get a summary of the last _n_ messages.
- **Custom Prompts**: Ask specific questions about the conversation.
- **Private or Public Summaries**: Choose to receive the summary as a DM or post it publicly in the channel.
- **Help Command**: Easily access usage instructions.

## Installation

This bot requires Python 3.9+ and Poetry for package management.

### 1. Clone the Repository

```bash
git clone https://github.com/Desperadus/DiscordTLDR.git
cd DiscordTLDR
```

### 2. Install Dependencies

Ensure you have Python 3.9 or higher installed. Then, install the dependencies using [Poetry](https://python-poetry.org/).

```bash
poetry install
```

### 3. Configure Environment Variables

Create a `.env` file based on the provided `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file and add your Discord bot token and Google Gemini API key:

```env
DISCORD_TOKEN=your_discord_bot_token_here
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

### 4. Enable Discord Intents

Go to the [Discord Developer Portal](https://discord.com/developers/applications), select your application, navigate to the "Bot" section, and enable the "Message Content Intent".

### 5. Run the Bot

Activate the Poetry virtual environment and run the bot:

```bash
poetry shell
python bot.py
```

Alternatively, you can run the bot directly using:

```bash
poetry run python bot.py
```

## Usage

Once the bot is running and added to your Discord server, you can use the following commands:

- `!tldr -h [hours]`: Summarize the last `[hours]` hours of conversation.
- `!tldr -m [messages]`: Summarize the last `[messages]` messages.
- `-c "Your custom prompt"`: Add a custom prompt to ask specific questions about the conversation.
- Add the `-p` flag to post the summary publicly in the channel instead of sending it as a DM.
- `!tldr --help`: Display help instructions.

### Examples

- `!tldr -h 2`: Summarize the last 2 hours of conversation privately.
- `!tldr -m 50 -p`: Summarize the last 50 messages publicly in the channel.
- `!tldr -h 1 -c "What were the main decisions made?"`: Summarize the last 1 hour of conversation with a specific focus on decisions.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

GNU 2.1 Lesser License

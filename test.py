import discord
import openai


# Set your OpenAI GPT-3 API key
openai.api_key = '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'

# Set the Discord bot token
TOKEN = 'MTE0MjMxMDg3NzE2MTMzMjgyNw.Gqi2Vu.07UpbKLoIQ2XHuJjhNcodRoKIjfJH2l6zsMlKY'


# Set up the intents
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True

# Set up the bot with intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Define a dictionary of predefined responses
responses = {
    "hi": ["Hey!", "Hello!", "Hi there!"],
    "hello": ["Hey!", "Hello!", "Hi there!"]
}

# Initialize a dictionary to store the last response for each channel
last_responses = {}

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# Event handler for incoming messages
@bot.event
async def on_message(message):
    # Process every message and send a response using GPT-3 or predefined responses
    if message.author != bot.user:  # Ensure the bot doesn't respond to itself
        try:
            text = message.content.lower()

            # Check for predefined responses
            if text in responses:
                reply = random.choice(responses[text])
                await message.channel.send(reply)
            else:
                # Check if the bot has replied with the same message before
                last_response = last_responses.get(message.channel.id, "")

                if last_response != text:
                    prompt = f"You said: {message.content}. What are your thoughts on this?"
                    response = openai.Completion.create(
                        engine="davinci",
                        prompt=prompt,
                        max_tokens=150,
                        temperature=0.5,
                        top_p=1,
                        n=1
                    )
                    reply = response.choices[0].text.strip()
                    last_responses[message.channel.id] = text
                    await message.channel.send(reply)

        except Exception as e:
            await message.channel.send(f"An error occurred: {e}")

    await bot.process_commands(message)  # Add this line to handle commands

# Run the bot with your Discord token
bot.run(TOKEN)
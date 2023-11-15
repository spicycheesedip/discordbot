import os
import random
import requests
import discord
import datetime
import asyncio
from discord.ext import commands
from bs4 import BeautifulSoup
import whois
import pywhatkit as kit
import openai
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from textblob import TextBlob
import spacy
import socket
import psutil
import sys
import re
import phonenumbers




# Initialize Discord bot
os.system('clear')
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)





# Create a dictionary to store meanings
dictionary = {}

# Load meanings from the list.txt file  `   `
with open('list.txt', 'r') as file:
    for line in file:
        line = line.strip()
        if "::" in line:
            parts = line.split("::")
            if len(parts) == 2:
                word, meaning = parts
                dictionary[word.strip()] = meaning.strip()
            else:
                print(f"Ignored line: {line}. Expected format 'word::meaning'")
        else:
            print(f"Ignored line: {line}. Separator '::' not found.")





# Define a list of allowed usernames
allowed_usernames = ["mr.letitblast", "iavd"]

# Define a deck of cards
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
deck = [{'value': value, 'suit': suit} for suit in suits for value in values]

# Define voidcoins dictionary
voidcoins = {}

# Utility Functions
def shuffle_deck():
    """Shuffle the deck of cards."""
    random.shuffle(deck)

def deal_card():
    """Deal a card from the deck."""
    if len(deck) == 0:
        shuffle_deck()
    return deck.pop()

def add_voidcoins(user_id, amount):
    """Add voidcoins to a user."""
    voidcoins[user_id] = voidcoins.get(user_id, 0) + amount

def calculate_score(hand):
    """Calculate the score of a hand in a blackjack game."""
    score = 0
    num_aces = 0
    for card in hand:
        if card['value'] in ['Jack', 'Queen', 'King']:
            score += 10
        elif card['value'] == 'Ace':
            score += 11
            num_aces += 1
        else:
            score += int(card['value'])

    while num_aces > 0 and score > 21:
        score -= 10
        num_aces -= 1

    return score

def format_hand(hand):
    """Format a hand for display."""
    return ', '.join([format_card(card) for card in hand])

def format_card(card):
    """Format a card for display."""
    return f"{card['value']} of {card['suit']}"

# Game Functions
async def blackjack_game(message):  # Change the parameter name from ctx to message
    """Start a game of Blackjack."""
    author = message.author
    if author.id not in voidcoins:
        voidcoins[author.id] = 100  # Give 100 voidcoins to the player if they don't have any

    player_balance = voidcoins[author.id]
    
    # Use message.channel.send to send messages in the game
    await message.channel.send(f"You have {player_balance} voidcoins.")

    if player_balance < 10:
        await message.channel.send("You need at least 10 voidcoins to play Blackjack.")
        return

    shuffle_deck()
    player_hand = [deal_card(), deal_card()]
    dealer_hand = [deal_card(), deal_card()]

    player_score = calculate_score(player_hand)
    dealer_score = calculate_score(dealer_hand)

    await message.channel.send(f"Your hand: {format_hand(player_hand)}, Score: {player_score}")
    await message.channel.send(f"Dealer's face-up card: {format_card(dealer_hand[0])}")

    while player_score < 21:
        response = await bot.wait_for('message', check=lambda m: m.author == author)
        if response.content.lower() == 'hit':
            player_hand.append(deal_card())
            player_score = calculate_score(player_hand)
            await message.channel.send(f"You drew {format_card(player_hand[-1])}, Your score: {player_score}")
        elif response.content.lower() == 'stand':
            break

    while dealer_score < 17:
        dealer_hand.append(deal_card())
        dealer_score = calculate_score(dealer_hand)

    await message.channel.send(f"Your final hand: {format_hand(player_hand)}, Your score: {player_score}")
    await message.channel.send(f"Dealer's final hand: {format_hand(dealer_hand)}, Dealer's score: {dealer_score}")

    if player_score > 21:
        await message.channel.send("Bust! You lose.")
        voidcoins[author.id] -= 10  # Remove 10 voidcoins for losing
    elif dealer_score > 21 or player_score > dealer_score:
        win_amount = random.randint(10, 50)  # Random voidcoins for the win (between 10 and 50)
        add_voidcoins(author.id, win_amount)
        await message.channel.send(f"You win {win_amount} voidcoins!")
    elif player_score == dealer_score:
        await message.channel.send("It's a tie!")
    else:
        await message.channel.send("You lose.")
        voidcoins[author.id] -= 10  # Remove 10 voidcoins for losing








# Function to scrape and send a random beer-related fact from a website
async def scrape_and_send_beer_fact(message):
    try:
        # Specify the URL of the website to scan for "beer" content
        website_url = "https://facts.net/beer-facts/"  # Replace with the actual website URL

        # Send a message indicating that the bot is fetching a beer-related fact
        await message.channel.send("Fetching a random beer-related fact...")

        # Make a GET request to the website
        response = requests.get(website_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the website
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all paragraphs containing "beer" and store them in a list
            beer_facts = []
            for paragraph in soup.find_all('p'):
                if 'beer' in paragraph.get_text().lower():
                    beer_facts.append(paragraph.get_text())

            # Send a random beer-related fact to the Discord channel
            if beer_facts:
                random_fact = random.choice(beer_facts)
                await message.channel.send(random_fact)
            else:
                await message.channel.send("No beer-related content found on the website.")
        else:
            await message.channel.send("Failed to fetch content from the website.")
    except Exception as e:
        print(f"An error occurred while scraping a beer-related fact: {str(e)}")
        await message.channel.send("An error occurred while scraping a beer-related fact. Please try again later.")



# Function to scrape and send a random weed-related fact from a website
async def scrape_and_send_weed_fact(message):
    try:
        # Specify the URL of the website to scan for "beer" content
        website_url = "https://www.dixonwellnesscollective.com/facts-about-cannabis/101-facts-about-cannabis-in-2023"  # Replace with the actual website URL

        # Send a message indicating that the bot is fetching a beer-related fact
        await message.channel.send("Fetching a random weed-related fact...fucking stoner..")

        # Make a GET request to the website
        response = requests.get(website_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the website
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all paragraphs containing "beer" and store them in a list
            beer_facts = []
            for paragraph in soup.find_all('p'):
                if 'cannabis' in paragraph.get_text().lower():
                    beer_facts.append(paragraph.get_text())

            # Send a random beer-related fact to the Discord channel
            if beer_facts:
                random_fact = random.choice(beer_facts)
                await message.channel.send(random_fact)
            else:
                await message.channel.send("No beer-related content found on the website.")
        else:
            await message.channel.send("Failed to fetch content from the website.")
    except Exception as e:
        print(f"An error occurred while scraping a beer-related fact: {str(e)}")
        await message.channel.send("An error occurred while scraping a beer-related fact. Please try again later.")





def get_server_health():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent

    if cpu_usage < 70 and memory_usage < 70:
        return "Server is running smoothly."
    elif cpu_usage >= 70 and memory_usage >= 70:
        return "Server is experiencing high load, it may be slow."
    else:
        return "Server is under moderate load."
    


def count_lines_of_code(file_path):
    with open(file_path, 'r') as file:
        return sum(1 for line in file)










# Define content and command variables outside the on_message function
content = ""
command = ""


@bot.event
async def on_message(message):
    global content, command, conversation_history

    content = message.content
    command = content.split()[0][1:]












# Event Handlers
@bot.event
async def on_ready():
    """Event handler when the bot is ready."""
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    """Event handler for processing messages."""
    # Ignore messages from bots
    if message.author.bot:
        return

    # Check if the message starts with the prefix
    if message.content.startswith('!'):
        args = message.content[1:].split()
        command = args[0].lower()

        # Command processing
        if command == 'ping':
            await message.reply('pong')


        elif command == 'credits':
            await message.channel.send('void')


        elif command == 'contact':
            await message.channel.send('''Hello

If you wish to have a command added or feature, report a bot error or want to buy them prem version then here is my contacts
                                       
                                       
Discord: @iavd
Kik: @spicycheesedip''')


    
        elif command == 'dm':

            # Check if the author's username is in the allowed_usernames list
            if message.author.name not in allowed_usernames:
                await message.channel.send("You are not allowed to use this command, must buy my premium version.")
                return

            if len(message.mentions) > 0 and len(args) >= 3:
                user = message.mentions[0]
                dm_message = ' '.join(args[2:])
                await user.send(dm_message)
                await message.delete()
            else:
                await message.channel.send('Invalid usage. Use `!dm @user message`.')
        elif command == 'commands':
            # List of available commands
            command_list = '''Here are my current commands!
-----------------------------------------
!ping (see if bots online.) \n
            
!credits (see who made this bot.) \n

!contact (contact the creator.)

!uptime (see how long the bot has been online for.)\n

!server (check to see what server the bots on)\n
!restart (restart the bot, this will help fix blackjack and other commands giving errors or going slow!)
-----------------------------------------
            FUN COMMANDS
-----------------------------------------
!search --> Type: !search whatever_you_are_searching_for (NOTE: THIS WILL SEARCH EVERYWHERE AND SEND MULITPLE LINKS.) \n
!wipe (this wipes the server once.)\n
!meaning --> type: !meaning word to find out what the word means to screamBot!
 -----------------------------------------
            GAMES
-----------------------------------------
!blackjack --> Start a game of Blackjack.
-----------------------------------------
            FACTS
-----------------------------------------
!beer --> Get some random facts about beer.\n
!weed --> Get some random facts about weed.\n
!xal --> Learn about some cool strains of weed.(Thought of by xalyui TFG/L)\n
!uhistory --> Learn some cool unknown history.
-----------------------------------------
         SERVERS
-----------------------------------------
!minecraft --> Get a list of our mc servers
-----------------------------------------
other commands \n !commands2

            '''
            await message.channel.send(command_list)
        elif command == 'ip':
                        # Check if the author's username is in the allowed_usernames list
            if message.author.name not in allowed_usernames:
                await message.channel.send("You are not allowed to use this command, must buy my premium version.")
                return
            

            if len(args) == 2:
                ip_address = args[1]
                try:
                    response = requests.get(f'https://ipinfo.io/{ip_address}/json')
                    ip_info = response.json()
                    info_message = f"IP: {ip_info['ip']}\nHostname: {ip_info['hostname']}\nCity: {ip_info['city']}\nRegion: {ip_info['region']}\nCountry: {ip_info['country']}\nLocation: {ip_info['loc']}\nOrganization: {ip_info['org']}"

                    domain = whois.whois(ip_address)
                    whois_info = str(domain)

                    await message.channel.send(f"{info_message}\n\nWHOIS Info:\n```{whois_info}```")
                except Exception as e:
                    await message.channel.send(f"Error: {str(e)}")
            else:
                await message.channel.send('Invalid usage. Use `!ip <ip_address>`.')
        
        
        
        elif command == 'blackjack':
            await blackjack_game(message)



        elif command == 'spam':

                        # Check if the author's username is in the allowed_usernames list
            if message.author.name not in allowed_usernames:
                await message.channel.send("You are not allowed to use this command, must buy my premium version.")
                return
            

            await message.delete()
            if len(args) >= 4:
                target_user = message.mentions[0]
                text_to_send = ' '.join(args[2:-1])
                num_messages = int(args[-1])

                for i in range(num_messages):
                    await target_user.send(text_to_send)
                    if i < num_messages - 1:
                        await asyncio.sleep(3)  # Pause for 3 seconds between messages (except for the last message)
                    else:
                        await asyncio.sleep(3)  # Pause for 3 seconds before repeating (after sending all messages)

                    print(f"Sent {i+1}/{num_messages} messages.")
            else:
                await message.channel.send('Invalid usage. Use `!spam @user message num_messages`.')
        elif command == 'search':
            if len(args) >= 2:
                query = ' '.join(args[1:])
                search_url = f"https://www.google.com/search?q={query}"

                await message.channel.send(f"Searching for '{query}'...")

                try:
                    response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
                    response.raise_for_status()

                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Find all search results (links) in the search page
                    search_results = soup.find_all('a')
                    relevant_links = []

                    for result in search_results:
                        href = result.get('href')
                        if href and href.startswith('/url?q='):
                            # Extract the actual URL from the href attribute
                            url = href[7:].split('&')[0]

                            # Check if the URL is a valid website (you can add more checks if needed)
                            if url.startswith('http') or url.startswith('https'):
                                relevant_links.append(url)

                    if relevant_links:
                        for url in relevant_links:
                            await message.channel.send(f"Found a relevant link: {url}")

                            # Fetch and send the content of the website
                            try:
                                page_response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                                page_response.raise_for_status()
                                await message.channel.send(f"Content of {url}:\n```{page_response.text}```")
                            except Exception as e:
                                await message.channel.send(f"Error fetching content from {url}: {str(e)}")

                    else:
                        await message.channel.send("No relevant results found.")

                except Exception as e:
                    await message.channel.send(f"An error occurred while searching: {str(e)}")
        elif command == 'uptime':
            current_time = datetime.datetime.utcnow()
            if startup_time is not None:
                uptime_duration = current_time - startup_time
                await message.channel.send(f'I have been online for {uptime_duration}')
            else:
                await message.channel.send('Uptime information is not available yet.')
        elif command == 'prem':
            contact_info = '''
            PREM COMMANDS
-----------------------------------
            DISCORD SERVER
-----------------------------------
!delete --> type: !delete #channel (this will delete the channel you want.)

!delete_all --> type: !delete_all to delete all channels.

!swipe --> type: !swipe (this will spam wipe the channel with 5 wipes.)\n
!flood --> spam the server with random messages, to stop say !stop.
-----------------------------------
          FUCK WITH USERS
-----------------------------------
!dm --> Type: !dm @user message (this makes the bot private message whoever you want unless dms are off.)

!ip --> Type: !ip ip_address (tracks the ip and does a whois lookup.) \n
            
!spam --> Type: !spam @user message amount_to_send (this spams the user with however many messages you want.)
-----------------------------------
       XBOX HACKS
-----------------------------------
!ulitmateglitch --> this will teach you how to get ulimtate for $1 a month
----------------------------------- 
            '''
            await message.channel.send(contact_info)

        elif command == 'delete':
            # Check if the message has content
            if len(args) < 2:
                await message.channel.send("Please provide the name or mention of the channel to delete.")
                return

            # Check if the author's username is in the allowed_usernames list
            if message.author.name not in allowed_usernames:
                await message.channel.send("You are not allowed to use this command, must buy my premium version.")
                return

            # Extract the channel name or mention from the message content
            channel_arg = args[1].strip()  # Remove leading/trailing spaces

            # Check if the argument is a channel mention (e.g., #channel)
            if channel_arg.startswith("<#") and channel_arg.endswith(">"):
                # Extract the channel ID from the mention
                channel_id = int(channel_arg[2:-1])
                # Get the channel object using the ID
                channel = message.guild.get_channel(channel_id)
            else:
                # Try to find the channel by name
                channel = discord.utils.get(message.guild.channels, name=channel_arg)

            if channel:
                # Check if the user has the necessary permissions to delete the channel
                if message.author.guild_permissions.manage_channels:
                    try:
                        # Delete the channel
                        await channel.delete()
                        await message.channel.send(f"I successfully deleted {channel.name}")
                    except discord.Forbidden:
                        await message.channel.send(f"I don't have permission to delete {channel.name}")
                    except discord.HTTPException as e:
                        await message.channel.send(f"An error occurred while deleting {channel.name}: {e}")
                else:
                    await message.channel.send(f"You do not have permission to delete {channel.name}")
            else:
                await message.channel.send(f"Channel {channel_arg} not found")



        elif command == 'delete_all':
            # Check if the user's username or nickname is in the allowed_usernames list
            author_name = message.author.name.lower()
            author_nick = message.author.display_name.lower()

            if author_name in allowed_usernames or author_nick in allowed_usernames:
                for channel in message.guild.channels:
                    await channel.delete()
                await message.channel.send("All channels have been deleted.")
            else:
                await message.channel.send("You don't have permission to use this command.")

        elif command == 'wipe':
            message_content = "‎ \n" * 200
            await message.channel.send(message_content)


        
        elif command == 'swipe':
            author_name = message.author.name.lower()
            if author_name in allowed_usernames:
                message_content = "‎ \n" * 200
                for _ in range(10):
                    await message.channel.send(message_content)
            else:
                await message.channel.send("You are not allowed to use this command, must buy my premium version.")




        elif command == 'beer':
            await scrape_and_send_beer_fact(message)

        elif command == 'weed':
            await scrape_and_send_weed_fact(message)

        
        elif command == 'xal':
            responses = [
        "Hindu Kush,  A 100% pure indica that's popular with fans of high THC strains. After smoking or vaping Hindu Kush, expect mental calm and unfocused haziness followed by hours of couchlock and deep relaxation. Pure indica; landrace strain; 22-32% THC.",
        "Afghan Kush. A potent indica strain that's most likely to put you to sleep. The fruity aroma accompanies a lazy, sleepy sensation. 100% indica; landrace strain from the Hindu Kush mountain range; 21% THC, 6% CBD, 1% CBN.",
        "Purple Kush. This pure indica was named one of the Top 10 Most Powerful Strains in the World by High Times magazine. An aroma of earthy sweet grapes and red wine precedes a quick euphoric head high and deep body numbness, eventually leading to sleep. 100% indica; Hindu Kush x Purple Afghani; 22% THC.",
        "Master Kush. Two-time Cannabis Cup award winner and a favorite of Snoop Dogg, this is a powerful strain that boasts euphoria, total relaxation, and sleepiness. Aromas of sweet earth and citrus. 90% indica/10% sativa; Hindu Kush x a pure skunk strain; 20-24% THC, 1% CBD, 1% CBN.",
        "Banana Kush. A delicious, fruity-flavored kush that's often used for sleeping. Best taken one hour before bed. 60% indica/40% sativa; OG Kush x Skunk Haze; 18-25% THC, 1% CBN.",
        "Kosher Kush. Kosher Kush is a blissfully sleepy hybrid strain with long-lasting effects that calm the mind. This strain won the High Times Indica Cup twice and is the only cannabis strain to have been blessed by a rabbi! Warning: Go easy on this strain as an overdose could lead to blurred vision. 80-100% indica; unknown lineage; 22-25% THC.",
        "Granddaddy Purple. Granddaddy Purps is one of the most famous purple cannabis strains and also one of the most potent indicas. Expect powerful full-bodied relaxing effects and a euphoric numbness, potentially with trippy visions and always a profound sense of peace. 70% indica/30% sativa (indica-dominant hybrid); Big Bud x Purple Urkle; 20-27% THC, 1% CBD."
    ]
            random_response = random.choice(responses)
            await message.channel.send(random_response)

        elif command == 'uhistory':
            responses = [
        "1. Augustus Caesar was the wealthiest man to ever live in history. \n \n The nephew and heir of Julius Caesar, Roman Emperor Augustus, had an estimated net worth of $4.6 trillion when counting for inflation. Some say that Mansa Musa, king of Timbuktu, was the world’s wealthiest man as his wealth was apparently too great to count. However, Augustus’s staggering wealth could be measured.",
        "2. Alexander the Great was buried alive… accidentally. \n \n At age 32, when he died, Alexander the Great had conquered and created the largest land-based empire the world has ever seen. It stretched from the Balkans to Pakistan. In 323 BC, Alexander fell ill, and after 12 days of excruciating pain, he seemingly passed away. However, his corpse didn’t show any signs of rot or decomposition for a whole six days. Modern-day scientists believe Alexander suffered from the neurological disorder Guillain-Barré Syndrome. They believe that when he “died,” he was actually just paralyzed and mentally aware. Basically, he was horrifically buried alive!",
        "3. The world’s most successful pirate in history was a lady. \n \n Named Ching Shih, she was a prostitute in China. This was until the Commander of the Red Flag Fleet bought and married her. But rather than just viewing her as a wife, her husband considered her his equal, and she became an active pirate commander in the fleet. Ching Shih soon earned the respect of her fellow pirates. So much so that after her husband’s death, she became the captain of the fleet. Under Shih’s leadership, the Red Flag Fleet consisted of over 300 warships, with a possible 1,200 more support ships. She even had a possible 40,000 – 80,000 men, women, and children. They terrorized the waters around China. The Red Flag Fleet was such a fearsome band of raiders that the Chinese government eventually pardoned Ching Shih and her entire fleet – just to get them off the high seas!",
        "4. In the Ancient Olympics, athletes performed naked. \n \n The athletes did this to imitate the Gods but also to help them easily clear toxins from their skin through sweating after each attempt at a sport. In fact, the word “gymnastics” comes from the Ancient Greek words “gumnasía” (“athletic training, exercise”) and “gumnós” (“naked”). This translates as “to train naked.”",
        "5. Julius Caesar was stabbed 23 times. \n \nJulius Caesar is probably the most iconic name associated with the Romans. Likewise, his assassination and death are also highly notorious. Due to his coup d’état of the Roman Republic and his proclamation of himself as Dictator for Life, along with his radical political views, a group of his fellow Roman senators led by his best friend Brutus assassinated him on March 15, 44 BC. During the assassination, Caesar was stabbed at least 23 times before finally succumbing to his wounds. He passed away with fabled words to his former best friend Brutus, allegedly being, “you too, sweet child?”",
        "6. The Colosseum was originally clad entirely in marble. \n \nWhen you visit or see the Colosseum these days, you’ll notice how the stone exterior appears to be covered in pockmarks all across its surface. Whilst you might assume this is just a degradation of the material due to its age, it is actually because it was originally clad almost entirely in marble. The reason for the pockmarks is after the fall of Rome; the city was looted and pillaged by the Goths. Yes, that’s right, the Goths! They took all of the marble from the Colosseum and stripped it (mostly) down to its bare stone setting. The holes in the stone are from where the iron clamps and poles attaching the marble cladding to it have been ripped out.",
        "7. It was named the Colosseum because it was next to a statue called the Colossus \n \n It was originally known as the Amphitheatrum Flavium, or Flavian Amphitheatre, as it was constructed during the Flavian dynasty. Residents of Rome nicknamed it the Colosseo. This was due to the fact that it was built next to a 164-foot statue of Emperor Nero known as “the colossus of Nero.”",
        "8. There were female Gladiators. \n \n A female gladiator was called a Gladiatrix, or Gladiatrices (plural). They were rarer than their male counterparts. Gladiatrices served the same purpose of executing criminals, fighting each other, and fighting animals in Rome’s various fighting pits.",
        "9. The Vikings were the first Europeans to discover America. \n \n Half a millennium before Christopher Columbus “discovered” America, Viking chief Leif Eriksson of Greenland landed on the Island of Newfoundland in the year 1,000 AD.The Vikings under Leif Eriksson settled Newfoundland as well as discovering and settling Labrador further north in Canada.",
        "10. In Ancient Asia, death by elephant was a popular form of execution. \n \n As elephants are very intelligent and easy to train, it proved easy enough to train them as executioners and torturers.They could be taught to slowly break bones, crush skulls, twist off limbs, or even execute people using large blades fitted to their tusks. In some parts of Asia, this method of execution was still popular up to the late 19th Century.",
        "11. The UK government collected postcards as intelligence for the D-Day landings. \n \n Starting in 1942, the BBC issued a public appeal for postcards and photographs of mainland Europe’s coast, from Norway to the Pyrenees. This was an intelligence-gathering exercise. Initiated by Lieutenant General Frederick Morgan, he was searching for the hardest beaches to defend. The postcards were sent to the War Office and helped form part of the decision to choose Normandy as the location for the eventual D-Day landings.",
    ]
            random_response = random.choice(responses)
            await message.channel.send(random_response)


        elif command == 'meaning':
            word = message.content.split('!meaning ', 1)[1].strip()
            if word in dictionary:
                meaning = dictionary[word]
                await message.channel.send(f"Meaning of '{word}': {meaning}")
            else:
                await message.channel.send(f"'{word}' not found in the dictionary or you missspelt it, try with lowercases or upercases. for example if you tried dantdm it will give this error but if you do danTDM it won't, if it has no meaning though and you wanna give it a meaning then send --> !add_meaning word::meaning")



               
        elif command == 'add_meaning':
            command = message.content.split('!add_meaning ', 1)[1]
            word, meaning = command.split('::', 1)
            dictionary[word.strip()] = meaning.strip()
                
            with open('list.txt', 'a') as file:
                file.write(f'{word}::{meaning}\n')
                await message.channel.send(f"Added meaning for '{word}': {meaning}")



        elif command == 'minecraft':
            await message.channel.send('Hello, We are now introducing our official minecraft server! \n\n If you are wanting a server where you yourself can be apart of our supports and my commuinty, have a place to stay safe out from mobs, etc, join our server \n\n we are currently working on shops so people will be able to get iron or such quicker, this is gonna be sorta a earth smp server. \n\n Minecraft Java Server: ungreatfulsin.aternos.me \n\n Minecraft Bedrock server: Unfound.')

        elif command == 'watchmoviesfree':
            await message.channel.send('These are sites you can watch any movie/show for free on! \n\n Go movies!: https://gomovies.sx/ \n\n Soap2day: https://soap2day.ph/x45/')

        elif command == 'commands2':
            await message.channel.send('''
           services
--------------------------------
!watchmoviesfree --> Get a list of streaming services that let you watch tv for free!
--------------------------------
''')
            


        elif command == 'ulitmateglitch':
            author_name = message.author.name.lower()
            if author_name in allowed_usernames:
                await message.channel.send('''HOW TO GET ULIMATE FOR $1 EVERY TIME IT CHARGES YOU?
                                       
                                        simple.
                                       
Go to where you will buy ulimate, before paying for it make sure you are on the $1 option. Purchace it, now go to your subscriptions and make sure it's active. if it is, good. now remeber the date it says it exipres. a day before it exipires, cancel the subscription and then go back to ultimate, rebuy the $1 plan.''')

        elif command == 'server':
            host_name = socket.gethostname()
            host_ip = socket.gethostbyname(host_name)
            server_health = get_server_health()
            script_lines = count_lines_of_code(__file__)
            response = f'Server Name: {host_name} \nServer IP: {host_ip}. \nServer Health: {server_health}\nNumber of lines in the script: {script_lines}'
            await message.channel.send(response)


        elif command == 'flood':
            if message.author.name not in allowed_usernames:
                await message.channel.send("You are not allowed to use this command, must buy my premium version.")
                return
            stop_flooding = False

            async def flood_messages():
                nonlocal stop_flooding
                while not stop_flooding:
                    random_messages = ["hoe", "whore", "slut", "MADE BY VOID, GET FUCKED BITCH", "NOW LOGGING ALL IPS AND SENDING THEM TO USER WHOM USE COMMAND!", "9/11 was a inside job", "trans people are weird and should kill theirself"]
                    await message.channel.send(random.choice(random_messages))
                    await asyncio.sleep(1)
            # Start the flood_messages task
            bot.loop.create_task(flood_messages())

            # Check for the stop command
            while True:
                response = await bot.wait_for('message', check=lambda m: m.author == message.author)
                if response.content.lower() == '!stop':
                    stop_flooding = True
                    await message.channel.send('Stopping flood, Thank you for using our prem commands!')
                    break



        elif command == 'restart':
            os.execv(sys.executable, ['python'] + sys.argv)




startup_time = datetime.datetime.utcnow()







# Run the bot with your token
bot.run('MTE0MjMxMDg3NzE2MTMzMjgyNw.Gqi2Vu.07UpbKLoIQ2XHuJjhNcodRoKIjfJH2l6zsMlKY')

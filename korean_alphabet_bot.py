import discord
import random
import asyncio
import json
import quiz_settings

# create a file called token.txt and put your token in there.
# make sure it is in the same hierarchy as this file.
def get_token():
    with open('token.txt', 'r') as f:
        return f.readlines()[0].strip()

def get_korean_alphabet():
    with open('alphabet.json', encoding = 'utf-8') as f:
        data = json.load(f)
        return data

# you could turn these into generators, but I need the length of the
# lists when I pick a random value from them.
def get_alphabet_lists():
    korean_alphabet = get_korean_alphabet()
    ko , en = 'ko', 'en'
    initial = [(i[ko], i[en]) for i in korean_alphabet['initial_jamo']]
    medial = [(i[ko], i[en]) for i in korean_alphabet['medial_jamo']]
    final = [(i[ko], i[en]) for i in korean_alphabet['final_jamo']]
    return initial, medial, final


token = get_token()
initial_list, medial_list, final_list = get_alphabet_lists()
client = discord.Client()
is_quiz_active = False # global - not sure if it is good to do. still kind of new to python things
settings = quiz_settings.Settings()
BOT_COMMAND = '!'


@client.event
async def on_ready():
    print('Connected!')
    print(f'Username: {client.user.name} --- D: {client.user.id}')

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author.id == client.user.id:
        return

    if not message.content.startswith(BOT_COMMAND):
        print('*** does not start with bot command ***')
        return

    # when the user answers, we'll want to leave so we don't run the code below.
    # the get_user_guess should be receiving the message if quiz is active.
    if is_quiz_active:
        return

    # debug thingy
    print(f'''User: {message.author} typed {message.content} in channel {message.channel} ''')

    user_message = message.content[len(BOT_COMMAND):].lower().split()
    user_channel = message.channel
    if user_message[0] == 'q':
        await start_quiz(message)
    elif user_message[0] == 'mode':
        await settings.set_quiz_mode(BOT_COMMAND, user_channel, user_message)
    elif user_message[0] == 'timer':
        await settings.set_timer(BOT_COMMAND, user_channel, user_message)
    elif user_message[0] == 'block':
        await settings.set_block_size(BOT_COMMAND, user_channel, user_message)
    elif user_message[0] == 'word':
        await settings.set_num_of_words(BOT_COMMAND, user_channel, user_message)

#TODO:  reset settings to default, show vowels, show consonants, show commands

async def start_quiz(message):
    global is_quiz_active
    is_quiz_active = True
    korean, english, jamos = get_korean_word()
    question, answer = (korean, english) if settings.quiz_mode == settings.KO_MODE else (english, korean)

    await message.channel.send(f'What is {question}?')
    answer_reason_message = f'It is {answer}.\nReason: {jamos}'

    # prints to see if answer reason hits the over 2000 char limit
    print(len(answer_reason_message))

    try:
        # i don' really understand wait_for that much. tried doing this without 'message' and thought
        # i could call get_user_guess and pass a parameter to it, but it didn't work or something
        user_guess = await client.wait_for('message', check=get_user_guess, timeout=settings.answer_timer)
    except asyncio.TimeoutError:
        is_quiz_active = False
        return await message.channel.send(f'You took too long to answer.\n{answer_reason_message}')

    await is_guess_correct(message.channel, user_guess.content, answer, answer_reason_message)
    is_quiz_active = False



# it is not really a word, but a combo of the korean alphabet.
# so it is potentially a word, so potential bad words may arise ( ͡° ͜ʖ ͡°)
# This return the korean word as a string, the english romanization of the korean word as a string, and the jamos(initial, medial and final) as a list
# maybe i should split it into different functions but I think this is okay at the moment.
# Korean UNICODE formula thing is found from this site:
# http://www.programminginkorean.com/programming/hangul-in-unicode/composing-syllables-in-unicode/
# you can't use random.choice on the jamo lists because you need the index to compute the korean block formula
def get_korean_word():
    korean_word = english_roman = jamos = ''
    KO_IDX, EN_IDX = 0, 1  # korean, english (romanization)

    common_final_jamo_idx = [0,0,0,0,0,0,0,0,0,0,1,2,4,4,4,4,7,8,8,8,16,16,17,19,20,20,21,21,21,22,23,24,25,26,27]

    for x in range(settings.num_of_words):
        for not_used in range(settings.block_size):
            rand_init_idx = random.randint(0, len(initial_list)-1)
            rand_medial_idx = random.randint(0, len(medial_list)-1)
            rand_final_idx = random.choice(common_final_jamo_idx)#21 #random.randint(0, len(final_list)-1)

            initial_jamo = initial_list[rand_init_idx]
            medial_jamo = medial_list[rand_medial_idx]
            final_jamo = final_list[rand_final_idx]

            block = chr((rand_init_idx * 588) + (rand_medial_idx * 28) + rand_final_idx + 44032)
            korean_word += block
            english_roman += initial_jamo[EN_IDX] + medial_jamo[EN_IDX] + final_jamo[EN_IDX]

            jamo = ' , '.join( [f'{j[KO_IDX]} : {j[EN_IDX]}' for j in (initial_jamo, medial_jamo, final_jamo) if j[KO_IDX]] )
            jamos += f'( {block} => {jamo}  )\n'

        korean_word += ' '
        english_roman += ' '

    return korean_word, english_roman, jamos


def get_user_guess(m):
    # i don't know if calling lower() on korean characters changes it,
    # so I am checking if the content is the english alphabet
    user_guess = m.content.lower() if m.content.isalpha() else m.content
    return user_guess


async def is_guess_correct(channel, guess, answer, answer_reason_message):
    user_guess , bot_answer = guess.split(), answer.split()
    confirmation = 'Yes!' if user_guess == bot_answer else 'No!'
    return await channel.send(f'{confirmation}\n{answer_reason_message}')


client.run(token)

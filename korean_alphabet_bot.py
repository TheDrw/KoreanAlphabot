import discord
import random
import asyncio
import json
import quiz_settings

# notes :
# * the quiz will mess up on the first !q and say the user is wrong.
#       it is ok. it goes away after that and doesn't happen often....i think.
# * i added numbers, so this file name kind of doesn't make sense-ish.
#       it is the last part i wanted to put.
#       i guess korean basics could've been a good name? 몰라요 ¯\_(ツ)_/¯
# *

# create a file called token.txt and put your token in there.
# make sure it is in the same hierarchy as this file.
def get_token():
    with open('token.txt', 'r') as f:
        return f.readlines()[0].strip()

def get_korean_things_from_file():
    with open('alphabet.json', encoding = 'utf-8') as f:
        data = json.load(f)
        return data

def get_alphabet(korean_data):
    ko , en = 'ko', 'en'
    # you could turn these into generators, but I need the length of the
    # lists when I pick a random value from them.
    initial = [(i[ko], i[en]) for i in korean_data['initial_jamo']]
    medial = [(i[ko], i[en]) for i in korean_data['medial_jamo']]
    final = [(i[ko], i[en]) for i in korean_data['final_jamo']]

    return initial, medial, final

def get_vowels(korean_data):
    ko, en = 'ko', 'en'
    basic_vowels = '\n'.join(f'({i[ko]} : {i[en]})' for i in korean_data['basic vowels'])
    iotized_vowels = '\n'.join(f'({i[ko]} : {i[en]})'for i in korean_data['iotized vowels'])
    diphthongs = '\n'.join(f'({i[ko]} : {i[en]})' for i in korean_data['diphthongs'])

    all_vowels = f'''basic vowels: \n{basic_vowels} 
                \niotized vowels: \n{iotized_vowels}
                \ndiphthongs: \n{diphthongs}'''

    return all_vowels

def get_consonants(korean_data):
    ko, en = 'ko', 'en'
    basic_consonants = '\n'.join(f'({i[ko]} : {i[en]})' for i in korean_data['basic consonants'])
    aspirants = '\n'.join(f'({i[ko]} : {i[en]})' for i in korean_data['aspirants'])
    tense_consonants = '\n'.join(f'({i[ko]} : {i[en]})' for i in korean_data['tense consonants'])

    all_consonants = f'''basic consonants: \n{basic_consonants} 
                    \naspirants: \n{aspirants} 
                    \ntense_consonants: \n{tense_consonants} '''

    return all_consonants

def get_numbers(korean_data):
    num, pure, sino = 'num', 'pure', 'sino'
    nums = ''.join(f'{i[num]} : {sino} - {i[sino]}    {pure} - {i[pure]}\n' for i in korean_data['numbers'])
    return f'Sino and Pure Korean numbers from 1 to 10\n\n{nums}'

token = get_token()

korean_json_data = get_korean_things_from_file() # not sure if it is ok to cache this ¯\_(ツ)_/¯
initial_list, medial_list, final_list = get_alphabet(korean_json_data)
all_vowels = get_vowels(korean_json_data)
all_consonants = get_consonants(korean_json_data)
korean_numbers = get_numbers(korean_json_data)

client = discord.Client()

is_quiz_active = False # global - not sure if it is good to do. still kind of new to python things
settings = quiz_settings.Settings()
BOT_CMD = '!' # dash can be used but may be confusing when calling help

# common occurences (to my eyes and un-proven) of the final jamo.
# the number of times the value is in the array,
# is the probability it will get chosen by random.
# it represents the index of the final jamo list.
common_final_jamo_idx = [
    0,0,0,0,0,0,0,0,0,0,0,0,0,
    1,1,1,1,1,2,2,2,3,4,4,4,4,4,4,4,
    5,6,7,7,7,7,8,8,8,8,8,8,8,8,8,9,10,
    11,11,11,12,13,14,15,16,16,16,16,16,16,
    17,17,17,17,18,19,19,19,19,20,20,20,20,
    21,21,21,21,21,21,21,22,22,22,23,23,23,
    24,24,24,25,25,25,26,26,26,27,27,27
    ]

# not sure how necessary this dictionary is, but I think it is all right.
# i mainly have it so when i use it, i reference it anywher that needs it
# that way i don't have a misspelling bug and can't find it.
# I reference it in the help message and when message enters a command.
# when adding to the dictionary, try to keep the key ordered by alphabet to make it easier to check things.
# if you want to change the cmds, change the values and not the key.
cmds_dict = {
    'about' : 'about',
    'block' : 'block',
    'consonants' : 'consonants',
    'help': 'help',
    'nums' : 'nums',
    'mode' : 'mode',
    'quiz' : ('q','ㅂ'), # if in en to ko mode, it is easier to have the user choose 'ㅂ'
    'reset' : 'reset',
    'timer' : 'timer',
    'settings' : 'settings',
    'vowels' : 'vowels',
    'words' : 'words'
    }

@client.event
async def on_ready():
    print('Connected!')
    print(f'Username: {client.user.name} --- D: {client.user.id}')

    activity = discord.Activity(name=f'{BOT_CMD}{cmds_dict["help"]} for commands', type=discord.ActivityType.playing)
    await client.change_presence(activity = activity )

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author.id == client.user.id:
        return

    if not message.content.startswith(BOT_CMD):
        print('*** does not start with bot command ***')
        return

    # when the user answers, we'll want to leave so we don't run the code below.
    # the get_user_guess should be receiving the message if quiz is active.
    if is_quiz_active:
        return

    print(f'User: {message.author} typed {message.content} in channel {message.channel} ')

    user_message = message.content[len(BOT_CMD):].lower().split()
    if len(user_message) == 0:
        return

    user_channel = message.channel
    user_command = user_message[0]

    # order doesn't really matter, but it would help organizing it
    # in case if changes may arise
    if user_command in cmds_dict['quiz'] :
        await start_quiz(message)
    elif user_command == cmds_dict['mode']:
        await settings.set_quiz_mode(BOT_CMD, user_channel, user_message)
    elif user_command == cmds_dict['timer']:
        await settings.set_timer(BOT_CMD, user_channel, user_message)
    elif user_command == cmds_dict['block']:
        await settings.set_block_size(BOT_CMD, user_channel, user_message)
    elif user_command == cmds_dict['words']:
        await settings.set_num_of_words(BOT_CMD, user_channel, user_message)
    elif user_command == cmds_dict['vowels']:
        await show_vowels(user_channel)
    elif user_command == cmds_dict['consonants']:
        await show_consonants(user_channel)
    elif user_command == cmds_dict['reset']:
        await settings.reset_settings(user_channel)
    elif user_command == cmds_dict['settings']:
        await settings.show_settings(user_channel)
    elif user_command == cmds_dict['help']:
        await show_help(user_channel)
    elif user_command == cmds_dict['nums']:
        await show_numbers(user_channel)
    elif user_command == cmds_dict['about']:
        await show_about(user_channel)

async def show_help(channel):
    general_help_message = (
        f'<< These are the following commands >>\n\n'
        f'{BOT_CMD}{cmds_dict["quiz"][0]} or {BOT_CMD}{cmds_dict["quiz"][1]} - to start quiz\n'
        f'\n-- quiz settings --\n'
        f'{BOT_CMD}{cmds_dict["block"]} - change number of blocks per word.\n'
        f'{BOT_CMD}{cmds_dict["help"]} - show this help message again.\n'
        f'{BOT_CMD}{cmds_dict["mode"]} - switch answer modes.\n'
        f'{BOT_CMD}{cmds_dict["reset"]} - reset current settings.\n'
        f'{BOT_CMD}{cmds_dict["settings"]} - show current settings.\n'
        f'{BOT_CMD}{cmds_dict["timer"]} - change amount of time to answer.\n'
        f'{BOT_CMD}{cmds_dict["words"]} - change number of words.\n'
        f'\n-- alphabet -- \n'
        f'{BOT_CMD}{cmds_dict["consonants"]} - show Korean consonants.\n'
        f'{BOT_CMD}{cmds_dict["vowels"]} - show Korean vowels.\n'
        f'\n-- numbers -- \n'
        f'{BOT_CMD}{cmds_dict["nums"]} - show sino and pure Korean numbers from 1 to 10.\n'
        f'\n-- about -- \n'
        f'{BOT_CMD}{cmds_dict["about"]} - show lore about this bot.'
        )
    return await channel.send(general_help_message)

async def show_about(channel):
    msg = (
        f'Hello or 안녕하세요!\n\n'
        f'I am drw. Thank you for using my dumb bot. '
        f'This was built by me to help recognize Korean characters '
        f'by mashing up a bunch of Korean characters randomly into a "word". '
        f'The words it creates are not intended to be real words, '
        f'but in some cases they can be. Also, bad words may arise, '
        f'so sorry in advance! This bot is not the best, but it kind of works. '
        f'Anyways, I hope it helps you. Have fun and keep learning!\n\n'
        f'감사합니다!!'
    )
    return await channel.send(msg)

async def show_numbers(channel):
    return await channel.send(korean_numbers)

async def show_vowels(channel):
    return await channel.send(all_vowels)

async def show_consonants(channel):
    return await channel.send(all_consonants)

async def start_quiz(message):
    global is_quiz_active
    is_quiz_active = True
    korean, english, jamos = get_korean_word()
    question, answer = (korean, english) if settings.quiz_mode == quiz_settings.KO_MODE else (english, korean)

    await message.channel.send(f'What is {question}?')
    answer_reason_message = f'It is {answer}.\nReason: {jamos}'

    # prints to see if answer reason hits the over 2000 char limit
    #print(len(answer_reason_message))

    try:
        # i don't really understand wait_for that much. tried doing this without 'message' and thought
        # i could call get_user_guess and pass a parameter to it, but it didn't work or something
        user_guess = await client.wait_for('message', check=get_user_guess, timeout=settings.answer_timer)
    except asyncio.TimeoutError:
        is_quiz_active = False
        return await message.channel.send(f'You took too long to answer.\n{answer_reason_message}')

    await is_guess_correct(message.channel, user_guess.content, answer, answer_reason_message)
    is_quiz_active = False

# it is not really a word, but a combo of the korean alphabet.
# so it is potentially a word, so potential bad words may arise ( ͡° ͜ʖ ͡°)
# This return the korean word as a string, the english romanization of the korean word as a string,
# and the jamos(initial, medial and final) as a list
# maybe i should split it into different functions but I think this is okay at the moment.
# Korean UNICODE formula thing is found from this site:
# http://www.programminginkorean.com/programming/hangul-in-unicode/composing-syllables-in-unicode/
# you can't use random.choice on the jamo lists because you need the index to compute the korean block formula
def get_korean_word():
    korean_word = english_roman = jamos = ''
    KO_IDX, EN_IDX = 0, 1  # consts : korean, english (romanization)

    for not_used in range(settings.num_of_words):
        for not_used_either in range(settings.block_size):
            rand_init_idx = random.randint(0, len(initial_list)-1)
            rand_medial_idx = random.randint(0, len(medial_list)-1)
            rand_final_idx = random.choice(common_final_jamo_idx)

            init_jamo = initial_list[rand_init_idx]
            med_jamo = medial_list[rand_medial_idx]
            fin_jamo = final_list[rand_final_idx]

            block = chr((rand_init_idx * 588) + (rand_medial_idx * 28) + rand_final_idx + 44032)
            korean_word += block
            english_roman += init_jamo[EN_IDX] + med_jamo[EN_IDX] + fin_jamo[EN_IDX]

            jamo = ' , '.join((f'{j[KO_IDX]} : {j[EN_IDX]}' for j in (init_jamo, med_jamo, fin_jamo) if j[KO_IDX]))
            jamos += f'( {block} => {jamo}  )\n'

        # put a space after every block or 'word'
        korean_word += ' '
        english_roman += ' '

    # korean_word and english_roman add a space in the end of their loop,
    # so [:-1] will just pass back the string except that last space
    return korean_word[:-1], english_roman[:-1], jamos

def get_user_guess(m):
    return m.content

async def is_guess_correct(channel, guess, answer, answer_reason_message):
    user_guess , bot_answer = guess.lower().split(), answer.split()
    confirmation = 'Yes!' if user_guess == bot_answer else 'No!'
    return await channel.send(f'{confirmation}\n{answer_reason_message}')

client.run(token)
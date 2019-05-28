import re

class Settings:
    # consts - not to be modified by clients.
    # not sure if best to be here.
    KO_MODE, EN_MODE = 'ko', 'en'

    quiz_mode = KO_MODE  # quiz initially starts at 'ko' for korean
    answer_timer = 30.0  # amount of time given to answer
    block_size = 1
    num_of_words = 3


    # in user_message, it is split into a list, so you'll need to check if it contains more than one element
    # the 2nd element should contain the mode the user chooses.
    @classmethod
    async def set_quiz_mode(cls, bot_command, channel, user_message):
        korean_char, en_roman = 'Korean characters', 'English romanization'
        mode_help_message = f'Current mode is : {cls.quiz_mode}.\nTo change the mode, type:\n{bot_command}mode {cls.KO_MODE}\nfor the Korean quiz and you answer in {en_roman}, or\n!mode {cls.EN_MODE}\nfor the English quiz and you answer in {korean_char}.'
        if len(user_message) == 1:
            return await channel.send(mode_help_message)

        user_mode = user_message[1]
        if user_mode not in [cls.KO_MODE, cls.EN_MODE]:
            return await channel.send(f'Invalid mode!\n{mode_help_message}')

        cls.quiz_mode = user_mode
        quiz_in, answer_in = None, None
        if user_mode == cls.KO_MODE:
            quiz_in, answer_in = korean_char, en_roman
        elif user_mode == cls.EN_MODE:
            quiz_in, answer_in = en_roman, korean_char

        return await channel.send(f'Switching quiz mode to quiz in {quiz_in}. You will have to answer in {answer_in}.')



    # the user_message passes a list where [0] is teh command and [1] is the possible time message as strings.
    # if the len is 1, that means there's no time given in the message, so say the default message.
    # if len > 1, that means there's a possible time given, so we check if it is a number and if it is btwn [1,60]
    # i think the regex may be overkill, but i am using it because i am learning it.
    @classmethod
    async def set_timer(cls, bot_command, channel, user_message):
        MIN_TIMER, MAX_TIMER = 1, 60
        timer_help_message = f'Current timer is : {cls.answer_timer}.\nTo change the mode, type:\n{bot_command}timer {MIN_TIMER}-{MAX_TIMER}\n where {MIN_TIMER}-{MAX_TIMER} is from {MIN_TIMER} to {MAX_TIMER} seconds.'
        if len(user_message) == 1:
            return await channel.send(timer_help_message)

        user_time = user_message[1]
        CONTAINS_ONLY_TWO_DIGITS = re.match(r'^[\d]{1,2}$', user_time)
        if not CONTAINS_ONLY_TWO_DIGITS:
            return await channel.send(f'Invalid time! {timer_help_message}')

        user_time = int(user_time)
        if user_time < MIN_TIMER or user_time > MAX_TIMER:
            return await channel.send(f'Invalid time! {timer_help_message}')

        cls.answer_timer = user_time
        return await channel.send(f'Timer set to {user_time}')



    # block size max is 6. there's a 2000 char limit when replying. so if word size is 10 and this is 5, it reaches around ~1800 max.
    # the function is pretty much the same implementation as set_timer.
    @classmethod
    async def set_block_size(cls, bot_command, channel, user_message):
        MIN_BLOCK, MAX_BLOCK = 1, 5
        block_size_help_message = f'Current block size is : {cls.block_size}.\nTo change the block size, type:\n{bot_command}block {MIN_BLOCK}-{MAX_BLOCK}\n where {MIN_BLOCK}-{MAX_BLOCK} is a block size from {MIN_BLOCK} to {MAX_BLOCK}.'
        if len(user_message) == 1:
            return await channel.send(block_size_help_message)

        user_block_size = user_message[1]
        CONTAINS_ONLY_ONE_DIGIT = re.match(r'^[\d]{1}$', user_block_size)
        if not CONTAINS_ONLY_ONE_DIGIT:
            return await channel.send(f'Invalid block size! {block_size_help_message}')

        user_block_size = int(user_block_size)
        if user_block_size < MIN_BLOCK or user_block_size > MAX_BLOCK:
            return await channel.send(f'Invalid block size! {block_size_help_message}')

        cls.block_size = user_block_size
        return await channel.send(f'Block size set to {user_block_size}')



    # see set_timer for implementation details. it is pretty much the same
    @classmethod
    async def set_num_of_words(cls, bot_command, channel, user_message):
        MIN_WORDS, MAX_WORDS = 1, 10
        num_of_words_help_message = f'Current number of words: {cls.num_of_words}.\nTo change the number of words, type:\n{bot_command}words {MIN_WORDS}-{MAX_WORDS} where{MIN_WORDS}-{MAX_WORDS} is the number of words from {MIN_WORDS} to {MAX_WORDS}'
        if len(user_message) == 1:
            return await channel.send(num_of_words_help_message)

        user_num_of_words = user_message[1]
        CONTAINS_ONLY_TWO_DIGITS = re.match(r'^[\d]{1,2}$', user_num_of_words)
        if not CONTAINS_ONLY_TWO_DIGITS:
            return await channel.send(f'Invalid number of words! {num_of_words_help_message}')

        user_num_of_words = int(user_num_of_words)
        if user_num_of_words < MIN_WORDS or user_num_of_words > MAX_WORDS:
            return await channel.send(f'Invalid number of words! {num_of_words_help_message}')

        cls.num_of_words = user_num_of_words
        return await channel.send(f'Number of words set to {user_num_of_words}')

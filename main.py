
import os
import logging

from dotenv import load_dotenv
load_dotenv()

from config import MSG_SIZE, SPAM_LIMIT

from telethon import TelegramClient, events

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    level=logging.INFO
)

bot = TelegramClient(
    os.environ['SESSION_NAME'],
    os.environ['API_ID'],
    os.environ['API_HASH']
)


@bot.on(events.NewMessage(pattern='/help'))
async def help_cmd(event) -> None:
    logging.info(f'{event.sender_id=} called cmd=help in {event.chat_id=}')
    await event.respond('You have to add bot to group to use these commands below\n\n' \
                        '/all - call all group members (@all optionally)\n' \
                        '/spam - spams in chat, args: /spam <count> <message>\n\n' \
                        '/help - information about bot and developer\n\n' \
                        'Developer contacts: @Honey_Niisan')


@bot.on(events.NewMessage(pattern=r'/all'))
@bot.on(events.NewMessage(pattern=r'^@all$'))
async def all_cmd(event) -> None:
    logging.info(f'{event.sender_id=} called cmd=all in {event.chat_id=}')
    
    if event.is_group:
        members = await bot.get_participants(event.chat_id)
        members = [f'[⁬ඞ](tg://user?id={m.id})' for m in members if not m.is_self and not m.bot]
        
        for i in range(0, len(members), MSG_SIZE):
            text = ''.join(members[i:i + MSG_SIZE])
            await event.respond(text)

    elif event.is_private:
        await event.respond('Add me to group to use this command')


@bot.on(events.NewMessage(pattern='/spam'))
async def spam_cmd(event) -> None:
    logging.info(f'{event.sender_id=} called cmd=spam in {event.chat_id=}')

    if (event.is_private or event.is_channel) and not event.is_group:
        return await event.reply('Add me to group to use this command')
    
    args = event.text.split(maxsplit=2)[1:]
    if len(args) < 2:
        return await event.reply('Too few arguments!\nTry /spam <count> <message>')
    
    if not args[0].isnumeric():
        return await event.reply('<count> is not a number!\nTry again')
    
    if int(args[0]) < 1 or int(args[0]) > SPAM_LIMIT:
        return await event.reply(f'<count> should be between 1 and {SPAM_LIMIT}!\nTry again')

    for _ in range(int(args[0])):
        if event.reply_to is None:
            await bot.send_message(event.chat_id, args[1])            
        else:
            await bot.send_message(event.chat_id, args[1], reply_to=event.reply_to.reply_to_msg_id)


if __name__ == '__main__':
    logging.info('starting bot')
    bot.start(bot_token=os.environ['BOT_TOKEN'])
    bot.run_until_disconnected()

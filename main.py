import os
import disnake
from disnake.ext import commands

command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True
bot = commands.Bot(
    command_prefix='.',
    intents=disnake.Intents.all(),
    test_guilds=[767577186995011634],
    help_command=None,
    command_sync_flags=command_sync_flags
    )
# Когда бот готов
@bot.event
async def on_ready():
    print("Бот готов!")

#коги
for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')


bot.run("Bot_Token")

#обработка ошибок
@bot.event
async def on_command_error(inter, error):
    print(error)
    
    if isinstance(error, commands.MissingPermissions):
        await inter.send(f'{inter.author}, у вас недостаточно прав для выполнения этой команды')
    elif isinstance(error, commands.UserInputError):
        await inter.send(embed=disnake.Embed(
        description= f'Правильное использование команды: {inter.prefix}{inter.commdnd.name}({inter.command.brief})\nExample: {inter.prefix}{inter.command.usage}'))



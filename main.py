async def on_ready():
    print("Бот готов!")

#коги
for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
# Инициализация базы данных
conn = sqlite3.connect('C:\\Users\\Admin\\Desktop\\FunGame\\rps_rating.db')
cursor = conn.cursor()

# Создание таблицы, если она не существует
cursor.execute("""
CREATE TABLE IF NOT EXISTS rating (
    user_id INTEGER PRIMARY KEY,
    rating INTEGER
)
""")
conn.commit()

bot.run("Token")

#обработка ошибок
@bot.event
async def on_command_error(inter, error):
    print(error)
    
    if isinstance(error, commands.MissingPermissions):
        await inter.send(f'{inter.author}, у вас недостаточно прав для выполнения этой команды')
    elif isinstance(error, commands.UserInputError):
        await inter.send(embed=disnake.Embed(
        description= f'Правильное использование команды: {inter.prefix}{inter.commdnd.name}({inter.command.brief})\nExample: {inter.prefix}{inter.command.usage}'))



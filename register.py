import disnake
from disnake.ext import commands
import sqlite3

class RegisterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('C:\\Users\\Admin\\Desktop\\FunGame\\rps_rating.db')
        self.cursor = self.conn.cursor()

    @commands.slash_command(description='регистрация профиля')
    async def register(self, ctx):
        # Проверяем, что пользователь еще не зарегистрирован
        user_id = ctx.author.id
        self.cursor.execute("SELECT user_id FROM rating WHERE user_id=?", (user_id,))
        existing_user = self.cursor.fetchone()

        if existing_user:
            await ctx.send("Вы уже зарегистрированы.")
        else:
            # Добавляем нового пользователя в базу данных
            self.cursor.execute("INSERT INTO rating (user_id, rating) VALUES (?, ?)", (user_id, 100))
            self.conn.commit()
            await ctx.send("Вы успешно зарегистрированы с рейтингом 100.")

    @commands.slash_command(description='Получить профиль')
    async def profile(self, ctx):
        # Получить ID пользователя
        user_id = ctx.author.id

        # Проверяем, что пользователь зарегистрирован
        self.cursor.execute("SELECT user_id, rating FROM rating WHERE user_id=?", (user_id,))
        user_data = self.cursor.fetchone()

        if user_data:
            user_id, rating = user_data
            await ctx.send(f"Ваш ID: {user_id}\nВаш рейтинг: {rating}")
        else:
            await ctx.send("Вы не зарегистрированы. Используйте `/register`, чтобы зарегистрироваться.")
    
    @commands.slash_command(description='Топ 10 игроков')
    async def leaderboard(self, ctx):
        self.cursor.execute("SELECT user_id, rating FROM rating ORDER BY rating DESC LIMIT 10")
        leaderboard = self.cursor.fetchall()

        embed = disnake.Embed(title="Топ 10 игроков", description="", color=disnake.Color.blue())
        for i, (user_id, score) in enumerate(leaderboard, 1):
            member = await ctx.guild.fetch_member(user_id)
            embed.description += f"{i}. {member.mention} - {score} ммр\n"

        await ctx.send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(RegisterCog(bot))

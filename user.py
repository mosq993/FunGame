import disnake
from disnake.ext import commands


class UserInfo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description='тег и айди пользователя')
    async def user(inter):
        await inter.response.send_message(f"Ваш тег: {inter.author}\nВаш ID: {inter.author.id}")
    @commands.slash_command(description='Hello')
    async def hello(inter):
        await inter.response.send_message("World")
    @commands.slash_command(description='количество людей на сервере')
    async def server(inter):
        await inter.send(
            f"Название сервера: {inter.guild.name}\nВсего участников: {inter.guild.member_count}"
        )
    @commands.slash_command()
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        """Получить текущую задержку бота."""
        await inter.response.send_message(f"Понг! {round(self.bot.latency * 1000)}мс")
    @commands.slash_command()
    async def profile(self, inter: disnake.ApplicationCommandInteraction):
        """ответное сообщение"""
        await inter.response.send_message("Привет, ты используешь COGS")
def setup(bot: commands.Bot):
    bot.add_cog(UserInfo(bot))
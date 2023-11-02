import random
import disnake
from disnake.ext import commands
import asyncio

class RockPaperScissors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    @commands.command()
    async def start_game(self, ctx):
        # Проверяем, что автор команды находится в голосовом канале
        if ctx.author.voice is None:
            await ctx.send("Вы должны быть в голосовом канале для начала игры.")
            return

        # Проверяем, что уже нет запущенной игры
        if ctx.guild.id in self.games:
            await ctx.send("Игра уже запущена.")
            return

        # Проверяем, что в голосовом канале есть минимум 2 участника
        voice_channel = ctx.author.voice.channel
        if len(voice_channel.members) < 2:
            await ctx.send("В голосовом канале должно быть минимум два участника для начала игры.")
            return

        # Создаем встроенное сообщение с кнопкой о готовности
        embed = disnake.Embed(title="Готовы ли вы начать игру?", color=disnake.Color.green())
        embed.add_field(name="Инструкция", value="Нажмите на кнопку ✅, чтобы присоединиться к игре.")
        message = await ctx.send(embed=embed)

        # Добавляем реакцию-кнопку "Готов"
        await message.add_reaction("✅")

        # Сохраняем информацию о запущенной игре
        self.games[ctx.guild.id] = {
            "channel_id": ctx.channel.id,
            "voice_channel_id": voice_channel.id,
            "players": voice_channel.members,
            "message_id": message.id,
            "ready_players": [],
            "player_choices": {},
            "scores": {},
            "round": 1  # Инициализация раунда
        }

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Проверяем, что реакция была добавлена к сообщению готовности и реакцию добавил автор команды
        if reaction.emoji != "✅" or user == self.bot.user:
            return
            
        # Проверяем, что игра запущена в том же текстовом канале, где была добавлена реакция
        guild_id = reaction.message.guild.id
        if guild_id not in self.games or reaction.message.id != self.games[guild_id]["message_id"]:
            return
        
        # Проверяем, что игра еще не началась
        if len(self.games[guild_id]["ready_players"]) >= 2:
            return
        
        ctx = await self.bot.get_context(reaction.message)
        allowed_channel_id = 1168080942276026428  # Замените на ID разрешенного канала
        if ctx.channel.id != allowed_channel_id:
            await self.send("Вы не можете использовать эту команду в данном канале.")
            return
        
        # Добавляем игрока в список готовых
        self.games[guild_id]["ready_players"].append(user)

        # Обновляем встроенное сообщение с количеством готовых игроков
        embed = reaction.message.embeds[0]
        embed.title = f"Готовые игроки: ({len(self.games[guild_id]['ready_players'])}/2)"
        await reaction.message.edit(embed=embed)

        # Проверяем, если количество готовых игроков достигло 2
        if len(self.games[guild_id]["ready_players"]) == 2:
            await self.start_round(guild_id)

    async def start_round(self, guild_id):
        game_data = self.games[guild_id]
        channel = self.bot.get_channel(game_data["channel_id"])
        voice_channel = self.bot.get_channel(game_data["voice_channel_id"])

        # Удаляем встроенное сообщение о готовности
        message = await channel.fetch_message(game_data["message_id"])
        await message.delete()

        # Создаем индивидуальные текстовые каналы для игроков
        category_id = 1168080762415886357  # Замените на ID вашей категории
        category = self.bot.get_channel(category_id)

        if category:
            players = game_data["players"]
            player1, player2 = players[0], players[1]
            channel1 = await category.guild.create_text_channel(f"{player1.name}-game", category=category)
            channel2 = await category.guild.create_text_channel(f"{player2.name}-game", category=category)

            # Устанавливаем разрешения для текстовых каналов
            await channel1.set_permissions(player1, read_messages=True, send_messages=False)
            await channel1.set_permissions(player2, read_messages=False, send_messages=False)
            await channel2.set_permissions(player2, read_messages=True, send_messages=False)
            await channel2.set_permissions(player1, read_messages=False, send_messages=False)

            # Отправляем сообщение с кнопками для выбора игроков
            choice_msg = "Выберите предмет:"
            buttons = [
                disnake.ui.Button(style=disnake.ButtonStyle.primary, label="Камень", custom_id="choice_rock"),
                disnake.ui.Button(style=disnake.ButtonStyle.primary, label="Ножницы", custom_id="choice_scissors"),
                disnake.ui.Button(style=disnake.ButtonStyle.primary, label="Бумага", custom_id="choice_paper"),
            ]
            action_row = disnake.ui.ActionRow(*buttons)
            choice_message1 = await channel1.send(choice_msg, components=action_row)
            choice_message2 = await channel2.send(choice_msg, components=action_row)
        else:
            # Если категория не найдена
            print("Категория не найдена. Не удалось создать каналы.")

        def check_button(inter):
            return inter.message.id in (choice_message1.id, choice_message2.id) and inter.user in players

        try:
            # Wait for both players to make a choice using buttons
            for _ in range(2):
                interaction = await self.bot.wait_for("button_click", check=check_button, timeout=15)
                player_choice = interaction.component.custom_id  # Get the custom_id of the clicked button
                game_data["player_choices"][interaction.user.id] = player_choice
                await interaction.response.defer()  # Acknowledge the button click

            # Determine the winner based on choices
            player1_choice = game_data["player_choices"][player1.id]
            player2_choice = game_data["player_choices"][player2.id]

            result = self.determine_winner(player1_choice, player2_choice)
            if result == 1:
                winner = player1
                loser = player2
                game_data["round"] += 1
                game_data["scores"][player1.id] = game_data["scores"].get(player1.id, 0) + 1
            elif result == 2:
                winner = player2
                loser = player1
                game_data["round"] += 1
                game_data["scores"][player2.id] = game_data["scores"].get(player2.id, 0) + 1
            else:
                winner = None

            # Send the result message
            if winner is not None:
                winner_msg = f"{winner.mention} побеждает!"
            else:
                winner_msg = "Ничья!"
            await channel.send(winner_msg)

            # Удаляем индивидуальные текстовые каналы для игроков
            await channel1.delete()
            await channel2.delete()

            # Проверяем, окончена ли игра после этого раунда
            winner_id = max(game_data["scores"], key=game_data["scores"].get)
            winner_score = game_data["scores"][winner_id]
            if game_data["round"] >= 5 or winner_score >= 3 :
                del self.games[guild_id]
                final_embed = disnake.Embed(title="Игра завершена", color=disnake.Color.green())
                if "scores" in game_data:
                    winner_id = max(game_data["scores"], key=game_data["scores"].get)
                    loser_id = min(game_data["scores"], key=game_data["scores"].get)
                    winner = await channel.guild.fetch_member(int(winner_id))
                    loser = await channel.guild.fetch_member(int(loser_id))
                    winner_score = game_data["scores"][winner_id]
                    loser_score = game_data["scores"][loser_id]
                    final_embed.description = f"{winner.mention} победил со счетом {winner_score}:{loser_score} {loser.mention}"
                else:
                    final_embed.description = "Никто не победил. Игра завершена."
                message = await channel.send(embed=final_embed)
            else:
                # The game is not completed, proceed to start a new round
                game_data["ready_players"] = []

                # Создаем встроенное сообщение для нового раунда
                embed = disnake.Embed(title=f"Раунд ({game_data['round']}/5)", color=disnake.Color.blue())
                embed.add_field(name="Готовы ли вы начать игру?", value="Нажмите на кнопку 'Готов', чтобы присоединиться к игре.")
                message = await channel.send(embed=embed)

                # Сохраняем идентификатор сообщения с кнопкой
                game_data["message_id"] = message.id

                # Добавляем реакцию-кнопку "Готов"
                await message.add_reaction("✅")

        except asyncio.TimeoutError:
            await channel.send("Время на выбор истекло. Игра завершается.")
            del self.games[guild_id]

    def determine_winner(self, choice1, choice2):
        if choice1 == choice2:
            return 0
        elif (
            (choice1 == "choice_rock" and choice2 == "choice_scissors")
            or (choice1 == "choice_scissors" and choice2 == "choice_paper")
            or (choice1 == "choice_paper" and choice2 == "choice_rock")
        ):
            return 1
        else:
            return 2

def setup(bot: commands.Bot):
    bot.add_cog(RockPaperScissors(bot))
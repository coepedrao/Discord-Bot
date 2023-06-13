import discord
from discord.ext import commands
import json
from tmdbv3api import TMDb, Movie
import random
import asyncio
import datetime
from pytube import YouTube
import os

token = 'seu token'  
prefix = '!'  

intents = discord.Intents.default()
intents.members = True  
intents.message_content = True

bot = commands.Bot(command_prefix=prefix, intents=intents)
voice_client = None 

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')

    @bot.command()
async def play(ctx, url):
    global voice_client 

    try:
        video = YouTube(url)
        audio_stream = video.streams.filter(only_audio=True).first()
        audio_file = f'{video.video_id}.mp3'
        audio_stream.download(output_path='audio/', filename=audio_file)
        voice_channel = ctx.author.voice.channel
        voice_client = await voice_channel.connect()
        voice_client.play(discord.FFmpegPCMAudio(f'audio/{audio_file}'))

        await ctx.send(f'Che, puxei esse tango pra nós: {video.title}')
        
        while voice_client.is_playing():
            await asyncio.sleep(1)
        
        await voice_client.disconnect()

        os.remove(f'audio/{audio_file}')
    except Exception as e:
        print(f'Escreve direito loco: {str(e)}')

@bot.command()
async def stop(ctx):
    global voice_client  

    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send('Não ta sintonizando essa FM.')

@bot.command()
async def disconnect(ctx):
    global voice_client 

    if voice_client:
        await voice_client.disconnect()
        voice_client = None
        await ctx.send('Desconectado do canal de voz.')

tmdb = TMDb()
tmdb.api_key = 'key'
tmdb.language = 'pt-BR' 

@bot.command()
async def asordens(ctx):
    popular_movies = movie.popular()
    random_movie = random.choice(popular_movies)
    title = random_movie.title
    overview = random_movie.overview
    release_date = random_movie.release_date

    response = f"**{title}**\n\n*Sinopse:* {overview}\n*Lançamento:* {release_date}"
    await ctx.send(response)

movie = Movie()

moderadores = {
    'Moderador1': ['Redes sociais'],
    'Moderador2': ['Redes sociais'],
    'Moderador3': ['Redes sociais'],
    
}


@bot.command() 
async def contato(ctx, moderador):
    if moderador in moderadores:
        redes = moderadores[moderador]
        mensagem = f'Informações de {moderador}:\n'
        mensagem += '\n'.join(redes)
        await ctx.send(mensagem)
    else:
        await ctx.send('Home, escreve certo o nome dos cara.')


@bot.command()
@commands.has_permissions(manage_messages=True)
async def limpar(ctx, quantidade: int):
    if quantidade <= 0:
        await ctx.send('Por favor, forneça um número válido maior que zero.')
        return

    await ctx.channel.purge(limit=quantidade + 1)  

    await ctx.send(f'Qualquer brincadeira da gurizada foi completamente apagada')

player_data = {}

def carregar_dados():
    try:
        with open('dados.json', 'r') as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        return {}

def salvar_dados(dados):
    with open('dados.json', 'w') as arquivo:
        json.dump(dados, arquivo)

player_data = carregar_dados()

titulos = {
    1: "Gaúcho de Santa Catarina",
    2: "Guri de apartamento",
    3: "Maciu",
    4: "Guri de maneco",
    5: "Gauchinho que toma ximas em copo stanley",
    6: "Pouca bosta",
    7: "Carancho",
    8: "Atoa",
    9: "Taragui",
    10: "Sapucaiador",
    20: "Male",
    30: "Ginete",
    40: "Bitata",
    50: "Peleiador",
    60: "Taura",
    70: "Indião ticudo",
    80: "Indio veio",
    90: "Criado a pão com banha",
    100: "Gauchão",
}

@bot.command()
async def perfil(ctx):
    user = ctx.author
    if str(user.id) not in player_data:
        await ctx.send('Tu tem que ser parceiro da gurizada antes de se aparecer!')
        return

    xp = player_data[str(user.id)]['xp']
    level = player_data[str(user.id)]['level']
    coins = player_data[str(user.id)]['coins']

    titulo = titulos.get(level, "Desconhecido")  

    await ctx.send(f'Perfil de {user.name}: Nível {level} - {titulo}, XP: {xp}, Moedas: {coins}')

@bot.event
async def on_message(message):
    user = message.author
    if user.bot:
        return

    if str(user.id) not in player_data:
        player_data[str(user.id)] = {'xp': 0, 'level': 1, 'coins': 0}

    player_data[str(user.id)]['xp'] += 3

    if player_data[str(user.id)]['xp'] >= 50:
        player_data[str(user.id)]['xp'] = 0
        player_data[str(user.id)]['level'] += 1
        player_data[str(user.id)]['coins'] += player_data[str(user.id)]['level'] * 2

        titulo = titulos.get(player_data[str(user.id)]['level'], "Desconhecido")  
        await message.channel.send(f'Bota male {user.mention}! Feito, agora tu é um {titulo}!')

    salvar_dados(player_data)

    await bot.process_commands(message)

@bot.command()
async def pila(ctx):
    user = ctx.author
    if str(user.id) not in player_data:
        player_data[str(user.id)] = {'xp': 0, 'level': 1, 'coins': 0}

    today = datetime.date.today().strftime('%Y-%m-%d')
    if 'daily_coins' not in player_data[str(user.id)]:
        player_data[str(user.id)]['daily_coins'] = {'date': today, 'count': 0}

    if player_data[str(user.id)]['daily_coins']['date'] != today:
        player_data[str(user.id)]['daily_coins'] = {'date': today, 'count': 0}

    if player_data[str(user.id)]['daily_coins']['count'] >= 2:
        await ctx.send('Te liga, já tenteou demais!')
        return

    player_data[str(user.id)]['daily_coins']['count'] += 1
    player_data[str(user.id)]['coins'] += 2
    salvar_dados(player_data)

    await ctx.send(f'{user.mention}, Che, toma esses 2 pila! Agora te aquieta e só me chama amanhã.')

@bot.command()
async def doar(ctx, quantidade: int, membro: discord.Member):
    user = ctx.author
    if str(user.id) not in player_data:
        await ctx.send('Tu precisa ser chegado dos guri antes de fazer doações!')
        return

    if quantidade <= 0:
        await ctx.send('A quantidade dos pila tem que ser alta!')
        return

    if player_data[str(user.id)]['coins'] < quantidade:
        await ctx.send('Bah, tu ta mais pelado que eu!')
        return

    if str(membro.id) not in player_data:
        player_data[str(membro.id)] = {'xp': 0, 'level': 1, 'coins': 0}

    player_data[str(user.id)]['coins'] -= quantidade
    player_data[str(membro.id)]['coins'] += quantidade

    salvar_dados(player_data)

    await ctx.send(f'{user.name} fez um empréstimo de {quantidade} pra esse pelado {membro.name}!')


@bot.command()
async def desafiar(ctx, member: discord.Member, aposta: int):
    player1 = ctx.author
    player2 = member

    if player1 == player2:
        await ctx.send("Larga da banda!")
        return

    if aposta <= 0:
        await ctx.send("Bota todos pila na mesa!")
        return

    player1_coins = int(player_data.get(str(player1.id), {}).get('coins', 0))
    player2_coins = int(player_data.get(str(player2.id), {}).get('coins', 0))

    if aposta > player1_coins:
        await ctx.send("Com esse teus pila, tu não chega nem em maneco!")
        return

    if aposta > player2_coins:
        await ctx.send(f"{player2.mention} ta pelado, não tem nem aonde cair morto!")
        return

    await ctx.send(f"Dois guaipecas entraram numa peleia: {player1.mention} vs {player2.mention}.")
    await asyncio.sleep(3)  

    winner = random.choice([player1, player2])

    player_data[str(player1.id)]['coins'] -= aposta
    player_data[str(player2.id)]['coins'] -= aposta
    player_data[str(winner.id)]['coins'] += aposta * 2

    await ctx.send(f"{winner.mention} ganhou a pauleira e recebeu {aposta * 2} pilas!")

@bot.command()
async def buenas(ctx):
    await ctx.send('Cucurenas, indião!')

@bot.command()
async def comandos(ctx):
    await ctx.send('Che, por agora só temo esses aqui !play, !asordens, !contato, !perfil, !pila, !doar, !desafiar, !buenas e !comandos')

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel is not None:
        await channel.send(f'Buenas, taura {member.mention}!')

bot.run(token)

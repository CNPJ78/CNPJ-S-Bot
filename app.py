import discord
from discord import app_commands
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import logging.handlers
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

email_remetente = 'lucasgabrielinaciodes@gmail.com'
email_senha = 'tqrgchjkqvbfotsv'
smtp_servidor = 'smtp.gmail.com'
smtp_porta = 587



class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sincroniza
        await self.tree.sync()

bot = MyBot()

@bot.event
async def on_ready():
    print(f'O bot \033[2;32m{bot.user}\033[m está on-line')


@bot.tree.command(
        name='email',
        description='Envia uma mensagem e-mail pelo o bot.')
@app_commands.describe(
        para='E-mail de destino',
        assunto='Assunto do e-mail',
        mensagem='Mensagem do e-mail')
async def enviar_email(
        interaction: discord.Interaction,
        para: str,
        assunto: str,
        mensagem: str):
        await interaction.response.defer(thinking=True, ephemeral=True)

        try:
            msg = MIMEMultipart()
            msg['From'] = email_remetente
            msg['To'] = para
            msg['Subject'] = assunto

            msg.attach(MIMEText(mensagem, 'plain', 'utf-8'))

            server = smtplib.SMTP(smtp_servidor, smtp_porta)
            server.starttls()
            server.login(email_remetente, email_senha)
            server.send_message(msg)
            server.quit()

            await interaction.followup.send(
                    ' 📨 E-mail enviado com sucesso!',
                    ephemeral=True)
        except Exception as e:
                await interaction.followup.send(
                        f'🎈 Erro ao enviar e-mail:\n```{e}```',
                        ephemeral=True)

@bot.tree.command(name='ping', description='Teste de latência.')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('Pong 🏓!')

@bot.tree.command(name='adição', description='Faz a adição entre dois numeros e mostra a soma entre eles.')

@app_commands.describe(
        n1='Primeiro valor',
        n2='Segundo valor')
async def soma(
        interaction: discord.Interaction,
        n1: int,
        n2: int):
    await interaction.response.send_message(f'A soma de {n1} e {n2} é {n1 + n2}.', ephemeral=False)

@bot.tree.command(name='limpar', description='Apaga mensagens do canal atual.')
@app_commands.describe(quantidade='Número de mensagens para apagar (1 a 100)')
async def limpar(interaction: discord.Interaction, quantidade: int):
    # Verifica permissão
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message('Você nao tem permissão para usar este comando.', ephemeral=True)
        return
    # Validacão de quantidade
    if quantidade < 1 or quantidade > 100:
        await interaction.response.send_message('O número deve estar entre 1 e 100.', ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)

    # Apagar mensagens
    canal = interaction.channel
    apagadas = await canal.purge(limit=quantidade)

    await interaction.followup.send(f'Foram apagadas {len(apagadas)} mensagens.', ephemeral=True)


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
        encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Assume client refers to a discord.Client subclass...
# Suppress the default configuration since we have our own
bot.run(TOKEN, log_handler=None)

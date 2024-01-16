import discord
from discord.ext import commands
import mysql.connector

TOKEN = 'TOKEN'
DB_HOST = 'host'
DB_USER = 'user'
DB_PASSWORD = 'password'
DB_NAME = 'vagos'

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='+', intents=intents)
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        item_id INT AUTO_INCREMENT PRIMARY KEY,
        item_name VARCHAR(255) NOT NULL
    )
''')
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS coffre (
        item_name VARCHAR(255) PRIMARY KEY,
        quantity INT NOT NULL
    )
''')
conn.commit()

coffre_channel_id = channel_id

async def update_coffre_message():
    channel = bot.get_channel(coffre_channel_id)
    if channel:
        cursor.execute('SELECT * FROM coffre WHERE quantity > 0')
        items = cursor.fetchall()

        if not items:
            await channel.send('Le coffre est vide.')
            return

        embed = discord.Embed(title='Coffre', color=0xFFA500)

        for item in items:
            embed.add_field(name=item[0], value=f"QuantitÃ©: {item[1]}", inline=False)

        async for message in channel.history(limit=100):
            if message.author == bot.user:
                await message.edit(embed=embed)
                return

        await channel.send(embed=embed)

@bot.command(name='add')
@commands.has_permissions(administrator=True)
async def add_item(ctx, *, item_name):
    cursor.execute('SELECT item_name FROM items WHERE item_name = %s', (item_name,))
    item_exists = cursor.fetchone()

    if item_exists:
        await ctx.send(f"L'item {item_name} existe dÃ©jÃ  dans la base de donnÃ©es.")
    else:
        cursor.execute('INSERT INTO items (item_name) VALUES (%s)', (item_name,))
        conn.commit()
        await ctx.send(f'Item ajoutÃ© Ã  la base de donnÃ©es : {item_name}')
        await update_coffre_message()

@bot.command(name='ajouter')
async def ajouter_item(ctx, item_name, quantity: int):
    cursor.execute('SELECT item_name FROM items WHERE item_name = %s', (item_name,))
    item_exists = cursor.fetchone()

    if item_exists:
        cursor.execute('INSERT INTO coffre (item_name, quantity) VALUES (%s, %s) ON DUPLICATE KEY UPDATE quantity = quantity + %s', (item_name, quantity, quantity))
        conn.commit()
        await ctx.send(f'Item ajoutÃ© au coffre : {item_name} (QuantitÃ©: {quantity})')
        await update_coffre_message()
    else:
        await ctx.send(f"L'item {item_name} n'existe pas dans la base de donnÃ©es.")

@bot.command(name='supprimer')
async def supprimer_item(ctx, item_name, quantity: int):
    cursor.execute('UPDATE coffre SET quantity = GREATEST(quantity - %s, 0) WHERE item_name = %s', (quantity, item_name))
    conn.commit()
    await ctx.send(f'Item supprimÃ© du coffre : {item_name} (QuantitÃ©: {quantity})')
    await update_coffre_message()

@bot.command(name='liste')
async def stockage(ctx):
    cursor.execute('SELECT item_name FROM items')
    items = cursor.fetchall()

    if not items:
        await ctx.send('Aucun item trouvÃ© dans la base de donnÃ©es.')
        return

    embed = discord.Embed(title='Liste des items', color=0xFFA500)

    item_list = "\n".join([f"{index + 1}. {item[0]}" for index, item in enumerate(items)])
    embed.add_field(name='Items', value=item_list, inline=False)

    await ctx.send(embed=embed)

bot.run(TOKEN)

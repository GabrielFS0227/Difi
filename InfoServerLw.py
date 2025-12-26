import discord
from discord import app_commands
import aiohttp
import asyncio

class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()
URL_API = "https://servers.realitymod.com/api/ServerInfo"
URL_MAP_GALLERY = "https://mapgallery.realitymod.com/maps/"

def format_game_mode(mode):
    modes = {
        "gpm_cq": "AAS",
        "gpm_insurgency": "INS",
        "gpm_vehicles": "Vehicle Warfare",
        "gpm_skirmish": "Skirmish",
        "gpm_coop": "Co-Operative"
    }
    return modes.get(mode.lower(), mode)

def get_map_image_url(map_name):
    """
    Traduz o nome do mapa da API para o diretório correto no MapGallery.
    """
    # Dicionário de tradução (API Name -> Folder Name no site)
    # Adicione novos mapas aqui seguindo o padrão do site
    map_translation = {
        "Muttrah City": "muttrah_city_2",
        "Beirut": "beirut",
        "Operation Falcon": "operation_falcon",
        "Asad Khal": "asad_khal",
        "Kashan Desert": "kashan_desert",
        "Kozelsk": "kozelsk",
        "Sahel": "sahel",
        "Silent Eagle": "silent_eagle",
        "Fools Road": "fools_road",
        "Gaza": "gaza_2",
        "Hades Peak": "hades_peak",
        "Nuijamaa": "nuijamaa",
        "Pavlovsk Bay": "pavlovsk_bay",
        "Ramiel": "ramiel",
        "_3km_kandagal": "kandagal"
    }

    # Se o mapa estiver no dicionário, usa o nome traduzido. 
    # Se não, tenta o padrão: minúsculo com underline.
    folder_name = map_translation.get(map_name)
    
    if not folder_name:
        folder_name = map_name.lower().replace(" ", "_")

    return f"{URL_MAP_GALLERY}{folder_name}/map.jpg"

def get_flag_emoji(country_code):
    if not country_code or country_code == "N/A":
        return "🌐"
    return f":flag_{country_code.lower()}:"

@bot.event
async def on_ready():
    print(f'Sistemas integrados. Bot: {bot.user}')

@bot.tree.command(name="servidores", description="Lista os servidores ativos com fotos dos mapas")
async def servidores(interaction: discord.Interaction):
    await interaction.response.defer()

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(URL_API, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    print(data)
                    servers = data.get("servers", [])

                    if not servers:
                        return await interaction.followup.send("Nenhum servidor encontrado.")

                    servers.sort(key=lambda x: int(x.get("properties", {}).get("numplayers", 0)), reverse=True)

                    embeds = []
                    # Limitado aos 5 primeiros para evitar spam
                    for server in servers[:5]:
                        props = server.get("properties", {})
                        
                        name = props.get("hostname", "Unknown Server")
                        map_name = props.get("mapname", "N/A")
                        players = props.get("numplayers", "0")
                        max_p = props.get("maxplayers", "0")
                        mode = format_game_mode(props.get("gametype", ""))
                        flag = get_flag_emoji(props.get("countrycode", ""))

                        embed = discord.Embed(
                            title=f"{flag} {name}",
                            color=0x2b2d31
                        )
                        
                        embed.add_field(name="🗺️ Mapa", value=f"`{map_name}`", inline=True)
                        embed.add_field(name="🕹️ Modo", value=f"`{mode}`", inline=True)
                        embed.add_field(name="👤 Jogadores", value=f"`{players}/{max_p}`", inline=True)
                        
                        # Gera a URL da imagem e aplica no embed
                        image_url = get_map_image_url(map_name)
                        embed.set_image(url=image_url)
                        
                        embeds.append(embed)

                    await interaction.followup.send(embeds=embeds)
                else:
                    raise Exception("Erro na API")

        except Exception as e:
            print(f"Erro detectado: {e}")
            error_embed = discord.Embed(
                title="📡 Status of the INDEV World Connections Server",
                description="🔴 **Server offline or unreachable.**\n\n**Erro**\n`timed out`",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=error_embed)

# Utilize seu Token abaixo
bot.run('token test by iury')
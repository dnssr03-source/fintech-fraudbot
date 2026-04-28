import discord
import anthropic
import os
import asyncio
import json
from datetime import datetime
import urllib.request
import urllib.parse

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
NEWS_API_KEY = os.environ["NEWS_API_KEY"]
CANAL_NOTICIAS_ID = int(os.environ["CANAL_NOTICIAS_ID"])

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def buscar_noticias():
    queries = [
        "financial fraud detection machine learning",
        "fraude financeira digital",
        "payment fraud fintech"
    ]
    artigos = []
    for query in queries:
        params = urllib.parse.urlencode({
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 3,
            "apiKey": NEWS_API_KEY
        })
        url = f"https://newsapi.org/v2/everything?{params}"
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                data = json.loads(r.read())
                if data.get("articles"):
                    artigos.extend(data["articles"][:3])
        except Exception as e:
            print(f"Erro ao buscar notícias para '{query}': {e}")
    return artigos[:6]

def resumir_noticia(titulo, descricao, url):
    prompt = f"""És o assistente de um projeto académico sobre Deteção de Fraude em Transações Financeiras com Machine Learning na Coimbra Business School.

Escreve um resumo curto (máximo 3 frases) desta notícia, em português europeu, destacando a sua relevância para o tema de fraude financeira e machine learning. Sê direto e informativo.

Título: {titulo}
Descrição: {descricao}
URL: {url}

Formato da resposta:
RESUMO: [3 frases máximo]
RELEVÂNCIA: [1 frase ligando ao projeto]"""

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"Não foi possível gerar resumo: {e}"

async def publicar_noticias():
    await client.wait_until_ready()
    canal = client.get_channel(CANAL_NOTICIAS_ID)
    if not canal:
        print(f"Erro: Canal com ID {CANAL_NOTICIAS_ID} não encontrado.")
        return

    while not client.is_closed():
        try:
            now = datetime.now()
            print(f"[{now.strftime('%H:%M')}] A verificar notícias...")
            artigos = buscar_noticias()

            if artigos:
                embed_intro = discord.Embed(
                    title="📰 Atualização Diária — Fraude Financeira & ML",
                    description=f"Notícias relevantes para o projeto • {now.strftime('%d/%m/%Y às %H:%M')}",
                    color=discord.Color.dark_blue()
                )
                await canal.send(embed=embed_intro)

                for artigo in artigos[:4]:
                    titulo = artigo.get("title", "Sem título")
                    descricao = artigo.get("description", "") or artigo.get("content", "") or "Sem descrição disponível."
                    url_artigo = artigo.get("url", "")
                    fonte = artigo.get("source", {}).get("name", "Fonte desconhecida")
                    imagem = artigo.get("urlToImage", None)

                    resumo_texto = resumir_noticia(titulo, descricao[:500], url_artigo)

                    embed = discord.Embed(
                        title=titulo[:250],
                        url=url_artigo,
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="Resumo IA", value=resumo_texto[:1000], inline=False)
                    embed.set_footer(text=f"Fonte: {fonte}")
                    if imagem:
                        embed.set_thumbnail(url=imagem)

                    await canal.send(embed=embed)
                    await asyncio.sleep(2)

                embed_fim = discord.Embed(
                    description="*Resumos gerados automaticamente pelo Claude Sonnet 4.6 (Anthropic) • Projeto FinTech CBS 2025/2026*",
                    color=discord.Color.dark_grey()
                )
                await canal.send(embed=embed_fim)

        except Exception as e:
            print(f"Erro no ciclo de notícias: {e}")

        # Aguarda 24 horas até à próxima publicação
        await asyncio.sleep(24 * 60 * 60)

@client.event
async def on_ready():
    print(f"Bot de notícias ligado como {client.user}")
    client.loop.create_task(publicar_noticias())

client.run(DISCORD_TOKEN)

import discord
import os
import asyncio
import xml.etree.ElementTree as ET
import urllib.request
from datetime import datetime, timezone
import html
import re

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
CANAL_NOTICIAS_ID = int(os.environ["CANAL_NOTICIAS_ID"])

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# ─────────────────────────────────────────────────────────────
# FONTES RSS GRATUITAS — sem necessidade de API paga
# ─────────────────────────────────────────────────────────────

RSS_FEEDS = [
    {
        "nome": "KrebsOnSecurity",
        "url": "https://krebsonsecurity.com/feed/",
        "emoji": "🔐"
    },
    {
        "nome": "Fraud Magazine (ACFE)",
        "url": "https://www.fraud-magazine.com/rss.xml",
        "emoji": "🏦"
    },
    {
        "nome": "Finextra — Fraud",
        "url": "https://www.finextra.com/rss/rssfeeds.aspx?section=fraud",
        "emoji": "💳"
    },
    {
        "nome": "The Paypers",
        "url": "https://thepaypers.com/rss/all",
        "emoji": "💰"
    },
    {
        "nome": "Google News — Financial Fraud",
        "url": "https://news.google.com/rss/search?q=financial+fraud+machine+learning&hl=en&gl=US&ceid=US:en",
        "emoji": "📰"
    },
    {
        "nome": "Google News — Fraude Financeira",
        "url": "https://news.google.com/rss/search?q=fraude+financeira+detecao&hl=pt&gl=PT&ceid=PT:pt",
        "emoji": "🇵🇹"
    }
]

KEYWORDS_RELEVANTES = [
    "fraud", "fraude", "machine learning", "fintech", "payment",
    "detection", "deteção", "financial", "financeiro", "scam",
    "phishing", "cybercrime", "banking", "transaction", "transação",
    "artificial intelligence", "inteligência artificial", "data",
    "credit card", "cartão", "chargeback", "money laundering"
]

def limpar_html(texto):
    if not texto:
        return ""
    texto = html.unescape(texto)
    texto = re.sub(r'<[^>]+>', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto[:400] + "..." if len(texto) > 400 else texto

def e_relevante(titulo, descricao):
    texto = (titulo + " " + (descricao or "")).lower()
    return any(kw.lower() in texto for kw in KEYWORDS_RELEVANTES)

def buscar_rss(url):
    artigos = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            conteudo = r.read()
        root = ET.fromstring(conteudo)
        channel = root.find("channel")
        if channel is None:
            return []
        items = channel.findall("item")[:5]
        for item in items:
            titulo = limpar_html(item.findtext("title", ""))
            descricao = limpar_html(item.findtext("description", ""))
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")
            if titulo and e_relevante(titulo, descricao):
                artigos.append({
                    "titulo": titulo,
                    "descricao": descricao,
                    "link": link,
                    "data": pub_date
                })
    except Exception as e:
        print(f"Erro ao ler RSS {url}: {e}")
    return artigos

def gerar_resumo_local(titulo, descricao):
    titulo_lower = titulo.lower()
    descricao_lower = (descricao or "").lower()
    texto = titulo_lower + " " + descricao_lower

    if "machine learning" in texto or "ai" in texto or "artificial intelligence" in texto or "inteligência artificial" in texto:
        contexto = "Relevante para a Skill 2 e o Agente IA do projeto — demonstra aplicações reais de ML na deteção de fraude."
    elif "regulation" in texto or "regulação" in texto or "psd2" in texto or "gdpr" in texto or "rgpd" in texto or "dora" in texto:
        contexto = "Diretamente relacionado com o quadro regulatório abordado na revisão de literatura (Skill 1)."
    elif "phishing" in texto or "account takeover" in texto or "credential" in texto:
        contexto = "Illustra a tipologia Account Takeover (ATO) estudada na revisão de literatura."
    elif "card" in texto or "payment" in texto or "cartão" in texto or "pagamento" in texto:
        contexto = "Relacionado com fraude card-not-present (CNP), o tipo mais prevalente no dataset utilizado."
    elif "money laundering" in texto or "lavagem" in texto:
        contexto = "Relacionado com lavagem de dinheiro, uma das tipologias de fraude estudadas no projeto."
    elif "bank" in texto or "banco" in texto or "financial" in texto or "financeiro" in texto:
        contexto = "Contexto de fraude no setor bancário, diretamente relevante para o projeto."
    else:
        contexto = "Notícia relevante sobre fraude financeira e segurança digital no setor Fintech."

    return contexto

async def publicar_noticias():
    await client.wait_until_ready()
    canal = client.get_channel(CANAL_NOTICIAS_ID)

    if not canal:
        print(f"❌ Canal {CANAL_NOTICIAS_ID} não encontrado.")
        return

    while not client.is_closed():
        try:
            now = datetime.now()
            print(f"[{now.strftime('%H:%M')}] A recolher notícias via RSS...")

            todos_artigos = []
            for feed in RSS_FEEDS:
                artigos = buscar_rss(feed["url"])
                for a in artigos:
                    a["fonte_nome"] = feed["nome"]
                    a["fonte_emoji"] = feed["emoji"]
                todos_artigos.extend(artigos)

            # Remove duplicados por título
            vistos = set()
            artigos_unicos = []
            for a in todos_artigos:
                chave = a["titulo"][:60].lower()
                if chave not in vistos:
                    vistos.add(chave)
                    artigos_unicos.append(a)

            artigos_final = artigos_unicos[:5]

            if artigos_final:
                embed_intro = discord.Embed(
                    title="📰 Atualização Diária — Fraude Financeira & FinTech",
                    description=(
                        f"**{len(artigos_final)} notícias relevantes** para o projeto • "
                        f"{now.strftime('%d/%m/%Y às %H:%M')}\n"
                        f"*Recolhidas automaticamente de fontes especializadas em fraude financeira*"
                    ),
                    color=discord.Color.dark_blue()
                )
                await canal.send(embed=embed_intro)

                for artigo in artigos_final:
                    resumo_contexto = gerar_resumo_local(artigo["titulo"], artigo["descricao"])

                    embed = discord.Embed(
                        title=artigo["titulo"][:250],
                        url=artigo["link"] if artigo["link"] else None,
                        color=discord.Color.blue()
                    )
                    if artigo["descricao"]:
                        embed.add_field(
                            name="Resumo",
                            value=artigo["descricao"][:500],
                            inline=False
                        )
                    embed.add_field(
                        name="🎓 Relevância para o Projeto",
                        value=resumo_contexto,
                        inline=False
                    )
                    embed.set_footer(
                        text=f"{artigo['fonte_emoji']} {artigo['fonte_nome']}"
                        + (f" • {artigo['data'][:22]}" if artigo.get('data') else "")
                    )
                    await canal.send(embed=embed)
                    await asyncio.sleep(2)

                embed_fim = discord.Embed(
                    description=(
                        f"*Notícias recolhidas automaticamente via RSS • "
                        f"Projeto FinTech — Deteção de Fraude com ML • CBS 2025/2026*"
                    ),
                    color=discord.Color.dark_grey()
                )
                await canal.send(embed=embed_fim)
                print(f"✅ {len(artigos_final)} notícias publicadas com sucesso.")
            else:
                print("⚠️ Nenhuma notícia relevante encontrada desta vez.")

        except Exception as e:
            print(f"❌ Erro no ciclo de notícias: {e}")

        # Aguarda 24 horas
        await asyncio.sleep(24 * 60 * 60)

@client.event
async def on_ready():
    print(f"✅ Bot 3 (Notícias) ligado como {client.user}")
    client.loop.create_task(publicar_noticias())

client.run(DISCORD_TOKEN)

import discord
from discord import app_commands
import anthropic
import os
import json

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot ligado como {client.user}")

@tree.command(name="analisar", description="Analisa uma transação e deteta se é fraudulenta")
@app_commands.describe(
    valor="Valor da transação em dólares (ex: 45.50)",
    horas_registo="Horas desde o registo até à compra (ex: 0.003 = 10 segundos)",
    dispositivo_partilhado="Dispositivo partilhado por vários utilizadores? (sim/nao)",
    canal="Canal de aquisição: SEO, Ads ou Direct",
    pais="País de origem da transação",
    idade="Idade do utilizador",
    browser="Browser utilizado (Chrome, Firefox, Safari, IE, Opera)"
)
async def analisar(
    interaction: discord.Interaction,
    valor: float,
    horas_registo: float,
    dispositivo_partilhado: str,
    canal: str,
    pais: str,
    idade: int,
    browser: str
):
    await interaction.response.defer(thinking=True)

    if horas_registo < 0.017:
        tempo_label = f"{horas_registo * 3600:.0f} segundos"
    elif horas_registo < 1:
        tempo_label = f"{horas_registo * 60:.0f} minutos"
    elif horas_registo < 24:
        tempo_label = f"{horas_registo:.1f} horas"
    else:
        tempo_label = f"{horas_registo / 24:.1f} dias"

    prompt = f"""És um agente especializado em deteção de fraude em transações de e-commerce.
Analisa a seguinte transação com base nos padrões identificados na análise exploratória do dataset Fraud E-Commerce (Kaggle, 151.112 transações, 9.4% fraudes).

DADOS DA TRANSAÇÃO:
- Valor: ${valor}
- Tempo desde registo até compra: {tempo_label} ({horas_registo} horas)
- Dispositivo partilhado: {dispositivo_partilhado}
- Canal de aquisição: {canal}
- País: {pais}
- Idade: {idade} anos
- Browser: {browser}

PADRÕES CHAVE DA EDA:
1. Transações <1h após registo: 99.5% são fraudulentas (mediana legítima ~60 dias, fraudulenta ~1 segundo)
2. Dispositivo partilhado: 52.5% de fraude vs 3.0% em dispositivo único
3. Valor: NÃO é preditor — médias idênticas ($36.93 vs $36.99)
4. Canal Direct tem taxa ligeiramente maior (10.54%)

Responde APENAS em JSON válido sem texto adicional:
{{
  "classificacao": "FRAUDULENTA" ou "LEGITIMA",
  "confianca": "Muito Alta (>95%)" ou "Alta (>85%)" ou "Média (>70%)" ou "Baixa (<70%)",
  "fatores": ["fator 1", "fator 2", "fator 3"],
  "explicacao": "2-3 frases a explicar o raciocínio.",
  "acao": "BLOQUEAR" ou "REVER MANUALMENTE" ou "APROVAR"
}}"""

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        resultado = json.loads(text)

        is_fraud = resultado["classificacao"] == "FRAUDULENTA"
        emoji_verdict = "🔴" if is_fraud else "🟢"
        emoji_acao = "🚫" if resultado["acao"] == "BLOQUEAR" else ("⚠️" if resultado["acao"] == "REVER MANUALMENTE" else "✅")
        cor = discord.Color.red() if is_fraud else discord.Color.green()

        embed = discord.Embed(
            title=f"{emoji_verdict} Transação {resultado['classificacao']}",
            color=cor
        )
        embed.add_field(name="Confiança", value=resultado["confianca"], inline=True)
        embed.add_field(name="Valor", value=f"${valor}", inline=True)
        embed.add_field(name="Tempo desde registo", value=tempo_label, inline=True)
        embed.add_field(
            name="Fatores Identificados",
            value="\n".join(f"• {f}" for f in resultado["fatores"]),
            inline=False
        )
        embed.add_field(name="Raciocínio do Agente", value=resultado["explicacao"], inline=False)
        embed.add_field(
            name=f"{emoji_acao} Ação Recomendada",
            value=f"**{resultado['acao']}**",
            inline=False
        )
        embed.set_footer(text="Agente IA Fintech — Deteção de Fraude | Coimbra Business School 2025/2026")

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"❌ Erro na análise: {str(e)}")

client.run(DISCORD_TOKEN)

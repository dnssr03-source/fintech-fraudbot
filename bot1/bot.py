import discord
from discord import app_commands
import os

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ─────────────────────────────────────────────────────────────
# MOTOR DE DETEÇÃO — baseado nos resultados reais da EDA
# Dataset: Fraud E-Commerce (Kaggle, 151.112 transações, 9.4% fraudes)
# ─────────────────────────────────────────────────────────────

def calcular_score(horas_registo, dispositivo_partilhado, canal, valor, pais):
    score = 0
    fatores = []
    niveis = []

    # FATOR 1 — Tempo desde registo (preditor mais forte: 99.5% de fraude em <1h)
    if horas_registo < 0.017:          # menos de 1 minuto
        score += 60
        fatores.append(f"Compra realizada {horas_registo * 3600:.0f} segundos após registo — padrão fortemente associado a fraude (99.5% dos casos)")
        niveis.append("alto")
    elif horas_registo < 1:            # menos de 1 hora
        score += 50
        fatores.append(f"Compra realizada {horas_registo * 60:.0f} minutos após registo — dentro da janela de alto risco (<1 hora)")
        niveis.append("alto")
    elif horas_registo < 24:           # menos de 1 dia
        score += 10
        fatores.append(f"Compra realizada {horas_registo:.1f} horas após registo — risco moderado")
        niveis.append("medio")
    elif horas_registo < 168:          # menos de 1 semana
        score += 2
        fatores.append(f"Utilizador com {horas_registo / 24:.0f} dias de histórico — perfil de risco baixo")
        niveis.append("baixo")
    else:                              # mais de 1 semana
        score -= 5
        fatores.append(f"Utilizador com histórico de {horas_registo / 24:.0f} dias — padrão típico de utilizador legítimo")
        niveis.append("baixo")

    # FATOR 2 — Dispositivo partilhado (52.5% fraude vs 3.0% em único)
    if dispositivo_partilhado.lower() in ["sim", "s", "yes", "y"]:
        score += 30
        fatores.append("Dispositivo partilhado por múltiplos utilizadores — taxa de fraude de 52.5% vs 3.0% em dispositivos únicos")
        niveis.append("alto")
    else:
        score -= 5
        fatores.append("Dispositivo exclusivo do utilizador — fator de confiança")
        niveis.append("baixo")

    # FATOR 3 — Canal de aquisição (Direct: 10.54% de fraude)
    if canal.lower() == "direct":
        score += 8
        fatores.append("Acesso direto sem navegação prévia — canal com maior taxa de fraude (10.54%)")
        niveis.append("medio")
    elif canal.lower() == "ads":
        score += 2
        fatores.append("Canal de aquisição via anúncios — risco ligeiramente elevado")
        niveis.append("baixo")
    else:  # SEO
        score -= 3
        fatores.append("Canal de aquisição via pesquisa orgânica — comportamento de navegação normal")
        niveis.append("baixo")

    # FATOR 4 — Valor (nota: NÃO é preditor segundo a EDA, mas valores extremos são sinalizados)
    if valor > 500:
        score += 5
        fatores.append(f"Valor elevado (${valor:.2f}) — acima do padrão habitual, embora o valor médio não diferencie fraude")
        niveis.append("medio")
    elif valor < 5:
        score += 3
        fatores.append(f"Valor muito baixo (${valor:.2f}) — pode indicar teste de cartão")
        niveis.append("medio")
    else:
        fatores.append(f"Valor da transação (${valor:.2f}) — dentro do intervalo típico, sem poder preditivo significativo")
        niveis.append("baixo")

    # FATOR 5 — País de alto risco (baseado em padrões gerais de fraude internacional)
    paises_alto_risco = ["nigeria", "roménia", "romania", "ghana", "camarões", "cameroon", "indonesia", "filipinas", "philippines"]
    if pais.lower() in paises_alto_risco:
        score += 10
        fatores.append(f"País de origem ({pais}) associado a maior incidência de fraude em e-commerce")
        niveis.append("medio")
    elif pais.lower() in ["portugal", "espanha", "spain", "france", "franca", "alemanha", "germany", "reino unido", "uk"]:
        score -= 3
        fatores.append(f"País de origem ({pais}) com baixo risco histórico")
        niveis.append("baixo")

    return score, fatores, niveis


def classificar(score, horas_registo, dispositivo_partilhado):
    # Threshold calibrado com base nos resultados da EDA
    if score >= 70:
        classificacao = "FRAUDULENTA"
        confianca = "Muito Alta (>95%)"
        acao = "BLOQUEAR"
    elif score >= 45:
        classificacao = "FRAUDULENTA"
        confianca = "Alta (>85%)"
        acao = "BLOQUEAR"
    elif score >= 25:
        classificacao = "FRAUDULENTA"
        confianca = "Média (>70%)"
        acao = "REVER MANUALMENTE"
    elif score >= 10:
        classificacao = "LEGÍTIMA"
        confianca = "Média (>70%)"
        acao = "REVER MANUALMENTE"
    else:
        classificacao = "LEGÍTIMA"
        confianca = "Alta (>85%)"
        acao = "APROVAR"

    return classificacao, confianca, acao


def gerar_explicacao(classificacao, score, horas_registo, dispositivo_partilhado, canal):
    partilhado = dispositivo_partilhado.lower() in ["sim", "s", "yes", "y"]

    if classificacao == "FRAUDULENTA":
        if horas_registo < 1 and partilhado:
            return (
                f"A transação apresenta os dois indicadores mais críticos identificados na análise exploratória: "
                f"compra realizada {horas_registo * 60:.0f} minutos após o registo (padrão presente em 99.5% das fraudes) "
                f"e dispositivo partilhado por múltiplos utilizadores (taxa de fraude de 52.5%). "
                f"A combinação destes fatores eleva substancialmente a probabilidade de fraude organizada."
            )
        elif horas_registo < 1:
            return (
                f"O principal indicador de risco é o tempo entre registo e compra: "
                f"{horas_registo * 60:.0f} minutos. Na análise exploratória do dataset, "
                f"99.5% das transações realizadas menos de 1 hora após o registo são fraudulentas, "
                f"com uma mediana de apenas 1 segundo nas contas fraudulentas face a 60 dias nas legítimas."
            )
        elif partilhado:
            return (
                f"O fator determinante é o dispositivo partilhado por múltiplos utilizadores, "
                f"que apresenta uma taxa de fraude de 52.5% face a apenas 3.0% em dispositivos únicos. "
                f"Este padrão é consistente com redes de fraude organizada que operam com "
                f"poucos dispositivos e múltiplas identidades falsas."
            )
        else:
            return (
                f"A transação acumulou múltiplos indicadores de risco moderado (score: {score}). "
                f"Embora nenhum fator seja isoladamente conclusivo, a combinação "
                f"de canal {canal}, tempo de conta reduzido e outros padrões justifica revisão."
            )
    else:
        if horas_registo >= 168:
            return (
                f"O utilizador tem um histórico de {horas_registo / 24:.0f} dias na plataforma, "
                f"consistente com o padrão de utilizadores legítimos (mediana de ~60 dias entre registo e compra). "
                f"O dispositivo é exclusivo e o canal de aquisição não levanta suspeitas."
            )
        else:
            return (
                f"A transação não apresenta os indicadores críticos identificados na EDA. "
                f"O tempo desde o registo ({horas_registo:.1f} horas) e os restantes fatores "
                f"não atingem os limiares associados a comportamento fraudulento."
            )


# ─────────────────────────────────────────────────────────────
# COMANDO DISCORD
# ─────────────────────────────────────────────────────────────

@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot 1 ligado como {client.user}")

@tree.command(name="analisar", description="Analisa uma transação e deteta se é fraudulenta")
@app_commands.describe(
    valor="Valor da transação em dólares (ex: 45.50)",
    horas_registo="Horas desde o registo até à compra (ex: 0.003 = 10 segundos, 720 = 30 dias)",
    dispositivo_partilhado="Dispositivo partilhado por vários utilizadores? (sim / nao)",
    canal="Canal de aquisição: SEO, Ads ou Direct",
    pais="País de origem da transação (ex: Portugal)",
    idade="Idade do utilizador (ex: 32)",
    browser="Browser utilizado: Chrome, Firefox, Safari, IE ou Opera"
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
    score, fatores, niveis = calcular_score(horas_registo, dispositivo_partilhado, canal, valor, pais)
    classificacao, confianca, acao = classificar(score, horas_registo, dispositivo_partilhado)
    explicacao = gerar_explicacao(classificacao, score, horas_registo, dispositivo_partilhado, canal)

    # Formatar tempo
    if horas_registo < 0.017:
        tempo_label = f"{horas_registo * 3600:.0f} segundos"
    elif horas_registo < 1:
        tempo_label = f"{horas_registo * 60:.0f} minutos"
    elif horas_registo < 24:
        tempo_label = f"{horas_registo:.1f} horas"
    else:
        tempo_label = f"{horas_registo / 24:.1f} dias"

    is_fraud = classificacao == "FRAUDULENTA"
    emoji_verdict = "🔴" if is_fraud else "🟢"
    cor = discord.Color.red() if is_fraud else discord.Color.green()
    emoji_acao = "🚫" if acao == "BLOQUEAR" else ("⚠️" if acao == "REVER MANUALMENTE" else "✅")

    fatores_texto = "\n".join(
        f"{'🔴' if n == 'alto' else '🟡' if n == 'medio' else '🟢'} {f}"
        for f, n in zip(fatores, niveis)
    )

    embed = discord.Embed(
        title=f"{emoji_verdict}  Transação {classificacao}",
        color=cor
    )
    embed.add_field(name="Confiança", value=confianca, inline=True)
    embed.add_field(name="Score de Risco", value=f"{min(score, 100)}/100", inline=True)
    embed.add_field(name="Valor", value=f"${valor:.2f}", inline=True)
    embed.add_field(name="Tempo desde registo", value=tempo_label, inline=True)
    embed.add_field(name="Dispositivo partilhado", value=dispositivo_partilhado.capitalize(), inline=True)
    embed.add_field(name="Canal", value=canal, inline=True)
    embed.add_field(name="Fatores Identificados", value=fatores_texto, inline=False)
    embed.add_field(name="Raciocínio", value=explicacao, inline=False)
    embed.add_field(name=f"{emoji_acao}  Ação Recomendada", value=f"**{acao}**", inline=False)
    embed.set_footer(text="Motor de deteção baseado na EDA do dataset Fraud E-Commerce (Kaggle) • CBS FinTech 2025/2026")

    await interaction.response.send_message(embed=embed)

client.run(DISCORD_TOKEN)

import discord
from discord import app_commands
import os

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ─────────────────────────────────────────────────────────────
# BASE DE CONHECIMENTO DO PROJETO
# ─────────────────────────────────────────────────────────────

FAQ = {
    # GRUPO
    "grupo": {
        "keywords": ["grupo", "equipa", "membros", "quem", "autores", "alunos"],
        "resposta": (
            "**Grupo do Projeto**\n"
            "• **Bernardo Vieira** (a2021124221) — Skill 1: Revisão de Literatura com IA\n"
            "• **Duarte Ribeiro** (a2023142440) — Skill 2: Análise Exploratória de Dados (EDA)\n"
            "• **Artur Yakovenko** (a2023138730) — Agente IA: Detetor de Fraude em Tempo Real\n\n"
            "Projeto da UC de FinTech — Licenciatura em Ciência de Dados para a Gestão\n"
            "Coimbra Business School | 2025/2026"
        )
    },
    # DATASET
    "dataset": {
        "keywords": ["dataset", "dados", "data", "kaggle", "transações", "registos", "fraudes"],
        "resposta": (
            "**Dataset Utilizado — Fraud E-Commerce (Kaggle)**\n"
            "• **Fonte:** kaggle.com/datasets/vbinh002/fraud-ecommerce\n"
            "• **Total de transações:** 151.112\n"
            "• **Fraudes:** 14.151 (9,4%)\n"
            "• **Legítimas:** 136.961 (90,6%)\n"
            "• **Período:** 2015\n"
            "• **Valores em falta:** 0 (dataset limpo)\n"
            "• **Variáveis principais:** purchase_value, signup_time, purchase_time, device_id, source, browser, sex, age, ip_address, class"
        )
    },
    # EDA - DESCOBERTAS
    "eda": {
        "keywords": ["eda", "análise", "descobertas", "resultados", "padrões", "exploratória"],
        "resposta": (
            "**Principais Descobertas da EDA**\n\n"
            "🔴 **Descoberta 1 — Tempo entre registo e compra** *(preditor mais forte)*\n"
            "Das 7.641 transações realizadas menos de 1 hora após o registo, **99,5% são fraudulentas**.\n"
            "Mediana legítima: ~1.443 horas (~60 dias) | Mediana fraudulenta: ~0,0003 horas (~1 segundo)\n\n"
            "🔴 **Descoberta 2 — Dispositivos partilhados**\n"
            "Dispositivo único: taxa de fraude de **3,0%**\n"
            "Dispositivo partilhado: taxa de fraude de **52,5%**\n"
            "→ Indica redes de fraude organizada com poucos dispositivos e múltiplas identidades\n\n"
            "🟢 **Descoberta 3 — Valor da transação** *(não é preditor!)*\n"
            "Média legítima: $36,93 | Média fraudulenta: $36,99\n"
            "→ Fraudadores calibram os valores propositadamente para não disparar alertas"
        )
    },
    # TEMPO
    "tempo": {
        "keywords": ["tempo", "registo", "horas", "minutos", "segundos", "signup", "purchase", "time_diff"],
        "resposta": (
            "**Variável: Tempo entre Registo e Compra (time_diff_hours)**\n\n"
            "Esta é a variável mais poderosa do dataset — não existia originalmente, foi criada a partir de `signup_time` e `purchase_time`.\n\n"
            "**Resultados:**\n"
            "• Transações < 1 hora após registo → **99,5% fraudulentas** (7.604 de 7.641)\n"
            "• Mediana legítima: ~1.443 horas (~60 dias)\n"
            "• Mediana fraudulenta: ~0,0003 horas (~1 segundo)\n\n"
            "**Interpretação:** Contas fraudulentas agem de imediato, antes que os sistemas detetem comportamentos suspeitos. É o maior 'red flag' do dataset."
        )
    },
    # DISPOSITIVO
    "dispositivo": {
        "keywords": ["dispositivo", "device", "device_id", "partilhado", "shared"],
        "resposta": (
            "**Variável: Dispositivo Partilhado (device_id)**\n\n"
            "O `device_id` identifica o dispositivo físico usado na transação. Quando o mesmo device_id aparece associado a múltiplos utilizadores diferentes, é um sinal de alerta.\n\n"
            "**Resultados:**\n"
            "• Dispositivo exclusivo (1 utilizador): **3,0%** de taxa de fraude\n"
            "• Dispositivo partilhado (2+ utilizadores): **52,5%** de taxa de fraude\n\n"
            "**Interpretação:** Redes de fraude organizada operam com poucos dispositivos e muitas identidades falsas — é a assinatura digital de um fraud ring."
        )
    },
    # AGENTE IA
    "agente": {
        "keywords": ["agente", "ia", "inteligência", "artificial", "bot", "classificação", "modelo"],
        "resposta": (
            "**Agente IA — Detetor de Fraude em Tempo Real**\n"
            "*Responsável: Artur Yakovenko*\n\n"
            "**Arquitetura:** Motor de classificação baseado nas regras empíricas da EDA\n"
            "**Interface:** Aplicação web HTML + Bot Discord\n\n"
            "**Inputs:**\n"
            "→ Valor da transação\n"
            "→ Tempo desde o registo (horas)\n"
            "→ Dispositivo partilhado (Sim/Não)\n"
            "→ Canal de aquisição (SEO/Ads/Direct)\n"
            "→ País, Idade, Browser\n\n"
            "**Outputs:**\n"
            "→ Classificação: FRAUDULENTA / LEGÍTIMA\n"
            "→ Nível de Confiança\n"
            "→ Fatores de Risco identificados\n"
            "→ Explicação do raciocínio\n"
            "→ Ação Recomendada: BLOQUEAR / REVER / APROVAR\n\n"
            "**Usa o comando `/analisar` neste servidor para testar em tempo real!**"
        )
    },
    # SKILL 1
    "skill1": {
        "keywords": ["skill 1", "skill1", "revisão", "literatura", "bernardo", "prompts"],
        "resposta": (
            "**Skill 1 — Revisão de Literatura com IA**\n"
            "*Responsável: Bernardo Vieira*\n\n"
            "Utilizou o **Claude Sonnet 4.6 (Anthropic)** como copiloto intelectual para pesquisa, síntese e estruturação da revisão de literatura.\n\n"
            "**Processo:**\n"
            "1. Definição do âmbito temático (história, tipologias, regulamentação, ML)\n"
            "2. Elaboração de prompts específicos para cada bloco\n"
            "3. Iteração e refinamento das respostas\n"
            "4. Validação com Google Scholar, Scopus, EBA, BCE, Nilson Report\n\n"
            "**Exemplo de prompt usado:**\n"
            "*'Faz uma síntese cronológica da evolução das transações financeiras digitais desde os anos 1970 até hoje, destacando os marcos mais importantes e como cada inovação criou novas oportunidades de fraude.'*\n\n"
            "**Conclusão:** A IA não substitui a investigação académica — acelera-a e enriquece-a."
        )
    },
    # SKILL 2
    "skill2": {
        "keywords": ["skill 2", "skill2", "eda", "exploratória", "duarte", "análise exploratória"],
        "resposta": (
            "**Skill 2 — Análise Exploratória de Dados (EDA)**\n"
            "*Responsável: Duarte Ribeiro*\n\n"
            "EDA sobre o dataset Fraud E-Commerce (Kaggle, 151.112 transações).\n\n"
            "**Fases do processo:**\n"
            "1. Carregamento e validação (0 valores em falta)\n"
            "2. Estatísticas descritivas por variável\n"
            "3. Engenharia de variáveis — criação de `time_diff_hours`\n"
            "4. Análise diferenciada por classe (fraude vs legítima)\n\n"
            "**Ferramentas:** Python, pandas, numpy, Claude Sonnet 4.6\n\n"
            "**Principais conclusões:**\n"
            "• `time_diff_hours` — preditor mais poderoso (99,5% fraude em <1h)\n"
            "• Dispositivo partilhado — 52,5% vs 3,0% de fraude\n"
            "• Valor da transação — sem poder preditivo\n"
            "• Idade e browser — poder preditivo muito baixo"
        )
    },
    # REGULAMENTAÇÃO
    "regulamentação": {
        "keywords": ["regulamentação", "regulação", "psd2", "rgpd", "gdpr", "dora", "lei", "diretiva", "europeia"],
        "resposta": (
            "**Regulamentação Europeia Abordada no Projeto**\n\n"
            "📋 **PSD2 (Payment Services Directive 2)**\n"
            "Obriga à Autenticação Forte do Cliente (SCA) e à monitorização contínua de transações suspeitas.\n\n"
            "📋 **RGPD (Regulamento Geral de Proteção de Dados)**\n"
            "Artigo 22.º: decisões automatizadas com impacto significativo devem ser explicáveis. Condiciona o uso de dados nos modelos de ML.\n\n"
            "📋 **DORA (Digital Operational Resilience Act)**\n"
            "Resiliência operacional digital no setor financeiro — em vigor desde janeiro de 2025.\n\n"
            "📋 **5AMLD / 6AMLD**\n"
            "Diretivas Anti-Branqueamento de Capitais — reforçam obrigações de monitorização e reporte de transações suspeitas."
        )
    },
    # MACHINE LEARNING
    "ml": {
        "keywords": ["machine learning", "ml", "algoritmos", "modelos", "random forest", "xgboost", "smote", "autoencoder", "lstm", "gnn"],
        "resposta": (
            "**Algoritmos de ML Estudados no Projeto**\n\n"
            "🌲 **Random Forest & Gradient Boosting (XGBoost, LightGBM)**\n"
            "Referência em produção — melhor equilíbrio entre desempenho e eficiência.\n\n"
            "🧠 **Autoencoders**\n"
            "Deteção de anomalias não supervisionada — treinados só em transações legítimas, identificam fraudes pelo erro de reconstrução elevado.\n\n"
            "🔄 **LSTM (Long Short-Term Memory)**\n"
            "Capturam padrões sequenciais no histórico de transações de cada cliente.\n\n"
            "🕸️ **Graph Neural Networks (GNN)**\n"
            "Deteção de fraud rings — modelam transações e utilizadores como nós de um grafo.\n\n"
            "📊 **Métricas usadas:** AUPRC, F1-Score, Recall (não acurácia — o dataset é desequilibrado)\n"
            "⚖️ **Balanceamento:** SMOTE para geração de amostras sintéticas da classe minoritária\n"
            "🔍 **Explicabilidade:** SHAP values para cumprir o RGPD (Art. 22.º)"
        )
    },
    # TIPOS DE FRAUDE
    "fraude": {
        "keywords": ["tipos", "fraude", "card", "cnp", "ato", "account", "takeover", "friendly", "lavagem", "dinheiro"],
        "resposta": (
            "**Tipos de Fraude Estudados**\n\n"
            "💳 **Card-Not-Present (CNP)**\n"
            "Uso de dados de cartão em transações online sem presença física. Representa >70% das perdas.\n\n"
            "🔑 **Account Takeover (ATO)**\n"
            "Acesso não autorizado a contas via credential stuffing ou phishing. Difícil de detetar — usa credenciais válidas.\n\n"
            "😊 **Friendly Fraud**\n"
            "Estornos fraudulentos por clientes legítimos. Gera >$20 mil milhões/ano de perdas globais.\n\n"
            "🏦 **Lavagem de Dinheiro**\n"
            "Dissimulação da origem ilícita de fundos via smurfing e entidades-ecrã.\n\n"
            "👔 **Fraude Interna**\n"
            "Perpetrada por colaboradores com acesso privilegiado — a mais difícil de detetar."
        )
    },
    # AJUDA GERAL
    "ajuda": {
        "keywords": ["ajuda", "help", "comandos", "o que", "o que podes", "o que sabes"],
        "resposta": (
            "**Assistente do Projeto FinTech — CBS 2025/2026**\n"
            "Posso responder a perguntas sobre qualquer aspeto do projeto. Experimenta perguntar sobre:\n\n"
            "• `/projeto dataset` — informação sobre os dados utilizados\n"
            "• `/projeto eda` — principais descobertas da análise exploratória\n"
            "• `/projeto agente` — como funciona o Agente IA\n"
            "• `/projeto skill1` ou `/projeto skill2` — detalhes de cada skill\n"
            "• `/projeto ml` — algoritmos de Machine Learning estudados\n"
            "• `/projeto fraude` — tipos de fraude financeira\n"
            "• `/projeto regulamentação` — PSD2, RGPD, DORA\n"
            "• `/projeto grupo` — membros e responsabilidades\n\n"
            "Ou escreve qualquer pergunta em linguagem natural!"
        )
    }
}

def encontrar_resposta(pergunta: str) -> str:
    pergunta_lower = pergunta.lower()

    # Procura correspondência por keywords
    melhor_match = None
    max_matches = 0

    for topico, dados in FAQ.items():
        matches = sum(1 for kw in dados["keywords"] if kw in pergunta_lower)
        if matches > max_matches:
            max_matches = matches
            melhor_match = dados["resposta"]

    if melhor_match and max_matches > 0:
        return melhor_match

    # Resposta genérica se não encontrar
    return (
        "Não encontrei uma resposta específica para essa pergunta na base de conhecimento do projeto.\n\n"
        "Experimenta perguntar sobre: **dataset**, **eda**, **agente**, **skill1**, **skill2**, "
        "**ml**, **fraude**, **regulamentação** ou **grupo**.\n\n"
        "Ou usa `/projeto ajuda` para ver todos os tópicos disponíveis."
    )


@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot 2 ligado como {client.user}")

@tree.command(name="projeto", description="Faz uma pergunta sobre o projeto de deteção de fraude")
@app_commands.describe(pergunta="Ex: 'O que é a EDA?', 'Quem fez a Skill 2?', 'Que algoritmos usaram?'")
async def projeto(interaction: discord.Interaction, pergunta: str):
    resposta = encontrar_resposta(pergunta)

    embed = discord.Embed(
        title="💡 Assistente do Projeto",
        description=resposta,
        color=discord.Color.blue()
    )
    embed.add_field(name="Pergunta", value=f"*{pergunta}*", inline=False)
    embed.set_footer(text=f"Perguntado por {interaction.user.display_name} • Deteção de Fraude com ML — CBS 2025/2026")

    await interaction.response.send_message(embed=embed)

client.run(DISCORD_TOKEN)

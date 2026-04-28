import discord
from discord import app_commands
import anthropic
import os

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

CONTEXTO_PROJETO = """
PROJETO: Deteção de Fraude em Transações Financeiras com Machine Learning
UNIDADE CURRICULAR: FinTech
INSTITUIÇÃO: Coimbra Business School — Licenciatura em Ciência de Dados para a Gestão
ANO LETIVO: 2025/2026

GRUPO:
- Bernardo Vieira (a2021124221) — Skill 1: Revisão de Literatura com IA
- Duarte Ribeiro (a2023142440) — Skill 2: Análise Exploratória de Dados (EDA)
- Artur Yakovenko (a2023138730) — Agente IA: Detetor de Fraude em Tempo Real

SKILL 1 — REVISÃO DE LITERATURA COM IA:
Utilizou o Claude Sonnet 4.6 da Anthropic como copiloto intelectual para pesquisa, síntese e estruturação da revisão de literatura sobre fraude financeira digital. O processo foi iterativo com prompts específicos para cada bloco temático (história das transações digitais, tipologias de fraude, regulamentação europeia, algoritmos de ML). Todo o conteúdo gerado foi validado com fontes académicas primárias (Google Scholar, Scopus) e relatórios institucionais (EBA, BCE, Nilson Report). A IA acelerou a investigação sem substituir o pensamento crítico humano.

SKILL 2 — ANÁLISE EXPLORATÓRIA DE DADOS (EDA):
Dataset: Fraud E-Commerce (Kaggle, vbinh002/fraud-ecommerce)
- 151.112 transações totais
- 14.151 fraudes (9.4%)
- 136.961 legítimas (90.6%)
- Período: 2015, sem valores em falta

PRINCIPAIS DESCOBERTAS DA EDA:
1. Tempo entre registo e compra: Das 7.641 transações realizadas menos de 1 hora após o registo, 7.604 (99.5%) são fraudulentas. Mediana legítima: ~1.443 horas (~60 dias). Mediana fraudulenta: ~0.0003 horas (~1 segundo).
2. Dispositivos partilhados: Taxa de fraude de 52.5% em dispositivos partilhados vs 3.0% em dispositivos únicos. Indica redes de fraude organizada com poucos dispositivos e múltiplas identidades.
3. Valor da transação: Sem diferença significativa. Média legítima: $36.93. Média fraudulenta: $36.99. Sistemas baseados em limites de valor são ineficazes.
4. Canal de aquisição: Direct tem maior taxa (10.54%). SEO e Ads têm taxas mais baixas.
5. Idade e browser: Poder preditivo muito baixo.

AGENTE IA FINTECH:
Modelo base: Claude Sonnet 4.6 (Anthropic)
Arquitetura: Agente de classificação com raciocínio explícito (Chain-of-Thought)
Interface: Aplicação web HTML/JavaScript + integração Discord
Inputs: valor, tempo desde registo, dispositivo partilhado, canal, país, idade, browser
Outputs: Classificação (FRAUDULENTA/LEGÍTIMA), Nível de Confiança, Fatores de Risco, Explicação, Ação Recomendada (BLOQUEAR/REVER/APROVAR)
Relevância regulatória: Cumpre requisitos de explicabilidade do AI Act europeu para sistemas de IA de alto risco em decisões financeiras.

REGULAMENTAÇÃO ABORDADA:
- PSD2 (Payment Services Directive 2): Autenticação Forte do Cliente, monitorização de transações
- RGPD: Artigo 22.º — explicabilidade de decisões automatizadas com impacto significativo
- DORA (Digital Operational Resilience Act): Resiliência operacional digital no setor financeiro
- 5AMLD/6AMLD: Diretivas Anti-Branqueamento de Capitais

TIPOS DE FRAUDE ESTUDADOS:
- Card-not-present (CNP): Mais prevalente em e-commerce
- Account Takeover (ATO): Comprometimento de credenciais
- Friendly Fraud: Estornos fraudulentos
- Lavagem de dinheiro: Smurfing e estruturas de dissimulação
- Fraude interna: Perpetrada por colaboradores com acesso privilegiado

ALGORITMOS DE ML ESTUDADOS:
- Random Forest e Gradient Boosting (XGBoost, LightGBM): Referência em produção
- Autoencoders: Deteção de anomalias não supervisionada
- LSTM: Padrões sequenciais no histórico de transações
- Graph Neural Networks: Deteção de fraud rings
- SHAP values: Explicabilidade das decisões dos modelos

DATASETS PÚBLICOS:
- Kaggle Credit Card Fraud Detection (284.807 transações, 0.17% fraudes, features anonimizadas por PCA)
- Fraud E-Commerce Dataset (151.112 transações, 9.4% fraudes, features comportamentais ricas)
- IEEE-CIS Fraud Detection (400+ variáveis, Vesta Corporation)
- PaySim (simulação de pagamentos móveis africanos)

CASO DE ESTUDO — WIRECARD:
Maior escândalo de fraude financeira europeu recente. 1.9 mil milhões de euros em dinheiro fictício. Fraude perpetrada durante anos, iludiu auditores da EY durante 9 anos. Técnicas de deteção de anomalias poderiam ter sinalizado margens de lucro anormais e inconsistências nos fluxos de caixa.

DESAFIOS TÉCNICOS:
- Desequilíbrio extremo de classes (<0.1% a 9.4% de fraudes)
- Técnicas de balanceamento: SMOTE, undersampling, class weights
- Métricas adequadas: AUPRC, F1-Score, Recall (não acurácia simples)
- Explicabilidade exigida pelo RGPD e AI Act

COLLECTIVE BRAIN / SECOND BRAIN:
- Obsidian: Vault com notas atómicas interligadas (metodologia Zettelkasten)
- Notion: Gestão de projeto, backlog, roadmap
- Discord: Comunicação em tempo real e partilha com outros grupos da UC
"""

historico_conversas = {}

@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot ligado como {client.user}")

@tree.command(name="projeto", description="Faz uma pergunta sobre o projeto de deteção de fraude")
@app_commands.describe(pergunta="A tua pergunta sobre o projeto, metodologia, resultados ou tecnologias")
async def projeto(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer(thinking=True)

    user_id = str(interaction.user.id)
    if user_id not in historico_conversas:
        historico_conversas[user_id] = []

    historico_conversas[user_id].append({"role": "user", "content": pergunta})

    if len(historico_conversas[user_id]) > 10:
        historico_conversas[user_id] = historico_conversas[user_id][-10:]

    system_prompt = f"""És o assistente especializado do projeto académico de Deteção de Fraude em Transações Financeiras com Machine Learning, desenvolvido na Coimbra Business School para a UC de FinTech 2025/2026.

Tens acesso completo a toda a informação do projeto e respondes de forma clara, precisa e academicamente fundamentada. Adaptas o nível de detalhe à pergunta — respostas curtas para perguntas simples, detalhadas para perguntas técnicas.

INFORMAÇÃO COMPLETA DO PROJETO:
{CONTEXTO_PROJETO}

Responde sempre em português europeu. Sê direto e útil. Se a pergunta não estiver relacionada com o projeto, indica isso educadamente e oferece ajuda sobre o que podes responder."""

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=system_prompt,
            messages=historico_conversas[user_id]
        )

        resposta = response.content[0].text
        historico_conversas[user_id].append({"role": "assistant", "content": resposta})

        if len(resposta) > 4000:
            resposta = resposta[:3997] + "..."

        embed = discord.Embed(
            title="💡 Assistente do Projeto",
            description=resposta,
            color=discord.Color.blue()
        )
        embed.add_field(name="Pergunta", value=f"*{pergunta}*", inline=False)
        embed.set_footer(text=f"Perguntado por {interaction.user.display_name} | Deteção de Fraude com ML — CBS 2025/2026")

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"❌ Erro ao processar a pergunta: {str(e)}")

@tree.command(name="limpar", description="Limpa o histórico da conversa com o assistente")
async def limpar(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    historico_conversas[user_id] = []
    await interaction.response.send_message("🗑️ Histórico limpo. Podes começar uma nova conversa com `/projeto`.", ephemeral=True)

client.run(DISCORD_TOKEN)

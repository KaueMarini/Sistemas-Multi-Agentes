import os
import asyncio
import json
import chainlit as cl
from google import genai
from google.genai import types
from duckduckgo_search import DDGS


API_KEY = "Axxxx.xxxx.xxx.xxx" 
ARQUIVO_FINAL = "PROJETO_MARKETING_FINAL.md"

if API_KEY == "SUA_API_KEY_AQUI":
    raise ValueError("⚠️ COLOQUE SUA API KEY!")

client = genai.Client(api_key=API_KEY)


async def market_research(niche, phase):
    """Busca tendências específicas para o nicho escolhido pelo usuário."""
    query = f"{niche} market trends {phase} 2026 analysis"
    print(f"🔎 Pesquisando: {query}")
    try:
        with DDGS() as ddgs:
            return [r for r in ddgs.text(query, max_results=3)]
    except: return []


async def agency_turn(agent, niche, phase, context, market_data):
    prompt = f"""
    VOCÊ É: {agent['name']} ({agent['role']})
    ESTAMOS CRIANDO UM PROJETO PARA: "{niche}"
    
    FASE ATUAL: {phase}
    
    DADOS REAIS DO MERCADO (2026): 
    {json.dumps(market_data, indent=2)}
    
    HISTÓRICO DA REUNIÃO:
    {context}
    
    SUA MISSÃO:
    1. Aja como um especialista de elite. Use a linguagem adequada ao nicho (se for Tech, use termos tech; se for Moda, use termos fashion).
    2. Critique as ideias anteriores. Se o Stratos foi conservador, o Pixel deve ousar. Se o Pixel viajou, o Metric deve cortar custos.
    3. Dê ideias concretas (Nomes, Preços, Slogans, Canais).
    4. {agent['style']}
    5. Fale Português.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.85)
        )
        return response.text.strip()
    except: return "Analisando..."


async def generate_final_doc(niche, history):
    prompt = f"""
    ATUE COMO O CEO DA AGÊNCIA.
    Compile o PLANO DE MARKETING FINAL para o cliente sobre: "{niche}".
    
    Use o histórico de discussão abaixo para preencher os tópicos. Seja profissional e organizado.
    
    HISTÓRICO:
    {history}
    
    FORMATO (MARKDOWN):
    # PLANEJAMENTO ESTRATÉGICO: {niche.upper()}
    
    ## 1. Visão Geral e Persona (Stratos)
    ## 2. Identidade Visual e Criativa (Pixel)
    ## 3. Estratégia de Crescimento e Vendas (Metric)
    ## 4. Roteiro de Lançamento (Next Steps)
    """
    try:
        res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return res.text.strip()
    except: return "Erro na compilação."


@cl.on_chat_start
async def start():
    
    stratos = {
        "name": "STRATOS", "emoji": "🧠",
        "role": "Estrategista de Marca",
        "style": "Foque no 'Porquê'. Defina quem compra e qual a dor que resolvemos. Seja analítico."
    }
    pixel = {
        "name": "PIXEL", "emoji": "🎨",
        "role": "Diretor Criativo",
        "style": "Foque na 'Emoção'. Pense no nome, no logo, na vibe do Instagram/TikTok. Quebre padrões."
    }
    metric = {
        "name": "METRIC", "emoji": "📊",
        "role": "Growth Hacker",
        "style": "Foque no 'Lucro'. Como vamos vender? Quanto custa? Onde anunciar (Ads, Influencers)? Seja pragmático."
    }
    
    team = [stratos, pixel, metric]
    history = []
    
    
    await cl.Message(content="🏢 **AGÊNCIA OPEN-MIND INICIADA**\n\nEu sou o seu Gerente de Contas. O time de elite (Stratos, Pixel e Metric) está na sala de reunião.\n\n**Qual é o produto, serviço ou ideia que você quer lançar hoje?**\n(Ex: 'Uma marca de roupas streetwear sustentável', 'Um App de IA para advogados', 'Uma barbearia temática')", author="SISTEMA").send()
    
    res = await cl.AskUserMessage(content="", timeout=600).send()
    user_niche = res['output']
    
    history.append(f"PROJETO DEFINIDO PELO CLIENTE: {user_niche}")
    
    
    phases = [
        "FASE 1: Diagnóstico, Público-Alvo e Diferenciação",
        "FASE 2: Naming, Branding e Identidade Visual",
        "FASE 3: Estratégia de Canais e Aquisição de Clientes",
        "FASE 4: Ação de Lançamento (O Big Bang)"
    ]

    for phase in phases:
        await cl.Message(content=f"📌 **{phase}**", author="SISTEMA").send()
        
        
        market_data = await market_research(user_niche, phase)
        
        for agent in team:
            msg = await agency_turn(agent, user_niche, phase, "\n".join(history[-8:]), market_data)
            await cl.Message(content=msg, author=f"{agent['emoji']} {agent['name']}").send()
            history.append(f"{agent['name']}: {msg}")
            await asyncio.sleep(4)
        
        await asyncio.sleep(2)

  
    await cl.Message(content="✅ **REUNIÃO ENCERRADA.** Gerando o Book do Projeto...", author="SISTEMA").send()
    final_doc = await generate_final_doc(user_niche, "\n".join(history))
    
    with open(ARQUIVO_FINAL, "w", encoding="utf-8") as f:
        f.write(final_doc)
    
    await cl.Message(content=f"📄 **PROJETO ENTREGUE:**\n\n{final_doc}", author="AGÊNCIA OPEN-MIND").send()
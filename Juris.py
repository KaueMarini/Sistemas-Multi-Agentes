import os
import asyncio
import chainlit as cl
from google import genai
from google.genai import types
from pypdf import PdfReader 


API_KEY = "xxxx.xxxxx.xxxx.xxxx" 

if API_KEY == "SUA_API_KEY_AQUI":
    raise ValueError("⚠️ COLOQUE SUA API KEY!")

client = genai.Client(api_key=API_KEY)


def extract_text_from_pdf(file_path):
    """Lê o PDF enviado e extrai o texto para a IA ler."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text[:30000] 
    except Exception as e:
        return f"Erro ao ler PDF: {e}"


async def legal_turn(agent, context, case_text):
    prompt = f"""
    VOCÊ É: {agent['name']} ({agent['role']})
    OBJETIVO: Montar a melhor defesa possível para o cliente baseada no arquivo.
    
    --- CONTEÚDO DO PROCESSO/DOCUMENTO (FATO REAL) ---
    {case_text}
    
    --- HISTÓRICO DA REUNIÃO ---
    {context}
    
    SUA MISSÃO:
    1. Analise os fatos friamente. Use termos jurídicos (Habeas Corpus, Dolo, Culpa, Nulidade, Prova Ilícita).
    2. {agent['style']}
    3. Se for o RIVALS, ataque impiedosamente a tese dos outros.
    4. Fale Português Jurídico (mas claro).
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7)
        )
        return response.text.strip()
    except: return "Consultando Vade Mecum..."


async def generate_legal_doc(history):
    prompt = f"""
    ATUE COMO JUIZ/RELATOR.
    Com base na discussão da banca jurídica abaixo, redija a ESTRATÉGIA FINAL DE DEFESA.
    
    DISCUSSÃO:
    {history}
    
    FORMATO (MARKDOWN):
    # ESTRATÉGIA DE DEFESA: [Nome do Caso]
    ## 1. Resumo dos Fatos
    ## 2. Teses Jurídicas Principais (Dr. Magnus)
    ## 3. Fundamentação Legal & Precedentes (Lexia)
    ## 4. Pontos Fracos & Como Mitigar (Análise do Rivals)
    ## 5. Conclusão e Pedidos
    """
    try:
        res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return res.text.strip()
    except: return "Erro ao redigir peça."


@cl.on_chat_start
async def start():
    
    magnus = {
        "name": "DR. MAGNUS", "emoji": "⚖️",
        "role": "Sócio Sênior / Estrategista",
        "style": "Foque na narrativa, na intenção do réu e nos princípios constitucionais (Dignidade, Ampla Defesa)."
    }
    lexia = {
        "name": "DRA. LEXIA", "emoji": "📚",
        "role": "Especialista Processual",
        "style": "Procure erros técnicos. A prova foi colhida legalmente? O prazo prescreveu? Cite Artigos de Lei."
    }
    rivals = {
        "name": "PROMOTOR RIVALS", "emoji": "😈",
        "role": "Simulação da Acusação",
        "style": "Seja agressivo. Aponte por que o réu vai perder. Mostre as falhas na defesa do Magnus."
    }
    
    team = [magnus, lexia, rivals]
    history = []

   
    files = None
    while files == None:
        files = await cl.AskFileMessage(
            content="📁 **SISTEMA JURIS PRIME INICIADO**\nPor favor, anexe o arquivo do caso (PDF ou Texto) para análise preliminar.",
            accept=["application/pdf", "text/plain"],
            max_size_mb=20,
            timeout=180
        ).send()

    file = files[0]
    
   
    msg = cl.Message(content=f"📖 Lendo autos do processo: `{file.name}`...", author="SISTEMA")
    await msg.send()
    
    if "pdf" in file.type:
        case_text = extract_text_from_pdf(file.path)
    else:
        with open(file.path, "r", encoding="utf-8") as f:
            case_text = f.read()
            
    msg.content = f"✅ **ANÁLISE CONCLUÍDA.** A banca está reunida. Iniciando debate..."
    await msg.update()

   
    phases = [
        "FASE 1: Análise dos Fatos e Busca de Nulidades",
        "FASE 2: Construção da Tese de Defesa (Mérito)",
        "FASE 3: Simulação de Julgamento (Ataque vs Defesa)"
    ]

    for phase in phases:
        await cl.Message(content=f"🏛️ **{phase}**", author="SISTEMA").send()
        
        for agent in team:
            resp = await legal_turn(agent, "\n".join(history[-6:]), case_text)
            await cl.Message(content=resp, author=f"{agent['emoji']} {agent['name']}").send()
            history.append(f"{agent['name']}: {resp}")
            await asyncio.sleep(3)
        
        await asyncio.sleep(2)

   
    await cl.Message(content="✍️ **Redigindo Estratégia Final...**", author="SISTEMA").send()
    final_doc = await generate_legal_doc("\n".join(history))
    
    await cl.Message(content=f"📜 **PARECER JURÍDICO PRONTO:**\n\n{final_doc}", author="JURIS PRIME").send()
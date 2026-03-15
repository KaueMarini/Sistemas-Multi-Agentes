import os
# Desativa telemetria chata
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"

import streamlit as st
import sys
import re
import time
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import SerperDevTool

# ================= CONFIGURAÇÃO VISUAL =================
st.set_page_config(page_title="DEBATE CHAT LIVE", page_icon="💬", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    /* Balões de Chat mais bonitos */
    .stChatMessage { border-radius: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ================= LOGGER (CÉREBRO) =================
class StreamolitLogger:
    def __init__(self, widget):
        self.widget = widget
        self.buffer = ""
    def write(self, text):
        # Limpa códigos de cor ANSI que poluem o texto
        text_clean = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)
        self.buffer += text_clean
        # Mostra o log no expander
        self.widget.code(self.buffer[-2000:], language="bash")
    def flush(self): pass

# ================= MOTOR DO DEBATE =================
class DebateManager:
    def __init__(self, google_key, serper_key):
        os.environ["GOOGLE_API_KEY"] = google_key
        os.environ["SERPER_API_KEY"] = serper_key
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            verbose=True,
            temperature=0.6,
            google_api_key=google_key
        )
        self.search_tool = SerperDevTool()

    # --- PASSO 1: GERAR O DIÁLOGO ---
    def gerar_dialogo(self, tema, historico, rodada):
        dom = Agent(
            role='Economista Libertário',
            goal='Debater usando dados de mercado.',
            backstory="Você é DOM. Defende privatizações e liberdade. Seja curto e direto.",
            llm=self.llm, tools=[self.search_tool], verbose=True, allow_delegation=False
        )

        che = Agent(
            role='Sociólogo Progressista',
            goal='Debater usando dados sociais.',
            backstory="Você é CHE. Defende o estado social. Seja curto e direto.",
            llm=self.llm, tools=[self.search_tool], verbose=True, allow_delegation=False
        )

        task_dialogo = Task(
            description=f"""
            RODADA {rodada} - TEMA: {tema}
            
            HISTÓRICO: {historico}
            
            1. DOM fala primeiro (baseado no histórico).
            2. CHE responde ao Dom.
            
            FORMATO OBRIGATÓRIO (NÃO MUDE ISSO):
            DOM: [Texto do Dom]
            CHE: [Texto do Che]
            """,
            expected_output="O diálogo exato entre os dois.",
            agent=dom
        )

        crew = Crew(agents=[dom, che], tasks=[task_dialogo], verbose=True)
        return crew.kickoff()

    # --- PASSO 2: JULGAMENTO (ATHENA) ---
    def julgar_dialogo(self, dialogo_atual):
        athena = Agent(
            role='Mediadora de IA',
            goal='Decidir o status do debate.',
            backstory="Você é ATHENA. Analise se chegaram a um CONSENSO ou se estão em LOOP.",
            llm=self.llm, verbose=True, allow_delegation=False
        )

        task_veredito = Task(
            description=f"""
            Analise este diálogo:
            "{dialogo_atual}"
            
            Eles concordaram em uma solução?
            
            Responda APENAS com uma das palavras:
            - "CONSENSO" (Se concordaram)
            - "STALEMATE" (Se estão repetindo o mesmo argumento)
            - "CONTINUE" (Se o debate está fluindo bem)
            
            Em seguida, adicione uma frase curta explicando.
            """,
            expected_output="Status e Explicação.",
            agent=athena
        )

        crew = Crew(agents=[athena], tasks=[task_veredito], verbose=True)
        return crew.kickoff()

# ================= INTERFACE =================

# Sidebar
with st.sidebar:
    st.title("🎛️ Controle")
    google_key = st.text_input("Gemini API", value="AIzaSyDoGigV5jCyqoyrOtI_G5YyPoS-NkZepvI", type="password")
    serper_key = st.text_input("Serper API", value="461510402522d9f28b9053e8d65be28bb15fe330", type="password")
    
    if st.button("Resetar Debate"):
        st.session_state.chat_history = []
        st.session_state.rodada = 0
        st.session_state.status = "PRONTO"
        st.rerun()

# Estado da Sessão
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "rodada" not in st.session_state: st.session_state.rodada = 0
if "status" not in st.session_state: st.session_state.status = "PRONTO"

st.title("💬 Debate Chat: Dom vs Che")

# Mostra o histórico visual do chat (O que já aconteceu)
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"], avatar=msg["avatar"]):
        st.write(msg["content"])

# Input do Tema
if st.session_state.status == "PRONTO":
    tema = st.chat_input("Digite o tema do debate...")
    if tema:
        st.session_state.tema = tema
        st.session_state.status = "RODANDO"
        # Adiciona mensagem do usuário
        st.session_state.chat_history.append({"role": "user", "avatar": "👤", "content": f"Tema: {tema}"})
        st.rerun()

# ================= LOOP DE EXECUÇÃO =================
if st.session_state.status == "RODANDO":
    
    st.session_state.rodada += 1
    
    # Coluna Expander para o "Cérebro" (Logs)
    with st.expander(f"🧠 Processamento da IA (Rodada {st.session_state.rodada})", expanded=True):
        log_placeholder = st.empty()
        logger = StreamolitLogger(log_placeholder)
        sys.stdout = logger # Redireciona o terminal para cá

        try:
            manager = DebateManager(google_key, serper_key)
            
            # --- FASE 1: O DEBATE ACONTECE ---
            # Prepara o histórico em texto para a IA ler
            hist_txt = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history if m['role'] in ['DOM', 'CHE']])
            
            # Roda o Crew de Diálogo
            dialogo_raw = str(manager.gerar_dialogo(st.session_state.tema, hist_txt, st.session_state.rodada))
            
            # --- FASE 2: ATUALIZA O CHAT VISUALMENTE ---
            # (Aqui fazemos o efeito de chat, processando a string)
            
            if "DOM:" in dialogo_raw:
                # Extrai fala do Dom
                fala_dom = dialogo_raw.split("DOM:")[1].split("CHE:")[0].strip()
                st.session_state.chat_history.append({"role": "DOM", "avatar": "🟦", "content": fala_dom})
            
            if "CHE:" in dialogo_raw:
                # Extrai fala do Che
                # Proteção caso venha texto depois ou não
                partes_che = dialogo_raw.split("CHE:")
                fala_che = partes_che[1].strip() if len(partes_che) > 1 else "..."
                st.session_state.chat_history.append({"role": "CHE", "avatar": "🟥", "content": fala_che})

            # --- FASE 3: O JULGAMENTO ---
            veredito = str(manager.julgar_dialogo(dialogo_raw))
            
            # Checa o status
            status_final = "CONTINUE"
            if "CONSENSO" in veredito: status_final = "CONSENSO"
            elif "STALEMATE" in veredito: status_final = "STALEMATE"

            # Adiciona aviso da Athena no chat
            st.session_state.chat_history.append({"role": "ATHENA", "avatar": "⚖️", "content": f"**Status:** {veredito}"})

            # Lógica de Loop
            if status_final == "CONSENSO":
                st.balloons()
                st.success("Consenso Alcançado!")
                st.session_state.status = "FIM"
            elif status_final == "STALEMATE":
                st.warning("O debate travou.")
                st.session_state.status = "FIM"
            else:
                # Se for CONTINUE, ele dá um rerun e volta pro começo do IF, rodando a próxima rodada
                time.sleep(2)
                st.rerun()

        except Exception as e:
            st.error(f"Erro: {e}")
            st.session_state.status = "ERRO"
        
        finally:
            sys.stdout = sys.__stdout__ # Devolve o terminal
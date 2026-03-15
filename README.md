# 🤖 Ecossistema de Sistemas Multi-Agentes (Multi-Agent Systems)

Este repositório contém uma suíte de três aplicações independentes focadas em **Orquestração de Inteligência Artificial** e **Agentes Autônomos**. O objetivo é demonstrar como sistemas multi-agentes podem ser arquitetados para resolver problemas complexos de negócios, utilizando raciocínio adversarial, Retrieval-Augmented Generation (RAG) e grounding com buscas na web.

Todas as aplicações são alimentadas pelo modelo **Gemini 2.0 Flash** (Google GenAI) e orquestradas com frameworks de ponta.

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python
* **LLM Core:** Gemini 2.0 Flash (`google-genai`, `langchain-google-genai`)
* **Orquestração de Agentes:** CrewAI, LangChain
* **Interfaces Gráficas:** Streamlit, Chainlit
* **Ferramentas (Tools):** DuckDuckGo Search (Web Scraping/Grounding em tempo real), PyPDF (Ingestão de dados/RAG), SerperDevTool.

---

## 📂 Visão Geral dos Projetos

### 1. 💬 Debate Chat: Orquestração de Consenso (CrewAI + Streamlit)
Uma arena de debates automatizada onde duas IAs com perfis diametralmente opostos discutem um tema proposto pelo usuário.
* **A Arquitetura:** Utiliza `CrewAI` para gerenciar a interação.
* **Os Agentes:** * `Dom` (Economista Libertário) e `Che` (Sociólogo Progressista) debatem os argumentos.
  * `Athena` atua como uma IA Mediadora invisível, analisando o debate em tempo real a cada rodada para determinar se houve um "CONSENSO" ou se a discussão entrou em loop ("STALEMATE"), interrompendo a execução de forma autônoma.
* **Casos de Uso:** Resolução de conflitos lógicos, análise de múltiplos cenários e simulação de negociações.

### 2. ⚖️ Juris Prime: Simulador de Banca Jurídica com RAG (Chainlit)
Ferramenta focada em LegalTech. O sistema ingere arquivos PDF reais (processos, inquéritos ou contratos) e simula uma "Banca Jurídica" analisando os fatos.
* **A Arquitetura:** RAG (Retrieval-Augmented Generation) acoplado a um fluxo adversarial.
* **Os Agentes:**
  * `Dr. Magnus` (Estrategista Sênior): Foca em princípios constitucionais e narrativas de defesa.
  * `Dra. Lexia` (Especialista Processual): Busca ativamente por nulidades, erros técnicos e prazos prescricionais.
  * `Promotor Rivals`: Ataca as teses da defesa para encontrar pontos fracos antes do julgamento real.
* **O Resultado:** O sistema atua como um "Juiz Relator" no final, compilando a discussão em um documento estruturado (Markdown) com a melhor estratégia de defesa possível.

### 3. 🏢 Agência Open-Mind: Planejador de Marketing B2B (Chainlit + Web Search)
Simulador de uma agência de publicidade de elite. O usuário fornece um nicho de mercado e os agentes constroem um planejamento estratégico completo.
* **A Arquitetura:** Grounding em tempo real. Antes de qualquer agente falar, o sistema usa `DuckDuckGo Search` para buscar as tendências de mercado mais recentes (2026) daquele nicho específico, evitando alucinações genéricas.
* **Os Agentes:**
  * `Stratos`: Focado no diagnóstico e público-alvo (O "Porquê").
  * `Pixel`: Diretor criativo, responsável por Naming, Branding e Identidade Visual (A "Emoção").
  * `Metric`: Growth Hacker focado em canais de aquisição, CAC e precificação (O "Lucro").
* **O Resultado:** Exportação automática de um arquivo físico (`PROJETO_MARKETING_FINAL.md`) contendo o plano de negócios estruturado e pronto para execução.

---


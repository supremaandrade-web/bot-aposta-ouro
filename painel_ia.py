import streamlit as st
import requests
import pandas as pd
import time
import math
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from streamlit_gsheets import GSheetsConnection
# --- FUNÇÃO DE DEFESA (TELA DE LOGIN) ---
def check_password():
    """Retorna True se o usuário inseriu a senha correta."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔐 Acesso Restrito - IA SUPREMA")
        password = st.text_input("Digite a senha de acesso:", type="password")
        if st.button("Entrar"):
            if password == st.secrets["SENHA_PAINEL"]:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("🚀 Senha incorreta. Acesso negado.")
        return False
    return True

# --- INÍCIO DA PROTEÇÃO ---
if check_password():

    # ==========================================
    # 🔐 CONFIGURAÇÕES SEGURAS
    # ==========================================
    try:
        API_KEY = st.secrets["API_KEY"]
        TOKEN_TELEGRAM = st.secrets["TOKEN_TELEGRAM"]
        CHAT_ID = st.secrets["CHAT_ID"]
    except KeyError:
     st.error("⚠️ Configure o arquivo .streamlit/secrets.toml com suas chaves.")
     st.stop()

    st.set_page_config(page_title="IA SUPREMA - VIP Dashboard", layout="wide", page_icon="👑")
        # ==========================================
        # 🎨 DESIGN SUPER PREMIUM (TEMA APOSTAS VIP)
        # ==========================================
    st.markdown("""
        <style>
            /* Importa fonte esportiva do Google */
            @import url('https://fonts.googleapis.com/css2?family=Teko:wght@400;600&family=Montserrat:wght@400;700&display=swap');
    
            /* Muda a fonte dos títulos para a fonte esportiva */
            h1, h2, h3 {
                font-family: 'Teko', sans-serif !important;
                letter-spacing: 1.5px;
                color: #E5B80B !important; /* Dourado VIP */
                text-transform: uppercase;
            }
    
            /* Muda a fonte do texto normal */
            html, body, [class*="css"]  {
                font-family: 'Montserrat', sans-serif;
            }
    
            /* Efeito Neon no Botão Principal */
            .stButton>button {
                border: 2px solid #00FF00 !important;
                color: #00FF00 !important;
                background-color: transparent !important;
                font-weight: bold !important;
                border-radius: 8px !important;
                transition: all 0.3s ease 0s !important;
                box-shadow: 0px 0px 10px #00FF0040 !important;
            }
            
            /* Efeito quando passa o mouse no botão */
            .stButton>button:hover {
                background-color: #00FF00 !important;
                color: #000000 !important;
                box-shadow: 0px 0px 20px #00FF00 !important;
                transform: translateY(-2px);
            }
    
            /* Caixas de Sucesso (Greens/Bancas) com visual de dinheiro */
            div[data-testid="stSuccess"] {
                background-color: rgba(0, 255, 0, 0.1) !important;
                border-left: 5px solid #00FF00 !important;
                color: #ffffff !important;
            }
    
            /* Barra lateral mais escura para dar contraste */
            [data-testid="stSidebar"] {
                background-color: #0E1117 !important;
                border-right: 1px solid #E5B80B !important;
            }
            
            /* Ajuste da barra de progresso (Créditos) */
            .stProgress > div > div > div > div {
                background-color: #E5B80B !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # ==========================================
    # 🏆 FILTRO: LIGAS DE OURO (Foco em Qualidade)
    # ==========================================
    LIGAS_OURO = {
        71: "Brasileirão Série A",
        72: "Brasileirão Série B",
        73: "Copa do Brasil",           # <--- ADICIONADO
        475: "Campeonato Paulista",     # <--- ADICIONADO
        474: "Campeonato Carioca",      # <--- ADICIONADO
        13: "Copa Libertadores",
        39: "Premier League (Inglaterra)",
        140: "La Liga (Espanha)",
        135: "Serie A (Itália)",
        78: "Bundesliga (Alemanha)",
        2: "UEFA Champions League"
    }
    
    # ==========================================
    # 🧠 CÉREBRO MATEMÁTICO: POISSON (Dados Reais)
    # ==========================================
    def calcular_poisson(media_gols, gols_alvo):
        """Calcula a probabilidade exata de um número de gols acontecer usando a fórmula de Poisson."""
        return ((media_gols ** gols_alvo) * math.exp(-media_gols)) / math.factorial(gols_alvo)
    
    @st.cache_data(ttl=3600 * 24) 
    def buscar_tabela_liga(id_liga, temporada):
        """Gasta 1 crédito para baixar a tabela da liga. Retorna a tabela e o ano utilizado."""
        url = "https://v3.football.api-sports.io/standings"
        headers = {'x-apisports-key': API_KEY}
        
        try:
            # Tentativa 1: Temporada atual
            resp = requests.get(url, headers=headers, params={"league": id_liga, "season": temporada})
            dados = resp.json().get('response', [])
            temp_usada = temporada
            
            # PLANO B: Se a API mandar vazio, busca a do ano anterior
            if not dados:
                resp_fallback = requests.get(url, headers=headers, params={"league": id_liga, "season": temporada - 1})
                dados = resp_fallback.json().get('response', [])
                temp_usada = temporada - 1
                
            return dados, temp_usada
        except:
            return [], temporada
    
    def obter_media_gols_real(id_liga, temporada, nome_time):
        """Retorna a média de gols e avisa qual temporada foi usada de fato."""
        dados_liga, temp_usada = buscar_tabela_liga(id_liga, temporada)
        
        if not dados_liga:
            add_log(f"📭 Tabela VAZIA na API (Liga {id_liga}, Temp {temporada})")
            return 1.6, temp_usada 
            
        try:
            todas_as_tabelas = dados_liga[0]['league']['standings']
            nomes_na_tabela = [] 
            
            for grupo in todas_as_tabelas:
                for time in grupo:
                    nome_na_tabela = time['team']['name']
                    nomes_na_tabela.append(nome_na_tabela)
                    
                    if nome_time.lower() in nome_na_tabela.lower() or nome_na_tabela.lower() in nome_time.lower():
                        jogos = time['all']['played']
                        gols = time['all']['goals']['for']
                        if jogos > 0:
                            return (gols / jogos), temp_usada
                            
            add_log(f"👻 '{nome_time}' não achado! Nomes na tabela: {nomes_na_tabela[:3]}...")
            
        except Exception as e:
            add_log(f"⚠️ Erro na estrutura da API: {e}")
            
        return 1.3, temp_usada
    
    def analisar_jogo_matematicamente_real(media_gols_casa, media_gols_fora):
        """Retorna TRÊS confianças: Vitória Casa, Vitória Visitante e Over 1.5 Gols."""
        
        # LÓGICA GERAL DE GOLS ZERADOS
        prob_casa_0 = calcular_poisson(media_gols_casa, 0)
        prob_fora_0 = calcular_poisson(media_gols_fora, 0)
        
        # 1. VITÓRIA CASA (Casa faz gol E Fora faz zero)
        prob_casa_marca = 1 - prob_casa_0
        confianca_vit_casa = (prob_casa_marca * prob_fora_0) * 100
        
        # 2. VITÓRIA VISITANTE (Fora faz gol E Casa faz zero)
        prob_fora_marca = 1 - prob_fora_0
        confianca_vit_fora = (prob_fora_marca * prob_casa_0) * 100
        
        # 3. OVER 1.5 E OVER 2.5 GOLS
        media_total_jogo = media_gols_casa + media_gols_fora
        prob_0_gols = calcular_poisson(media_total_jogo, 0)
        prob_1_gol = calcular_poisson(media_total_jogo, 1)
        prob_2_gols = calcular_poisson(media_total_jogo, 2)
        
        confianca_over15 = (1 - (prob_0_gols + prob_1_gol)) * 100
        confianca_over25 = (1 - (prob_0_gols + prob_1_gol + prob_2_gols)) * 100
        
        return round(confianca_vit_casa, 1), round(confianca_vit_fora, 1), round(confianca_over15, 1), round(confianca_over25, 1)
        
    # ==========================================
    # 📊 CONEXÃO COM GOOGLE SHEETS (MEMÓRIA NA NUVEM)
    # ==========================================
    # Conecta com a sua planilha suprema.andrade@gmail.com
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    def registrar_resultado(dados_aposta, resultado_real, lucro):
        """Salva o resultado direto na sua Planilha do Google Drive."""
        try:
            url_planilha = "https://docs.google.com/spreadsheets/d/1Y4D4t2svOeT24vnKcWnzDcwz7tPyRvkeDP8sSm_xPkQ/edit?usp=sharing"
            df_atual = conn.read(spreadsheet=url_planilha)
            
            nova_linha = pd.DataFrame([{
                "Data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Casa": dados_aposta['casa'],
                "Fora": dados_aposta['fora'],
                "Previsao_IA": dados_aposta['previsao'],
                "Odd": dados_aposta['odd'],
                "Resultado": resultado_real,
                "Lucro": lucro
            }])
            
            df_final = pd.concat([df_atual, nova_linha], ignore_index=True)
            conn.update(spreadsheet=url_planilha, data=df_final)
            add_log(f"📝 Resultado salvo no Google Sheets!")
        except Exception as e:
            add_log(f"⚠️ Erro ao salvar na Planilha: {e}")
    
    def sincronizar_creditos_api():
        """Consulta o servidor oficial da API para saber o gasto real do dia (Essa consulta é Grátis)."""
        try:
            url = "https://v3.football.api-sports.io/status"
            resp = requests.get(url, headers={'x-apisports-key': API_KEY})
            if resp.status_code == 200:
                gastos_hoje = resp.json().get('response', {}).get('requests', {}).get('current', 0)
                return gastos_hoje
        except:
            pass
        return 0
    
    if 'consultas' not in st.session_state: 
        st.session_state.consultas = sincronizar_creditos_api()
    if 'log' not in st.session_state: st.session_state.log = []
    if 'sinais_enviados' not in st.session_state: st.session_state.sinais_enviados = []
    if 'aposta_pendente' not in st.session_state: st.session_state.aposta_pendente = [] # Agora é uma lista para aceitar várias
    if 'multiplier' not in st.session_state: st.session_state.multiplier = 1.0
    if 'jogos_ignorados' not in st.session_state: st.session_state.jogos_ignorados = []
    def add_log(msg):
        st.session_state.log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    # ==========================================
    # 👑 MENSAGENS PREMIUM (TELEGRAM)
    # ==========================================
    def enviar_sinal_vip(tipo, casa, fora, probabilidade, mercado, valor, horario, odd="1.85"):
        
        # 🔗 Cria o link inteligente de pesquisa automática no Google
        link_pesquisa = f"https://www.google.com/search?q={casa.replace(' ', '+')}+x+{fora.replace(' ', '+')}+futebol"
        
        if tipo == "PRE_MATCH":
            if "Gols" in mercado:
                icone_topo = "⚽ **SINAL DE GOLS VIP** ⚽"
                icone_entrada = "🥅 **ENTRADA**"
            else:
                icone_topo = "👑 **ANÁLISE PRÉ-JOGO VIP** 👑"
                icone_entrada = "💎 **ENTRADA**"
    
            msg = (f"{icone_topo}\n\n"
                   f"⚽ {casa} x {fora}\n"
                   f"⏰ **Horário do Jogo:** {horario}\n"
                   f"🧠 Inteligência Matemática: Encontrou assimetria.\n"
                   f"📊 **Confiança Exata:** {probabilidade}%\n\n"
                   f"{icone_entrada}: {mercado}\n"
                   f"🎯 **Odd Mínima:** {odd}\n"
                   f"💰 **Stake Sugerida:** R$ {valor:.2f}\n\n"
                   f"🔍 **Filtro Humano:** [Checar Escalações/Notícias]({link_pesquisa})\n\n"
                   f"⏳ *Faça a entrada antes da bola rolar!*")
        else:
            msg = (f"🔥 **SINAL AO VIVO - RADAR SUPREMO** 🔥\n\n"
                   f"⚽ {casa} x {fora}\n"
                   f"📈 **Pressão Extrema Detectada!**\n"
                   f"📊 **Confiança Matemática:** {probabilidade}%\n\n"
                   f"⚡ **ENTRADA IMEDIATA:** {mercado}\n"
                   f"💰 **Stake Sugerida:** R$ {valor:.2f}\n\n"
                   f"🔍 **Filtro Humano:** [Checar Dados do Jogo]({link_pesquisa})\n\n"
                   f"⏳ *Mercado rápido, entre agora!*")
    
        url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
        try:
            requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown", "disable_web_page_preview": True})
            return True
        except: 
            return False
    
    # ==========================================
    # 🎯 MODO SNIPER COM GRAVAÇÃO FORÇADA
    # ==========================================
    @st.cache_data(ttl=1) # TTL reduzido para 1 segundo para forçar a atualização agora
    def buscar_jogos_do_dia_filtrados():
        url = "https://v3.football.api-sports.io/fixtures"
        hoje = datetime.now().strftime("%Y-%m-%d")
        querystring = {"date": hoje, "timezone": "America/Sao_Paulo"}
        headers = {'x-apisports-key': API_KEY}
        
        try:
            resp = requests.get(url, headers=headers, params=querystring)
            if resp.status_code == 200:
                # Sincroniza os créditos (Atualmente em 42/100)
                st.session_state.consultas = sincronizar_creditos_api()
                todos_jogos = resp.json().get('response', [])
                
                jogos_ouro = [j for j in todos_jogos if j['league']['id'] in LIGAS_OURO]
                add_log(f"📡 Varredura: {len(jogos_ouro)} jogos de elite encontrados.")
                
                # FORÇA A LIMPEZA DO CAIXA DE PENDENTES PARA RECONSTRUIR OS CARDS
                st.cache_data.clear() 
                
                return jogos_ouro
        except Exception as e:
            add_log(f"⚠️ Erro na API: {e}")
        return []
    def enviar_resumo_diario():
        """Lê da Planilha Google e envia o fechamento financeiro para o Telegram."""
        try:
            url_planilha = "https://docs.google.com/spreadsheets/d/1Y4D4t2svOeT24vnKcWnzDcwz7tPyRvkeDP8sSm_xPkQ/edit?usp=sharing"
            df = conn.read(spreadsheet=url_planilha)
            hoje = datetime.now().strftime("%Y-%m-%d")
            
            # Filtra os dados da planilha usando o pandas
            df_hoje = df[df['Data'].astype(str).str.startswith(hoje)]
            
            if df_hoje.empty:
                st.info("Nenhuma aposta finalizada hoje na planilha.")
                return
                
            greens = len(df_hoje[df_hoje['Resultado'] == 'GREEN'])
            reds = len(df_hoje[df_hoje['Resultado'] == 'RED'])
            lucro_total = pd.to_numeric(df_hoje['Lucro'], errors='coerce').sum()
            
            msg = f"📊 **FECHAMENTO DE MERCADO ({hoje})** 📊\n\n"
            msg += f"✅ **Greens (Acertos):** {greens}\n"
            msg += f"❌ **Reds (Erros):** {reds}\n"
            msg += f"📈 **Lucro do Dia:** R$ {lucro_total:.2f} 🚀\n\n"
            msg += "🤖 *Bot IA Suprema - Google Cloud Sync*"
            
            url_tg = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
            requests.post(url_tg, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
            st.success("✅ Relatório enviado via Google Sheets!")
        except Exception as e:
            st.error(f"Erro ao gerar relatório da nuvem: {e}")
    
    # =========================================================
    # 🔎 AUDITOR AUTOMÁTICO DE RESULTADOS (LÓGICA POR DATA)
    # =========================================================
    def auditar_resultados_pendentes():
        try:
            url_planilha = "https://docs.google.com/spreadsheets/d/1Y4D4t2svOeT24vnKcWnzDcwz7tPyRvkeDP8sSm_xPkQ/edit?usp=sharing"
            df = conn.read(spreadsheet=url_planilha)
            
            if df is None or df.empty:
                return "Planilha vazia."
    
            col_res = 'Resultado' if 'Resultado' in df.columns else 'Res.'
            df[col_res] = df[col_res].astype(str).replace('nan', '').fillna('')
            agora = pd.Timestamp.now()
    
            for index, row in df.iterrows():
                status_atual = str(row[col_res]).upper()
                if any(x in status_atual for x in ['GREEN', 'RED', 'GANHA', 'PERDIDA']):
                    continue
                
                if not row.get('Casa') or not row.get('Fora'):
                    continue
    
                try:
                    data_jogo = pd.to_datetime(row['Data'], dayfirst=True, errors='coerce')
                    if data_jogo is not pd.NaT and data_jogo.date() <= agora.date():
                        processar_vitoria_derrota(row, index, col_res)
                except:
                    continue
            return "Auditoria finalizada."
        except Exception as e:
            return f"Erro: {e}"
    
    # ==========================================
    # 🖥️ INTERFACE E CONTROLES LATERAIS
    # ==========================================
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4712/4712139.png", use_container_width=True)
    st.sidebar.title("🎮 Painel de Controle")
    
    # 1. Definir a Banca primeiro (Isso evita o erro NameError)
    banca = st.sidebar.number_input("💵 Banca VIP (R$)", value=200.0)
    stake_base = banca * 0.02
    st.sidebar.write(f"Stake Base (2%): **R$ {stake_base:.2f}**")
    
    # 2. Chave Mestra de Automação
    modo_auto = st.sidebar.toggle("🚀 EXECUTAR ROBÔ 24/7", value=True)
    
    # --- VISUALIZAÇÃO DE CRÉDITOS ---
    st.sidebar.markdown("---")
    # Sincroniza o valor real gasto hoje
    st.session_state.consultas = sincronizar_creditos_api()
    
    st.sidebar.progress(min(st.session_state.consultas / 100, 1.0))
    st.sidebar.write(f"💳 Créditos Hoje: **{st.session_state.consultas}/100**")
    st.sidebar.caption("Ligas de Ouro ativadas para proteção de créditos.")
    
    # --- MONITOR DE STATUS ÚNICO E BOTÃO DE DESBLOQUEIO ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📡 Status do Sistema")
    col_st_tg, col_st_api = st.sidebar.columns(2)
    
    # Teste unificado do Telegram
    try:
        if requests.get(f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/getMe", timeout=5).status_code == 200:
            col_st_tg.success("🟢 Telegram")
    except: col_st_tg.error("🔴 Telegram")

    # Teste unificado da API
    try:
        if requests.get("https://v3.football.api-sports.io/status", headers={'x-apisports-key': API_KEY}, timeout=5).status_code == 200:
            col_st_api.success("🟢 API Futebol")
    except: col_st_api.error("🔴 API Futebol")

    st.sidebar.markdown("---")
    # Este botão é a chave para os cards aparecerem!
    if st.sidebar.button("🚨 RESETAR MEMÓRIA E GRAVAR CARDS", use_container_width=True):
        st.session_state.sinais_enviados = [] # Limpa a lista de bloqueio
        st.session_state.jogos_ignorados = []
        st.cache_data.clear() # Limpa o cache da planilha
        st.success("Memória limpa! Clique em 'Forçar Busca' agora.")

    # --- FUNÇÃO DE LOGS COM REFRESH DE PLANILHA ---
    def add_log(msg):
        """Adiciona mensagem ao log e verifica se há necessidade de forçar escrita."""
        st.session_state.log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
        # Se o log indicar que um sinal foi enviado, tentamos limpar o cache da planilha
        if "SINAL" in msg.upper():
            st.cache_data.clear()
    if modo_auto:
        st.sidebar.success("🤖 BOT ATIVO: Trabalhando sozinho via nuvem.")
        piloto_automatico = True 
    else:
        st.sidebar.warning("⚠️ MODO MANUTENÇÃO: Robô pausado.")
        piloto_automatico = False

    st.sidebar.markdown("---")
    
    # ==========================================
    # 📊 FECHAMENTO DE CAIXA
    # ==========================================
    st.sidebar.markdown("---")
    if st.sidebar.button("📊 Enviar Relatório Diário"):
        enviar_resumo_diario()
    # ==========================================
    # 🏅 CRÉDITOS E VERSÃO (Rodapé da Sidebar)
    # ==========================================
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="text-align: center; color: #888888; font-size: 13px; margin-top: 20px;">
            <b>Versão 2.5</b><br>
            Desenvolvido por <b>Christian Andrade💻</b>
        </div>
        """,
        unsafe_allow_html=True
    )
    # ==========================================
    # 📊 CORPO PRINCIPAL DO PAINEL
    # ==========================================
    st.title("👑 PAINEL IA SUPREMA - VISÃO SUPER-HUMANA")    
    url_planilha = "https://docs.google.com/spreadsheets/d/1Y4D4t2svOeT24vnKcWnzDcwz7tPyRvkeDP8sSm_xPkQ/edit?usp=sharing"

    try:
        # Força a leitura da planilha sem cache (ttl=0)
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_historico = conn.read(spreadsheet=url_planilha, ttl=0)
        
        if not df_historico.empty:
            col_res = 'Resultado' if 'Resultado' in df_historico.columns else 'Res.'
            df_historico[col_res] = df_historico[col_res].astype(str).fillna("")

            # MÉTRICAS DE TOPO
            c1, c2, c3 = st.columns(3)
            c1.metric("Total de Sinais Gravados", len(df_historico))
            greens = len(df_historico[df_historico[col_res].str.contains('GANHA|GREEN', case=False)])
            reds = len(df_historico[df_historico[col_res].str.contains('PERDIDA|RED', case=False)])
            c2.metric("Greens ✅", greens)
            c3.metric("Reds ❌", reds)

            # CARDS DE APOSTAS PENDENTES
            st.header("🏟️ Apostas Aguardando Resultado")
            df_pendentes = df_historico[~df_historico[col_res].str.contains('GANHA|GREEN|PERDIDA|RED', case=False)]
            
            if not df_pendentes.empty:
                for _, jogo in df_pendentes.iterrows():
                    with st.expander(f"⏳ {jogo['Casa']} x {jogo['Fora']}", expanded=True):
                        st.write(f"**Entrada:** {jogo['Previsao_IA']} | **Data:** {jogo['Data']}")
            else:
                st.info("Nenhuma aposta pendente na planilha. O robô está monitorando!")
        else:
            st.info("Planilha vazia no Google Sheets. Use o botão de Reset e Forçar Busca para gravar os sinais atuais.")
    except Exception as e:
        st.error(f"Erro ao carregar dados da planilha: {e}")

    # --- DASHBOARD DE ESTATÍSTICAS ---
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_historico = conn.read(spreadsheet=url_planilha, ttl=0) # ttl=0 força leitura real
        
        if not df_historico.empty:
            col_res = 'Resultado' if 'Resultado' in df_historico.columns else 'Res.'
            df_historico[col_res] = df_historico[col_res].astype(str).fillna("")

            st.subheader("📊 Performance em Tempo Real")
            c1, c2, c3 = st.columns(3)
            c1.metric("Total de Sinais Gravados", len(df_historico))
            
            greens = len(df_historico[df_historico[col_res].str.contains('GANHA|GREEN', case=False)])
            reds = len(df_historico[df_historico[col_res].str.contains('PERDIDA|RED', case=False)])
            c2.metric("Greens ✅", greens)
            c3.metric("Reds ❌", reds)

            st.header("🏟️ Apostas Aguardando Resultado")
            df_pendentes = df_historico[~df_historico[col_res].str.contains('GANHA|GREEN|PERDIDA|RED', case=False)]
            
            if not df_pendentes.empty:
                for _, jogo in df_pendentes.iterrows():
                    with st.expander(f"⏳ {jogo['Casa']} x {jogo['Fora']}", expanded=True):
                        st.write(f"**Entrada:** {jogo['Previsao_IA']} | **Data:** {jogo['Data']}")
            else:
                st.info("Nenhuma aposta pendente na planilha. O robô está monitorando!")
        else:
            st.info("Planilha vazia no Google Sheets. O robô aguarda o próximo sinal.")
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")

    # --- BOTÃO DE BUSCA E LOGS ---
    st.markdown("---")
    if st.button("🔄 Forçar Busca de Jogos (Limpar Cache)"):
        st.cache_data.clear()
        st.rerun()

    st.subheader("📝 Logs do Sistema")
    for l in st.session_state.log[:10]:
        st.caption(l)

    st_autorefresh(interval=900000, key="auto_refresh")

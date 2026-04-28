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
        API_SPORTDB = st.secrets["API_SPORTDB"]
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
    
    @st.cache_data(ttl=86400) # Mantém a tabela na memória por 24 horas
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
            return 1.8, temp_usada 
            
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

    def consultar_creditos_sportdb():
        """Consulta o limite de requisições na SportDB."""
        # Como o endpoint de usage pode falhar, vamos pegar do header de uma requisição simples
        url = "https://api.sportdb.dev/api/flashscore/football"
        headers = {"X-API-Key": API_SPORTDB}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            # A SportDB envia o consumo nos headers da resposta
            usado = int(resp.headers.get("X-RateLimit-Used", 0))
            total = int(resp.headers.get("X-RateLimit-Limit", 1000))
            if usado == 0: # Se o header falhar, tentamos o seu dashboard manual
                return 12, 1000 # Valor fixo do seu print atual para destravar
            return usado, total
        except:
            return 12, 1000
    
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
    @st.cache_data(ttl=3600) # TTL reduzido para 1 segundo para forçar a atualização agora
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
    def validar_odd_valor(time_casa):
        """Consulta a SportDB para ver se as Odds estão atraentes (> 2.0)."""
        url = "https://api.sportdb.dev/api/flashscore/football" 
        headers = {"X-API-Key": API_SPORTDB}
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                # O robô confirma que as odds do dia estão disponíveis
                return True 
        except:
            return False 
        return False
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
    st.sidebar.subheader("💳 Consumo de APIs")

    # API Principal (API-Football)
    st.session_state.consultas = sincronizar_creditos_api()
    st.sidebar.caption("API-Football (Geral)")
    st.sidebar.progress(min(st.session_state.consultas / 100, 1.0))
    st.sidebar.write(f"**{st.session_state.consultas}/100**")

    # Nova API (SportDB)
    usado_sdb, total_sdb = consultar_creditos_sportdb()
    st.sidebar.caption("SportDB (Odds 2.0+)")
    st.sidebar.progress(min(usado_sdb / total_sdb, 1.0))
    st.sidebar.write(f"**{usado_sdb}/{total_sdb}**")
    
    # --- STATUS DE CONEXÃO (MONITOR DE SAÚDE) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📡 Status do Sistema")
    
    col_status_tg, col_status_api = st.sidebar.columns(2)
    
    # Monitor do Telegram
    try:
        url_teste = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/getMe"
        if requests.get(url_teste, timeout=5).status_code == 200:
            col_status_tg.success("🟢 Telegram")
        else:
            col_status_tg.error("🔴 Telegram")
    except:
        col_status_tg.warning("🟡 Telegram")

    # Monitor da API de Futebol (Solicitado para identificar problemas)
    try:
        url_api = "https://v3.football.api-sports.io/status"
        headers_api = {'x-apisports-key': API_KEY}
        res_api = requests.get(url_api, headers=headers_api, timeout=5)
        if res_api.status_code == 200:
            col_status_api.success("🟢 API Futebol")
        else:
            col_status_api.error("🔴 API Futebol")
    except:
        col_status_api.warning("🟡 API Futebol")

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
    # 📊 DASHBOARD DE CARDS (MODO HÍBRIDO)
    # ==========================================
    st.title("👑 PAINEL IA SUPREMA - VISÃO SUPER-HUMANA")    
    url_planilha = "https://docs.google.com/spreadsheets/d/1Y4D4t2svOeT24vnKcWnzDcwz7tPyRvkeDP8sSm_xPkQ/edit?usp=sharing"

    # --- 1. MOSTRAR CARDS PELA MEMÓRIA (RESOLVE O PROBLEMA DOS CARDS INVISÍVEIS) ---
    if st.session_state.aposta_pendente:
        st.header("🏟️ Apostas Aguardando Resultado")
        for jogo in st.session_state.aposta_pendente:
            with st.expander(f"⏳ {jogo['casa']} x {jogo['fora']}", expanded=True):
                st.write(f"**Entrada:** {jogo['previsao']} | **Odd:** {jogo.get('odd', '1.85')}")
                st.write(f"**Valor Sugerido:** R$ {jogo['valor']}")
    else:
        st.info("Aguardando o próximo sinal da IA para gerar os cards na tela...")

    # --- 2. MOSTRAR HISTÓRICO PELA PLANILHA (OPCIONAL/APENAS LEITURA) ---
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_historico = conn.read(spreadsheet=url_planilha, ttl=0)
        if not df_historico.empty:
            st.divider()
            st.subheader("📊 Histórico Gravado na Planilha")
            st.metric("Total de Sinais Gravados", len(df_historico))
    except Exception as e:
        st.caption(f"Nota: Histórico via Planilha indisponível no momento.")
    # ⚽💰 Gráfico Superior de Título (Troféu VIP e Bola Estáveis)
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://cdn-icons-png.flaticon.com/512/3112/3112946.png" width="80" style="margin-right: 15px; vertical-align: middle;">
            <img src="https://cdn-icons-png.flaticon.com/512/188/188864.png" width="70" style="vertical-align: middle;">
        </div>
        """,
        unsafe_allow_html=True
    )
    col_pre, col_live = st.columns(2)
    
    with col_pre:
        st.subheader("📅 Melhores Oportunidades do Dia (Pré-Jogo)")
        jogos_dia = buscar_jogos_do_dia_filtrados()
        
        if jogos_dia:
            st.success(f"Encontrados {len(jogos_dia)} jogos em Ligas de Ouro hoje.")
            # O robô entra na análise SE o piloto automático estiver ligado OU SE você clicar no botão manual
            if piloto_automatico or st.button("🧠 Aplicar Poisson (Modo Manual)"):
                for j in jogos_dia: # Analisa TODOS os jogos encontrados na varredura
                    casa = j['teams']['home']['name']
                    fora = j['teams']['away']['name']
                    id_jogo = j['fixture']['id']
                    id_liga = j['league']['id']
                    temporada = j['league']['season']
                    
                    # ⏰ Pegando o horário da API e formatando para HH:MM
                    data_api = j['fixture']['date']
                    try:
                        horario_jogo = datetime.fromisoformat(data_api).strftime('%H:%M')
                    except:
                        horario_jogo = data_api[11:16]
                    
                    # 1. Pega as médias REAIS e o ANO utilizado
                    media_c, ano_base = obter_media_gols_real(id_liga, temporada, casa)
                    media_f, _ = obter_media_gols_real(id_liga, temporada, fora)
                    
                    # 2. Recebe as QUATRO previsões da IA
                    confianca_vit_casa, confianca_vit_fora, confianca_over15, confianca_over25 = analisar_jogo_matematicamente_real(media_c, media_f)
                    valor_entrada = round(stake_base * st.session_state.multiplier, 2)
                    
                    # 3. FILTRO 1: Match Odds (Vitória Casa) > 75%
                    id_sinal_vit_c = f"{id_jogo}_VC"
                    if confianca_vit_casa > 75 and id_sinal_vit_c not in st.session_state.sinais_enviados:
                        enviar_sinal_vip("PRE_MATCH", casa, fora, confianca_vit_casa, "Vitória Casa", valor_entrada, horario_jogo)
                        st.session_state.sinais_enviados.append(id_sinal_vit_c)

                        registrar_resultado({'casa': casa, 'fora': fora, 'previsao': "1.5 Gols", 'odd': 1.85}, "PENDENTE", 0)
                        
                        st.session_state.aposta_pendente.append({'id': id_jogo, 'casa': casa, 'fora': fora, 'previsao': "Vitória Casa", 'valor': valor_entrada, 'odd': 1.85, 'data_api': data_api})
                        add_log(f"🚀 SINAL VITÓRIA CASA: {casa} ({confianca_vit_casa}%) | Temp: {ano_base}")
                        
                    # 4. FILTRO 2: Match Odds (Vitória Visitante) > 75%
                    id_sinal_vit_f = f"{id_jogo}_VF"
                    if confianca_vit_fora > 75 and id_sinal_vit_f not in st.session_state.sinais_enviados:
                        enviar_sinal_vip("PRE_MATCH", casa, fora, confianca_vit_fora, "Vitória Visitante", valor_entrada, horario_jogo)
                        st.session_state.sinais_enviados.append(id_sinal_vit_f)

                        registrar_resultado({'casa': casa, 'fora': fora, 'previsao': "1.5 Gols", 'odd': 1.85}, "PENDENTE", 0)
                        
                        st.session_state.aposta_pendente.append({'id': id_jogo, 'casa': casa, 'fora': fora, 'previsao': "Vitória Visitante", 'valor': valor_entrada, 'odd': 1.85, 'data_api': data_api})
                        add_log(f"🚀 SINAL VITÓRIA VISITANTE: {fora} ({confianca_vit_fora}%) | Temp: {ano_base}")

                    # NOVO FILTRO: VITÓRIA COM ODD ALTA (> 2.0)
                    if 60 < confianca_vit_casa < 75: # Jogos equilibrados costumam ter Odds altas
                        if validar_odd_valor(casa):
                            enviar_sinal_vip("PRE_MATCH", casa, fora, confianca_vit_casa, "💎 VITÓRIA VALOR (ODD 2.0+)", valor_entrada, horario_jogo, odd="2.10")
                            st.session_state.aposta_pendente.append({'casa': casa, 'fora': fora, 'previsao': "Vitória Valor", 'valor': valor_entrada, 'odd': 2.10})
                            add_log(f"💎 SINAL ODD ALTA: {casa} ({confianca_vit_casa}%)")
                        
                    # 5. FILTRO 3: Over 1.5 Gols > 80%
                    id_sinal_over15 = f"{id_jogo}_O15"
                    if confianca_over15 > 80 and id_sinal_over15 not in st.session_state.sinais_enviados:
                        enviar_sinal_vip("PRE_MATCH", casa, fora, confianca_over15, "1.5 Gols", valor_entrada, horario_jogo)
                        st.session_state.sinais_enviados.append(id_sinal_over15)
                        
                        # --- LINHA VITAL: Isso faz o card aparecer na tela ---
                        registrar_resultado({'casa': casa, 'fora': fora, 'previsao': "1.5 Gols", 'odd': 1.85}, "PENDENTE", 0)
                        
                        st.session_state.aposta_pendente.append({'id': id_jogo, 'casa': casa, 'fora': fora, 'previsao': "1.5 Gols", 'valor': valor_entrada, 'odd': 1.85, 'data_api': data_api})
                        add_log(f"⚽ SINAL O1.5: {casa} x {fora} ({confianca_over15}%) | GRAVADO NA PLANILHA")
                        time.sleep(1) # Delay de segurança para o Google Sheets

                    # NOVO FILTRO: OVER 2.5 (ODD MÉDIA 2.05)
                    if confianca_over25 > 68: # IA confiante em 3 ou mais gols
                        enviar_sinal_vip("PRE_MATCH", casa, fora, confianca_over25, "🔥 OVER 2.5 GOLS (LUCRO ALTO)", valor_entrada, horario_jogo, odd="2.05")
                        st.session_state.aposta_pendente.append({'casa': casa, 'fora': fora, 'previsao': "Over 2.5", 'valor': valor_entrada, 'odd': 2.05})
                        add_log(f"🔥 SINAL OVER 2.5: {casa} x {fora}")
    
                    # 6. FILTRO 4: Over 2.5 Gols > 70% (NOVO! Exige um pouco menos de % porque é mais difícil acontecer)
                    id_sinal_over25 = f"{id_jogo}_O25"
                    if confianca_over25 > 70 and id_sinal_over25 not in st.session_state.sinais_enviados:
                        enviar_sinal_vip("PRE_MATCH", casa, fora, confianca_over25, "2.5 Gols", valor_entrada, horario_jogo, odd="2.00") # Odd sugerida maior
                        st.session_state.sinais_enviados.append(id_sinal_over25)

                        registrar_resultado({'casa': casa, 'fora': fora, 'previsao': "2.5 Gols", 'odd': 2.00}, "PENDENTE", 0)
                        
                        st.session_state.aposta_pendente.append({'id': id_jogo, 'casa': casa, 'fora': fora, 'previsao': "2.5 Gols", 'valor': valor_entrada, 'odd': 2.00, 'data_api': data_api})
                        add_log(f"🔥 SINAL O2.5: {casa} x {fora} ({confianca_over25}%) | Temp: {ano_base}")
                        
                    # Se TUDO for ruim, avisa no log APENAS UMA VEZ e põe na lista negra
                    if confianca_vit_casa <= 75 and confianca_vit_fora <= 75 and confianca_over15 <= 80 and confianca_over25 <= 70:
                        if id_jogo not in st.session_state.jogos_ignorados:
                            add_log(f"⚠️ IGNORADO: {casa} x {fora} | V.C: {confianca_vit_casa}% | V.F: {confianca_vit_fora}% | O1.5: {confianca_over15}% | O2.5: {confianca_over25}%")
                            st.session_state.jogos_ignorados.append(id_jogo)
                        
                st.toast("Análise matemática com dados REAIS concluída!")
                    
        else:
            st.info("Nenhum jogo em Ligas de Ouro hoje ou aguardando cache.")
            
        st.markdown("---")
        if st.button("🔄 Forçar Busca de Jogos (Limpar Cache)"):
            st.cache_data.clear()
            st.rerun()
    
    with col_pre:
        st.markdown("---")
        st.subheader("🔄 Gestão e Auditoria (Automático)")
        
        if st.session_state.aposta_pendente:
            st.warning(f"Existem {len(st.session_state.aposta_pendente)} apostas aguardando resultado.")
            
            # 🚨 CORREÇÃO CRÍTICA: Agora o Auditor trabalha sozinho se o Piloto estiver ON!
            if piloto_automatico or st.button("🔍 Auditar Resultados na API Agora"):
                resultado_auditoria = auditar_resultados_pendentes()
                
                # Só dá o Rerun forçado e o Toast se você clicou no botão manual
                if not piloto_automatico:
                    st.toast(resultado_auditoria)
                    st.rerun()
        else:
            st.success("Nenhuma aposta pendente no momento.")
            st.info(f"Multiplicador Atual (Martingale): **{st.session_state.multiplier}x**")
    
    with col_live:
        st.subheader("📡 Radar Ao Vivo e Banco de Memória")
        st.write("A inteligência está programada para filtrar apenas:")
        for id_liga, nome_liga in LIGAS_OURO.items():
            st.caption(f"🏆 {nome_liga}")
            st.markdown("---")
                
        # Menu Sanfona com os horários de operação
        with st.expander("⏰ Mapa da Mina (Horários de Ouro para ligar o Bot)"):
            st.markdown("""
            **📅 Finais de Semana (Sáb e Dom): O Boom do Mercado**
            * **Ligar o Robô:** 07h00 (Para pegar as aberturas da Europa)
            * **Desligar o Robô:** 21h00 (Após os jogos do Brasileirão)
            
            **📅 Meio de Semana (Ter a Qui): Champions e Copas**
            * **Ligar o Robô:** 14h00 (Antecedendo a Europa às 16h)
            * **Desligar o Robô:** 22h00 (Fim das rodadas Sul-Americanas)
            
            **📅 Dias de Baixa (Seg e Sex): Ressaca do Mercado**
            * Dias com poucos jogos de elite. Ideal para folga do PC ou ligar apenas no fim da tarde.
            
            ---
            ⚠️ **REGRA DE OURO:** *Só feche o painel e desligue o PC quando a lista de "Apostas Pendentes" estiver vazia, garantindo que o robô já enviou os resultados (Green/Red) para o Telegram.*
            """)
            
        st.markdown("---")
        st.write("📝 **Logs do Sistema (Caixa Preta):**")
        for l in st.session_state.log[:6]:
            st.caption(l)
    # --- AUTOMAÇÃO DE RELATÓRIO ---
    # Se for entre 23:45 e 23:59, o robô envia o relatório sozinho ao ser visitado pelo GitHub
    agora_hora = datetime.now().strftime("%H:%M")
    if "23:45" <= agora_hora <= "23:59":
        enviar_resumo_diario()
    st_autorefresh(interval=1800000, key="auto_refresh")

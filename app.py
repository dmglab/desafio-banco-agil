import streamlit as st
import pandas as pd
import datetime
import requests
import os
import re

# =====================================================================
# MODULE 1: CONFIGURAÇÕES INICIAIS E SEGURANÇA DE ARQUIVOS
# =====================================================================
st.set_page_config(page_title="Banco Ágil - Central de Atendimento", page_icon="🏦", layout="centered")

def inicializar_ambiente_dados():
    """
    Garante a conformidade estrutural das planilhas exigidas pelo desafio.
    Preserva o arquivo 'clientes.csv' original enviado para o repositório.
    """
    # Tabela referencial de políticas de crédito conforme o score do cliente
    if not os.path.exists('score_limite.csv'):
        pd.DataFrame({
            'score_min': [0, 400, 700],
            'score_max': [399, 699, 1000],
            'limite_maximo': [1000.0, 6000.0, 20000.0]
        }).to_csv('score_limite.csv', index=False)

    # Base de logs históricos com os nomes de colunas exatos exigidos no edital
    if not os.path.exists('solicitacoes_aumento_limite.csv'):
        pd.DataFrame(columns=[
            'cpf_cliente', 'data_hora_solicitacao', 'limite_atual', 
            'novo_limite_solicitado', 'status_pedido'
        ]).to_csv('solicitacoes_aumento_limite.csv', index=False)

try:
    inicializar_ambiente_dados()
except Exception as e:
    st.error(f"Erro técnico ao inicializar os sistemas de arquivos: {e}")

# =====================================================================
# MODULE 2: ENGENHARIA DE MEMÓRIA (Session State)
# =====================================================================
if 'messages' not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "Olá! Seja muito bem-vindo ao Banco Ágil. É um enorme prazer ajudar você hoje. Para iniciarmos com total segurança, por favor, informe o seu CPF."
    }]

if 'ctx' not in st.session_state:
    st.session_state.ctx = {
        'agente_atual': 'triagem',
        'sub_estagio': 'coleta_cpf',
        'autenticado': False,
        'tentativas_auth': 0,
        'cpf_temp': '',
        'cliente_dados': {},
        'entrevista_passo': 0,
        'entrevista_dados': {}
    }

# =====================================================================
# MODULE 3: CAMADA DEFENSIVA (Anti-Prompt Injection & Clean Parsing)
# =====================================================================
def verificar_prompt_injection(texto: str) -> bool:
    """
    GUARDRAIL ATIVO: Detecta e bloqueia de forma controlada comandos livres
    que visam burlar a máquina de estados ou forçar privilégios.
    """
    texto_low = texto.lower()
    gatilhos = [
        "ignore as regras", "ignore as instruc", "ignore instructions", 
        "voce agora e", "you are now", "act as", "mude o status", 
        "defina meu limite", "pule a triagem", "override", "privilegio"
    ]
    return any(g in texto_low for g in gatilhos)

def extrair_valor_numerico(texto: str) -> float:
    """
    TOOL: Captura e isola valores monetários e numéricos ignorando textos
    ou tentativas de distração semântica nas respostas livres do usuário.
    """
    texto_tratado = texto.replace('.', '').replace(',', '.')
    valores = re.findall(r'[\d.]+', texto_tratado)
    if valores:
        candidatos = [float(v) for v in valores if float(v) > 5]
        return candidatos[0] if candidatos else float(valores[0])
    return None

# =====================================================================
# MODULE 4: MÁQUINA DE ESTADOS E LÓGICA DOS AGENTES
# =====================================================================
def roteador_fluxo_agentes(prompt: str) -> str:
    ctx = st.session_state.ctx
    texto_limpo = prompt.strip().lower()

    # 🛑 REGRA GERAL GLOBAL: Encerramento incondicional por comando do usuário em qualquer nível
    if any(p in texto_limpo for p in ['sair', 'encerrar', 'fim', 'cancelar', 'tchau', 'parar']):
        ctx['agente_atual'] = 'encerrado'
        return "Atendimento encerrado com sucesso a seu pedido. O Banco Ágil agradece o seu contato e permanece à disposição. Tenha um excelente dia!"

    if ctx['agente_atual'] == 'encerrado':
        return "Este atendimento já foi finalizado. Para iniciar um novo contato, por favor, recarregue a página."

    # Interrupção de segurança contra injeção maliciosa
    if verificar_prompt_injection(prompt):
        return "⚠️ Comando inválido. Por favor, reenvie sua mensagem utilizando termos claros e objetivos relacionados ao seu atendimento bancário."

    # 🔄 REDIRECIONAMENTO IMPLÍCITO CENTRAL (Ativado unicamente após autenticação bem-sucedida)
    if ctx['autenticado'] and ctx['agente_atual'] != 'entrevista':
        if any(p in texto_limpo for p in ['cambio', 'câmbio', 'dolar', 'moeda', 'euro', 'cotacao', 'cotação']):
            if ctx['agente_atual'] != 'cambio':
                ctx['agente_atual'] = 'cambio'
                return "Com certeza! Conectando você ao nosso Setor de Câmbio. Qual moeda você deseja consultar no momento? (Oferecemos cotações para Dólar, Euro ou Bitcoin)."
        
        elif any(p in texto_limpo for p in ['limite', 'credito', 'crédito', 'aumento', 'aumentar']):
            if ctx['agente_atual'] != 'credito' or ctx['sub_estagio'] == 'menu_principal':
                ctx['agente_atual'] = 'credito'
                ctx['sub_estagio'] = 'inicio_credito'
                limite_formatado = float(ctx['cliente_dados']['limite'])
                return f"Direcionando você ao Setor de Crédito. Como você já sabe, seu limite disponível é de R$ {limite_formatado:,.2f}. Você gostaria de solicitar um aumento desse valor de crédito?"

    # -----------------------------------------------------------------
    # AGENTE 1: TRIAGEM E AUTENTICAÇÃO
    # -----------------------------------------------------------------
    if ctx['agente_atual'] == 'triagem':
        if ctx['sub_estagio'] == 'coleta_cpf':
            cpf_filtrado = "".join(re.findall(r'\d+', texto_limpo))
            if len(cpf_filtrado) != 11:
                return "Por favor, certifique-se de digitar um CPF válido contendo exatamente os 11 dígitos numéricos."
            ctx['cpf_temp'] = cpf_filtrado
            ctx['sub_estagio'] = 'coleta_nascimento'
            return "CPF registrado com sucesso. Agora, para mantermos o sigilo dos seus dados, informe sua data de nascimento no formato DD/MM/AAAA."

        elif ctx['sub_estagio'] == 'coleta_nascimento':
            try:
                if not os.path.exists('clientes.csv'):
                    return "Aviso Técnico: A base principal de clientes ('clientes.csv') não foi localizada no servidor."
                
                df_clientes = pd.read_csv('clientes.csv', dtype={'cpf': str, 'data_nascimento': str})
                match = df_clientes[(df_clientes['cpf'] == ctx['cpf_temp']) & (df_clientes['data_nascimento'] == prompt.strip())]
                
                if not match.empty:
                    ctx['autenticado'] = True
                    ctx['cliente_dados'] = match.iloc[0].to_dict()
                    ctx['sub_estagio'] = 'menu_principal'
                    
                    # REQUISITO EXATO DA JORNADA: Exibe o limite imediatamente antes de abrir os caminhos
                    nome_cliente = ctx['cliente_dados']['nome']
                    limite_atual = float(ctx['cliente_dados']['limite'])
                    
                    return (
                        f"Acesso autenticado com total segurança! É uma grande satisfação atender você hoje, **{nome_cliente}**! ✨\n\n"
                        f"Consultei seus dados e identifiquei que o seu **limite de crédito atual em conta é de R$ {limite_atual:,.2f}**.\n\n"
                        f"Para podermos prosseguir de forma ágil, digite o que precisa resolver agora. Aqui estão as suas opções:\n\n"
                        f"📌 **Setor de Crédito:** Digite termos como **'Limite'** ou **'Aumento'** (caso você queira solicitar uma alteração desse valor de crédito).\n"
                        f"📌 **Setor de Câmbio:** Digite termos como **'Câmbio'** ou **'Moeda'** (para checar a cotação atualizada em tempo real).\n\n"
                        f"🛑 *Lembrete de Autonomia:* Você pode digitar a palavra **'Encerrar'** ou **'Sair'** em **qualquer momento** do atendimento para finalizar a sessão."
                    )
                else:
                    ctx['tentativas_auth'] += 1
                    # REQUISITO EXATO: 3 falhas consecutivas encerram o loop de execução amigavelmente
                    if ctx['tentativas_auth'] >= 3:
                        ctx['agente_atual'] = 'encerrado'
                        return "Não foi possível validar seus dados cadastrais após 3 tentativas seguidas. Por motivos de segurança digital, este atendimento foi encerrado de maneira agradável."
                    return f"Dados divergentes. Por favor, confira e reinsira sua data de nascimento (Tentativa {ctx['tentativas_auth'] + 1} de 3):"
            except Exception as e:
                return f"Ocorreu um erro inesperado ao ler a base de dados ({e}). Por favor, digite novamente a data de nascimento:"

        elif ctx['sub_estagio'] == 'menu_principal':
            nome_cliente = ctx['cliente_dados']['nome']
            limite_atual = float(ctx['cliente_dados']['limite'])
            return (
                f"Estou aqui para ajudar, **{nome_cliente}**. Lembrando que seu **limite disponível é de R$ {limite_atual:,.2f}**.\n"
                f"Como deseja prosseguir? Escolha uma de nossas opções estruturadas:\n\n"
                f"🔹 Digite **'Limite'** ou **'Aumento'** para ir ao Setor de Crédito.\n"
                f"🔹 Digite **'Câmbio'** ou **'Moeda'** para ir ao Setor de Câmbio.\n\n"
                f"💡 Se preferir finalizar agora, basta digitar **'Encerrar'**."
            )

    # -----------------------------------------------------------------
    # AGENTE 2: CRÉDITO E ANÁLISE DE LIMITE
    # -----------------------------------------------------------------
    elif ctx['agente_atual'] == 'credito':
        valor_capturado = extrair_valor_numerico(prompt)

        if ctx['sub_estagio'] == 'inicio_credito':
            if valor_capturado and any(p in texto_limpo for p in ['sim', 'quero', 'solicitar', 'aumentar', 'aumento']):
                ctx['sub_estagio'] = 'aguardando_valor_limite'
            elif any(p in texto_limpo for p in ['sim', 'quero', 'solicitar', 'aumentar', 'aumento', 'consultar']):
                ctx['sub_estagio'] = 'aguardando_valor_limite'
                return "Perfeito! Por favor, informe o valor total do novo limite de crédito que você deseja solicitar:"
            elif any(p in texto_limpo for p in ['nao', 'não', 'voltar', 'cancelar']):
                ctx['sub_estagio'] = 'menu_principal'
                return "Entendido. Mantivemos seu limite atual sem alterações. O que mais posso fazer por você no menu principal?"
            else:
                return f"Seu limite atual em conta é de R$ {float(ctx['cliente_dados']['limite']):,.2f}. Deseja prosseguir com uma solicitação de aumento?"

        if ctx['sub_estagio'] == 'aguardando_valor_limite':
            if not valor_capturado:
                return "Para darmos andamento à análise, digite o valor desejado em algarismos numéricos (Exemplo: 4500)."

            limite_atual = float(ctx['cliente_dados']['limite'])
            score_atual = int(ctx['cliente_dados']['score'])
            cpf_cliente = ctx['cliente_dados']['cpf']
            
            # TOOL: Validação matemática baseada na tabela de score
            try:
                df_regras = pd.read_csv('score_limite.csv')
                regra = df_regras[(df_regras['score_min'] <= score_atual) & (df_regras['score_max'] >= score_atual)]
                limite_max_permitido = float(regra.iloc[0]['limite_maximo']) if not regra.empty else 1000.0
            except Exception:
                limite_max_permitido = 1000.0

            # AJUSTE DE ALINHAMENTO: Status 'reprovado' mapeado rigorosamente conforme a condicional do edital
            status_pedido = 'aprovado' if valor_capturado <= limite_max_permitido else 'reprovado'

            # TOOL: Persistência imediata de logs formais com timestamp estruturado em ISO 8601
            try:
                nova_solicitacao = pd.DataFrame({
                    'cpf_cliente': [str(cpf_cliente)],
                    'data_hora_solicitacao': [datetime.datetime.now().isoformat()],
                    'limite_atual': [limite_atual],
                    'novo_limite_solicitado': [valor_capturado],
                    'status_pedido': [status_pedido]
                })
                nova_solicitacao.to_csv('solicitacoes_aumento_limite.csv', mode='a', header=False, index=False)
            except Exception as e:
                st.error(f"Erro de Gravação de Log de Crédito: {e}")

            if status_pedido == 'aprovado':
                try:
                    df_cli = pd.read_csv('clientes.csv', dtype={'cpf': str})
                    df_cli.loc[df_cli['cpf'] == str(cpf_cliente), 'limite'] = valor_capturado
                    df_cli.to_csv('clientes.csv', index=False)
                    ctx['cliente_dados']['limite'] = valor_capturado
                except Exception:
                    pass
                ctx['sub_estagio'] = 'menu_principal'
                return f"Excelente notícia! O seu pedido de R$ {valor_capturado:,.2f} foi APROVADO pelos nossos critérios automáticos de score! O limite já se encontra disponível. Como posso ajudar você agora?"
            else:
                # REQUISITO EXATO: Se o status for 'reprovado', oferece redirecionamento para o Agente de Entrevista
                ctx['sub_estagio'] = 'oferecer_entrevista'
                return f"Avaliamos o seu pedido de aumento para R$ {valor_capturado:,.2f}, contudo, o seu status de solicitação constou como REPROVADO devido ao seu score atual ({score_atual} pontos). Gostaria de passar por uma breve entrevista financeira consultiva para atualizar seus dados e tentar reajustar seu score?"

        elif ctx['sub_estagio'] == 'oferecer_entrevista':
            if any(p in texto_limpo for p in ['sim', 'aceito', 'quero', 'pode', 'ok', 'com certeza']):
                ctx['agente_atual'] = 'entrevista'
                ctx['entrevista_passo'] = 1
                return "Ótimo! Vamos iniciar o questionário de atualização financeira. Para começar, por favor me informe: qual é a sua renda mensal bruta aproximada?"
            else:
                ctx['sub_estagio'] = 'menu_principal'
                return "Compreendido. Sua opção foi registrada. Retornamos ao menu central do Banco Ágil. O que deseja fazer a seguir?"

    # -----------------------------------------------------------------
    # AGENTE 3: ENTREVISTA DE CRÉDITO (CÁLCULO DE SCORE)
    # -----------------------------------------------------------------
    elif ctx['agente_atual'] == 'entrevista':
        passo = ctx['entrevista_passo']

        if passo == 1:
            valor = extrair_valor_numerico(prompt)
            ctx['entrevista_dados']['renda'] = valor if valor else 1000.0
            ctx['entrevista_passo'] = 2
            return "Obrigado. Segunda pergunta: qual é o seu tipo de vínculo empregatício atual? (Por favor, digite exatamente uma das opções: formal, autônomo ou desempregado)."

        elif passo == 2:
            tipo = 'desempregado'
            if 'formal' in texto_limpo: tipo = 'formal'
            elif 'auton' in texto_limpo or 'autón' in texto_limpo: tipo = 'autônomo'
            ctx['entrevista_dados']['emprego'] = tipo
            ctx['entrevista_passo'] = 3
            return "Entendido. Terceira pergunta: qual o valor médio aproximado de suas despesas fixas mensais?"

        elif passo == 3:
            valor = extrair_valor_numerico(prompt)
            ctx['entrevista_dados']['despesas'] = valor if valor else 0.0
            ctx['entrevista_passo'] = 4
            return "Registrado. Quarta pergunta: quantos dependentes financeiros diretos você possui atualmente? (Responda em números: 0, 1, 2 ou 3 para mais de 3)."

        elif passo == 4:
            nums = re.findall(r'\d+', texto_limpo)
            ctx['entrevista_dados']['dependentes'] = int(nums[0]) if nums else 0
            ctx['entrevista_passo'] = 5
            return "Para concluirmos o cálculo, quinta pergunta: você possui alguma restrição financeira ativa ou dívidas vencidas pendentes? (Responda apenas sim ou não)."

        elif passo == 5:
            ctx['entrevista_dados']['dividas'] = 'sim' if 'sim' in texto_limpo else 'não'
            
            # TOOL: Execução fiel da Fórmula de Score Ponderada descrita na especificação
            try:
                renda = float(ctx['entrevista_dados']['renda'])
                despesas = float(ctx['entrevista_dados']['despesas'])
                
                peso_renda = 30
                peso_emprego = {"formal": 300, "autônomo": 200, "desempregado": 0}
                
                dep_informado = ctx['entrevista_dados']['dependentes']
                if dep_informado == 0: peso_dep = 100
                elif dep_informado == 1: peso_dep = 80
                elif dep_informado == 2: peso_dep = 60
                else: peso_dep = 30
                
                peso_dividas = {"sim": -100, "não": 100}
                div_status = ctx['entrevista_dados']['dividas']

                score_calculado = (
                    (renda / (despesas + 1)) * peso_renda + 
                    peso_emprego[ctx['entrevista_dados']['emprego']] + 
                    peso_dep + 
                    peso_dividas[div_status]
                )
                
                novo_score = max(0, min(1000, int(score_calculado)))
                
                # TOOL: Atualização instantânea dos dados na base clientes.csv
                cpf_cliente = ctx['cliente_dados']['cpf']
                df_cli = pd.read_csv('clientes.csv', dtype={'cpf': str})
                df_cli.loc[df_cli['cpf'] == str(cpf_cliente), 'score'] = novo_score
                df_cli.to_csv('clientes.csv', index=False)
                
                ctx['cliente_dados']['score'] = novo_score
                
                # REQUISITO EXATO: Redireciona o cliente de volta ao Agente de Crédito para nova análise
                ctx['agente_atual'] = 'credito'
                ctx['sub_estagio'] = 'inicio_credito'
                return f"Entrevista financeira finalizada com total sucesso! Seus dados foram computados e sua pontuação de crédito foi atualizada para **{novo_score} pontos** no sistema. Retornamos você ao Setor de Crédito. Deseja realizar uma nova tentativa de aumento de limite agora?"
                
            except Exception as e:
                ctx['agente_atual'] = 'triagem'
                ctx['sub_estagio'] = 'menu_principal'
                return f"Tratamento de Exceção: Ocorreu uma interrupção ao processar a fórmula ({e}). Retornamos ao menu central."

    # -----------------------------------------------------------------
    # AGENTE 4: OPERAÇÕES DE CÂMBIO
    # -----------------------------------------------------------------
    elif ctx['agente_atual'] == 'cambio':
        moeda_alvo = "USD"
        nome_moeda = "Dólar Comercial"
        
        if 'euro' in texto_limpo:
            moeda_alvo = "EUR"
            nome_moeda = "Euro"
        elif 'bit' in texto_limpo or 'btc' in texto_limpo:
            moeda_alvo = "BTC"
            nome_moeda = "Bitcoin"

        # TOOL: Consumo controlado de API externa (AwesomeAPI - Sem necessidade de chaves expostas no código)
        try:
            url = f"https://economia.awesomeapi.com.br/json/last/{moeda_alvo}-BRL"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                dados_api = response.json()
                cotacao = float(dados_api[f"{moeda_alvo}BRL"]["bid"])
                msg_retorno = f"Conectando aos servidores cambiais... A taxa de conversão atual do **{nome_moeda}** é de R$ {cotacao:,.2f} por unidade."
            else:
                msg_retorno = "A API externa de moedas apresentou instabilidade temporária. Valor referencial de contingência (Dólar): R$ 5,50."
        except Exception:
            msg_retorno = "Não foi possível contatar o serviço de moedas em tempo real devido a uma falha de rede. Valor referencial de contingência (Dólar): R$ 5,50."

        # REQUISITO EXATO: Encerrar o atendimento específico de cotação com uma mensagem amigável e limpa
        ctx['agente_atual'] = 'triagem'
        ctx['sub_estagio'] = 'menu_principal'
        return f"{msg_retorno} Consulta de câmbio encerrada com sucesso! Retornamos você ao menu central. O que mais deseja resolver no Banco Ágil?"

    return "Peço desculpas, mas não captei o comando exato. Como posso te apoiar hoje?"

# =====================================================================
# MODULE 5: CAMADA VISUAL E BLINDAGEM DE RENDERIZAÇÃO (Streamlit UI)
# =====================================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

with st.form(key="central_chat_safe", clear_on_submit=True):
    col_input, col_btn = st.columns([0.83, 0.17])
    with col_input:
        prompt_usuario = st.text_input(
            "Mensagem",
            label_visibility="collapsed",
            placeholder="Digite sua solicitação ou digite 'Encerrar'..."
        )
    with col_btn:
        enviado = st.form_submit_button("Enviar ➔", use_container_width=True)

if enviado and prompt_usuario.strip():
    st.session_state.messages.append({"role": "user", "content": prompt_usuario})
    resposta_sistema = roteador_fluxo_agentes(prompt_usuario)
    st.session_state.messages.append({"role": "assistant", "content": resposta_sistema})
    st.rerun()

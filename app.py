import os
import re
from datetime import datetime
import mesop as me
import mesop.labs as mel
import pandas as pd

# Utilizando @me.stateclass para evitar erro de contexto no carregamento
@me.stateclass
class ChatState:
    messages: list = []
    current_agent: str = "triagem"
    customer_cpf: str = ""
    authenticated: bool = False
    auth_attempts: int = 0
    current_score: int = 0
    current_limit: float = 0.0
    interview_step: int = 0
    interview_data: dict = {}

def processar_atendimento(texto_usuario: str, state: ChatState) -> str:
    texto_limpo = texto_usuario.strip().lower()
    
    if "sair" in texto_limpo or "encerrar" in texto_limpo:
        state.current_agent = "end"
        return "Atendimento encerrado pelo cliente. O Banco Ágil agradece o seu contato!"

    if state.current_agent == "triagem":
        if not state.customer_cpf:
            numeros = "".join(re.findall(r'\d+', texto_limpo))
            if len(numeros) == 11:
                state.customer_cpf = numeros
                return "CPF localizado. Agora, por favor, digite sua Data de Nascimento (Exemplo: 15/05/1990):"
            return "Olá! Bem-vindo ao Banco Ágil. Por favor, digite o seu CPF (apenas os 11 números) para iniciar o atendimento:"
        
        if not state.authenticated:
            try:
                # Buscando arquivos diretamente na raiz
                df = pd.read_csv("clientes.csv", dtype={"cpf": str})
                cliente = df[(df["cpf"] == state.customer_cpf) & (df["data_nascimento"] == texto_usuario.strip())]
                
                if not cliente.empty:
                    state.authenticated = True
                    state.current_score = int(cliente.iloc[0]["score"])
                    state.current_limit = float(cliente.iloc[0]["limite"])
                    return "Autenticação realizada com sucesso! Como posso ajudar você hoje? (Você pode pedir 'aumento de limite' ou consultar taxas de 'câmbio')."
                else:
                    state.auth_attempts += 1
                    if state.auth_attempts >= 3:
                        state.current_agent = "end"
                        return "Não foi possível validar seus dados após 3 tentativas. Por segurança, este atendimento foi finalizado."
                    return f"Dados incorretos. Você possui mais {3 - state.auth_attempts} tentativa(s). Digite a data de nascimento novamente:"
            except Exception:
                return "Erro ao ler a base de dados. Digite a data de nascimento novamente:"

        if any(k in texto_limpo for k in ["limite", "crédito", "aumento"]):
            state.current_agent = "credito"
            return f"Você está na Central de Crédito. Seu limite atual é R$ {state.current_limit:.2f}. Qual o novo valor total de limite que deseja solicitar?"
        elif any(k in texto_limpo for k in ["câmbio", "dólar", "moeda", "cotação"]):
            state.current_agent = "cambio"
            return "Você está na Central de Câmbio. A cotação comercial simulada do Dólar hoje é de R$ 5,25. Algo mais em que posso ajudar?"

    if state.current_agent == "credito":
        valores = re.findall(r'\d+', texto_limpo)
        if valores:
            novo_limite = float(valores[0])
            status_pedido = "rejeitado"
            
            try:
                # Buscando arquivo na raiz
                df_score = pd.read_csv("score_limite.csv")
                faixa = df_score[df_score["score_minimo"] <= state.current_score]
                if not faixa.empty and novo_limite <= float(faixa.iloc[-1]["limite_maximo"]):
                    status_pedido = "approved"
            except Exception:
                if state.current_score >= 600: status_pedido = "approved"

            timestamp = datetime.utcnow().isoformat() + "Z"
            
            # Log salvo na raiz
            log_caminho = "solicitacoes_aumento_limite.csv"
            log_linha = f"{state.customer_cpf},{timestamp},{state.current_limit},{novo_limite},{status_pedido}\n"
            
            if not os.path.exists(log_caminho):
                with open(log_caminho, "w", encoding="utf-8") as f:
                    f.write("cpf_cliente,data_hora_solicitacao,limite_atual,novo_limite_solicitado,status_pedido\n")
            with open(log_caminho, "a", encoding="utf-8") as f:
                f.write(log_linha)

            if status_pedido == "approved":
                state.current_limit = novo_limite
                state.current_agent = "end"
                return f"Parabéns! Seu novo limite de R$ {novo_limite:.2f} foi aprovado. Atendimento encerrado com sucesso!"
            else:
                return f"O pedido de R$ {novo_limite:.2f} não foi pré-aprovado devido ao seu score atual ({state.current_score}). Gostaria de passar por nossa entrevista para atualizar seu score? (Responda APENAS 'SIM' ou 'NÃO')"

        if "sim" in texto_limpo or "quero" in texto_limpo:
            state.current_agent = "entrevista"
            state.interview_step = 1
            return "Vamos iniciar a entrevista. Informe apenas o número da sua Renda Mensal (Exemplo: 4000):"
        elif "não" in texto_limpo or "nao" in texto_limpo:
            state.current_agent = "end"
            return "Entendido. Central de crédito finalizada. Obrigado por utilizar o Banco Ágil!"

    if state.current_agent == "entrevista":
        passo = state.interview_step
        if passo == 1:
            state.interview_data["renda"] = float("".join(c for c in texto_limpo if c.isdigit()) or 1000)
            state.interview_step = 2
            return "Qual o seu tipo de emprego atual? (Digite exatamente: formal, autônomo ou desempregado):"
        elif passo == 2:
            state.interview_data["emprego"] = texto_limpo if texto_limpo in ["formal", "autônomo", "desempregado"] else "desempregado"
            state.interview_step = 3
            return "Qual o valor médio das suas Despesas Fixas por mês? (Digite apenas números):"
        elif passo == 3:
            state.interview_data["despesas"] = float("".join(c for c in texto_limpo if c.isdigit()) or 0)
            state.interview_step = 4
            return "Quantos dependentes financeiros você possui? (Digite: 0, 1, 2 ou 3+):"
        elif passo == 4:
            state.interview_data["dependentes"] = texto_limpo
            state.interview_step = 5
            return "Última pergunta: Você possui outras dívidas ativas em aberto? (Digite: sim ou não):"
        elif passo == 5:
            dividas = texto_limpo
            
            p_renda = 30
            p_emp = {"formal": 300, "autônomo": 200, "desempregado": 0}
            p_dep = {"0": 100, "1": 80, "2": 60, "3+": 30, "3": 30}
            p_div = {"sim": -100, "não": 100, "nao": 100}
            
            renda = state.interview_data.get("renda", 1000)
            despesas = state.interview_data.get("despesas", 0)
            emp = state.interview_data.get("emprego", "desempregado")
            dep = state.interview_data.get("dependentes", "0")
            div = "sim" if "sim" in dividas else "não"
            
            novo_score = int(((renda / (despesas + 1)) * p_renda) + p_emp.get(emp, 0) + p_dep.get(dep, 30) + p_div.get(div, 100))
            state.current_score = max(0, min(1000, novo_score))
            
            state.current_agent = "credito"
            state.interview_step = 0
            return f"Entrevista concluída! Seu score foi recalculado para {state.current_score} pontos. De volta à Central de Crédito: Digite novamente o valor do limite que deseja solicitar:"

    if state.current_agent == "cambio":
        state.current_agent = "end"
        return "Consulta efetuada. O Banco Ágil agradece o contato!"

    return "Desculpe, não compreendi. Como posso ajudar?"

@me.page(path="/")
def page():
    me.text("🏦 Central de Atendimento - Banco Ágil", type="headline-5", style=me.Style(margin=me.Margin(bottom=20, top=10)))
    mel.chat(transform, title="Assistente Multi-Agente Corporativo (Google Native)", placeholder="Envie sua mensagem por aqui...")

def transform(user_input: str, history: list[mel.ChatMessage]):
    state = me.state(ChatState)
    resposta = processar_atendimento(user_input, state)
    if state.current_agent == "end":
        resposta += "\n\n🔒 [SESSÃO ENCERRADA DE FORMA SEGURA]"
    return resposta

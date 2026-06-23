import os
import re
from datetime import datetime
from dataclasses import dataclass, field
import mesop as me
import mesop.labs as mel
import pandas as pd

@me.stateclass
class ChatState:
    messages: list = field(default_factory=list)
    current_agent: str = "triagem"
    customer_cpf: str = ""
    authenticated: bool = False
    auth_attempts: int = 0
    current_score: int = 0
    current_limit: float = 0.0
    interview_step: int = 0
    interview_data: dict = field(default_factory=dict)

def processar_atendimento(texto_usuario: str, state: ChatState) -> str:
    texto_limpo = texto_usuario.strip().lower()
    
    # Lógica de Triagem e Autenticação
    if state.current_agent == "triagem":
        if not state.customer_cpf:
            numeros = "".join(re.findall(r'\d+', texto_limpo))
            if len(numeros) == 11:
                state.customer_cpf = numeros
                return "CPF localizado. Por favor, digite sua Data de Nascimento (Ex: dd/mm/aaaa):"
            return "Olá! Digite seu CPF para iniciar:"
        
        if not state.authenticated:
            try:
                df = pd.read_csv("clientes.csv", dtype={"cpf": str})
                cliente = df[(df["cpf"] == state.customer_cpf) & (df["data_nascimento"] == texto_usuario.strip())]
                if not cliente.empty:
                    state.authenticated = True
                    state.current_score = int(cliente.iloc[0]["score"])
                    state.current_limit = float(cliente.iloc[0]["limite"])
                    return "Autenticado! Digite 'limite' para ver opções ou 'sair' para encerrar."
                return "Dados incorretos. Tente novamente:"
            except:
                return "Erro no sistema. Tente novamente."
        
        if "limite" in texto_limpo:
            state.current_agent = "credito"
            return f"Seu limite atual é R$ {state.current_limit:.2f}. Qual o novo valor?"

    # Lógica de Crédito
    if state.current_agent == "credito":
        valor = re.findall(r'\d+', texto_limpo)
        if valor:
            novo_limite = float(valor[0])
            state.current_agent = "end"
            return f"Pedido de R$ {novo_limite} registrado! Obrigado por usar o Banco Ágil."
            
    return "Não entendi, tente novamente."

@me.page(path="/")
def page():
    me.text("🏦 Banco Ágil")
    mel.chat(transform, title="Assistente")

def transform(user_input: str, history: list[mel.ChatMessage]):
    return processar_atendimento(user_input, me.state(ChatState))

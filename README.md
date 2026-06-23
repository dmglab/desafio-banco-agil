
### Central de Atendimento Multi-Agente — Banco Ágil

### Visão Geral do Projeto

Este repositório apresenta a solução de engenharia para o desafio técnico do Banco Ágil, uma central de atendimento bancário baseada em agentes cognitivos especializados com escopos estritamente blindados. O sistema gerencia de forma integrada as jornadas de triagem de segurança, análise de propostas de crédito, recálculo algorítmico de score através de uma entrevista conversacional estruturada e consultas cambiais em tempo real, utilizando uma interface de chat unificada e reativa.

---

### Arquitetura do Sistema e Engenharia de Fluxos

O sistema adota o padrão arquitetural de Máquina de Estados Finita (FSM). O controle estrito da sessão reside em um estado encapsulado compartilhado de forma centralizada, mitigando riscos de vazamento de contexto ou atuação de agentes fora de seus escopos regulamentares.


```

```
              ┌─────────────────────────┐
              │    Agente de Triagem    │ ◄─── Entrada Obrigatória (Login)
              └────────────┬────────────┘
                           │ (Autenticado)
                           ▼
              ┌─────────────────────────┐
              │    Roteador Central     │ ◄─── Redirecionamento Implícito
              └──────┬───────────┬──────┘
                     │           │
     ┌───────────────┘           └───────────────┐
     ▼                                           ▼

```

┌─────────────────┐                         ┌─────────────────┐
│Agente de Crédito│                         │Agente de Câmbio │
└────────┬────────┘                         └─────────────────┘
│ (Se Reprovado)
▼
┌─────────────────┐
│   Agente de     │
│   Entrevista    │ ───► (Atualiza Score e retorna ao Crédito)
└─────────────────┘

```

### Escopo de Atuação dos Agentes

### Agente de Triagem
Porta de entrada compulsória do canal digital. Responsável pela coleta isolada de CPF e data de nascimento, realizando o cruzamento de dados. Bloqueia o fluxo de execução de forma amigável após a 3ª falha consecutiva.

### Agente de Crédito
Atua exclusivamente na consulta de limites disponíveis e processamento de substituidores de aumento. Avalia a proposta contra políticas de risco rígidas e encaminha o usuário de forma integrada ao fluxo consultivo em caso de recusa.

### Agente de Entrevista de Crédito
Conduz uma sub-máquina de estados sequencial de 5 passos para coleta estruturada de dados socioeconômicos, atualizando dinamicamente as variáveis de risco do cliente.

### Agente de Câmbio
Consome APIs externas de mercado para retornar cotações em tempo real e finaliza o escopo de atendimento cambial, devolvendo o controle com segurança.

---

### Modelagem e Manipulação de Dados (Persistência)

O sistema opera com persistência baseada em arquivos planos locais estruturados (CSV), manipulados por meio da biblioteca pandas, garantindo portabilidade em ambientes de teste.

### Estrutura das Bases Relacionais

| Arquivo | Descrição | Colunas Chave |
| :--- | :--- | :--- |
| clientes.csv | Cadastro mestre de correntistas activos | cpf, nome, data_nascimento, score, limite |
| score_limite.csv | Matriz regulatória estática de tetos de crédito | score_min, score_max, limite_maximo |
| solicitacoes_aumento_limite.csv | Histórico Append-Only de auditoria interna | cpf_cliente, data_hora_solicitacao, limite_atual, novo_limite_solicitado, status_pedido |

---

### Funcionalidades Implementadas

### Redirecionamento Implícito
Transições transparentes entre agentes através do roteador de intenções sem que o cliente perceba que mudou de canal de atendimento.

### Resiliência a Entradas Livres
Captura e higienização de valores monetários e numéricos inseridos no meio de frases por meio de ferramentas baseadas em Expressões Regulares (re).

### Tratamento de Exceções Nativo
Mecanismos de contingência para falhas de rede em APIs externas e blindagem contra injeções de prompt no input do usuário.

### Logs Padronizados
Registro cronológico de propostas com carimbo de data/hora sob a especificação internacional ISO 8601.

---

### Desafios Enfrentados e Soluções

### 1. Transição Invisível de Contexto (Redirecionamento Implícito)
Desafio: Garantir que a troca de agentes ocorresse estritamente sem comandos artificiais e de modo orgânico para o usuário.
Solução: Implementação de um Roteador Semântico Central no ciclo de vida da mensagem que intercepta palavras-chave de intenção (aumento, câmbio) logo após a triagem, redefinindo as chaves de estado de forma silenciosa na memória do chat.

### 2. Persistência e Reatividade no Streamlit
Desafio: O Streamlit reexecuta todo o script do topo ao rodapé a cada clique ou envio de mensagem, o que por padrão resetaria as variáveis locais da conversa.
Solução: Encapsulamento completo de todos os metadados dos agentes dentro do dicionário de contexto corporativo armazenado em st.session_state.ctx, blindando a persistência do chat entre as iterações.

---

### Escolhas Técnicas e Justificativas de Stack

### Streamlit Framework
Escolhido como interface do usuário (UI) devido à sua excelente capacidade de renderização reativa em Python puro, criando uma camada de apresentação rápida e eficiente para o escopo do desafio.

### Pandas
Utilizado para a manipulação de dados por fornecer operações vetoriais de alta performance e leitura/escrita atômica em arquivos CSV, agindo como nossa camada de banco de dados leve.

### Fórmula de Score Parametrizada
A lógica matemática foi implementada de maneira puramente determinística seguindo rigorosamente a equação e a distribuição de pesos indicadas no edital, garantindo auditoria limpa do resultado.

---

### Tutorial de Execução e Guia de Testes

### Preparação do Ambiente
1. Certifique-se de ter o Python instalado (Versão recomendada: 3.10 ou superior).
2. Clone este repositório para sua máquina local.
3. Instale as dependências executando o comando no terminal:
```bash
pip install -r requirements.txt

```

### Inicialização da Aplicação

Execute o servidor local do Streamlit com o seguinte comando:

```bash
streamlit run app.py

```

A interface do chat abrirá automaticamente no seu navegador padrão (geralmente sob o endereço http://localhost:8501).

---

### Cenários Homologados para Auditoria (Para o Avaliador)

Para validar a integridade de ponta a ponta dos fluxos exigidos, utilize as massas de teste oficiais cadastradas no banco:

### Caso de Teste 1: Fluxo de Sucesso e Câmbio (Carlos Silva)

* CPF: 12345678901
* Data de Nascimento: 15/05/1990
* Roteiro Recomendado: Efetue a autenticação. O sistema trará o nome dele e o limite atual de R$ 5.000,00. Em seguida, digite "Quero ver a cotação do Euro". O roteador mudará de agente implicitamente, consultará a API financeira e o trará de volta ao menu principal.

### Caso de Teste 2: Reprovação e Entrevista Estruturada (Ana Souza)

* CPF: 98765432100
* Data de Nascimento: 20/10/1985
* Roteiro Recomendado: Efetue a autenticação (Limite atual: R$ 1.500,00 | Score: 400). Solicite um limite de valor elevado digitando "Quero aumento para 20000". O sistema registrará o log com status reprovado, oferecerá a entrevista financeira, recalculará o score ao término das 5 perguntas e a redirecionará de volta ao canal de crédito.

---

### Proteção de Propriedade Intelectual e Direitos Autorais

Este projeto está protegido sob as diretrizes da Licença Pública GNU v3.0 (GPL-3.0). É vedada a cópia, distribuição sem créditos ou utilização comercial de qualquer trecho desta arquitetura para fins institucionais sem autorização prévia. O acesso a este código destina-se estritamente à avaliação técnica em processos seletivos.

```

```

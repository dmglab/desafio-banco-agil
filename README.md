Como solicitado, aqui está o conteúdo completo para o seu `README.md`, estruturado inteiramente em texto para que você possa copiar e colar sem qualquer formatação visual ou blocos gráficos adicionais:

# Central de Atendimento Multi-Agente - Banco Ágil

## Visão Geral do Projeto

Este repositório apresenta a solução completa para o desafio do Banco Ágil, uma central de atendimento bancário baseada em agentes cognitivos especializados com escopos estritamente blindados. O sistema gerencia interações de triagem de segurança, análise de propostas de crédito e recálculo algorítmico de score através de uma interface de chat unificada.

## Proteção de Propriedade Intelectual e Direitos Autorais

Este projeto está legalmente protegido sob as diretrizes da Licença Pública GNU v3.0 (GPL-3.0). É estritamente proibida a cópia, distribuição ou utilização comercial de qualquer trecho desta arquitetura de software para fins lucrativos ou institucionais sem a devida autorização do autor. O acesso a este código destina-se única e exclusivamente à avaliação técnica em processos seletivos.

## Dados de Teste Homologados (Para o Avaliador)

Para testar os fluxos de triagem, erro, crédito e entrevista financeira, utilize os dados abaixo:

### Cliente 1: Carlos Silva

* CPF: 12345678901
* Data de Nascimento: 15/05/1990
* Sugestão de teste: Faça o login com esses dados e peça: "Quero ver a cotação do dólar".

### Cliente 2: Ana Souza

* CPF: 98765432100
* Data de Nascimento: 20/10/1985
* Sugestão de teste: Faça o login (ela tem score baixo) e peça um limite alto: "Quero 25000 de limite". O robô recusará e oferecerá a entrevista financeira.

## Arquitetura do Sistema e Engenharia de Fluxos

O projeto adota a arquitetura de Máquina de Estados Finita (FSM). O controle da sessão reside em um estado compartilhado (ChatState), impedindo vazamento de contexto.

1. Agente de Triagem: Porta de entrada obrigatória. Bloqueia o atendimento na 3ª falha consecutiva.
2. Agente de Crédito: Avalia propostas contra tabelas de risco. Grava logs sob a normativa ISO 8601 (UTC/Z).
3. Agente de Entrevista: Executa uma sub-máquina de estados sequencial isolada para cálculo de score.
4. Agente de Câmbio: Atende requisições de mercado e encerra o ciclo.

## Manipulação de Dados (Persistência)

* data/clientes.csv: Base de identificação e scores.
* data/score_limite.csv: Tabela estática de limites.
* data/solicitacoes_aumento_limite.csv: Registro Append-Only em padrão ISO 8601.

## Funcionalidades Implementadas

* Lógica de autenticação com limite de 3 tentativas.
* Roteamento semântico baseado na intenção do usuário.
* Motor de cálculo de score dinâmico parametrizado.
* Persistência estruturada em arquivos CSV locais.

## Escolhas Técnicas e Justificativa de Stack

* Google Mesop UI: O projeto optou pelo framework Mesop (Google) em substituição a ferramentas tradicionais por três pilares fundamentais:
1. Segurança de Estado: O Mesop oferece gerenciamento de ChatState nativo e rígido, essencial para manter a blindagem dos escopos entre agentes bancários.
2. Produtividade e Reatividade: Permite construir toda a interface via Python puro, eliminando a necessidade de um frontend separado e reduzindo a superfície de erro técnico.
3. Modernidade da Arquitetura: O framework lida nativamente com o fluxo reativo de IAs, garantindo respostas rápidas sem a complexidade de gerenciar sockets ou recarregamentos de página.


* Isolamento por Máquina de Estados: Lógica nativa em Python garantindo resiliência total nos ciclos de retorno entre agentes.

## Tutorial de Execução e Homologação de Testes

### 1. Preparação do Ambiente

Certifique-se de ter o Python 3.10+ instalado. Abra o terminal na raiz do projeto.

### 2. Instalação de Dependências

Instale as bibliotecas necessárias executando o comando:
pip install -r requirements.txt

### 3. Execução do Servidor

Inicie o servidor da aplicação executando o comando:
mesop app.py

### 4. Acesso à Interface

Após a inicialização, abra o seu navegador de internet e acesse o endereço local:
http://localhost:32123

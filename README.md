# Central de Atendimento Multi-Agente - Banco Agil

## Visao Geral do Projeto
Este repositorio apresenta a solucao completa para o desafio do Banco Agil, uma central de atendimento bancario baseada em agentes cognitivos especializados com escopos estritamente blindados. O sistema gerencia interacoes de triagem de seguranca, analise de propostas de credito e recalculgocritmico de score atraves de uma interface de chat unificada.

## Protecao de Propriedade Intelectual e Direitos Autorais
Este projeto esta legalmente protegido sob as diretrizes da Licenca Publica GNU v3.0 (GPL-3.0), anexada ao arquivo LICENSE deste repositorio. E estritamente proibida a copia, distribuicao ou utilizacao comercial de qualquer trecho desta arquitetura de software para fins lucrativos ou institucionais sem a devida autorizacao do autor, sob pena das sancoes previstas na lei de patentes e direitos autorais. O acesso a este codigo destina-se unica e exclusivamente a avaliacao tecnica em processos seletivos.

## Dados de Teste Homologados (Para o Avaliador)
Para testar os fluxos de triagem, erro, credito e entrevista financeira, utilize os dados abaixo que ja estao cadastrados no sistema:

### Cliente 1: Carlos Silva
* CPF: 12345678901
* Data de Nascimento: 15/05/1990
* Sugestao de teste: Faca o login com esses dados e peca: "Quero ver a cotacao do dolar".

### Cliente 2: Ana Souza
* CPF: 98765432100
* Data de Nascimento: 20/10/1985
* Sugestao de teste: Faca o login com esses dados (ela tem score baixo) e peca um limite alto: "Quero 25000 de limite". O robo vai recusar e oferecer a entrevista financeira para recalcular o score dela.

## Arquitetura do Sistema e Engenharia de Fluxos
O projeto adota a arquitetura de Maquina de Estados Finita (FSM) para gerenciar a transicao implicita entre os robos. O controle da sessao reside em um estado compartilhado (ChatState), impedindo vazamento de contexto ou perda do historico de mensagens.

1. Agente de Triagem: Porta de entrada obrigatoria. Realiza buscas indexadas e bloqueia o terminal de atendimento na 3ª falha consecutiva de login por motivos de compliance bancario.
2. Agente de Credito: Avalia propostas de aumento em tempo real contra tabelas de risco. Grava logs incrementais contendo carimbos de tempo sob a normativa internacional ISO 8601 (UTC/Z).
3. Agente de Entrevista: Executa uma sub-maquina de estados sequencial isolada para coleta de dados socioeconomicos, aplicando um motor matematico parametrizado para recalcular o score.
4. Agente de Cambio: Atende a requisicoes de mercado e encerra o ciclo de forma limpa.

### Manipulacao de Dados (Persistencia)
* clientes.csv: Base de identificacao de clientes e saldos de score.
* score_limite.csv: Tabela estatica com limites permitidos por faixa.
* solicitacoes_aumento_limite.csv: Arquivo de registro "Append-Only" preenchido automaticamente pelo robo no padrao internacional de data e hora ISO 8601.

## Funcionalidades Implementadas
- [x] Logica de autenticacao com limite rigido de retentativas (3 falhas bloqueiam a sessao).
- [x] Roteamento semantico baseado na intencao do usuario sem comandos manuais de transicao.
- [x] Motor de calculo de score dinamico parametrizado com limitadores logicos entre 0 e 1000 pontos.
- [x] Persistencia estruturada em arquivos CSV locais com tratamento de erros preventivo.

## Escolhas Tecnicas e Justificativas: Inovacao com Stack 100% Google
Diferenciando-se das implementacoes convencionais de mercado que comumente recorrem ao Streamlit, este projeto foi arquitetado utilizando uma abordagem Google-Native:
* Google Mesop UI: Adotado como o front-end principal. Por ser o novo framework oficial open-source da Google voltado para aplicativos de Inteligencia Artificial Generativa, o Mesop oferece um ecossistema reativo baseado em funcoes Python muito mais veloz, eliminando gargalos de re-renderizacao comuns e garantindo o gerenciamento de sessoes estritamente tipado.
* Isolamento por Maquina de Estados: A logica foi implementada nativamente em Python sobre a estrutura do Mesop, garantindo resiliencia total nos ciclos de retorno (Ex: Credito -> Entrevista -> Retorno Automaotico ao Credito).

## Desafios Enfrentados e Solucoes
* Desafio da Coleta Linear: Fazer com que o cliente responda as 5 perguntas da entrevista financeira em ordem correta.
* Solucao: Desenvolvimento de um controle indexador por etapas (interview_step). O robo intercepta qualquer mensagem e so avanca a regua de calculo apos a validacao do input anterior.

## Tutorial de Execucao e Homologacao de Testes

### 1. Preparacao do Ambiente
Abra o prompt de comando ou terminal na raiz do projeto e instale as dependencias:
```bash
pip install -r requirements.txt

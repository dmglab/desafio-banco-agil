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
- Lógica de autenticação com limite de 3 tentativas.
- Roteamento semântico baseado na intenção do usuário.
- Motor de cálculo de score dinâmico parametrizado.
- Persistência estruturada em arquivos CSV locais.

## Escolhas Técnicas e Justificativa de Stack
- Google Mesop UI: Optei pelo framework Mesop (Google) por três pilares:
    1. Segurança de Estado: Gerenciamento de ChatState nativo e rígido.
    2. Produtividade e Reatividade: Interface via Python puro, reduzindo a superfície de erro.
    3. Modernidade: Fluxo reativo para IAs sem complexidade de sockets.
- Isolamento por Máquina de Estados: Lógica nativa em Python garantindo resiliência.

## Tutorial de Execução
1. Preparação: Tenha o Python 3.10+ instalado.
2. Instalação: pip install -r requirements.txt
3. Execução: mesop app.py
4. Acesso: http://localhost:32123

### Notas de Engenharia para o Avaliador:

Ambiente: O projeto foi desenvolvido em Python 3.10+.

Persistência: O sistema utiliza pandas para ler os CSVs na pasta data/. Certifique-se de que a estrutura de pastas foi mantida ao clonar o repositório.

Blindagem: Cada agente atua em um escopo de memória isolado. Caso o chat apresente comportamento inesperado, recarregue a página para limpar o ChatState (reset total da sessão).

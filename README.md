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

1. **Agente de Triagem**: Porta de entrada obrigatória. Bloqueia o atendimento na 3ª falha consecutiva.
2. **Agente de Crédito**: Avalia propostas contra tabelas de risco. Grava logs sob a normativa ISO 8601 (UTC/Z).
3. **Agente de Entrevista**: Executa uma sub-máquina de estados sequencial isolada para cálculo de score.
4. **Agente de Câmbio**: Atende requisições de mercado e encerra o ciclo.

### Manipulação de Dados (Persistência)
* `data/clientes.csv`: Base de identificação e scores.
* `data/score_limite.csv`: Tabela estática de limites.
* `data/solicitacoes_aumento_limite.csv`: Registro "Append-Only" em padrão ISO 8601.

## Funcionalidades Implementadas
- [x] Lógica de autenticação com limite de 3 tentativas.
- [x] Roteamento semântico baseado na intenção do usuário.
- [x] Motor de cálculo de score dinâmico parametrizado.
- [x] Persistência estruturada em arquivos CSV locais.

## Escolhas Técnicas
* **Google Mesop UI**: Framework oficial Google para IA Generativa, garantindo reatividade e tipagem estrita de sessões.
* **Isolamento por Máquina de Estados**: Lógica nativa em Python garantindo resiliência nos ciclos de retorno.

## Tutorial de Execução e Homologação de Testes

### 1. Preparação do Ambiente
Certifique-se de ter o Python 3.10+ instalado. Abra o terminal na raiz do projeto.

### 2. Instalação de Dependências
Instale as bibliotecas necessárias executando:
```bash
pip install -r requirements.txt

### 3. Execução do Servidor
Inicie o servidor da aplicação executando o comando:

Bash
mesop app.py

### 4. Acesso à Interface
Após a inicialização, abra o seu navegador de internet e acesse o endereço local:
http://localhost:32123

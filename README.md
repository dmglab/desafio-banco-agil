#  Central de Atendimento Multi-Agente - Banco Ágil

##  Visão Geral do Projeto
Este repositório apresenta a solução completa para o desafio do **Banco Ágil**, uma central de atendimento bancário baseada em agentes cognitivos especializados com escopos estritamente blindados. O sistema gerencia interações de triagem de segurança, análise de propostas de crédito e recálculo algorítmico de score através de uma interface de chat unificada.

##  Proteção de Propriedade Intelectual e Direitos Autorais
Este projeto está legalmente protegido sob as diretrizes da **Licença Pública GNU v3.0 (GPL-3.0)**, anexada ao arquivo `LICENSE` deste repositório. É estritamente proibida a cópia, distribuição ou utilização comercial de qualquer trecho desta arquitetura de software para fins lucrativos ou institucionais sem a devida autorização do autor, sob pena das sanções previstas na lei de patentes e direitos autorais. O acesso a este código destina-se única e exclusivamente à avaliação técnica em processos seletivos.

##  Arquitetura do Sistema e Engenharia de Fluxos
O projeto adota a arquitetura de **Máquina de Estados Finita (FSM)** para gerenciar a transição implícita entre os robôs. O controle da sessão reside em um estado compartilhado (`ChatState`), impedindo vazamento de contexto ou perda do histórico de mensagens.

1. **Agente de Triagem:** Porta de entrada obrigatória. Realiza buscas indexadas e bloqueia o terminal de atendimento na 3ª falha consecutiva de login por motivos de compliance bancário.
2. **Agente de Crédito:** Avalia propostas de aumento em tempo real contra tabelas de risco. Grava logs incrementais contendo carimbos de tempo sob a normativa internacional **ISO 8601** (UTC/Z).
3. **Agente de Entrevista:** Executa uma sub-máquina de estados sequencial isolada para coleta de dados socioeconômicos, aplicando um motor matemático parametrizado para recalcular o score.
4. **Agente de Câmbio:** Atende a requisições de mercado e encerra o ciclo de forma limpa.

###  Manipulação de Dados (Persistência)
* `clientes.csv`: Base de identificação de clientes e saldos de score.
* `score_limite.csv`: Tabela estática com limites permitidos por faixa.
* `solicitacoes_aumento_limite.csv`: Arquivo de registro "Append-Only" preenchido automaticamente pelo robô no padrão internacional de data e hora **ISO 8601**.

##  Funcionalidades Implementadas
- [x] Lógica de autenticação com limite rígido de retentativas (3 falhas bloqueiam a sessão).
- [x] Roteamento semântico baseado na intenção do usuário sem comandos manuais de transição.
- [x] Motor de cálculo de score dinâmico parametrizado com limitadores lógicos entre 0 e 1000 pontos.
- [x] Persistência estruturada em arquivos CSV locais com tratamento de erros preventivo.

##  Escolhas Técnicas e Justificativas: Inovação com Stack 100% Google
Diferenciando-se das implementações convencionais de mercado que comumente recorrem ao Streamlit, este projeto foi arquitetado utilizando uma abordagem **Google-Native**:
* **Google Mesop UI:** Adotado como o front-end principal. Por ser o novo framework oficial open-source da Google voltado para aplicativos de Inteligência Artificial Generativa, o Mesop oferece um ecossistema reativo baseado em funções Python muito mais veloz, eliminando gargalos de re-renderização comuns e garantindo o gerenciamento de sessões estritamente tipado.
* **Isolamento por Máquina de Estados:** A lógica foi implementada nativamente em Python sobre a estrutura do Mesop, garantindo resiliência total nos ciclos de retorno (Ex: Crédito -> Entrevista -> Retorno Automático ao Crédito).

##  Desafios Enfrentados e Soluções
* *Desafio da Coleta Linear:* Fazer com que o cliente responda às 5 perguntas da entrevista financeira em ordem correta.
* *Solução:* Desenvolvimento de um controle indexador por etapas (`interview_step`). O robô intercepta qualquer mensagem e só avança a régua de cálculo após a validação do input anterior.

##  Tutorial de Execução e Homologação de Testes

### 1. Preparação do Ambiente
Abra o prompt de comando ou terminal na raiz do projeto e instale as dependências:
```bash
pip install -r requirements.txt

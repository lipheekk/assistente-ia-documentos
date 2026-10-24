# assistente-ia-documentos

> **Projeto de estudo.** Este repositório faz parte de um estudo independente sobre inteligência artificial, feito por fora do trabalho, para o meu desenvolvimento pessoal. Não é um produto pronto para produção: o objetivo é aprender, na prática, a integrar modelos de IA em aplicações Python.

Aplicação web em que o usuário envia um documento (PDF, TXT ou Markdown) e faz perguntas sobre o conteúdo. As respostas são geradas por um modelo de IA via API, com base apenas no texto do documento.

## O que este projeto pratica

- Integração com a API de um modelo de IA (Anthropic) usando o SDK oficial em Python
- Engenharia de prompt: instruir o modelo a responder só com base no documento
- Back-end com Flask: upload de arquivos, rotas JSON e tratamento de erros
- Gerenciamento seguro de segredos com variáveis de ambiente
- Interface web simples em HTML, CSS e JavaScript puro

## Tecnologias

Python 3.10+, Flask, pypdf, python-dotenv, SDK `anthropic`.

## Estrutura

```
assistente-ia-documentos/
├── app.py              # servidor Flask, leitura do documento e chamada à API
├── templates/
│   └── index.html      # interface web
├── requirements.txt
├── .env.example        # modelo das variáveis de ambiente
└── .gitignore
```

## Instalação

```bash
git clone https://github.com/<seu-usuario>/assistente-ia-documentos.git
cd assistente-ia-documentos

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # Windows: copy .env.example .env
```

Abra o `.env` e preencha `ANTHROPIC_API_KEY` com a sua chave, criada no [Console da Anthropic](https://console.anthropic.com/). O arquivo `.env` está no `.gitignore` e **nunca deve ser enviado ao repositório**.

| Variável | Obrigatória | Descrição |
|---|---|---|
| `ANTHROPIC_API_KEY` | Sim | Chave de acesso à API |
| `ANTHROPIC_MODEL` | Não | Modelo usado (padrão: `claude-sonnet-5-5`) |
| `MAX_CHARS_DOCUMENTO` | Não | Limite de caracteres enviados ao modelo (padrão: 150000) |
| `PORT` | Não | Porta do servidor (padrão: 5000) |

## Como usar

```bash
python app.py
```

Acesse `http://localhost:5000`, envie um documento e faça perguntas.

**Exemplos de perguntas**

- "Faça um resumo de três linhas deste documento."
- "Qual é o prazo de pagamento citado?"
- "Quais são as obrigações da parte contratada?"
- "O documento menciona multa por atraso?" (se não mencionar, o assistente avisa)

**Usando pela linha de comando (curl)**

```bash
# 1. enviar o documento (a resposta traz o doc_id)
curl -F "arquivo=@contrato.pdf" http://localhost:5000/upload

# 2. perguntar usando o doc_id recebido
curl -X POST http://localhost:5000/perguntar \
  -H "Content-Type: application/json" \
  -d '{"doc_id": "COLE_O_DOC_ID", "pergunta": "Qual é o prazo de pagamento?"}'
```

## Tratamento de erros

| Situação | Comportamento |
|---|---|
| Chave ausente ou inválida | Mensagem orientando a configurar o `.env` |
| Limite de requisições (429) | Pede para aguardar e tentar de novo |
| Falha de conexão | Informa que não foi possível acessar a API |
| Formato não suportado ou arquivo > 10 MB | Rejeitado com mensagem clara |
| PDF escaneado, vazio ou corrompido | Informa que não foi possível extrair texto |
| Documento muito longo | Usa só o início e avisa na tela |

## Limitações conhecidas

- Os documentos ficam só em memória e somem ao reiniciar o servidor.
- PDFs escaneados (imagens) não são lidos, pois não há OCR.
- Cada pergunta é independente: não há histórico de conversa.
- Documentos muito longos são cortados em vez de divididos em partes.

## Próximos passos (ideias de estudo)

- [ ] Dividir documentos longos em trechos e buscar os mais relevantes (RAG)
- [ ] Manter o histórico da conversa
- [ ] Suporte a `.docx` e a OCR
- [ ] Respostas em streaming
- [ ] Testes automatizados com a API simulada (mock)
- [ ] Deploy com Docker

## Licença

Uso livre para fins de estudo.

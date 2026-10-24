# assistente-ia-documentos

Projeto que fiz como estudo sobre IA, por fora do trabalho, para meu desenvolvimento pessoal. Não é um produto pronto, é um jeito de aprender na prática como usar a API de um modelo de IA dentro de uma aplicação.

Você envia um documento (PDF, TXT ou Markdown) e faz perguntas sobre ele. O modelo responde usando só o conteúdo do documento.

## Tecnologias

Python, Flask, pypdf e a API da Anthropic. A interface é uma página HTML simples.

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

## Como rodar

Você vai precisar do Python 3.10 ou mais novo e de uma chave de API da Anthropic (https://console.anthropic.com/).

```bash
git clone https://github.com/<seu-usuario>/assistente-ia-documentos.git
cd assistente-ia-documentos

python -m venv .venv
source .venv/bin/activate   # no Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env        # no Windows: copy .env.example .env
```

Abra o arquivo `.env` e coloque sua chave em `ANTHROPIC_API_KEY`. Esse arquivo não vai pro repositório.

Depois é só rodar:

```bash
python app.py
```

E abrir http://localhost:5000.

## Exemplos de uso

Pela página, envie um arquivo e pergunte coisas como:

- Faça um resumo deste documento em três linhas.
- Qual é o prazo de pagamento citado?
- O documento fala de multa por atraso?

Se a resposta não estiver no documento, o assistente avisa que não encontrou.

Também dá para usar pelo terminal:

```bash
curl -F "arquivo=@contrato.pdf" http://localhost:5000/upload

curl -X POST http://localhost:5000/perguntar \
  -H "Content-Type: application/json" \
  -d '{"doc_id": "ID_RETORNADO_NO_UPLOAD", "pergunta": "Qual é o prazo de pagamento?"}'
```

## Configuração

Além da chave, o `.env` aceita estas variáveis, todas opcionais:

- `ANTHROPIC_MODEL`: modelo usado (padrão `claude-sonnet-5-5`)
- `MAX_CHARS_DOCUMENTO`: limite de caracteres enviados ao modelo (padrão 150000)
- `PORT`: porta do servidor (padrão 5000)

## Erros tratados

Chave ausente ou inválida, limite de requisições, falta de conexão, formato de arquivo não aceito, arquivo maior que 10 MB e PDF sem texto. Em todos os casos o usuário recebe uma mensagem explicando o que houve.

## Limitações

- Os documentos ficam só na memória e somem quando o servidor reinicia.
- PDF escaneado (imagem) não funciona, não tem OCR.
- Cada pergunta é independente, não há histórico de conversa.
- Documentos muito grandes são cortados.

## O que quero estudar depois

Dividir documentos grandes em partes e buscar só as mais relevantes (RAG), guardar o histórico da conversa e mostrar a resposta aos poucos, em streaming.

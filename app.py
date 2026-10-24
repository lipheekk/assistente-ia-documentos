"""Assistente de IA para documentos: envie um arquivo e pergunte sobre o conteúdo."""
import os
import uuid
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from pypdf import PdfReader

load_dotenv()

MODELO = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
MAX_CHARS = int(os.getenv("MAX_CHARS_DOCUMENTO", "150000"))
EXTENSOES = {".pdf", ".txt", ".md"}

SYSTEM_PROMPT = (
    "Você é um assistente que responde perguntas sobre um documento. "
    "Responda somente com base no conteúdo do documento fornecido, em português. "
    "Se a resposta não estiver no documento, diga claramente que não encontrou a informação. "
    "Quando possível, indique o trecho em que baseou a resposta."
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

# Documentos ficam só em memória (projeto de estudo): somem ao reiniciar o servidor.
documentos: dict[str, dict] = {}


class ErroUsuario(Exception):
    """Erro com mensagem segura para mostrar ao usuário."""

    def __init__(self, mensagem: str, status: int = 400):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status


def obter_cliente() -> anthropic.Anthropic:
    chave = os.getenv("ANTHROPIC_API_KEY")
    if not chave:
        raise ErroUsuario(
            "Chave da API não configurada. Copie .env.example para .env e preencha ANTHROPIC_API_KEY.",
            500,
        )
    return anthropic.Anthropic(api_key=chave)


def extrair_texto(arquivo, extensao: str) -> str:
    if extensao == ".pdf":
        try:
            leitor = PdfReader(arquivo)
            texto = "\n".join((pagina.extract_text() or "") for pagina in leitor.pages)
        except Exception:
            raise ErroUsuario("Não foi possível ler o PDF. Verifique se o arquivo não está corrompido ou protegido por senha.")
    else:
        try:
            texto = arquivo.read().decode("utf-8")
        except UnicodeDecodeError:
            raise ErroUsuario("O arquivo de texto precisa estar codificado em UTF-8.")
    texto = texto.strip()
    if not texto:
        raise ErroUsuario("Nenhum texto encontrado. PDFs escaneados (imagens) ainda não são suportados.")
    return texto


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/upload")
def upload():
    arquivo = request.files.get("arquivo")
    if not arquivo or not arquivo.filename:
        raise ErroUsuario("Selecione um arquivo para enviar.")
    extensao = Path(arquivo.filename).suffix.lower()
    if extensao not in EXTENSOES:
        raise ErroUsuario(f"Formato não suportado. Use: {', '.join(sorted(EXTENSOES))}.")

    texto = extrair_texto(arquivo, extensao)
    truncado = len(texto) > MAX_CHARS
    doc_id = uuid.uuid4().hex
    documentos[doc_id] = {"nome": arquivo.filename, "texto": texto[:MAX_CHARS]}
    return jsonify(doc_id=doc_id, nome=arquivo.filename, caracteres=len(texto), truncado=truncado)


@app.post("/perguntar")
def perguntar():
    dados = request.get_json(silent=True) or {}
    pergunta = (dados.get("pergunta") or "").strip()
    doc = documentos.get(dados.get("doc_id"))
    if not doc:
        raise ErroUsuario("Documento não encontrado. Envie o arquivo novamente.", 404)
    if not pergunta:
        raise ErroUsuario("Digite uma pergunta.")

    cliente = obter_cliente()
    try:
        resposta = cliente.messages.create(
            model=MODELO,
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"<documento nome=\"{doc['nome']}\">\n{doc['texto']}\n</documento>\n\nPergunta: {pergunta}",
            }],
        )
    except anthropic.AuthenticationError:
        raise ErroUsuario("Chave da API inválida. Confira o valor de ANTHROPIC_API_KEY.", 401)
    except anthropic.RateLimitError:
        raise ErroUsuario("Limite de requisições atingido. Aguarde um pouco e tente de novo.", 429)
    except anthropic.APIConnectionError:
        raise ErroUsuario("Sem conexão com a API. Verifique sua internet.", 503)
    except anthropic.APIStatusError as e:
        raise ErroUsuario(f"A API retornou um erro ({e.status_code}). Tente novamente.", 502)

    texto = "".join(bloco.text for bloco in resposta.content if bloco.type == "text")
    return jsonify(resposta=texto)


@app.errorhandler(ErroUsuario)
def tratar_erro_usuario(e: ErroUsuario):
    return jsonify(erro=e.mensagem), e.status


@app.errorhandler(413)
def arquivo_grande(_):
    return jsonify(erro="Arquivo maior que 10 MB."), 413


if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")

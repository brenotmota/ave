"""
Módulo para geração de boleto via API Cora (mTLS + OAuth 2.0).

Referência: https://developers.cora.com.br/reference

Cuidados:
- A API exige mutual TLS: os certificados ficam em certs/cora_cert.pem e certs/cora_key.pem.
- O token OAuth expira em 1 h; _obter_token() renova automaticamente.
- A URL base (produção vs. sandbox) vem de CORA_BASE_URL no .env.
"""
import os
import time
from datetime import date, timedelta
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("CORA_BASE_URL", "https://matls-clients.api.cora.com.br")
CLIENT_ID = os.getenv("CORA_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CORA_CLIENT_SECRET", "")
CERT = ("certs/cora_cert.pem", "certs/cora_key.pem")

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Cache simples de token em memória
_token_cache: dict = {"access_token": None, "expires_at": 0.0}


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def _obter_token() -> str:
    """Retorna token válido, renovando se necessário (buffer de 60 s)."""
    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"] - 60:
        return _token_cache["access_token"]

    with httpx.Client(cert=CERT, timeout=30) as client:
        resp = client.post(
            f"{BASE_URL}/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        data = resp.json()

    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + int(data.get("expires_in", 3600))
    return _token_cache["access_token"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _apenas_digitos(texto: str) -> str:
    return "".join(c for c in texto if c.isdigit())


def _valor_para_centavos(valor: str) -> int:
    """Converte '1.500,00' ou '1500.00' para centavos inteiros."""
    # Normaliza: remove separadores de milhar e converte vírgula → ponto
    normalizado = valor.replace(".", "").replace(",", ".")
    return int(round(float(normalizado) * 100))


# ---------------------------------------------------------------------------
# Função pública
# ---------------------------------------------------------------------------

def gerar_boleto(
    cnpj: str,
    valor: str,
    descricao: str,
    nf_pdf: str | None = None,  # reservado para futura anexação
) -> dict:
    """
    Cria um boleto bancário na API Cora e faz download do PDF.

    Parâmetros:
        cnpj      – CNPJ do sacado (formatado ou só dígitos)
        valor     – valor do serviço, ex: '1.500,00'
        descricao – descrição que aparece no boleto (max 100 chars)
        nf_pdf    – caminho do PDF da NF (reservado, não usado ainda)

    Retorna dict com: pdf_path, url, vencimento, codigo_barras.
    Lança httpx.HTTPStatusError em caso de falha na API.
    """
    token = _obter_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    cnpj_digits = _apenas_digitos(cnpj)
    valor_centavos = _valor_para_centavos(valor)
    vencimento = (date.today() + timedelta(days=3)).isoformat()
    codigo_referencia = f"NF-{cnpj_digits[:8]}-{date.today().strftime('%Y%m%d')}"

    payload = {
        "code": codigo_referencia,
        "customer": {
            "name": "Cliente",  # TODO: buscar razão social via API Receita se necessário
            "document": {
                "type": "CNPJ",
                "number": cnpj_digits,
            },
        },
        "payment_terms": {
            "due_date": vencimento,
            "amount": valor_centavos,
        },
        "description": descricao[:100],
    }

    with httpx.Client(cert=CERT, timeout=30) as client:
        # Cria o boleto
        resp = client.post(f"{BASE_URL}/invoices", json=payload, headers=headers)
        resp.raise_for_status()
        boleto = resp.json()
        boleto_id = boleto["id"]

        # Download do PDF
        pdf_resp = client.get(
            f"{BASE_URL}/invoices/{boleto_id}/pdf",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        pdf_resp.raise_for_status()

    pdf_path = str(DOWNLOAD_DIR / f"boleto_{boleto_id}.pdf")
    Path(pdf_path).write_bytes(pdf_resp.content)

    return {
        "pdf_path": pdf_path,
        "url": boleto.get("link", ""),
        "vencimento": vencimento,
        "codigo_barras": boleto.get("barcode", ""),
    }

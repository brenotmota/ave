"""
Módulo Google Drive + Sheets via Service Account.

Requisitos:
- credentials/google_sa.json  — arquivo da Service Account
- A SA deve ter acesso compartilhado à pasta do Drive (GDRIVE_FOLDER_ID)
  e à planilha (GSHEET_ID).
- Scopes necessários: drive + spreadsheets.

Estrutura da planilha (aba "Registros"):
  A: Data | B: CNPJ | C: Descrição | D: Valor | E: Link NF | F: Link Boleto
"""
import os
from datetime import datetime
from pathlib import Path

import googleapiclient.discovery
import googleapiclient.http
from dotenv import load_dotenv
from google.oauth2 import service_account

load_dotenv()

FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID", "")
SHEET_ID = os.getenv("GSHEET_ID", "")
SA_FILE = "credentials/google_sa.json"
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _credenciais() -> service_account.Credentials:
    return service_account.Credentials.from_service_account_file(SA_FILE, scopes=SCOPES)


def _upload_pdf(drive, nome: str, caminho: str) -> str:
    """
    Faz upload de um PDF para a pasta GDRIVE_FOLDER_ID e torna público.
    Retorna o webViewLink do arquivo.
    """
    metadata = {"name": nome, "parents": [FOLDER_ID]}
    media = googleapiclient.http.MediaFileUpload(caminho, mimetype="application/pdf")
    arquivo = (
        drive.files()
        .create(body=metadata, media_body=media, fields="id,webViewLink")
        .execute()
    )
    # Permissão pública de leitura
    drive.permissions().create(
        fileId=arquivo["id"],
        body={"type": "anyone", "role": "reader"},
    ).execute()
    return arquivo["webViewLink"]


def _nome_arquivo(prefixo: str, cnpj: str) -> str:
    data = datetime.today().strftime("%Y-%m-%d")
    cnpj_limpo = "".join(c for c in cnpj if c.isdigit())[:14]
    return f"{prefixo}_{cnpj_limpo}_{data}.pdf"


# ---------------------------------------------------------------------------
# Função pública
# ---------------------------------------------------------------------------

def registrar_e_enviar(
    cnpj: str,
    valor: str,
    descricao: str,
    nf_pdf: str,
    boleto_pdf: str | None,
    boleto_url: str,
) -> dict:
    """
    Faz upload dos PDFs para o Google Drive e registra uma linha na planilha.

    Parâmetros:
        cnpj       – CNPJ do tomador
        valor      – valor do serviço
        descricao  – descrição do serviço
        nf_pdf     – caminho local do PDF da NF
        boleto_pdf – caminho local do PDF do boleto (ou None)
        boleto_url – URL externa do boleto (fallback se boleto_pdf ausente)

    Retorna dict com: nf_url, boleto_url, sheet_url.
    """
    creds = _credenciais()
    drive = googleapiclient.discovery.build("drive", "v3", credentials=creds, cache_discovery=False)
    sheets = googleapiclient.discovery.build("sheets", "v4", credentials=creds, cache_discovery=False)

    # Upload NF
    nf_url = _upload_pdf(drive, _nome_arquivo("NF", cnpj), nf_pdf)

    # Upload boleto (se tiver PDF local, prefere ele)
    boleto_drive_url = boleto_url
    if boleto_pdf and Path(boleto_pdf).exists():
        boleto_drive_url = _upload_pdf(drive, _nome_arquivo("Boleto", cnpj), boleto_pdf)

    # Linha na planilha
    linha = [
        datetime.today().strftime("%d/%m/%Y"),
        cnpj,
        descricao,
        valor,
        nf_url,
        boleto_drive_url,
    ]
    sheets.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range="Registros!A:F",
        valueInputOption="USER_ENTERED",
        body={"values": [linha]},
    ).execute()

    sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    return {"nf_url": nf_url, "boleto_url": boleto_drive_url, "sheet_url": sheet_url}

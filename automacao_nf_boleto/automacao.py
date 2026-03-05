"""
Orquestrador principal: ISS → Cora → Google Drive/Sheets.

Uso:
    from automacao import executar
    executar(dados, callback=lambda msg: print(msg))
"""
import asyncio
from typing import Callable

from iss_nf import emitir_nf
from cora_boleto import gerar_boleto
from google_drive import registrar_e_enviar


def executar(dados: dict, callback: Callable[[str], None] | None = None) -> dict:
    """
    Executa o fluxo completo para um conjunto de dados de serviço.

    Parâmetros:
        dados     – dict com chaves: cnpj, valor, descricao
        callback  – função chamada a cada etapa para notificar o usuário

    Retorna dict com: nf_url, boleto_url, sheet_url, vencimento, codigo_barras
    Lança exceção em caso de falha (app.py trata e notifica o usuário).
    """

    def notify(msg: str):
        if callback:
            callback(msg)

    cnpj = dados["cnpj"]
    valor = dados["valor"]
    descricao = dados["descricao"]

    # Etapa 1 — NF no portal ISS
    notify("*Etapa 1/3* — Emitindo NF no portal ISS...")
    nf_pdf = asyncio.run(emitir_nf(cnpj=cnpj, valor=valor, descricao=descricao))
    notify(f"NF emitida. PDF salvo em `{nf_pdf}`")

    # Etapa 2 — Boleto Cora
    notify("*Etapa 2/3* — Gerando boleto na Cora...")
    boleto = gerar_boleto(cnpj=cnpj, valor=valor, descricao=descricao, nf_pdf=nf_pdf)
    notify(
        f"Boleto criado.\n"
        f"  Vencimento: {boleto['vencimento']}\n"
        f"  Código: `{boleto['codigo_barras']}`"
    )

    # Etapa 3 — Google Drive + Sheets
    notify("*Etapa 3/3* — Registrando no Google Drive e Sheets...")
    links = registrar_e_enviar(
        cnpj=cnpj,
        valor=valor,
        descricao=descricao,
        nf_pdf=nf_pdf,
        boleto_pdf=boleto.get("pdf_path"),
        boleto_url=boleto.get("url", ""),
    )

    resultado = {
        **links,
        "vencimento": boleto["vencimento"],
        "codigo_barras": boleto["codigo_barras"],
    }

    notify(
        "Concluído!\n"
        f"  NF: {resultado['nf_url']}\n"
        f"  Boleto: {resultado['boleto_url']}\n"
        f"  Planilha: {resultado['sheet_url']}"
    )

    return resultado

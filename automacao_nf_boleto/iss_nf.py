"""
Módulo Playwright para emissão de NF no portal ISS municipal.

Atenção — leia antes de modificar:
- O portal usa RichFaces 4 com AJAX pesado. Não simplifique a sequência de cliques.
- Não remova os asyncio.sleep() — o portal precisa processar o AJAX antes do próximo passo.
- Não troque page.evaluate() por locator.click() em campos com listeners AJAX.
- Não altere seletores CSS sem testar; o portal muda layout sem aviso.
- Timeouts de 30 s são normais — não reduza.
"""
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from playwright.async_api import Page, async_playwright

load_dotenv()

ISS_URL = os.getenv("ISS_URL", "").rstrip("/")
ISS_USER = os.getenv("ISS_USER", "")
ISS_PASS = os.getenv("ISS_PASS", "")

TIMEOUT = 30_000  # ms — portal ISS é lento, não reduza
MAX_RETRIES = 3    # tentativas totais antes de desistir
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

async def _fazer_login(page: Page) -> None:
    await page.goto(ISS_URL + "/login", wait_until="networkidle", timeout=TIMEOUT)
    await page.locator("#username").fill(ISS_USER)
    await page.locator("#password").fill(ISS_PASS)
    await page.locator("button[type=submit]").click()
    await page.wait_for_url("**/home", timeout=TIMEOUT)


async def _garantir_login(page: Page) -> None:
    """Re-faz login se a sessão expirou."""
    if "/login" in page.url:
        await _fazer_login(page)


async def _preencher_ajax(page: Page, selector: str, valor: str) -> None:
    """
    Preenche um campo e dispara change + blur, que o RichFaces precisa para
    acionar os listeners AJAX associados ao campo.
    NÃO use locator.click() aqui — o evento não propaga corretamente.
    """
    loc = page.locator(selector)
    await loc.wait_for(state="visible", timeout=TIMEOUT)
    await loc.fill(valor)
    await page.evaluate(
        """(sel) => {
            const el = document.querySelector(sel);
            el.dispatchEvent(new Event('change', { bubbles: true }));
            el.dispatchEvent(new Event('blur',   { bubbles: true }));
        }""",
        selector,
    )


def _apenas_digitos(texto: str) -> str:
    return "".join(c for c in texto if c.isdigit())


def _valor_para_numerico(valor: str) -> str:
    """Converte '1.500,00' → '1500.00' (notação ponto para o portal)."""
    # Remove separadores de milhar e troca vírgula por ponto
    sem_milhar = valor.replace(".", "")
    return sem_milhar.replace(",", ".")


# ---------------------------------------------------------------------------
# Função pública
# ---------------------------------------------------------------------------

async def _emitir_nf_uma_vez(cnpj_digits: str, valor_numerico: str, descricao: str) -> str:
    """Tenta emitir a NF uma única vez. Lançada exceção em qualquer falha."""
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        # Login
        await _fazer_login(page)

        # Navega para o formulário de emissão
        await page.goto(ISS_URL + "/nfe/emitir", wait_until="networkidle", timeout=TIMEOUT)
        await _garantir_login(page)

        # --- Tomador ---
        # TODO: confirmar seletores contra o portal real
        await _preencher_ajax(page, "#cnpjTomador", cnpj_digits)
        await asyncio.sleep(1.5)  # aguarda AJAX buscar dados do tomador pelo CNPJ

        await page.wait_for_selector("#nomeTomador", timeout=TIMEOUT)

        # --- Discriminação ---
        await _preencher_ajax(page, "#discriminacao", descricao)
        await asyncio.sleep(0.5)

        # --- Valor do serviço ---
        await _preencher_ajax(page, "#valorServico", valor_numerico)
        await asyncio.sleep(0.5)

        # --- Emitir e baixar PDF ---
        async with page.expect_download(timeout=60_000) as download_info:
            await page.locator("#btnEmitir").click()

        download = await download_info.value
        pdf_path = str(DOWNLOAD_DIR / download.suggested_filename)
        await download.save_as(pdf_path)

        await browser.close()

    return pdf_path


async def emitir_nf(cnpj: str, valor: str, descricao: str) -> str:
    """
    Emite NF no portal ISS municipal via Playwright.

    Tenta até MAX_RETRIES vezes com backoff exponencial (2 s, 4 s, 8 s…)
    em caso de erros de rede ou timeout do portal.

    Parâmetros:
        cnpj      – CNPJ do tomador (formatado ou só dígitos)
        valor     – valor do serviço, ex: '1.500,00' ou '1500,00'
        descricao – descrição/discriminação do serviço

    Retorna o caminho local do PDF da NF gerada.
    Lança a última exceção após esgotar as tentativas.
    """
    cnpj_digits = _apenas_digitos(cnpj)
    valor_numerico = _valor_para_numerico(valor)
    ultimo_erro: Exception | None = None

    for tentativa in range(1, MAX_RETRIES + 1):
        try:
            return await _emitir_nf_uma_vez(cnpj_digits, valor_numerico, descricao)
        except Exception as e:
            ultimo_erro = e
            if tentativa < MAX_RETRIES:
                espera = 2 ** tentativa  # 2 s, 4 s, 8 s
                await asyncio.sleep(espera)

    raise ultimo_erro

"""
Testes de integração com o sandbox da API Cora.

Antes de rodar:
1. Configure CORA_BASE_URL no .env apontando para o sandbox:
       CORA_BASE_URL=https://matls-clients.api.cora.com.br/sandbox   (confirmar URL no portal Cora)
2. Certifique-se de que certs/cora_cert.pem e certs/cora_key.pem existem.
3. CORA_CLIENT_ID e CORA_CLIENT_SECRET devem ser os do ambiente sandbox.

Rodar:
    cd automacao_nf_boleto
    pytest tests/test_cora_sandbox.py -v

    # ou diretamente:
    python tests/test_cora_sandbox.py
"""
import sys
import os

# Garante que os módulos do projeto sejam encontrados
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

# Pula todos os testes se as credenciais não estiverem configuradas
import pytest

CREDS_OK = all([
    os.getenv("CORA_CLIENT_ID"),
    os.getenv("CORA_CLIENT_SECRET"),
    os.path.exists("certs/cora_cert.pem"),
    os.path.exists("certs/cora_key.pem"),
])

pytestmark = pytest.mark.skipif(
    not CREDS_OK,
    reason="Credenciais Cora não configuradas. Veja o cabeçalho do arquivo.",
)


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------

def test_obter_token_retorna_string_nao_vazia():
    from cora_boleto import _obter_token

    token = _obter_token()
    assert isinstance(token, str) and len(token) > 0, "Token vazio ou inválido"


def test_token_e_reutilizado_do_cache():
    from cora_boleto import _obter_token, _token_cache

    token1 = _obter_token()
    token2 = _obter_token()
    assert token1 == token2, "Token deveria vir do cache na segunda chamada"


def test_gerar_boleto_retorna_campos_obrigatorios():
    from cora_boleto import gerar_boleto

    resultado = gerar_boleto(
        cnpj="00.000.000/0001-91",  # CNPJ fictício aceito pelo sandbox
        valor="150,00",
        descricao="Teste sandbox — consultoria de TI",
    )

    assert "pdf_path" in resultado, "Campo pdf_path ausente"
    assert "url" in resultado, "Campo url ausente"
    assert "vencimento" in resultado, "Campo vencimento ausente"
    assert "codigo_barras" in resultado, "Campo codigo_barras ausente"


def test_pdf_do_boleto_e_salvo_localmente():
    import os
    from cora_boleto import gerar_boleto

    resultado = gerar_boleto(
        cnpj="00.000.000/0001-91",
        valor="200,00",
        descricao="Teste sandbox — download PDF",
    )

    pdf_path = resultado["pdf_path"]
    assert os.path.exists(pdf_path), f"PDF não encontrado em {pdf_path}"
    assert os.path.getsize(pdf_path) > 1_000, "PDF parece vazio (< 1 KB)"


def test_valor_centavos_arredondamento():
    """Garante que a conversão de valor não perde centavos."""
    from cora_boleto import _valor_para_centavos

    assert _valor_para_centavos("1.500,00") == 150_000
    assert _valor_para_centavos("1500.00") == 150_000
    assert _valor_para_centavos("0,99") == 99
    assert _valor_para_centavos("1000") == 100_000


# ---------------------------------------------------------------------------
# Execução direta (sem pytest)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not CREDS_OK:
        print("ERRO: Credenciais Cora não configuradas. Veja o cabeçalho do arquivo.")
        sys.exit(1)

    testes = [
        test_obter_token_retorna_string_nao_vazia,
        test_token_e_reutilizado_do_cache,
        test_gerar_boleto_retorna_campos_obrigatorios,
        test_pdf_do_boleto_e_salvo_localmente,
        test_valor_centavos_arredondamento,
    ]

    passou = 0
    falhou = 0
    for teste in testes:
        try:
            teste()
            print(f"  OK  {teste.__name__}")
            passou += 1
        except Exception as e:
            print(f"FAIL  {teste.__name__}: {e}")
            falhou += 1

    print(f"\n{passou} passou(ram), {falhou} falhou(ram).")
    sys.exit(0 if falhou == 0 else 1)

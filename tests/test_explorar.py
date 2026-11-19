"""Explorar SEG na versão pública: pasta de exemplo, busca, abrir PDF e troca de abas."""
from conftest import HTML


def abrir(pg):
    pg.goto(HTML + "?demo#explorar")
    pg.wait_for_function("window.__EX && __EX.ok && __EX.indice && !__EX.indexando && __EX.recentes", timeout=60000)


def test_explorar_abre_com_a_demo(pagina):
    abrir(pagina)
    assert pagina.is_visible("#vExplorar")
    assert pagina.locator(".exp-at").count() >= 5          # atalhos do setor achados nas pastas de exemplo
    assert pagina.locator(".exp-lista .exp-it").count() > 0  # chegou por último
    assert not pagina.erros


def test_busca_sem_acento_e_varias_palavras(pagina):
    abrir(pagina)
    pagina.fill("#expBusca", "nr 35 turma")
    pagina.press("#expBusca", "Enter")
    nomes = pagina.locator(".exp-lista .exp-nm").all_inner_texts()
    assert any("NR-35" in n for n in nomes)
    pagina.fill("#expBusca", "licenca operacao")
    pagina.press("#expBusca", "Enter")
    assert pagina.locator(".exp-lista .exp-it").count() == 1


def test_abrir_pdf_em_aba_nova(pagina):
    abrir(pagina)
    with pagina.context.expect_page() as nova:
        pagina.locator(".exp-lista .exp-it .exp-ab").first.click()
    assert nova.value.locator("iframe").count() == 1


def test_troca_de_abas(pagina):
    abrir(pagina)
    pagina.click(".nav button[data-v=painel]")
    assert pagina.is_visible("#vPainel") and pagina.is_hidden("#vExplorar")
    pagina.click(".nav button[data-v=explorar]")
    assert pagina.is_visible("#vExplorar") and pagina.is_hidden("#vPainel")
    assert not pagina.erros


def test_sem_demo_pede_a_pasta(pagina):
    pagina.goto(HTML + "#explorar")
    pagina.wait_for_selector("[data-conectar]")
    assert "Escolher a pasta SEG" in pagina.inner_text("#vExplorar")

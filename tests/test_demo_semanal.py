"""Modo demonstração e relatório semanal de DDS (tudo com dados fictícios gerados no navegador)."""
from conftest import HTML, baixar
from pypdf import PdfReader


def abrir_demo(pg):
    pg.goto(HTML)
    pg.click("#dDemo")
    pg.wait_for_function("!D.varrendo && D.docs.length>0", timeout=60000)


def test_demo_monta_os_quatro_tipos(pagina):
    abrir_demo(pagina)
    tipos = pagina.evaluate("[...new Set(D.docs.map(d=>d.tipo))].sort()")
    assert tipos == ["DDS", "MS", "PT", "QA"]
    assert pagina.is_visible("#demoAviso")
    # a demonstração não fica guardada no navegador
    assert pagina.evaluate("IDB.get('cache')") is None
    assert not pagina.erros


def test_demo_pelo_endereco(pagina):
    pagina.goto(HTML + "?demo")
    pagina.wait_for_function("!D.varrendo && D.docs.length>0", timeout=60000)
    assert not pagina.erros


def test_relatorio_semanal_de_dds(pagina, tmp_path):
    abrir_demo(pagina)
    pagina.click(".nav button[data-v=juntar]")
    pagina.click(".tipo[data-tipo=DDS]")
    pagina.select_option("#mes", "3")
    pagina.wait_for_timeout(300)
    pagina.click("#puxarBtn")
    pagina.wait_for_selector("#semCard:not([hidden])", timeout=30000)
    pagina.wait_for_function("!document.querySelector('#puxarBtn') || !/Carregando/.test(document.querySelector('#puxarBtn').textContent)")
    assert pagina.locator("#semSemanas button").count() >= 4
    # participação: presentes/total vira %, texto inválido é marcado
    part = pagina.locator("#semLinhas .sem-l").first.locator("input[data-c=part]")
    part.fill("29/35")
    assert "82,86%" in pagina.locator("#semLinhas .sem-l").first.inner_text()
    part.fill("abc")
    assert "valor inválido" in pagina.locator("#semLinhas .sem-l").first.inner_text()
    part.fill("90")
    pdf = baixar(pagina, "#semPdf").path()
    texto = PdfReader(pdf).pages[0].extract_text()
    assert "RELATÓRIO DE DDS" in texto and "90%" in texto
    assert not pagina.erros


def test_semanal_some_fora_do_dds(pagina):
    abrir_demo(pagina)
    pagina.click(".nav button[data-v=juntar]")
    pagina.click(".tipo[data-tipo=PT]")
    assert pagina.is_hidden("#semCard")

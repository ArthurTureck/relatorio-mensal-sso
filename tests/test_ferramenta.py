"""Ferramenta 'Juntar e classificar': arquivos com problema, volume e entradas estranhas."""
import time
from pypdf import PdfReader
from conftest import HTML, FIX, baixar

def abrir(pg, arquivos):
    pg.goto(HTML + "#juntar"); pg.wait_for_timeout(300)
    pg.set_input_files("#arquivos", [str(p) for p in arquivos]); pg.wait_for_timeout(3500)

def test_arquivos_com_problema_sao_avisados_e_ficam_de_fora(pagina, tmp_path):
    abrir(pagina, sorted((FIX/"problemas").iterdir()))
    ch = pagina.inner_text("#checks")
    assert pagina.get_attribute(".tipo[aria-pressed=true]", "data-tipo") == "QA"
    for esperado in ["Arquivo vazio", "corrompido", "protegido por senha", "Imagem corrompida",
                     "dia inválido", "sem o dia", "idêntico", "parecem ser de DDS", "imagem(ns)"]:
        assert esperado in ch, esperado
    assert "2 arquivo(s) ignorado" in pagina.inner_text("#ignorados")        # Thumbs.db e .txt
    html = pagina.inner_html("#lista")
    assert "<img src=x" not in html and "&lt;img" in html                   # nome malicioso escapado
    assert "Dia 25" in pagina.inner_text("#lista")                          # "25.1 - ..." = dia 25
    n = int(pagina.inner_text("#kpi"))
    dl = baixar(pagina, "#gerar"); f = tmp_path/dl.suggested_filename; dl.save_as(f)
    assert len(PdfReader(f).pages) == n
    assert not pagina.erros

def test_funciona_com_armazenamento_do_navegador_bloqueado(navegador, tmp_path):
    ctx = navegador.new_context(accept_downloads=True)
    ctx.add_init_script("Storage.prototype.setItem=()=>{throw new Error('bloqueado')};Storage.prototype.getItem=()=>{throw new Error('bloqueado')};")
    pg = ctx.new_page(); erros = []; pg.on("pageerror", lambda e: erros.append(str(e)))
    abrir(pg, sorted((FIX/"problemas").glob("0[1-3] - Relato*.pdf")))
    dl = baixar(pg, "#gerar"); f = tmp_path/dl.suggested_filename; dl.save_as(f)
    assert len(PdfReader(f).pages) == 3 and not erros
    ctx.close()

def test_121_pts_lidas_e_juntadas_rapido(pagina, tmp_path):
    t0 = time.time()
    pagina.goto(HTML + "#juntar"); pagina.set_input_files("#arquivos", [str(p) for p in sorted((FIX/"muitos").iterdir())])
    pagina.wait_for_function("document.querySelector('#kpi').textContent==='121'", timeout=60000)
    dl = baixar(pagina, "#gerar"); f = tmp_path/dl.suggested_filename; dl.save_as(f)
    assert len(PdfReader(f).pages) == 121                                   # só a 1ª página de cada
    assert time.time() - t0 < 30

def test_mes_curto_e_ano_invalido(pagina):
    abrir(pagina, sorted((FIX/"muitos").iterdir()))
    pagina.select_option("#mes", "2"); pagina.wait_for_timeout(200)
    assert "dia inválido" in pagina.inner_text("#checks")                    # dia 30 em fevereiro
    pagina.fill("#ano", "1800"); pagina.dispatch_event("#ano", "change")
    assert "1800" not in pagina.inner_text("#nomeSaida") and "NaN" not in pagina.inner_text("#nomeSaida")

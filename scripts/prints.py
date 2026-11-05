"""Gera as imagens do README (docs/*.png) usando só os dados fictícios de tests/fixtures."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "tests"))
from conftest import HTML, FIX, MOCK_PASTA
from playwright.sync_api import sync_playwright
DOCS = pathlib.Path(__file__).resolve().parent.parent / "docs"; DOCS.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={"width": 1280, "height": 860}, device_scale_factor=1.5); ctx.add_init_script(MOCK_PASTA)
    pg = ctx.new_page(); pg.goto(HTML)
    pg.evaluate("()=>{const i=document.createElement('input');i.type='file';i.id='__fx';i.webkitdirectory=true;i.multiple=true;document.body.appendChild(i);}")
    pg.set_input_files("#__fx", str(FIX/"rede"/"Seguranca do Trabalho")); pg.evaluate("window.__montar([...document.getElementById('__fx').files])")
    pg.click("#dConectar2"); pg.wait_for_function("!D.varrendo && D.docs.length>0")
    pg.select_option("#dPreset", "custom"); pg.fill("#dIni", "2026-01-01"); pg.fill("#dFim", "2026-10-31"); pg.dispatch_event("#dFim", "change"); pg.evaluate("document.activeElement.blur()"); pg.wait_for_timeout(400)
    pg.screenshot(path=str(DOCS/"painel-visao-geral.png"))
    pg.click("#dTipos button[data-t=QA]"); pg.wait_for_timeout(400); pg.evaluate("window.scrollTo(0,560)"); pg.wait_for_timeout(200)
    pg.screenshot(path=str(DOCS/"painel-quase-acidentes.png"))
    pg.click(".nav button[data-v=juntar]"); pg.click(".tipo[data-tipo=PT]"); pg.select_option("#mes", "10"); pg.fill("#ano", "2026"); pg.dispatch_event("#ano", "change")
    pg.wait_for_timeout(300); pg.click("#puxarBtn"); pg.wait_for_function("itens.length>20", timeout=30000); pg.wait_for_timeout(1500)
    pg.evaluate("window.scrollTo(0,240)"); pg.wait_for_timeout(200)
    pg.screenshot(path=str(DOCS/"ferramenta-juntar.png"))
    b.close()
print("ok")

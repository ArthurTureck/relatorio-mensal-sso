"""Painel: lê uma árvore de pastas, filtra por tipo e período, detecta arquivos novos."""
import re
from conftest import HTML, FIX, baixar

BASE = FIX/"rede"/"Seguranca do Trabalho"
MES = re.compile(r"^\d{1,2}\. ")

def esperado():
    """Conta como o painel deve contar: só arquivos em pastas de mês, sem relatórios gerados nem investigação."""
    c = {}
    for tipo, pasta in {"PT": "02 - Operacional", "DDS": "01 - DDS", "QA": "04 - Emergencia/4.2.1 - Relato Quase Acidente",
                        "MS": "04 - Emergencia/4.2.2 - Melhorias de Segurança"}.items():
        c[tipo] = sum(1 for f in (BASE/pasta).rglob("*") if f.is_file() and MES.match(f.parent.name)
                      and f.suffix.lower() in (".pdf", ".png") and not f.name.startswith(("Permissão de Trabalho_", "Investiga")))
    return c

def conectar(pg):
    pg.goto(HTML); pg.wait_for_timeout(300)
    pg.evaluate("()=>{const i=document.createElement('input');i.type='file';i.id='__fx';i.webkitdirectory=true;i.multiple=true;document.body.appendChild(i);}")
    pg.set_input_files("#__fx", str(BASE))
    pg.evaluate("window.__montar([...document.getElementById('__fx').files])")
    pg.click("#dConectar2"); pg.wait_for_function("!D.varrendo && D.docs.length>0", timeout=60000)

def test_conta_cada_tipo_como_nas_pastas(pagina):
    conectar(pagina)
    achou = pagina.evaluate("Object.fromEntries(['PT','DDS','QA','MS'].map(t=>[t,D.docs.filter(d=>d.tipo===t).length]))")
    assert achou == esperado()
    nomes = pagina.evaluate("D.docs.map(d=>d.nome).join('|')")
    for fora in ["Permissão de Trabalho_", "Investigação", "IMG_0001", "PT em branco", "Thumbs"]:
        assert fora not in nomes, fora
    assert pagina.evaluate("(()=>{const d=D.docs.find(x=>x.nome.startsWith('Document_'));return [d.tipo,d.mes,d.dia]})()") == ["QA", 2, None]
    assert pagina.evaluate("(()=>{const d=D.docs.find(x=>x.nome.includes('Gilson'));return [d.tipo,d.mes,d.dia]})()") == ["QA", 8, 11]
    assert not pagina.erros

def test_filtros_clique_na_barra_busca_e_exportacoes(pagina, tmp_path):
    conectar(pagina)
    pagina.select_option("#dPreset", "custom"); pagina.fill("#dIni", "2026-01-01"); pagina.fill("#dFim", "2026-12-31")
    pagina.dispatch_event("#dFim", "change"); pagina.click("#dTipos button[data-t=QA]"); pagina.wait_for_timeout(300)
    assert pagina.inner_text("#dCorpo .kpis .v").startswith(str(esperado()["QA"]))
    pagina.evaluate("document.querySelectorAll('[data-g=mes] g.m')[7].dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    agosto = sum(1 for f in (BASE/"04 - Emergencia/4.2.1 - Relato Quase Acidente/8. Agosto").iterdir() if f.suffix.lower() in (".pdf", ".png"))
    assert pagina.evaluate("document.querySelectorAll('.tabela-docs tbody tr').length") == min(agosto, 60)
    for sel in ("#dPdf", "#dCsv", "[data-dpng=mes]"):
        dl = baixar(pagina, sel); f = tmp_path/dl.suggested_filename; dl.save_as(f); assert f.stat().st_size > 1000
    assert not pagina.erros

def test_detecta_documento_novo_e_carrega_na_ferramenta(pagina):
    conectar(pagina)
    pagina.evaluate("""()=>{const out=window.__raiz.filhos.get('04 - Emergencia').filhos.get('4.2.1 - Relato Quase Acidente').filhos.get('10. Outubro');
      const n='30 - Relato de Quase Acidente - Novo.pdf';out.filhos.set(n,{kind:'file',name:n,file:new File(['%PDF-1.4'],n,{lastModified:Date.now()})});}""")
    pagina.click("#dAtualizar"); pagina.wait_for_function("!D.varrendo && D.novos.size===1", timeout=30000)
    pagina.click(".nav button[data-v=juntar]"); pagina.click(".tipo[data-tipo=PT]")
    pagina.select_option("#mes", "10"); pagina.fill("#ano", "2026"); pagina.dispatch_event("#ano", "change"); pagina.wait_for_timeout(300)
    n = len(list((BASE/"02 - Operacional/2.1 - PT/PTs escaneadas 2026/10. Outubro").glob("*.pdf")))
    pagina.click("#puxarBtn"); pagina.wait_for_function(f"itens.length==={n}", timeout=30000)
    assert int(pagina.inner_text("#kpi")) == n

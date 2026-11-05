import pathlib, pytest
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parent.parent
HTML = (RAIZ / "dist" / "relatorio-mensal-sso.html").as_uri()
FIX = pathlib.Path(__file__).parent / "fixtures"

# Simula a API de pastas do navegador (showDirectoryPicker) a partir de arquivos reais do teste
MOCK_PASTA = """
window.__montar=(files)=>{
  const raiz={kind:'directory',name:'Seguranca do Trabalho',filhos:new Map()};
  for(const f of files){const p=f.webkitRelativePath.split('/').slice(1);let d=raiz;
    for(const s of p.slice(0,-1)){if(!d.filhos.has(s))d.filhos.set(s,{kind:'directory',name:s,filhos:new Map()});d=d.filhos.get(s);}
    d.filhos.set(p[p.length-1],{kind:'file',name:p[p.length-1],file:f});}
  const wrap=n=>n.kind==='file'?{kind:'file',name:n.name,getFile:async()=>n.file}:{kind:'directory',name:n.name,_n:n,
     entries:async function*(){for(const [k,v] of n.filhos)yield [k,wrap(v)];},isSameEntry:async o=>o&&o._n===n,
     queryPermission:async()=>'granted',requestPermission:async()=>'granted'};
  window.__raiz=raiz;window.showDirectoryPicker=async()=>wrap(raiz);
};"""

@pytest.fixture(scope="session")
def navegador():
    if not (RAIZ / "dist" / "relatorio-mensal-sso.html").exists():
        pytest.exit("Rode antes: python scripts/build.py")
    if not FIX.exists():
        pytest.exit("Rode antes: python tests/gerar_fixtures.py")
    with sync_playwright() as p:
        b = p.chromium.launch(); yield b; b.close()

@pytest.fixture
def pagina(navegador):
    ctx = navegador.new_context(accept_downloads=True, viewport={"width": 1300, "height": 900})
    ctx.add_init_script(MOCK_PASTA)
    pg = ctx.new_page(); pg.erros = []
    pg.on("pageerror", lambda e: pg.erros.append(str(e)))
    yield pg
    ctx.close()

def baixar(pg, seletor):
    with pg.expect_download(timeout=60000) as d:
        pg.click(seletor)
    return d.value

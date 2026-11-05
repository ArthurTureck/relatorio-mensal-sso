"""Gera dist/relatorio-mensal-sso.html: um único arquivo, que funciona offline.

As bibliotecas são baixadas do npm (versões fixas) e embutidas no HTML.
Uso:  python scripts/build.py
"""
import base64, pathlib, subprocess, tarfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
VENDOR = RAIZ / "vendor"
PACOTES = {
    "pdf-lib": "1.17.1",
    "pdfjs-dist": "3.11.174",
    "tesseract.js": "7.0.0",
    "tesseract.js-core": "6.1.2",
    "@tesseract.js-data/por": "1.0.0",
}

def baixar(nome, versao):
    destino = VENDOR / nome.replace("/", "__")
    if not destino.exists():
        VENDOR.mkdir(exist_ok=True)
        tgz = subprocess.run(["npm", "pack", f"{nome}@{versao}", "--silent"], cwd=VENDOR,
                             capture_output=True, text=True, check=True, shell=False).stdout.strip().splitlines()[-1]
        with tarfile.open(VENDOR / tgz) as t:
            t.extractall(destino, filter="data")
    return destino / "package"

def js(p):  # evita que "</script" dentro da biblioteca feche a tag
    return p.read_text(encoding="utf-8").replace("</script", "<\\/script")

def main():
    p = {n: baixar(n, v) for n, v in PACOTES.items()}
    html = (RAIZ / "src" / "relatorio.html").read_text(encoding="utf-8")
    trocas = {
        "/*PDFLIB*/": js(p["pdf-lib"] / "dist/pdf-lib.min.js"),
        "/*PDFJS*/": js(p["pdfjs-dist"] / "build/pdf.min.js"),
        "/*PDFWORKER*/": js(p["pdfjs-dist"] / "build/pdf.worker.min.js"),
        "/*TESSLIB*/": js(p["tesseract.js"] / "dist/tesseract.min.js"),
        "/*TESSCORE*/": js(p["tesseract.js-core"] / "tesseract-core-lstm.wasm.js"),
        "/*TESSWK*/": js(p["tesseract.js"] / "dist/worker.min.js"),
        "/*TESSTD*/": base64.b64encode((p["@tesseract.js-data/por"] / "4.0.0_best_int/por.traineddata.gz").read_bytes()).decode(),
    }
    for marca, conteudo in trocas.items():
        assert marca in html, f"marcador {marca} não encontrado em src/relatorio.html"
        html = html.replace(marca, conteudo)
    saida = RAIZ / "dist" / "relatorio-mensal-sso.html"
    saida.parent.mkdir(exist_ok=True)
    saida.write_text(html, encoding="utf-8")
    print(f"{saida.relative_to(RAIZ)}  ({saida.stat().st_size / 1e6:.1f} MB)")

if __name__ == "__main__":
    main()

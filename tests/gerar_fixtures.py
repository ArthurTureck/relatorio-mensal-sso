"""Cria pastas e PDFs FICTÍCIOS para os testes (nenhum documento real).

Gera tests/fixtures/:
  rede/Seguranca do Trabalho/...   árvore parecida com a pasta de rede (PT, DDS, Quase Acidente, Melhorias)
  problemas/                       arquivos com defeito para testar os avisos
  muitos/                          120 PTs para teste de volume
"""
import os, random, shutil, pathlib
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
from pypdf import PdfReader, PdfWriter

RAIZ = pathlib.Path(__file__).parent / "fixtures"
MESES = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
PESSOAS = ["Ana Souza","Bruno Lima","Carla Dias","Diego Rocha","Elisa Prado","Fabio Nunes","Sem Nome"]
TEMAS = ["Uso de EPI","Regras de Ouro","Ergonomia","Trabalho em Altura","Quase Acidentes"]
random.seed(42)

def formulario(caminho, titulo, linhas, paginas=1):
    """PDF com cara de formulário escaneado: faixa escura com o título e campos."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(caminho), pagesize=A4); w, h = A4
    for p in range(paginas):
        c.setFillGray(.25); c.rect(50, h-110, w-100, 26, fill=1, stroke=0)
        c.setFillGray(1); c.setFont("Helvetica-Bold", 13); c.drawCentredString(w/2, h-102, titulo)
        c.setFillGray(0); c.setFont("Helvetica", 11); y = h-140
        for l in linhas + (["(continuação)"] if p else []):
            c.drawString(60, y, l); c.line(60, y-4, w-60, y-4); y -= 26
        c.rect(50, y-10, w-100, h-110-(y-10), stroke=1, fill=0); c.showPage()
    c.save()

def rede():
    base = RAIZ / "rede" / "Seguranca do Trabalho"
    pt = base / "02 - Operacional/2.1 - PT/PTs escaneadas 2026"
    n = 100
    for m in range(1, 11):
        for _ in range(random.randint(18, 26)):
            d = random.randint(1, 28)
            formulario(pt/f"{m}. {MESES[m-1]}"/f"{d:02d} - PT {n}.pdf", f"PERMISSÃO DE TRABALHO - PT Nº {n}",
                       [f"Data: {d:02d}/{m:02d}/2026", "Serviço: manutenção preventiva", "Executante: equipe fictícia"], paginas=4); n += 1
    formulario(pt/"9. Setembro"/"Permissão de Trabalho_Unidade A_09.2026.pdf", "RELATÓRIO GERADO", ["não deve ser contado"])
    formulario(base/"02 - Operacional/2.1 - PT/2.1.1 - Modelos de PT/PT em branco.pdf", "MODELO", ["não deve ser contado"])
    dds = base / "01 - DDS/2026"
    for m in range(1, 11):
        for k in range(random.randint(8, 12)):
            d = random.randint(1, 28); tema = random.choice(TEMAS); quem = random.choice(PESSOAS[:4])
            formulario(dds/f"{m}. {MESES[m-1]}"/f"{d:02d} - DDS - {tema} {k} - {quem}.pdf", "DDS", [f"Evento: {tema}", f"Palestrante: {quem}"], paginas=2)
    qa = base / "04 - Emergencia/4.2.1 - Relato Quase Acidente"; ms = base / "04 - Emergencia/4.2.2 - Melhorias de Segurança"
    for m in range(1, 11):
        for k in range(random.randint(3, 30)):
            d = random.randint(1, 28); quem = random.choice(PESSOAS)
            formulario(qa/f"{m}. {MESES[m-1]}"/f"{d:02d}{'.1' if k%5==4 else ''} - Relato de Quase Acidente - {quem}.pdf", "RELATO DE QUASE ACIDENTE",
                       ["Local: Pátio", "Gravidade: Baixo ( ) Média ( ) Alta ( )", f"Data: {d:02d}/{m:02d}/2026", f"Nome (Opcional): {quem}"])
        for k in range(random.randint(0, 12)):
            d = random.randint(1, 28); quem = random.choice(PESSOAS)
            formulario(ms/f"{m}. {MESES[m-1]}"/f"{d:02d} - Melhoria de Segurança - {quem}.pdf", "MELHORIAS DE SEGURANÇA",
                       ["Local: Portaria", "Impacto: Baixo ( ) Média ( ) Alta ( )", f"Data: {d:02d}/{m:02d}/2026"])
    formulario(qa/"2. Fevereiro"/"Document_261005_151619_5-11.pdf", "RELATO DE QUASE ACIDENTE", ["sem dia no nome: conta pela pasta"])
    formulario(qa/"3. Março"/"Investigação de quase acidentes - MARÇO.pdf", "INVESTIGAÇÃO", ["não é relato"])
    (qa/"0. Controle"/"Evidências").mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (40, 40), "gray").save(qa/"0. Controle"/"Evidências"/"IMG_0001.JPG")
    (qa/"0. Controle"/"Controle de quase acidente.xlsx").write_text("x")
    (qa/"8. Agosto"/"Thumbs.db").write_bytes(b"\0"*64)
    # PDF salvo com extensão .png (aconteceu de verdade)
    tmp = RAIZ/"tmp.pdf"; formulario(tmp, "RELATO DE QUASE ACIDENTE", ["extensão errada"])
    shutil.move(tmp, qa/"8. Agosto"/"11 - Relato de Quase Acidente - Gilson.png")

def problemas():
    d = RAIZ/"problemas"; d.mkdir(parents=True, exist_ok=True)
    for i, quem in enumerate(["Ana Souza","Bruno Lima","Carla Dias","Diego Rocha"], 1):
        formulario(d/f"0{i} - Relato de Quase Acidente - {quem}.pdf", "RELATO DE QUASE ACIDENTE", [f"Nome: {quem}"])
    (d/"07 - Relato de Quase Acidente - Vazio.pdf").write_bytes(b"")
    (d/"08 - Relato de Quase Acidente - Quebrado.pdf").write_bytes(b"%PDF-1.4 lixo")
    w = PdfWriter(); w.add_page(PdfReader(d/"01 - Relato de Quase Acidente - Ana Souza.pdf").pages[0]); w.encrypt("segredo")
    w.write(d/"09 - Relato de Quase Acidente - Senha.pdf")
    Image.new("RGB", (800, 400), (235, 235, 235)).save(d/"11 - Relato de Quase Acidente - Foto.jpg")
    (d/"12 - Relato de Quase Acidente - Falsa.png").write_text("não sou png")
    (d/"Thumbs.db").write_bytes(b"\0"*64); (d/"notas.txt").write_text("x")
    shutil.copy(d/"02 - Relato de Quase Acidente - Bruno Lima.pdf", d/"15 - Relato de Quase Acidente - <img src=x onerror=alert(1)>.pdf")
    shutil.copy(d/"03 - Relato de Quase Acidente - Carla Dias.pdf", d/"25.1 - Relato de Quase Acidente - Elisa Prado.pdf")
    shutil.copy(d/"04 - Relato de Quase Acidente - Diego Rocha.pdf", d/"00 - Relato de Quase Acidente - Dia Zero.pdf")
    shutil.copy(d/"01 - Relato de Quase Acidente - Ana Souza.pdf", d/"Document_261005_151619_5-11.pdf")
    formulario(d/"02 - DDS - Uso de EPI - Ana Souza.pdf", "DDS", ["DDS no meio dos relatos"])

def muitos():
    d = RAIZ/"muitos"
    for i in range(120):
        formulario(d/f"{i%28+1:02d} - PT {300+i}.pdf", f"PERMISSÃO DE TRABALHO - PT Nº {300+i}", ["teste de volume"], paginas=2)
    formulario(d/"30 - PT 999.pdf", "PERMISSÃO DE TRABALHO - PT Nº 999", ["dia 30: inválido em fevereiro"])

if __name__ == "__main__":
    shutil.rmtree(RAIZ, ignore_errors=True)
    rede(); problemas(); muitos()
    print("fixtures criadas em", RAIZ)

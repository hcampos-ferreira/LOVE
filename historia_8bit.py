"""
Nossa história em 8 bits
------------------------
Gera:
  1) historia.gif  -> animação pixel art
  2) index.html    -> página que mostra a animação (para hospedar)
  3) qrcode.png    -> QR code que aponta para a URL onde você hospedar

Uso:
  pip install pillow qrcode
  python historia_8bit.py
"""
import math
import os
import unicodedata
from PIL import Image, ImageDraw

# =====================================================================
#  PERSONALIZE AQUI
# =====================================================================
URL_FINAL = "https://github.com/hcampos-ferreira/LOVE.git"  # onde vai hospedar
NOME_1 = "Thaissa"
NOME_2 = "Hudson"

# Cada cena: (tipo, texto). Use no máximo 2 linhas curtas (~20 letras).
# Tipos: "app", "faculdade", "halloween", "pedido", "fim"
CENAS = [
    ("app",       "Tudo começou em\num aplicativo..."),
    ("faculdade", "Depois, o encontro\nna faculdade"),
    ("halloween", "Festa de Halloween\nna faculdade"),
    ("pedido",    "E então ele pediu\nde joelhos..."),
    ("fim",       "ELA DISSE SIM!\nFASE 1 COMPLETA"),
]

# --- Ela: cabelo preto, óculos roxo, olhos pretos ---
CABELO_ELA = (48, 42, 62)
OCULOS_ELA = (160, 80, 240)
OLHOS = (0, 0, 0)
PELE_ELA = (252, 200, 152)
ROUPA_ELA = (232, 64, 160)
CALCA_ELA = (48, 40, 96)

# --- Ele: cabelo castanho enrolado, um pouco forte ---
CABELO_ELE = (120, 72, 36)
PELE_ELE = (252, 200, 152)
ROUPA_ELE = (56, 96, 232)
CALCA_ELE = (40, 48, 96)
# =====================================================================

W, H = 128, 72          # resolução "real" (pixel art)
ESCALA = 6              # ampliação final: 768x432
FPS_MS = 100            # ms por frame (menor = mais rápido)
FRAMES_POR_CENA = 36    # duração de cada cena

# Paleta geral
CEU = (24, 20, 56)
CEU_DIA = (92, 148, 252)
CHAO = (56, 168, 72)
CHAO_ESC = (32, 112, 48)
BRANCO = (252, 252, 252)
AMARELO = (252, 224, 64)
VERMELHO = (232, 48, 72)
ROSA = (252, 128, 176)
LARANJA = (252, 128, 24)
PRETO = (0, 0, 0)

# ---------------------------------------------------------------------
#  SPRITES  (h=cabelo s=pele c=roupa p=calça g=óculos e=olhos .=vazio)
# ---------------------------------------------------------------------
ELA_BODY = [
    "..hhhh..",
    ".hhhhhh.",
    ".hhsshh.",
    "hggssggh",
    "hgessegh",
    "hssssssh",
    "h.ssss.h",
    "hcccccch",
    "sccccccs",
    ".cccccc.",
]
ELA_LEGS = [[".pp..pp.", ".pp..pp."], [".pp.pp..", ".pp.pp.."]]
ELA_KNEEL = [".pppppp.", "pp....pp"]

ELE_BODY = [
    ".h.hhhh.h.",
    "hhhhhhhhhh",
    "hhsssssshh",
    ".ssessess.",
    ".ssssssss.",
    "..ssssss..",
    ".cccccccc.",
    "cccccccccc",
    "sccccccccs",
    ".cccccccc.",
]
ELE_LEGS = [[".ppp..ppp.", ".ppp..ppp."], [".ppp.ppp..", ".ppp.ppp.."]]
ELE_KNEEL = [".ppppppppp", "ppp.....pp"]

PERSONAGENS = {
    "ela": dict(body=ELA_BODY, legs=ELA_LEGS, kneel=ELA_KNEEL,
                cores={"h": CABELO_ELA, "s": PELE_ELA, "c": ROUPA_ELA,
                       "p": CALCA_ELA, "g": OCULOS_ELA, "e": OLHOS}),
    "ele": dict(body=ELE_BODY, legs=ELE_LEGS, kneel=ELE_KNEEL,
                cores={"h": CABELO_ELE, "s": PELE_ELE, "c": ROUPA_ELE,
                       "p": CALCA_ELE, "e": OLHOS}),
}

# Acessórios do Halloween: (matriz, cores, deslocamento vertical)
ACESSORIOS = {
    "chapeu":  (["....k...", "...kk...", "..kkkk..", "kkkkkkkk"],
                {"k": (110, 40, 170)}, -3),
    "chifres": (["r........r", ".r......r."],
                {"r": VERMELHO}, -2),
}

CORACAO = [
    ".rr.rr.",
    "rrrrrrr",
    "rrrrrrr",
    ".rrrrr.",
    "..rrr..",
    "...r...",
]
FANTASMA = [
    "..www..", ".wwwww.", "wwwwwww", "wkwwwkw",
    "wwwwwww", "wwwwwww", "wwwwwww", "w.w.w.w",
]
ABOBORA = [
    "....g....", ".ooooooo.", "ooooooooo", "oodooodoo",
    "ooooooooo", "oodddddoo", ".ooooooo.",
]
MORCEGO = [
    ["b...b", ".bbb.", "..b.."],
    ["..b..", "bbbbb", "..b.."],
]


# ---------------------------------------------------------------------
#  FONTE PIXEL ART 5x7 (maiúsculas, números e acentos do português)
# ---------------------------------------------------------------------
_G = {
 "A": ".###./#...#/#...#/#####/#...#/#...#/#...#",
 "B": "####./#...#/#...#/####./#...#/#...#/####.",
 "C": ".####/#..../#..../#..../#..../#..../.####",
 "D": "####./#...#/#...#/#...#/#...#/#...#/####.",
 "E": "#####/#..../#..../####./#..../#..../#####",
 "F": "#####/#..../#..../####./#..../#..../#....",
 "G": ".####/#..../#..../#..##/#...#/#...#/.####",
 "H": "#...#/#...#/#...#/#####/#...#/#...#/#...#",
 "I": "#####/..#../..#../..#../..#../..#../#####",
 "J": "..###/...#./...#./...#./...#./#..#./.##..",
 "K": "#...#/#..#./#.#../##.../#.#../#..#./#...#",
 "L": "#..../#..../#..../#..../#..../#..../#####",
 "M": "#...#/##.##/#.#.#/#.#.#/#...#/#...#/#...#",
 "N": "#...#/##..#/#.#.#/#..##/#...#/#...#/#...#",
 "O": ".###./#...#/#...#/#...#/#...#/#...#/.###.",
 "P": "####./#...#/#...#/####./#..../#..../#....",
 "Q": ".###./#...#/#...#/#...#/#.#.#/#..#./.##.#",
 "R": "####./#...#/#...#/####./#.#../#..#./#...#",
 "S": ".####/#..../#..../.###./....#/....#/####.",
 "T": "#####/..#../..#../..#../..#../..#../..#..",
 "U": "#...#/#...#/#...#/#...#/#...#/#...#/.###.",
 "V": "#...#/#...#/#...#/#...#/#...#/.#.#./..#..",
 "W": "#...#/#...#/#...#/#.#.#/#.#.#/##.##/#...#",
 "X": "#...#/#...#/.#.#./..#../.#.#./#...#/#...#",
 "Y": "#...#/#...#/.#.#./..#../..#../..#../..#..",
 "Z": "#####/....#/...#./..#../.#.../#..../#####",
 "0": ".###./#...#/#..##/#.#.#/##..#/#...#/.###.",
 "1": "..#../.##../..#../..#../..#../..#../.###.",
 "2": ".###./#...#/....#/...#./..#../.#.../#####",
 "3": "####./....#/....#/.###./....#/....#/####.",
 "4": "#...#/#...#/#...#/#####/....#/....#/....#",
 "5": "#####/#..../####./....#/....#/#...#/.###.",
 "6": ".###./#..../#..../####./#...#/#...#/.###.",
 "7": "#####/....#/...#./..#../.#.../.#.../.#...",
 "8": ".###./#...#/#...#/.###./#...#/#...#/.###.",
 "9": ".###./#...#/#...#/.####/....#/....#/.###.",
 ".": "...../...../...../...../...../...../..#..",
 ",": "...../...../...../...../..#../..#../.#...",
 "!": "..#../..#../..#../..#../..#../...../..#..",
 "?": ".###./#...#/....#/...#./..#../...../..#..",
 ":": "...../..#../...../...../...../..#../.....",
 "-": "...../...../...../.###./...../...../.....",
 "'": "..#../..#../...../...../...../...../.....",
 " ": "...../...../...../...../...../...../.....",
}
FONTE = {k: [list(r) for r in v.split("/")] for k, v in _G.items()}
# marcas de acento: lista de (coluna, linha) relativas ao topo da letra
MARCAS = {
    "\u0301": [(3, -2), (2, -1)],                  # agudo
    "\u0300": [(1, -2), (2, -1)],                  # grave
    "\u0302": [(1, -1), (2, -2), (3, -1)],         # circunflexo
    "\u0303": [(1, -1), (2, -2), (3, -2), (4, -1)],  # til
    "\u0327": [(2, 7), (1, 8)],                    # cedilha
}


def _normaliza(txt):
    return unicodedata.normalize("NFD", txt.upper())


def larg_texto(txt):
    n = sum(1 for c in _normaliza(txt) if c not in MARCAS)
    return max(n * 6 - 1, 0)


def pixel_texto(d, x, y, txt, cor, sombra=True):
    for dx, dy, c in ((1, 1, PRETO), (0, 0, cor)) if sombra else ((0, 0, cor),):
        cx, ultimo = x, x
        for ch in _normaliza(txt):
            if ch in MARCAS:
                for (mx, my) in MARCAS[ch]:
                    d.point((ultimo + mx + dx, y + my + dy), fill=c)
                continue
            ultimo = cx
            for j, linha in enumerate(FONTE.get(ch, FONTE[" "])):
                for i, v in enumerate(linha):
                    if v == "#":
                        d.point((cx + i + dx, y + j + dy), fill=c)
            cx += 6


# ---------------------------------------------------------------------
#  FUNÇÕES DE DESENHO
# ---------------------------------------------------------------------
def desenha_sprite(d, x, y, matriz, cores, espelhar=False):
    for j, linha in enumerate(matriz):
        if espelhar:
            linha = linha[::-1]
        for i, ch in enumerate(linha):
            if ch in cores:
                d.point((int(x) + i, int(y) + j), fill=cores[ch])


def pessoa(d, x, y, quem, espelhar=False, passo=0, pulo=0,
           acessorio=None, ajoelhado=False):
    per = PERSONAGENS[quem]
    y = y - pulo
    if ajoelhado:
        desenha_sprite(d, x, y + 2, per["body"][:8], per["cores"], espelhar)
        desenha_sprite(d, x, y + 10, per["kneel"], per["cores"], espelhar)
        topo = y + 2
    else:
        desenha_sprite(d, x, y, per["body"], per["cores"], espelhar)
        desenha_sprite(d, x, y + 10, per["legs"][passo % 2],
                       per["cores"], espelhar)
        topo = y
    if acessorio:
        mat, cores, dy = ACESSORIOS[acessorio]
        desenha_sprite(d, x, topo + dy, mat, cores, espelhar)


def coracao(d, x, y, cor=VERMELHO, esc=1):
    for j, linha in enumerate(CORACAO):
        for i, ch in enumerate(linha):
            if ch == "r":
                d.rectangle([x + i * esc, y + j * esc,
                             x + i * esc + esc - 1, y + j * esc + esc - 1],
                            fill=cor)


def fundo(d, noite=False, t=0):
    d.rectangle([0, 0, W, H], fill=CEU if noite else CEU_DIA)
    if noite:
        for k in range(18):
            sx = (k * 37 + 11) % W
            sy = 24 + (k * 17 + 5) % 24
            if (t // 4 + k) % 5 != 0:
                d.point((sx, sy), fill=BRANCO)
        d.ellipse([108, 26, 118, 36], fill=AMARELO)
    else:
        for nx in (20, 80):
            cx = (nx + t // 2) % (W + 20) - 10
            d.rectangle([cx, 30, cx + 12, 34], fill=BRANCO)
            d.rectangle([cx + 3, 27, cx + 9, 30], fill=BRANCO)
    d.rectangle([0, 52, W, H], fill=CHAO)
    for gx in range(0, W, 8):
        d.rectangle([gx, 52, gx + 3, 53], fill=CHAO_ESC)


def fundo_faculdade(d, t):
    fundo(d, False, t)
    d.rectangle([28, 28, 100, 52], fill=(196, 112, 84))      # prédio
    d.rectangle([26, 26, 102, 28], fill=(120, 64, 56))       # telhado
    for i in range(5):                                       # janelas
        wx = 34 + i * 13
        d.rectangle([wx, 31, wx + 6, 36], fill=(252, 232, 120))
        d.rectangle([wx + 3, 31, wx + 3, 36], fill=(196, 112, 84))
    d.rectangle([60, 43, 68, 52], fill=(88, 48, 32))         # porta
    for tx in (6, 114):                                      # árvores
        d.rectangle([tx + 2, 44, tx + 3, 51], fill=(104, 64, 32))
        d.ellipse([tx - 2, 32, tx + 8, 45], fill=(32, 136, 56))


def fundo_halloween(d, t):
    d.rectangle([0, 0, W, H], fill=(40, 16, 64))
    d.ellipse([104, 28, 118, 42], fill=(252, 168, 56))       # lua
    d.rectangle([0, 52, W, H], fill=(64, 40, 96))            # chão
    for gx in range(0, W, 10):
        d.rectangle([gx, 52, gx + 4, 53], fill=(40, 24, 72))
    # guirlanda de bandeirinhas
    d.rectangle([0, 24, W, 24], fill=(200, 190, 220))
    for k, gx in enumerate(range(2, W, 10)):
        cor = LARANJA if k % 2 == 0 else (150, 80, 220)
        d.polygon([(gx, 25), (gx + 6, 25), (gx + 3, 31)], fill=cor)
    # morcegos
    for k in range(3):
        bx = (t * 3 + k * 45) % (W + 10) - 5
        by = 36 + int(math.sin((t + k * 7) / 3) * 5)
        desenha_sprite(d, bx, by, MORCEGO[(t // 3 + k) % 2],
                       {"b": (170, 140, 220)})
    # abóboras
    for ax in (8, 111):
        desenha_sprite(d, ax, 45, ABOBORA,
                       {"o": LARANJA, "d": (60, 24, 0), "g": (60, 160, 60)})
        if t % 10 < 7:   # "brilho" da vela
            d.point((ax + 2, 48), fill=AMARELO)
            d.point((ax + 6, 48), fill=AMARELO)
    # fantasminha flutuando
    gx = 92 + int(math.sin(t / 6) * 6)
    gy = 34 + int(math.sin(t / 4) * 3)
    desenha_sprite(d, gx, gy, FANTASMA, {"w": BRANCO, "k": PRETO})


def celular(d, x, y, quem, curtiu):
    d.rectangle([x, y, x + 25, y + 39], fill=(16, 16, 24))
    d.rectangle([x + 2, y + 3, x + 23, y + 36], fill=(240, 236, 252))
    d.rectangle([x + 9, y + 1, x + 16, y + 1], fill=(80, 80, 96))
    if quem == "ela":
        d.rectangle([x + 7, y + 6, x + 18, y + 17], fill=CABELO_ELA)
        d.rectangle([x + 9, y + 8, x + 16, y + 16], fill=PELE_ELA)
        d.rectangle([x + 9, y + 11, x + 16, y + 11], fill=OCULOS_ELA)
        d.point((x + 11, y + 11), fill=OLHOS)
        d.point((x + 14, y + 11), fill=OLHOS)
    else:
        d.rectangle([x + 6, y + 5, x + 19, y + 10], fill=CABELO_ELE)
        d.rectangle([x + 9, y + 9, x + 16, y + 17], fill=PELE_ELE)
        d.point((x + 11, y + 12), fill=OLHOS)
        d.point((x + 14, y + 12), fill=OLHOS)
    d.rectangle([x + 6, y + 20, x + 19, y + 21], fill=(170, 160, 190))
    d.rectangle([x + 6, y + 24, x + 14, y + 24], fill=(200, 190, 215))
    d.rectangle([x + 5, y + 29, x + 10, y + 34], fill=(200, 190, 215))
    coracao(d, x + 14, y + 29, VERMELHO if curtiu else (200, 190, 215))


def cena_app(d, t):
    d.rectangle([0, 0, W, H], fill=(36, 24, 72))
    for k in range(12):   # coraçõezinhos de fundo
        hx = (k * 29 + 9) % W
        hy = 26 + (k * 13 + t // 2) % 44
        d.point((hx, hy), fill=(120, 80, 160))
    celular(d, 18, 28, "ela", t >= 8)
    celular(d, 85, 28, "ele", t >= 14)
    if 20 <= t < 26:
        q = (t - 20) / 5
        coracao(d, int(44 + q * 13), 40, VERMELHO)
        coracao(d, int(78 - q * 14), 40, VERMELHO)
    elif t >= 26:
        coracao(d, 57, 34, VERMELHO if (t // 3) % 2 == 0 else ROSA, esc=2)
        cor = AMARELO if (t // 3) % 2 == 0 else BRANCO
        pixel_texto(d, 64 - larg_texto("MATCH!") // 2, 53, "MATCH!", cor)


def texto(d, msg, y=3):
    d.rectangle([0, 0, W, 21], fill=(16, 12, 40))
    d.rectangle([0, 22, W, 22], fill=BRANCO)
    for i, linha in enumerate(msg.split("\n")):
        x = (W - larg_texto(linha)) // 2
        pixel_texto(d, x, y + i * 10, linha, BRANCO)


# ---------------------------------------------------------------------
#  CENAS
# ---------------------------------------------------------------------
def cena_frame(tipo, msg, t):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    p = t / (FRAMES_POR_CENA - 1)
    y = 40
    passo = t // 4

    if tipo == "app":
        cena_app(d, t)

    elif tipo == "faculdade":
        fundo_faculdade(d, t)
        a = min(p * 1.6, 1)
        andando = a < 1
        pessoa(d, -10 + a * 62, y, "ela", False, passo if andando else 0)
        pessoa(d, 130 - a * 62, y, "ele", True, passo if andando else 0)
        if not andando:
            coracao(d, 60, 32 - int(abs(math.sin(t / 3)) * 4))

    elif tipo == "halloween":
        fundo_halloween(d, t)
        pessoa(d, 46, y, "ela", False, 0,
               pulo=2 if (t // 4) % 2 == 0 else 0, acessorio="chapeu")
        pessoa(d, 70, y, "ele", True, 0,
               pulo=0 if (t // 4) % 2 == 0 else 2, acessorio="chifres")

    elif tipo == "pedido":
        fundo(d, True, t)
        ex = 50
        pessoa(d, ex, y, "ele", False, ajoelhado=True)
        # braço estendido com a caixinha do anel
        d.rectangle([ex + 10, y + 7, ex + 13, y + 8], fill=PELE_ELE)
        d.rectangle([ex + 13, y + 5, ex + 16, y + 7], fill=VERMELHO)
        d.rectangle([ex + 14, y + 4, ex + 15, y + 4], fill=AMARELO)
        if t % 6 < 3:
            d.point((ex + 17, y + 3), fill=BRANCO)
        pulo = 2 if (t > 20 and (t // 3) % 2 == 0) else 0
        pessoa(d, 70, y, "ela", True, 0, pulo=pulo)
        if t > 18 and (t // 3) % 2 == 0:
            coracao(d, 71, 28)

    elif tipo == "fim":
        fundo(d, True, t)
        cores = [VERMELHO, AMARELO, ROSA, (96, 200, 255), (120, 255, 140)]
        for k in range(30):   # confete
            cx = (k * 37) % W
            cy = 24 + (k * 7 + t * 2) % 28
            d.rectangle([cx, cy, cx + 1, cy + 1], fill=cores[k % 5])
        pulo = 3 if (t // 3) % 2 == 0 else 0
        pessoa(d, 46, y, "ela", False, 0, pulo=pulo)
        pessoa(d, 70, y, "ele", True, 0, pulo=pulo)
        for k in range(5):
            hx = 14 + k * 24
            hy = 30 + int(math.sin((t + k * 5) / 4) * 5)
            coracao(d, hx, hy)

    texto(d, msg)
    return img.resize((W * ESCALA, H * ESCALA), Image.NEAREST)


def gerar_gif(caminho):
    frames = []
    for tipo, msg in CENAS:
        for t in range(FRAMES_POR_CENA):
            frames.append(cena_frame(tipo, msg, t))
    frames[0].save(caminho, save_all=True, append_images=frames[1:],
                   duration=FPS_MS, loop=0, optimize=False)


def gerar_html(caminho):
    html = f"""<!doctype html>
<html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nossa história</title>
<style>
  body {{ margin:0; background:#181438; display:flex; min-height:100vh;
         align-items:center; justify-content:center; flex-direction:column;
         font-family:monospace; color:#fce040; }}
  img {{ width:min(96vw,768px); image-rendering:pixelated; }}
</style></head>
<body>
  <img src="historia.gif" alt="Nossa história em 8 bits">
  <p>♥ {NOME_1} &amp; {NOME_2} ♥</p>
</body></html>"""
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)


def gerar_qr(caminho, url):
    try:
        import qrcode
    except ImportError:
        print("Instale o qrcode para gerar o QR:  pip install qrcode")
        return
    qr = qrcode.QRCode(border=2, box_size=12)
    qr.add_data(url)
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(caminho)


if __name__ == "__main__":
    os.makedirs("saida", exist_ok=True)
    gerar_gif("saida/historia.gif")
    gerar_html("saida/index.html")
    gerar_qr("saida/qrcode.png", URL_FINAL)
    print("Pronto! Arquivos na pasta 'saida'.")

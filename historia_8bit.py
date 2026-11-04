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
URL_FINAL = "https://SEU-USUARIO.github.io/nossa-historia/"  # onde vai hospedar
NOME_1 = "Ela"
NOME_2 = "Ele"

# Cada cena: (tipo, texto). Use no máximo 2 linhas curtas (~20 letras).
# Tipos: "app", "faculdade", "halloween", "pedido", "fim",
#        "biblioteca", "restaurante", "italiano", "carro"
CENAS = [
    ("app",       "Tudo começou em\num aplicativo..."),
    ("faculdade", "Depois, o encontro\nna faculdade"),
    ("halloween", "Festa de Halloween\nna faculdade"),
    ("pedido",    "E então ele pediu\ne ela..."),
    ("fim",       "ELA DISSE SIM!\n"),
    ("biblioteca",  "FASE 1:\nbiblioteca Real"),
    ("restaurante", "FASE 2: Almoço\nsó nós dois"),
    ("italiano",    "FASE 3: italiana:\nmassa, vinho e amor"),
    ("carro",       "FASE 4:\n Continue..."),
]

# Texto da faixa do carro (2 linhas). Use ♥ para o coração.
FAIXA_L1 = "Feliz 4 anos,"
FAIXA_L2 = "Lhe amo ♥"

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
 "♥": ".#.#./#####/#####/.###./..#../...../.....",
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
            cor_ch = VERMELHO if (ch == "♥" and c != PRETO) else c
            for j, linha in enumerate(FONTE.get(ch, FONTE[" "])):
                for i, v in enumerate(linha):
                    if v == "#":
                        d.point((cx + i + dx, y + j + dy), fill=cor_ch)
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


def fundo_biblioteca(d, t):
    d.rectangle([0, 23, W, 51], fill=(58, 34, 24))
    cores = [(176, 48, 48), (48, 96, 176), (64, 144, 80),
             (216, 176, 56), (136, 72, 160), (200, 120, 56)]
    for r in range(5):                                   # estantes
        y0 = 24 + r * 6
        for x in range(0, W, 3):
            h = 3 + (x * 7 + r * 5) % 3
            d.rectangle([x, y0 + 5 - h, x + 1, y0 + 4],
                        fill=cores[(x // 3 + r * 2) % 6])
        d.rectangle([0, y0 + 5, W, y0 + 5], fill=(110, 66, 36))
    for cx in (0, 124):                                  # colunas
        d.rectangle([cx, 23, cx + 3, 51], fill=(84, 50, 28))
        d.rectangle([cx + 1, 23, cx + 1, 51], fill=(120, 76, 40))
    d.line([(100, 51), (104, 26)], fill=(170, 110, 60))  # escada
    d.line([(106, 51), (110, 26)], fill=(170, 110, 60))
    for yy in range(48, 26, -5):
        f = (51 - yy) / 25
        d.line([(100 + int(4 * f), yy), (106 + int(4 * f), yy)],
               fill=(170, 110, 60))
    d.rectangle([0, 52, W, H], fill=(126, 80, 44))       # chão
    for yy in (57, 63, 69):
        d.rectangle([0, yy, W, yy], fill=(100, 62, 34))
    d.rectangle([34, 52, 93, H], fill=(150, 30, 44))     # tapete
    d.rectangle([34, 52, 35, H], fill=(230, 190, 70))
    d.rectangle([92, 52, 93, H], fill=(230, 190, 70))


def lustre(d, t):
    ouro, ouro_esc = (232, 184, 56), (168, 120, 32)
    d.rectangle([64, 23, 64, 28], fill=ouro_esc)         # corrente
    d.rectangle([60, 29, 68, 30], fill=ouro)
    d.rectangle([56, 31, 72, 31], fill=ouro)
    d.line([(64, 31), (44, 33)], fill=ouro)
    d.line([(64, 31), (84, 33)], fill=ouro)
    d.rectangle([44, 33, 84, 33], fill=ouro)
    for bx in (44, 52, 60, 68, 76, 84):                  # velas
        d.rectangle([bx, 30, bx, 32], fill=(252, 244, 220))
        d.point((bx, 29), fill=AMARELO)
        if (t + bx) % 6 < 3:
            d.point((bx, 28), fill=(252, 170, 40))
    for bx in (46, 50, 78, 82):                          # cristais
        d.rectangle([bx, 34, bx, 35], fill=(200, 230, 252))


def fundo_restaurante(d, t):
    d.rectangle([0, 23, W, 51], fill=(26, 14, 30))
    glow = (48, 26, 38) if (t // 3) % 2 == 0 else (54, 30, 42)
    d.ellipse([44, 28, 86, 54], fill=glow)
    moldura = (80, 50, 40)                               # janela
    d.rectangle([52, 26, 76, 38], fill=moldura)
    d.rectangle([54, 28, 74, 36], fill=(18, 22, 58))
    d.rectangle([64, 28, 64, 36], fill=moldura)
    d.rectangle([54, 32, 74, 32], fill=moldura)
    for sx, sy in ((57, 30), (70, 29), (60, 35), (72, 34)):
        d.point((sx, sy), fill=BRANCO)
    for lx in (20, 108):                                 # luminárias
        d.ellipse([lx - 9, 30, lx + 9, 46], fill=(40, 24, 36))
        d.rectangle([lx, 23, lx, 28], fill=(90, 80, 70))
        d.polygon([(lx - 5, 33), (lx + 5, 33), (lx + 2, 28), (lx - 2, 28)],
                  fill=(196, 112, 40))
        d.rectangle([lx - 1, 34, lx + 1, 34], fill=(252, 200, 100))
    for mx in (10, 118):                                 # mesas ao fundo
        d.rectangle([mx - 6, 46, mx + 6, 47], fill=(70, 40, 44))
        d.rectangle([mx - 5, 48, mx + 5, 52], fill=(52, 28, 34))
        d.point((mx, 44), fill=(252, 180, 60) if (t // 3) % 2 else (252, 130, 40))
        d.point((mx, 45), fill=(240, 230, 200))
    d.rectangle([0, 52, W, H], fill=(44, 24, 24))
    for yy in (58, 64, 70):
        d.rectangle([0, yy, W, yy], fill=(34, 18, 20))


def fundo_italiano(d, t):
    mort = (110, 44, 36)
    d.rectangle([0, 23, W, 51], fill=(150, 64, 48))      # tijolos
    for i, yy in enumerate(range(24, 52, 4)):
        d.rectangle([0, yy, W, yy], fill=mort)
        for xx in range(0 if i % 2 == 0 else 5, W, 10):
            d.rectangle([xx, yy + 1, xx, yy + 3], fill=mort)
    d.rectangle([0, 24, W, 24], fill=(220, 210, 190))    # bandeirinhas
    tri = [(0, 146, 70), BRANCO, (206, 43, 55)]
    for k, gx in enumerate(range(2, W, 8)):
        d.polygon([(gx, 25), (gx + 6, 25), (gx + 3, 31)], fill=tri[k % 3])
    for sx, nome in ((2, "PIZZA"), (96, "PASTA")):        # placas
        d.rectangle([sx, 33, sx + 30, 43], fill=(40, 96, 56))
        d.rectangle([sx, 33, sx + 30, 43], outline=(240, 230, 200))
        pixel_texto(d, sx + (31 - larg_texto(nome)) // 2, 35, nome,
                    BRANCO, sombra=False)
    d.rectangle([0, 52, W, H], fill=(184, 100, 64))      # ladrilhos
    for yy in range(52, H, 6):
        for xx in range(((yy // 6) % 2) * 6, W, 12):
            d.rectangle([xx, yy, xx + 5, yy + 5], fill=(160, 84, 52))


def mesa_casal(d, t, italiano=False):
    cadeira = (120, 70, 36) if italiano else (74, 44, 32)
    d.rectangle([35, 36, 37, 48], fill=cadeira)
    d.rectangle([92, 36, 94, 48], fill=cadeira)
    # sentados: as pernas ficam escondidas atrás da mesa
    pessoa(d, 40, 35, "ela", False, 0, pulo=1 if (t // 5) % 3 == 0 else 0)
    pessoa(d, 80, 35, "ele", True, 0, pulo=1 if (t // 5) % 3 == 1 else 0)
    if italiano:
        d.rectangle([39, 45, 91, 46], fill=BRANCO)
        for cy in (47, 50):
            for cx in range(40, 91, 3):
                xadrez = ((cx - 40) // 3 + (cy - 47) // 3) % 2 == 0
                d.rectangle([cx, cy, min(cx + 2, 90), cy + 2],
                            fill=(206, 43, 55) if xadrez else BRANCO)
        d.ellipse([56, 42, 69, 46], fill=BRANCO)                 # prato
        d.rectangle([59, 41, 66, 43], fill=(252, 200, 80))       # macarrão
        for px, py in ((61, 42), (64, 41), (65, 43)):
            d.point((px, py), fill=(206, 43, 55))
        for k in range(3):                                       # vapor
            d.point((60 + k * 3, 39 - ((t // 2 + k * 3) % 6)),
                    fill=(220, 220, 235))
        d.rectangle([72, 38, 74, 44], fill=(30, 90, 50))         # garrafa
        d.rectangle([73, 35, 73, 37], fill=(30, 90, 50))
        d.point((73, 34), fill=(206, 43, 55))
        hy = 35
    else:
        d.rectangle([39, 45, 91, 46], fill=(190, 150, 150))
        d.rectangle([40, 47, 90, 52], fill=(110, 24, 36))
        d.rectangle([63, 41, 64, 44], fill=(250, 240, 210))      # vela
        d.rectangle([63, 39, 64, 40],
                    fill=AMARELO if (t // 2) % 2 == 0 else (252, 170, 40))
        if (t // 2) % 2 == 0:
            d.point((63, 38), fill=(252, 170, 40))
        hy = 33
    for gx in (51, 77):                                          # taças
        d.rectangle([gx, 40, gx + 2, 42], fill=(200, 230, 252))
        d.rectangle([gx, 41, gx + 2, 42], fill=(150, 30, 60))
        d.rectangle([gx + 1, 43, gx + 1, 44], fill=(200, 230, 252))
        d.rectangle([gx, 44, gx + 2, 44], fill=(200, 230, 252))
    if t >= 22:
        coracao(d, 61, hy - int(abs(math.sin(t / 3)) * 3))


def cena_carro(img, d, t):
    fundo(d, False, t)
    d.rectangle([0, 46, W, 52], fill=(40, 150, 64))              # colinas
    for k in range(4):                                           # árvores
        tx = (k * 40 - t * 3) % (W + 40) - 20
        d.rectangle([tx + 2, 40, tx + 3, 47], fill=(104, 64, 32))
        d.ellipse([tx - 2, 30, tx + 8, 41], fill=(32, 136, 56))
    d.rectangle([0, 52, W, H], fill=(72, 72, 88))                # estrada
    d.rectangle([0, 52, W, 53], fill=(200, 200, 210))
    for k in range(0, W + 16, 16):
        x = (k - t * 4) % (W + 16) - 16
        d.rectangle([x, 65, x + 7, 66], fill=(240, 230, 120))
    # faixa (desenhada à parte e colada coluna a coluna para "ondular")
    bw, bh = 82, 22
    ban = Image.new("RGB", (bw, bh), (255, 240, 245))
    bd = ImageDraw.Draw(ban)
    bd.rectangle([0, 0, bw - 1, bh - 1], outline=(206, 43, 55))
    azul = (30, 30, 120)
    pixel_texto(bd, (bw - larg_texto(FAIXA_L1)) // 2, 3, FAIXA_L1, azul, sombra=False)
    pixel_texto(bd, (bw - larg_texto(FAIXA_L2)) // 2, 12, FAIXA_L2, azul, sombra=False)
    for i in range(bw):
        amp = 0.2 + 0.9 * (1 - i / bw)
        off = int(round(math.sin(i / 6 + t / 2) * amp))
        img.paste(ban.crop((i, 0, i + 1, bh)), (3 + i, 27 + off))
    # carro branco
    bob = int(round(math.sin(t / 2) * 0.7))
    x0, y0 = 88, 43 + bob
    d.line([(84, 36), (89, y0 + 7)], fill=(60, 40, 30))          # cordas
    d.line([(84, 46), (89, y0 + 8)], fill=(60, 40, 30))
    d.rectangle([x0, y0 + 7, x0 + 39, y0 + 12], fill=BRANCO)
    d.rectangle([x0, y0 + 11, x0 + 39, y0 + 12], fill=(204, 204, 216))
    d.polygon([(x0 + 6, y0 + 7), (x0 + 10, y0 + 1),
               (x0 + 29, y0 + 1), (x0 + 34, y0 + 7)], fill=BRANCO)
    d.rectangle([x0 + 10, y0 + 2, x0 + 29, y0 + 6], fill=(150, 205, 245))
    desenha_sprite(d, x0 + 11, y0 + 2, ELA_BODY[:5], PERSONAGENS["ela"]["cores"])
    desenha_sprite(d, x0 + 19, y0 + 2, ELE_BODY[:5], PERSONAGENS["ele"]["cores"])
    d.rectangle([x0 + 20, y0 + 7, x0 + 20, y0 + 11], fill=(204, 204, 216))
    d.rectangle([x0 + 38, y0 + 8, x0 + 39, y0 + 9], fill=AMARELO)
    d.rectangle([x0, y0 + 8, x0 + 1, y0 + 9], fill=VERMELHO)
    for cx in (x0 + 8, x0 + 31):                                 # rodas
        d.ellipse([cx - 3, y0 + 9, cx + 3, y0 + 15], fill=(24, 24, 32))
        d.ellipse([cx - 1, y0 + 11, cx + 1, y0 + 13], fill=(180, 180, 190))
        gira = [(0, -2), (2, 0), (0, 2), (-2, 0)][t % 4]
        d.point((cx + gira[0], y0 + 12 + gira[1]), fill=(120, 120, 130))
    for k in range(3):                                           # corações
        coracao(d, 92 + k * 12, 36 - ((t + k * 5) % 13))


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

    elif tipo == "biblioteca":
        fundo_biblioteca(d, t)
        a = min(p * 1.6, 1)
        andando = a < 1
        pessoa(d, -10 + a * 60, y, "ela", False, passo if andando else 0)
        pessoa(d, 130 - a * 60, y, "ele", True, passo if andando else 0)
        lustre(d, t)
        if not andando:
            coracao(d, 60, 34 - int(abs(math.sin(t / 3)) * 3))

    elif tipo == "restaurante":
        fundo_restaurante(d, t)
        mesa_casal(d, t, italiano=False)

    elif tipo == "italiano":
        fundo_italiano(d, t)
        mesa_casal(d, t, italiano=True)

    elif tipo == "carro":
        cena_carro(img, d, t)

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

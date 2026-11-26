"""Gera o relatório da Sprint 2 (PDF) a partir das planilhas originais.

Uso (na raiz do repositório):
    python resultados/gerar_relatorio.py

Antes de entregar, preencha os campos da CAPA abaixo. Todos os números do texto
são recalculados a partir de dados/*.xlsx; as figuras são as geradas pelos
notebooks em resultados/figuras/ (execute os notebooks antes deste script).
"""
from pathlib import Path
import io

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image as PILImage

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

# ============================================================== CAPA (preencher)
CAPA = {
    "instituicao": "PONTIFÍCIA UNIVERSIDADE CATÓLICA DE CAMPINAS",
    "escola": "",          # ex.: "Escola Politécnica"  -> vazio aparece em vermelho
    "curso": "",           # ex.: "Engenharia de ..."   -> vazio aparece em vermelho
    "componente": "Estatística e Análise de Dados",
    "integrantes": [
        ("Giovanna Lima Salvagnini", "25015692"),
        ("Guilherme Oliveira Nogueira", "25006542"),
        ("Henrique Spadaccia Chambó", "25008942"),
    ],
    "cidade": "Campinas",
    "mes_ano": "Novembro de 2026",
}

RAIZ = Path(__file__).resolve().parents[1]
FIG = RAIZ / "resultados" / "figuras"
SAIDA = RAIZ / "resultados" / "relatorio-sprint-2.pdf"
COLUNA = "Tempo de carregamento (min)"

# ============================================================== cálculos
antes = pd.read_excel(RAIZ / "dados" / "planilha-1-antes-intervencao.xlsx")[COLUNA].dropna()
depois = pd.read_excel(RAIZ / "dados" / "planilha-2-depois-intervencao.xlsx")[COLUNA].dropna()
assert len(antes) == 300 and len(depois) == 100

A, B = 20, 30
N1, n = len(antes), len(depois)
mu0 = antes.mean()
sigma = antes.std(ddof=1)
med1 = antes.median()
xbar = depois.mean()
s2 = depois.std(ddof=1)
med2 = depois.median()

za, zb = (A - mu0) / sigma, (B - mu0) / sigma
p0 = stats.norm.cdf(zb) - stats.norm.cdf(za)
k1 = int(antes.between(A, B).sum())
p_obs1 = k1 / N1
k2 = int(depois.between(A, B).sum())
phat = k2 / n

ep_m = sigma / np.sqrt(n)
z_m = (xbar - mu0) / ep_m
pv_m = stats.norm.cdf(z_m)

ep_p = np.sqrt(p0 * (1 - p0) / n)
z_p = (phat - p0) / ep_p
pv_p = 1 - stats.norm.cdf(z_p)

ALFAS = (0.05, 0.01)
zc_m = {a: stats.norm.ppf(a) for a in ALFAS}
zc_p = {a: stats.norm.ppf(1 - a) for a in ALFAS}
assert all(z_m <= zc_m[a] for a in ALFAS) and all(z_p >= zc_p[a] for a in ALFAS), \
    "As decisões mudaram: revise o texto do relatório."

p0_43 = stats.norm.cdf(43, mu0, sigma) - stats.norm.cdf(20, mu0, sigma)
z_m_ddof0 = (xbar - mu0) / (antes.std(ddof=0) / np.sqrt(n))
z_p_obs = (phat - p_obs1) / np.sqrt(p_obs1 * (1 - p_obs1) / n)


def br(x, casas=4):
    return f"{x:.{casas}f}".replace(".", ",").replace("-", "−")


def pct(x, casas=2):
    return br(100 * x, casas) + "%"


# ============================================================== fontes e estilos
MPL_FONTS = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
pdfmetrics.registerFont(TTFont("DejaVu", str(MPL_FONTS / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-B", str(MPL_FONTS / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-I", str(MPL_FONTS / "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-BI", str(MPL_FONTS / "DejaVuSans-BoldOblique.ttf")))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-B", italic="DejaVu-I", boldItalic="DejaVu-BI")

TINTA = colors.HexColor("#191919")
TINTA2 = colors.HexColor("#666666")
AZUL = colors.HexColor("#1b64be")
LINHA = colors.HexColor("#d0d0d0")
FUNDO = colors.HexColor("#f3f6fa")
ALERTA = colors.HexColor("#dc3c3d")

corpo = ParagraphStyle("corpo", fontName="DejaVu", fontSize=10, leading=14.5, alignment=TA_JUSTIFY,
                       textColor=TINTA, spaceAfter=6)
item = ParagraphStyle("item", parent=corpo, leftIndent=14, bulletIndent=4, spaceAfter=3)
h1 = ParagraphStyle("h1", fontName="DejaVu-B", fontSize=13.5, leading=18, textColor=AZUL,
                    spaceBefore=12, spaceAfter=6, keepWithNext=1)
h2 = ParagraphStyle("h2", fontName="DejaVu-B", fontSize=11, leading=15, textColor=TINTA,
                    spaceBefore=9, spaceAfter=4, keepWithNext=1)
legenda = ParagraphStyle("legenda", parent=corpo, fontSize=8.5, leading=11.5, textColor=TINTA2,
                         alignment=TA_CENTER, spaceBefore=2, spaceAfter=10)
celula = ParagraphStyle("celula", fontName="DejaVu", fontSize=8.8, leading=11.5, textColor=TINTA)
celula_b = ParagraphStyle("celula_b", parent=celula, fontName="DejaVu-B")
capa_c = ParagraphStyle("capa_c", fontName="DejaVu", fontSize=12, leading=17, alignment=TA_CENTER,
                        textColor=TINTA)
capa_t = ParagraphStyle("capa_t", parent=capa_c, fontName="DejaVu-B", fontSize=17, leading=23)
destaque = ParagraphStyle("destaque", parent=corpo, backColor=FUNDO, borderPadding=(6, 8, 6, 8),
                          borderColor=LINHA, borderWidth=0.5, spaceBefore=6, spaceAfter=10)

LARG = A4[0] - 4.4 * cm  # largura útil


def P(txt, st=corpo):
    return Paragraph(txt, st)


def bullets(itens):
    return [Paragraph(t, item, bulletText="•") for t in itens]


def equacao(tex, tamanho=13):
    """Renderiza uma equação (mathtext) como imagem para o PDF."""
    fig = plt.figure()
    fig.text(0, 0, f"${tex}$", fontsize=tamanho, color="#191919")
    buf = io.BytesIO()
    plt.rcParams["mathtext.fontset"] = "dejavusans"
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight", pad_inches=0.04, transparent=True)
    plt.close(fig)
    buf.seek(0)
    w, h = PILImage.open(buf).size
    buf.seek(0)
    img = Image(buf, width=w / 300 * 72, height=h / 300 * 72)
    img.hAlign = "CENTER"
    return img


def figura(arquivo, texto):
    caminho = FIG / arquivo
    if not caminho.exists():
        raise FileNotFoundError(f"{caminho} não existe: execute os notebooks da Sprint 2 antes.")
    w, h = PILImage.open(caminho).size
    larg = LARG * 0.92
    img = Image(str(caminho), width=larg, height=larg * h / w)
    img.keepWithNext = 1  # título, figura e legenda ficam na mesma página
    return [img, P(texto, legenda)]


def tabela(linhas, larguras, cabecalho=True):
    dados = [[c if not isinstance(c, str) else Paragraph(c, celula_b if (cabecalho and i == 0) else celula)
              for c in linha] for i, linha in enumerate(linhas)]
    t = Table(dados, colWidths=larguras, hAlign="CENTER")
    estilo = [
        ("GRID", (0, 0), (-1, -1), 0.5, LINHA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    if cabecalho:
        estilo.append(("BACKGROUND", (0, 0), (-1, 0), FUNDO))
    t.setStyle(TableStyle(estilo))
    t.keepWithNext = 1  # a legenda acompanha a tabela
    return t


# atalhos tipográficos (sem caracteres combinantes)
XB = "x&#772;"          # x com barra
PH = "p&#770;"          # p chapéu
H0 = "H<sub>0</sub>"
H1 = "H<sub>1</sub>"
MU0 = "μ<sub>0</sub>"
P0 = "p<sub>0</sub>"
ZC = "z<sub>calc</sub>"

# ============================================================== conteúdo
s = []

# ---------- capa
def campo(valor, rotulo):
    if valor:
        return P(valor, capa_c)
    return P(f'<font color="#dc3c3d">[{rotulo} — preencher em resultados/gerar_relatorio.py]</font>', capa_c)

s += [Spacer(1, 1.2 * cm), P(f"<b>{CAPA['instituicao']}</b>", capa_c),
      campo(CAPA["escola"], "ESCOLA"), campo(CAPA["curso"], "FACULDADE / CURSO"),
      Spacer(1, 0.3 * cm), P(f"Componente curricular: {CAPA['componente']}", capa_c),
      Spacer(1, 3.2 * cm),
      P("PROJETO 2 — SPRINT 2", capa_t),
      P("Testes de hipótese para a média e para a proporção do tempo de carregamento "
        "de caminhões com grãos", ParagraphStyle("sub", parent=capa_c, fontSize=13, leading=18)),
      Spacer(1, 3.2 * cm), P("<b>Integrantes</b>", capa_c)]
s += [P(f"{nome} — RA {ra}", capa_c) for nome, ra in CAPA["integrantes"]]
s += [Spacer(1, 3.2 * cm), P(CAPA["cidade"], capa_c), P(CAPA["mes_ano"], capa_c), PageBreak()]

# ---------- introdução
s.append(P("Introdução: pergunta de investigação", h1))
s.append(P(
    "Na Sprint 1, a comparação entre os dados anteriores e posteriores à intervenção foi orientada pela "
    "pergunta: <i>“com base nos dados coletados antes e depois da intervenção, há indícios de que a "
    "padronização da preparação do carregamento contribuiu para reduzir o tempo de carregamento dos "
    "caminhões com grãos?”</i> A pergunta tem a direção correta (redução do tempo), mas não serve "
    "diretamente para um teste de hipótese: não indica qual parâmetro é comparado, não fixa um valor de "
    "referência e usa o termo “contribuiu”, de natureza causal, que um teste com dados antes/depois não "
    "consegue sustentar sozinho."))
s.append(P(
    "A pergunta foi reformulada, mantendo o objetivo da Sprint 1 (reduzir o tempo de carregamento e "
    "aumentar a proporção de carregamentos concluídos em até 30 minutos), em duas perguntas testáveis, "
    "que comparam um valor da amostra após a intervenção com o valor da população original (Planilha 1):"))
s += bullets([
    f"<b>Média:</b> o tempo médio de carregamento após a padronização é <b>menor</b> que "
    f"{br(mu0)} min, média da Planilha 1?",
    f"<b>Proporção:</b> a proporção de carregamentos concluídos entre {A} e {B} minutos após a padronização "
    f"é <b>maior</b> que {pct(p0)}, probabilidade dessa faixa estimada com o modelo normal da Planilha 1?",
])
s.append(P(
    f"<b>Ajuste do intervalo [a, b].</b> Na Sprint 1, o cálculo de probabilidade (Questão 5) usou o intervalo "
    f"[20, 43] min, enquanto a contagem após a intervenção (Questão 7.4) usou [20, 30] min. Um teste de "
    f"proporção precisa comparar o mesmo evento nos dois momentos. Por isso, conforme a orientação da "
    f"Sprint 2 de verificar a necessidade de correção, a probabilidade da Questão 5 foi recalculada para "
    f"[20, 30] min, faixa ligada ao objetivo da intervenção. O Apêndice mostra que o intervalo [20, 43] "
    f"não seria adequado.", destaque))

# ---------- 1. contexto
s.append(P("1. Situação, intervenção e análise preliminar", h1))
s.append(P(
    "<b>Situação e problema.</b> O carregamento de caminhões com grãos é uma etapa crítica do transporte: "
    "quando demora, os caminhões ficam parados, a fila cresce e as etapas seguintes atrasam. Antes da "
    f"intervenção, o tempo médio de carregamento era de {br(mu0, 2)} min, acima da meta de 30 min "
    "definida pelo grupo. As planilhas registram apenas os tempos, sem identificar a causa de cada demora."))
s.append(P(
    "<b>Objetivo.</b> Reduzir o tempo de carregamento e aumentar a proporção de carregamentos concluídos "
    "entre 20 e 30 minutos."))
s.append(P(
    "<b>Intervenção.</b> A ação proposta e registrada na Sprint 1 (Questão 7.1) é a padronização da preparação do carregamento antes da chegada ou do posicionamento "
    "do caminhão, com checklist de disponibilidade dos grãos, dos equipamentos e da equipe, e organização "
    "prévia da sequência de atendimento."))
s.append(P(
    f"<b>Dados.</b> Variável: tempo de carregamento, em minutos (coluna “{COLUNA}”). A Planilha 1 tem "
    f"{N1} observações anteriores à intervenção e é tratada como a <b>população</b> de referência. A Planilha 2 "
    f"tem {n} observações posteriores e é a <b>amostra</b>. Não há valores ausentes em nenhuma das planilhas, "
    f"e nenhum dado foi alterado."))

t1 = [
    ["Parâmetro", "Planilha 1 — antes (população)", "Planilha 2 — depois (amostra)"],
    ["Número de observações", f"N = {N1}", f"n = {n}"],
    ["Média do tempo", f"μ = {br(mu0)} min", f"{XB} = {br(xbar)} min"],
    ["Desvio-padrão", f"σ = {br(sigma)} min", f"s = {br(s2)} min"],
    ["Mediana", f"{br(med1, 2)} min", f"{br(med2, 2)} min"],
    [f"Proporção em [{A}, {B}] min",
     f"p = {br(p0)} ({pct(p0)}) — modelo normal<br/>"
     f"<font color='#666666'>observado: {k1}/{N1} = {pct(p_obs1)}</font>",
     f"{PH} = {k2}/{n} = {br(phat, 2)} ({pct(phat)})"],
]
s.append(tabela(t1, [4.2 * cm, 6.1 * cm, 6.1 * cm]))
s.append(P("Tabela 1. Parâmetros da população (Planilha 1) e da amostra (Planilha 2). Valores calculados "
           "nos notebooks da Sprint 2 com as planilhas originais.", legenda))
s.append(P(
    f"A probabilidade de referência foi obtida pelo modelo normal ajustado à Planilha 1, mesmo método da "
    f"Questão 5 da Sprint 1: z<sub>a</sub> = (20 − {br(mu0)})/{br(sigma)} = {br(za)} e "
    f"z<sub>b</sub> = (30 − {br(mu0)})/{br(sigma)} = {br(zb)}, de modo que "
    f"p = Φ({br(zb)}) − Φ({br(za)}) = {br(stats.norm.cdf(zb), 6)} − {br(stats.norm.cdf(za), 6)} = "
    f"{br(p0)}. O valor é próximo da frequência observada na Planilha 1 ({pct(p_obs1)}), o que reforça a "
    f"adequação do modelo normal verificada na Sprint 1."))
s.append(P(
    f"<b>Comparação preliminar.</b> A média caiu {br(mu0 - xbar, 2)} min ({pct((mu0 - xbar) / mu0)} da "
    f"média inicial) e a proporção de carregamentos em [20, 30] min passou de {pct(p0)} para {pct(phat)}, "
    f"um aumento de {br(100 * (phat - p0), 2)} pontos percentuais. A mediana também diminuiu "
    f"({br(med1, 2)} → {br(med2, 2)} min), e a dispersão permaneceu praticamente igual "
    f"({br(sigma)} e {br(s2)} min). Os dois critérios apontam na direção do objetivo e constituem "
    f"<b>indícios preliminares de eficácia</b> da intervenção. São indícios descritivos: sozinhos, não "
    f"mostram se as diferenças superam o que se esperaria por variação amostral, o que é avaliado a seguir."))

# ---------- 2. média
s.append(P("2. Teste de hipótese para a média", h1))
s.append(P("2.1 Hipóteses", h2))
s.append(P(
    f"O valor de referência é a média da Planilha 1, {MU0} = {br(mu0)} min. Como o objetivo é reduzir o "
    f"tempo, a hipótese alternativa indica média menor, e o teste é <b>unilateral à esquerda</b>. A hipótese "
    f"nula contém a igualdade:"))
s.append(equacao(r"H_0:\ \mu = 31{,}8867\ \mathrm{min} \qquad H_1:\ \mu < 31{,}8867\ \mathrm{min}"))
s.append(P(
    "Em palavras: H<sub>0</sub> afirma que o tempo médio de carregamento após a padronização é igual ao de "
    "antes; H<sub>1</sub> afirma que ele é menor."))

s.append(P("2.2 Estatística de teste", h2))
s.append(P(
    f"Foi usada a estatística da aula para a média, com σ igual ao desvio-padrão da Planilha 1 "
    f"({br(sigma)} min), já que a orientação trata essa planilha como população e a empresa não informou "
    f"outro valor. Como n = {n} > 30, pelo Teorema do Limite Central a média amostral tem distribuição "
    f"aproximadamente normal:"))
s.append(equacao(
    r"z_{calc} = \frac{\bar{x}-\mu_0}{\sigma/\sqrt{n}} = "
    rf"\frac{{{br(xbar).replace(',', '{,}')} - {br(mu0).replace(',', '{,}')}}}"
    rf"{{{br(sigma).replace(',', '{,}')}/\sqrt{{{n}}}}} = "
    rf"\frac{{{br(xbar - mu0).replace(',', '{,}').replace(chr(8722), '-')}}}{{{br(ep_m).replace(',', '{,}')}}}"
    rf" = {br(z_m).replace(',', '{,}').replace(chr(8722), '-')}", 13))
s.append(P(
    f"Os cálculos usam os valores sem arredondamento; os números exibidos têm 4 casas decimais. "
    f"Os valores críticos são os quantis da normal padrão: z = −1,645 para α = 5% e z = −2,326 para "
    f"α = 1% (arredondados na tabela da normal padrão, cerca de −1,64 e −2,33)."))

linhas_m = [["α", "Valor crítico", "Região de rejeição de H<sub>0</sub>",
             "Região de não rejeição de H<sub>0</sub>", f"{ZC}", "Decisão"]]
for a in ALFAS:
    xc = mu0 + zc_m[a] * ep_m
    linhas_m.append([f"{int(a * 100)}%", br(zc_m[a], 3),
                     f"z ≤ {br(zc_m[a], 3)}<br/>({XB} ≤ {br(xc, 2)} min)",
                     f"z > {br(zc_m[a], 3)}<br/>({XB} > {br(xc, 2)} min)",
                     br(z_m), "<b>Rejeitar H<sub>0</sub></b>"])
s.append(tabela(linhas_m, [1.3 * cm, 2.1 * cm, 3.9 * cm, 3.9 * cm, 2.2 * cm, 3.0 * cm]))
s.append(P("Tabela 2. Teste da média: valores críticos, regiões e decisão para os dois níveis de "
           "significância.", legenda))

s.append(P("2.3 Resultado para α = 5%", h2))
s.extend(figura("teste_media_alfa_05.png",
                "Figura 1. Teste da média, α = 5%: região de rejeição (vermelho hachurado, z ≤ −1,645), "
                f"região de não rejeição (azul) e z calculado = {br(z_m)}."))
s.append(P(
    f"<b>Decisão:</b> como {ZC} = {br(z_m)} ≤ −1,645, o valor calculado está na região de rejeição; "
    f"<b>rejeita-se H<sub>0</sub></b>. <b>Conclusão:</b> ao nível de significância de 5%, há evidência "
    f"estatística de que o tempo médio de carregamento após a padronização da preparação é menor que "
    f"{br(mu0, 2)} min. Para que H<sub>0</sub> fosse rejeitada, bastaria uma média amostral de até "
    f"{br(mu0 + zc_m[0.05] * ep_m, 2)} min; a média observada foi {br(xbar, 2)} min."))

s.append(P("2.4 Resultado para α = 1%", h2))
s.extend(figura("teste_media_alfa_01.png",
                "Figura 2. Teste da média, α = 1%: região de rejeição (vermelho hachurado, z ≤ −2,326), "
                f"região de não rejeição (azul) e z calculado = {br(z_m)}."))
s.append(P(
    f"<b>Decisão:</b> como {ZC} = {br(z_m)} ≤ −2,326, o valor calculado também está na região de "
    f"rejeição; <b>rejeita-se H<sub>0</sub></b>. <b>Conclusão:</b> mesmo com o critério mais rigoroso, de "
    f"1%, há evidência estatística de que o tempo médio de carregamento após a intervenção é menor que "
    f"{br(mu0, 2)} min. O limite para rejeição seria uma média amostral de até "
    f"{br(mu0 + zc_m[0.01] * ep_m, 2)} min, e a observada foi {br(xbar, 2)} min."))

s.append(P("2.5 Confronto com a análise preliminar", h2))
s.append(P(
    f"As conclusões para 1% e 5% <b>coincidem</b> com a análise preliminar: a redução da média, já "
    f"apontada como indício de eficácia, mostrou-se estatisticamente significativa. O teste acrescenta "
    f"uma informação que a comparação descritiva não dava: a diferença de {br(mu0 - xbar, 2)} min "
    f"corresponde a {br(abs(z_m), 2)} erros-padrão abaixo da média de referência, e a probabilidade de "
    f"obter uma média tão baixa por acaso, se H<sub>0</sub> fosse verdadeira, é da ordem de 10<super>−11</super> "
    f"(p-valor ≈ {br(pv_m * 1e12, 1)} × 10<super>−12</super>). Por isso a decisão não depende do nível "
    f"de significância escolhido."))
s.append(P(
    "A coincidência não elimina as limitações do estudo. A rejeição de H<sub>0</sub> indica que a média do "
    "período posterior é menor, mas não prova que a padronização foi a causa: a Planilha 2 foi coletada em "
    "outro período, e fatores como safra, equipe, fila e manutenção de equipamentos também podem ter "
    "mudado. O teste também supõe que os 100 carregamentos formam uma amostra representativa e "
    "independente, e que a dispersão se manteve. Essa última suposição é sustentada pelos desvios-padrão "
    f"praticamente iguais ({br(sigma)} e {br(s2)} min). Se a análise preliminar e o teste tivessem "
    "divergido, os motivos mais prováveis seriam uma diferença pequena em relação ao erro-padrão, uma "
    "amostra pequena ou uma variabilidade alta. Nenhum desses casos ocorreu aqui."))

# ---------- 3. proporção
s.append(P("3. Teste de hipótese para a proporção", h1))
s.append(P("3.1 Hipóteses", h2))
s.append(P(
    f"O evento analisado é “o carregamento leva entre {A} e {B} minutos”. A proporção de referência é "
    f"{P0} = {br(p0)}, probabilidade desse evento pelo modelo normal da Planilha 1 (Questão 5 corrigida). "
    f"A proporção amostral é {PH} = {k2}/{n} = {br(phat, 2)} (Questão 7.4(b) da Sprint 1). Como o objetivo "
    f"é aumentar a proporção de carregamentos nessa faixa, o teste é <b>unilateral à direita</b>:"))
s.append(equacao(r"H_0:\ p = 0{,}3097 \qquad H_1:\ p > 0{,}3097"))
s.append(P(
    "Em palavras: H<sub>0</sub> afirma que a proporção de carregamentos entre 20 e 30 min após a "
    "padronização é igual à de referência; H<sub>1</sub> afirma que ela é maior."))

s.append(P("3.2 Estatística de teste", h2))
s.append(P(
    f"A aproximação normal é adequada, porque n·{P0} = {br(n * p0, 2)} ≥ 5 e n·(1 − {P0}) = "
    f"{br(n * (1 - p0), 2)} ≥ 5. Com a estatística da aula para a proporção:"))
s.append(equacao(
    r"z_{calc} = \frac{\hat{p}-p_0}{\sqrt{p_0(1-p_0)/n}} = "
    rf"\frac{{0{{,}}57 - {br(p0).replace(',', '{,}')}}}"
    rf"{{\sqrt{{{br(p0).replace(',', '{,}')} \times {br(1 - p0).replace(',', '{,}')}/{n}}}}} = "
    rf"\frac{{{br(phat - p0).replace(',', '{,}')}}}{{{br(ep_p).replace(',', '{,}')}}} = "
    rf"{br(z_p).replace(',', '{,}')}", 13))
s.append(P("Os valores críticos são z = 1,645 para α = 5% e z = 2,326 para α = 1%."))

linhas_p = [["α", "Valor crítico", "Região de rejeição de H<sub>0</sub>",
             "Região de não rejeição de H<sub>0</sub>", f"{ZC}", "Decisão"]]
for a in ALFAS:
    pc = p0 + zc_p[a] * ep_p
    linhas_p.append([f"{int(a * 100)}%", br(zc_p[a], 3),
                     f"z ≥ {br(zc_p[a], 3)}<br/>({PH} ≥ {pct(pc)})",
                     f"z < {br(zc_p[a], 3)}<br/>({PH} < {pct(pc)})",
                     br(z_p), "<b>Rejeitar H<sub>0</sub></b>"])
s.append(tabela(linhas_p, [1.3 * cm, 2.1 * cm, 3.9 * cm, 3.9 * cm, 2.2 * cm, 3.0 * cm]))
s.append(P("Tabela 3. Teste da proporção: valores críticos, regiões e decisão para os dois níveis de "
           "significância.", legenda))

s.append(P("3.3 Resultado para α = 5%", h2))
s.extend(figura("teste_proporcao_alfa_05.png",
                "Figura 3. Teste da proporção, α = 5%: região de rejeição (vermelho hachurado, z ≥ 1,645), "
                f"região de não rejeição (azul) e z calculado = {br(z_p)}."))
s.append(P(
    f"<b>Decisão:</b> como {ZC} = {br(z_p)} ≥ 1,645, o valor calculado está na região de rejeição; "
    f"<b>rejeita-se H<sub>0</sub></b>. <b>Conclusão:</b> ao nível de 5%, há evidência estatística de que a "
    f"proporção de carregamentos concluídos entre 20 e 30 minutos após a padronização é maior que "
    f"{pct(p0)}. Para rejeitar H<sub>0</sub>, bastaria uma proporção amostral de pelo menos "
    f"{pct(p0 + zc_p[0.05] * ep_p)}; a observada foi {pct(phat)}."))

s.append(P("3.4 Resultado para α = 1%", h2))
s.extend(figura("teste_proporcao_alfa_01.png",
                "Figura 4. Teste da proporção, α = 1%: região de rejeição (vermelho hachurado, z ≥ 2,326), "
                f"região de não rejeição (azul) e z calculado = {br(z_p)}."))
s.append(P(
    f"<b>Decisão:</b> como {ZC} = {br(z_p)} ≥ 2,326, o valor calculado também está na região de "
    f"rejeição; <b>rejeita-se H<sub>0</sub></b>. <b>Conclusão:</b> mesmo ao nível de 1%, há evidência "
    f"estatística de que a proporção de carregamentos na faixa de 20 a 30 minutos aumentou em relação à "
    f"referência de {pct(p0)}. O limite para rejeição seria {pct(p0 + zc_p[0.01] * ep_p)}, bem abaixo "
    f"dos {pct(phat)} observados."))

s.append(P("3.5 Confronto com a análise preliminar", h2))
s.append(P(
    f"As conclusões para 1% e 5% <b>coincidem</b> com a análise preliminar: o aumento da proporção na "
    f"faixa-alvo, de {pct(p0)} para {pct(phat)}, não é explicado apenas pela variação amostral. O valor "
    f"{ZC} = {br(z_p, 2)} está muito acima dos dois valores críticos (p-valor ≈ "
    f"{br(pv_p * 1e9, 1)} × 10<super>−9</super>)."))
s.append(P(
    f"Valem as mesmas ressalvas do teste da média: o resultado indica mudança no período posterior, "
    f"não comprova causalidade, e depende da representatividade da amostra. Além disso, {P0} vem de um "
    f"modelo; com a frequência observada na Planilha 1 ({pct(p_obs1)}) como referência, obtém-se "
    f"z = {br(z_p_obs, 2)}, e a decisão é a mesma. Do ponto de vista prático, {100 - k2}% dos "
    f"carregamentos ainda ficaram fora da faixa-alvo: a melhora é estatisticamente significativa, mas "
    f"não elimina os tempos acima de 30 minutos."))

# ---------- 4. considerações finais
s.append(P("4. Considerações finais", h1))
s.append(P(
    f"Os dois testes de hipótese confirmam, aos níveis de 1% e 5%, os indícios observados na Sprint 1: "
    f"após a padronização da preparação do carregamento, o tempo médio de carregamento é menor que "
    f"{br(mu0, 2)} min ({ZC} = {br(z_m, 2)}), e a proporção de carregamentos concluídos entre 20 e 30 "
    f"minutos é maior que {pct(p0)} ({ZC} = {br(z_p, 2)}). As análises de sensibilidade (σ com divisor N: "
    f"z = {br(z_m_ddof0, 2)}; {P0} observado: z = {br(z_p_obs, 2)}) não alteram as decisões."))
s.append(P(
    "Os resultados sustentam a eficácia da intervenção no sentido estatístico, ou seja, a mudança observada "
    "não é atribuível apenas ao acaso. Como o estudo compara períodos diferentes, sem grupo de controle, "
    "não é possível afirmar que a padronização foi a única causa da melhora. Recomenda-se manter o "
    "monitoramento dos tempos, registrar fatores operacionais (equipe, fila, safra, equipamentos) e, se "
    "possível, repetir a coleta para confirmar a estabilidade do resultado."))

# ---------- referências
s.append(P("Referências", h1))
s += bullets([
    "Orientações Projeto 2 — Sprint 2. Estatística e Análise de Dados, PUC-Campinas, 2º semestre de 2026.",
    "Notas de aula: Distribuições amostrais e intervalos de confiança; Teste de hipótese para a média e "
    "proporção. Estatística e Análise de Dados, 2026.",
    "Relatório final da Sprint 1 — Projeto 2 (grupo), novembro de 2026.",
    "Planilha 1 (antes da intervenção, 300 observações) e Planilha 2 (depois da intervenção, "
    "100 observações) — tempo de carregamento de caminhões com grãos.",
    "Notebooks 01_teste_hipotese_media.ipynb e 02_teste_hipotese_proporcao.ipynb (Sprint 2), "
    "executados com as planilhas originais.",
])

# ---------- apêndice
s.append(P("Apêndice — Intervalo [20, 43] min da Questão 5 original", h1))
s.append(P(
    f"Com o intervalo original da Questão 5, p<sub>0</sub> = P(20 ≤ X ≤ 43) = {br(p0_43)} "
    f"({pct(p0_43)}). Nesse caso, n·(1 − p<sub>0</sub>) = {br(n * (1 - p0_43), 2)} &lt; 5, e a aproximação "
    f"normal do teste z não é válida. Além disso, um intervalo que contém quase todos os carregamentos não "
    f"mede o objetivo da intervenção, que é concluir o carregamento em até 30 minutos. Por isso, a análise "
    f"usou [20, 30] min tanto para p<sub>0</sub> quanto para {PH}, mantendo o mesmo evento nos dois "
    f"momentos. Para registro: na Planilha 2, a frequência em [20, 43] é "
    f"{pct(depois.between(20, 43).mean(), 0)}, menor que p<sub>0</sub>, porque também ficam fora dessa faixa "
    f"os carregamentos mais rápidos que 20 min, que não representam piora do processo."))


# ============================================================== montagem
def cabecalho_rodape(canvas, doc):
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setFont("DejaVu", 7)
    canvas.setFillColor(TINTA2)
    nomes = " | ".join(f"{nm} — RA {ra}" for nm, ra in CAPA["integrantes"])
    canvas.drawString(2.2 * cm, A4[1] - 1.3 * cm, nomes)
    canvas.drawString(2.2 * cm, 1.2 * cm, "Projeto 2 • Sprint 2 — Estatística e Análise de Dados")
    canvas.drawRightString(A4[0] - 2.2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


doc = SimpleDocTemplate(str(SAIDA), pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                        topMargin=2.0 * cm, bottomMargin=2.0 * cm,
                        title="Projeto 2 — Sprint 2: testes de hipótese",
                        author=", ".join(nm for nm, _ in CAPA["integrantes"]))
doc.build(s, onFirstPage=cabecalho_rodape, onLaterPages=cabecalho_rodape)
print(f"Relatório gerado: {SAIDA}")
if not CAPA["escola"] or not CAPA["curso"]:
    print("ATENÇÃO: preencha 'escola' e 'curso' em CAPA antes de entregar.")

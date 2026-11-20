#!/usr/bin/env python3
"""Gera o site Pro Gym (HTML estático) na própria pasta do repositório.
Requisitos: Python 3 e Pillow (pip install pillow).
Correr: python3 build.py   (regenera todas as páginas, sitemap e versões reduzidas das imagens)"""
import os, sys, json, html, urllib.parse, datetime
from PIL import Image
from i18n import EN

SITE_URL = "https://www.progym.co.mz"
OUT = os.path.dirname(os.path.abspath(__file__))
WA = "258844414441"
ADMIN_TEL = "+258 84 441 4441"
EMAIL = "info@progym.co.mz"
FB = "https://www.facebook.com/mozprogym"
IG = "https://www.instagram.com/mozprogym/"
LI = "https://www.linkedin.com/company/pro-gym-fitness-lda/"
IMG = "assets/img/"
YEAR = datetime.date.today().year

HOURS = [("Segunda a sexta", "05:00", "22:00"), ("Sábado", "06:00", "18:00"),
         ("Domingo", "06:00", "13:00"), ("Feriados", "06:00", "13:00")]

# ---------- idiomas ----------
# O site é escrito em português (texto-fonte). T() devolve a tradução em inglês quando LANG == "en".
# Todas as traduções vivem em i18n.py; se faltar alguma, o build em inglês falha e diz qual.
LANG = "pt"
MISSING = set()
def T(s):
    if LANG == "pt": return s
    v = EN.get(s)
    if v is None:
        MISSING.add(s); return s
    return v
def F(tpl, *a): return T(tpl) % a
def N(s):
    """Números: 2.990 / 3,6 em português; 2,990 / 3.6 em inglês."""
    return s.replace(".", "\0").replace(",", ".").replace("\0", ",") if LANG == "en" else s
def A(root):
    """Prefixo para ficheiros (imagens, css, js): na versão /en/ há mais um nível até à raiz."""
    return root + ("../" if LANG == "en" else "")
def wamsg(tpl, *a, en=None):
    pt = tpl % a
    if LANG == "pt": return pt
    return T(tpl) % (en if en is not None else a) + "\n\n(PT) " + pt

GYMS = [
 dict(slug="mares", name="Marés", area="Costa do Sol, Maputo",
  tel="+258 85 550 5550",
  addr="Centro Comercial Marés, Av. da Marginal, Maputo nº 9519, 1100 Maputo, Moçambique",
  desc="Localizado no coração do Centro Comercial Marés, em Costa do Sol, o Pro Gym Marés é o seu espaço de fitness familiar onde resultados, saúde e diversão se encontram. Aproveite equipamentos modernos, treinadores profissionais e uma comunidade acolhedora – tudo a poucos passos das suas lojas e restaurantes favoritos.",
  cover="gyms/mares/drone.jpg", photos=["drone","door","store","mares-3","cardio"], plan="plans/plano-mares.jpg"),
 dict(slug="alto-mae", name="Alto Maé", area="Alto Maé, Maputo",
  tel="+258 85 552 5552",
  addr="Av. da Tanzania nº 3533, Pro Gym - 1º Andar, Maputo 1100, Moçambique",
  desc="Situado no vibrante bairro de Alto Maé, em Maputo, o Pro Gym Alto Maé é o espaço ideal de fitness para energia, resultados e comunidade. Treine com equipamentos modernos, acompanhado por treinadores profissionais, num ambiente dinâmico e acolhedor bem no centro da cidade.",
  cover="gyms/alto-mae/drone.jpg", photos=["drone","side","door","reception","cardio","spinning"], plan="plans/plano-alto-mae.jpg"),
 dict(slug="matola", name="Matola", area="Parque dos Poetas, Matola",
  tel="+258 85 551 5551",
  addr="Parque dos Poetas, Av. União Africana (Jardim Municipal), Cidade da Matola 1114, Moçambique",
  desc="No coração do belo Parque dos Poetas, no centro da Matola, o Pro Gym Matola oferece muito mais do que um ginásio – é um verdadeiro destino de família e desporto. Com a nossa arena desportiva mesmo à frente (campos de padel, basquetebol e futsal), além de mini golfe, parque infantil e a única área de treino calisténico ao ar livre em Moçambique, é o lugar perfeito para fitness e diversão. No interior, encontrará equipamentos modernos, treinadores profissionais e uma comunidade acolhedora pronta para apoiar os seus objetivos.",
  cover="gyms/matola/matola-7.jpg", photos=["matola-7","matola-1","matola-2","matola-3","matola-4","matola-5","matola-6"], plan="plans/plano-matola.jpg"),
 dict(slug="zimpeto", name="Zimpeto", area="Estádio Nacional do Zimpeto, Maputo",
  tel="+258 85 553 5553",
  addr="Estádio Nacional do Zimpeto Bloco 06, Av. de Moçambique, Km 14, Maputo 1100, Moçambique",
  desc="No icónico Estádio Nacional do Zimpeto, o Pro Gym Zimpeto é muito mais do que um ginásio – é um centro de desporto, saúde e família. Temos o orgulho de apresentar o nosso ginásio mais recente, cheio de surpresas à sua espera! No interior, encontrará equipamentos de última geração, treinadores profissionais e uma comunidade solidária pronta para ajudar a alcançar os seus objetivos.",
  cover="gyms/zimpeto/side.jpg", photos=["side","door","spinning","crossfit","zimpeto-3","zimpeto-4","zimpeto-5","zimpeto-6"], plan=None),
]
ALT = {"drone": "vista aérea", "side": "vista lateral", "door": "entrada", "store": "loja",
       "cardio": "zona de cardio", "reception": "receção", "spinning": "sala de spinning", "crossfit": "área de CrossFit",
       "matola-7": "vista aérea", "matola-1": "fachada", "matola-2": "entrada", "matola-3": "zona de cardio",
       "matola-4": "área de treino funcional", "matola-5": "máquinas de força", "matola-6": "sala de spinning",
       "mares-3": "sala de treino", "zimpeto-3": "zona de cardio", "zimpeto-4": "zona de musculação",
       "zimpeto-5": "máquinas de força", "zimpeto-6": "zona de boxe"}

def e(s): return html.escape(s, quote=True)
def tel(s): return "tel:" + s.replace(" ", "")
def wa(msg, *a, **k): return "https://wa.me/%s?text=%s" % (WA, urllib.parse.quote(wamsg(msg, *a, **k)))
def maps(q): return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(q)

ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="square" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg>'

# ---------- imagens: dimensões explícitas + versões reduzidas (srcset) ----------
_cache = {}
def variants(rel):
    if rel in _cache: return _cache[rel]
    src = os.path.join(OUT, IMG, rel)
    w, h = Image.open(src).size
    vs = []
    if rel.lower().endswith((".jpg", ".jpeg")) and w >= 1300 and not rel.startswith("plans/"):
        base = rel.rsplit(".", 1)[0].replace("/", "_")
        for tw in (640, 1100, 1600):
            out = "_s/%s-%d.jpg" % (base, tw)
            p = os.path.join(OUT, IMG, out)
            if not os.path.exists(p):
                os.makedirs(os.path.dirname(p), exist_ok=True)
                im = Image.open(src).convert("RGB")
                im.resize((tw, round(h * tw / w)), Image.LANCZOS).save(p, "JPEG", quality=86, optimize=True, progressive=True)
            vs.append((out, tw))
    _cache[rel] = (w, h, vs)
    return _cache[rel]

def pic(root, rel, alt, sizes="100vw", eager=False, cls=""):
    w, h, vs = variants(rel)
    src = A(root) + IMG + rel
    srcset = ""
    if vs:
        srcset = ' srcset="%s" sizes="%s"' % (", ".join(["%s%s%s %dw" % (A(root), IMG, o, tw) for o, tw in vs] + ["%s %dw" % (src, w)]), sizes)
    load = ' fetchpriority="high" decoding="async"' if eager else ' loading="lazy" decoding="async"'
    c = ' class="%s"' % cls if cls else ""
    return '<img%s src="%s"%s width="%d" height="%d" alt="%s"%s>' % (c, src, srcset, w, h, e(alt), load)

def mask(root, rel, alt, sizes="50vw", par=False, extra=""):
    return '<div class="mask%s"%s%s><div class="in">%s</div></div>' % (" free" if False else "", " data-par" if par else "", extra, pic(root, rel, alt, sizes))

def sp(text):
    """Divide um título em palavras para a revelação palavra a palavra (o texto continua legível sem JS)."""
    return " ".join('<span class="w"><span>%s</span></span>' % e(w) for w in text.split())

def stmt_words(text):
    return " ".join('<span class="sw">%s</span>' % e(w) for w in text.split())

NAV = [("Ginásios", "gyms/", [(g["name"], "gyms/%s/" % g["slug"]) for g in GYMS]),
       ("Preços", "pricing/", None), ("Aulas", "plans/", None), ("Serviços", "services/", None),
       ("App", "app/", None), ("Loja", "store/", None), ("Contacto", "contact/", None)]

PAGES = []  # (path, indexable) da língua que está a ser gerada

def TP(s):
    """Nomes próprios e moradas: traduz só o que tem tradução, sem avisar do resto."""
    return EN.get(s, s) if LANG == "en" else s

def layout(path, title, desc, body, jsonld=None, og_img="hero/hero-2.jpg", noindex=False, preload=None):
    en = LANG == "en"
    depth = path.count("/")
    root = "../" * depth          # ligações dentro da mesma língua
    aroot = A(root)               # ficheiros (css, js, imagens) na raiz do site
    nav = []
    for label, href, sub in NAV:
        active = ' aria-current="page"' if (path == href or (sub and path.startswith("gyms/")) or (href != "gyms/" and path.startswith(href))) else ""
        if sub:
            items = "".join('<li><a href="%s%s">%s</a></li>' % (root, h, e(n)) for n, h in sub)
            nav.append('<li class="sub-nav"><a href="%s%s"%s>%s</a><ul class="drop">%s</ul></li>' % (root, href, active, T(label), items))
        else:
            nav.append('<li><a href="%s%s"%s>%s</a></li>' % (root, href, active, T(label)))
    pfx = "en/" if en else ""
    canon = SITE_URL + "/" + pfx + path
    ld = '<script type="application/ld+json">%s</script>' % json.dumps(jsonld, ensure_ascii=False) if jsonld else ""
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    pre = ""
    if preload and isinstance(preload, str):
        pre = '<link rel="preload" as="image" href="%s%s%s" fetchpriority="high">' % (aroot, IMG, preload)
    # seletor de língua: aponta para a mesma página na outra língua
    h_pt = (aroot + path) if en else (root + path)
    h_en = (root + path) if en else (aroot + "en/" + path)
    cur = ' aria-current="true"'
    lang_sw = ('<div class="lang" role="group" aria-label="%s"><a lang="pt" hreflang="pt" href="%s"%s title="Português">PT</a>'
               '<a lang="en" hreflang="en" href="%s"%s title="English">EN</a></div>') % (
        T("Idioma"), h_pt, "" if en else cur, h_en, cur if en else "")
    alt_links = "" if noindex else ('<link rel="alternate" hreflang="pt" href="%s/%s">\n<link rel="alternate" hreflang="en" href="%s/en/%s">\n<link rel="alternate" hreflang="x-default" href="%s/%s">' % (
        SITE_URL, path, SITE_URL, path, SITE_URL, path))
    return """<!DOCTYPE html>
<html lang="%(lang)s" class="t-uxpro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
%(robots)s
<link rel="canonical" href="%(canon)s">
%(alt)s
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:type" content="website">
<meta property="og:url" content="%(canon)s">
<meta property="og:image" content="%(site)s/%(img)s%(og)s">
<meta property="og:locale" content="%(loc)s">
<meta property="og:locale:alternate" content="%(loc2)s">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0A0A0A">
<link rel="icon" href="data:image/svg+xml,%%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%%3E%%3Crect width='64' height='64' rx='10' fill='%%230A0A0A'/%%3E%%3Ctext x='32' y='44' font-size='34' font-weight='900' text-anchor='middle' fill='%%23F97316' font-family='Arial Narrow,Arial'%%3EPG%%3C/text%%3E%%3C/svg%%3E">
<script>(function(){var r=document.documentElement;r.classList.add('js');if(!matchMedia('(prefers-reduced-motion: reduce)').matches){r.classList.add('motion');setTimeout(function(){if(!window.__pg)r.classList.remove('motion')},4500)}})();</script>
<link rel="preload" href="%(aroot)sassets/fonts/big-shoulders-display-latin-900-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="%(aroot)sassets/fonts/schibsted-grotesk-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
%(pre)s
<link rel="stylesheet" href="%(aroot)sassets/css/style.css">
<link rel="stylesheet" href="%(aroot)sassets/css/ux-pro.css">
%(ld)s
</head>
<body>
<a class="skip" href="#conteudo">%(skip)s</a>
<div id="navbar" aria-hidden="true"></div>
<header class="top" id="top">
  <div class="wrap nav">
    <a class="logo" href="%(root)s" aria-label="%(logo_l)s"><img src="%(aroot)s%(img)slogo.png" alt="Pro Gym Fitness" width="177" height="38"></a>
    <button class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="mainNav">%(menu)s</button>
    <nav id="mainNav" aria-label="%(main)s"><ul>%(nav)s</ul></nav>
    %(lang_sw)s
    <a class="btn small" href="%(root)s#marcar">%(cta)s</a>
  </div>
</header>
<main id="conteudo">
%(body)s
</main>
%(footer)s
<a class="wa-float" href="https://wa.me/%(wa)s" target="_blank" rel="noopener" aria-label="%(wa_l)s">WhatsApp</a>
<script src="%(aroot)sassets/js/vendor/gsap.min.js" defer></script>
<script src="%(aroot)sassets/js/vendor/ScrollTrigger.min.js" defer></script>
<script src="%(aroot)sassets/js/site.js" defer></script>
</body>
</html>
""" % dict(lang=LANG, title=e(title), desc=e(desc), robots=robots, canon=canon, alt=alt_links, site=SITE_URL, img=IMG, og=og_img, root=root, aroot=aroot, pre=pre,
           loc="en_US" if en else "pt_MZ", loc2="pt_MZ" if en else "en_US", lang_sw=lang_sw,
           ld=ld, nav="".join(nav), body=body, footer=footer(root), wa=WA,
           skip=T("Saltar para o conteúdo"), logo_l=T("Pro Gym Fitness, início"), menu=T("Menu"), main=T("Principal"), cta=T("Sessão grátis"), wa_l=T("Falar connosco no WhatsApp"))

def footer(root):
    g = "".join('<li><a href="%sgyms/%s/">%s</a></li>' % (root, x["slug"], x["name"]) for x in GYMS)
    return """<footer>
  <div class="wrap">
    <div class="foot">
      <div><img src="%(aroot)s%(img)slogo.png" alt="Pro Gym Fitness" width="205" height="44" loading="lazy"><p>%(l1)s<br>Best Price | Best Quality</p></div>
      <div><h3>%(h1)s</h3><ul>%(g)s</ul></div>
      <div><h3>%(h2)s</h3><ul>
        <li><a href="%(root)spricing/">%(pr)s</a></li><li><a href="%(root)splans/">%(cl)s</a></li>
        <li><a href="%(root)sservices/">%(sv)s</a></li><li><a href="%(root)sarena/">%(ar)s</a></li><li><a href="%(root)sapp/">%(ap)s</a></li>
        <li><a href="%(root)sstore/">%(st)s</a></li><li><a href="%(root)sgallery/">%(ev)s</a></li></ul></div>
      <div><h3>%(h3)s</h3><ul>
        <li><a href="tel:+258844414441">%(tel)s</a></li>
        <li><a href="https://wa.me/%(wa)s" target="_blank" rel="noopener">WhatsApp</a></li>
        <li><a href="mailto:%(em)s">%(em)s</a></li>
        <li><a href="%(fb)s" target="_blank" rel="noopener">Facebook</a></li>
        <li><a href="%(ig)s" target="_blank" rel="noopener">Instagram</a></li>
        <li><a href="%(li)s" target="_blank" rel="noopener">LinkedIn</a></li></ul></div>
    </div>
    <div class="mark" aria-hidden="true">Pro Gym</div>
    <div class="legal"><span>© %(y)d Pro Gym Fitness, Lda. %(rights)s</span><span>%(by)s</span></div>
  </div>
</footer>""" % dict(root=root, aroot=A(root), img=IMG, g=g, tel=ADMIN_TEL, wa=WA, em=EMAIL, fb=FB, ig=IG, li=LI, y=YEAR,
                    l1=T("Ginásios em Maputo e Matola."), h1=T("Ginásios"), h2=T("Explorar"), h3=T("Contactos"), pr=T("Preços"), cl=T("Aulas"),
                    sv=T("Serviços"), ar=T("Arena Matola"), ap=T("App Pro Gym"), st=T("Loja"), ev=T("Eventos"), rights=T("Todos os direitos reservados."), by=T("Website por YFX"))

def write(path, content):
    pfx = "en/" if LANG == "en" else ""
    full = os.path.join(OUT, pfx + path, "index.html") if (pfx + path) else os.path.join(OUT, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f: f.write(content)

def page_hero(root, crumbs, h1, lead, bg, alt):
    cr = " / ".join('<a href="%s%s">%s</a>' % (root, h, e(n)) if h is not None else '<span aria-current="page">%s</span>' % e(n) for n, h in crumbs)
    return """<section class="phero"><div class="phero-media">%s</div><div class="phero-in"><nav class="crumbs hr" aria-label="%s">%s</nav><h1 class="sp" data-hero aria-label="%s">%s</h1>%s</div></section>""" % (
        pic(root, bg, alt, "100vw", eager=True), T("Localização"), cr, e(h1), sp(h1), ('<p class="lead hr">%s</p>' % e(lead)) if lead else "")

def TIMETABLE_NOTE():
    """O horário das aulas é uma imagem do Pro Gym, em português; avisa quem lê em inglês."""
    return "" if LANG == "pt" else " " + T("O horário é publicado em português; os dias da semana aparecem também em inglês.")

def hrs(a, b): return F("%s às %s", a, b)

def hours_list():
    return '<ul class="hours">%s</ul>' % "".join("<li><span>%s</span><strong>%s</strong></li>" % (T(n), hrs(a, b)) for n, a, b in HOURS)

def booking_section(root, preset=None):
    opts = "".join('<option%s>%s</option>' % (" selected" if preset == g["name"] else "", g["name"]) for g in GYMS)
    times = "".join('<option value="%s">%s</option>' % (v, T(l)) for v, l in [("manhã", "Manhã"), ("tarde", "Tarde"), ("noite", "Noite")])
    return """<section class="orange-sec" id="marcar"><div class="wrap book">
  <div><h2 class="sp">%(h)s</h2><p class="sub rv" style="color:var(--iron)">%(s)s</p></div>
  <form class="f rv" id="bookForm" novalidate>
    <label>%(n)s<input id="fName" autocomplete="name" placeholder="%(ph)s" required></label>
    <div class="two"><label>%(g)s<select id="fUnit">%(o)s</select></label><label>%(d)s<input id="fDate" type="date"></label></div>
    <label>%(t)s<select id="fTime">%(tt)s</select></label>
    <div class="err" id="err" role="alert"></div>
    <button class="btn" type="submit">%(b)s</button>
    <p class="fine">%(f)s</p>
  </form></div></section>""" % dict(h=sp(T("A primeira sessão é grátis")), s=T("Escolhe o ginásio e o dia. A mensagem segue pelo WhatsApp para a receção e confirmamos contigo."),
        n=T("Nome"), ph=T("O teu nome"), g=T("Ginásio"), o=opts, d=T("Dia"), t=T("Hora preferida"), tt=times, b=T("Enviar pelo WhatsApp"),
        f=T("Abre o WhatsApp com a mensagem pronta. Este site não guarda os teus dados."))

FAQ = [
 ("Qual é o horário?", "Segunda a sexta das 05:00 às 22:00, sábado das 06:00 às 18:00, domingo e feriados das 06:00 às 13:00."),
 ("Quanto custa a mensalidade?", "A mensalidade normal custa 2.990 MT. Há também planos trimestral (8.490 MT), semestral (14.990 MT, com 1 mês grátis) e anual (24.990 MT, com 3,6 meses grátis)."),
 ("Há preços para estudantes, famílias e seniores?", "Sim. Estudantes até 21 anos pagam 1.500 MT para 1 ginásio ou 1.790 MT para todos os ginásios. A família (pais e filhos) paga 2.690 MT e os seniores (65+) pagam 1.990 MT."),
 ("Posso treinar só um dia ou uma semana?", "Sim. A entrada diária custa 500 MT e um pack de 10 entradas custa 4.500 MT. Também há plano semanal (1.490 MT), de duas semanas (1.990 MT) e de fins de semana (1.990 MT)."),
 ("Quanto custa a inscrição?", "A tabela de preços indica a anuidade de membro (900 MT), o cartão (500 MT) e o chaveiro (700 MT)."),
 ("Como ganho semanas grátis?", "Traz um membro ao ginásio e ganhas 1 semana grátis. Se trouxeres 4 membros, ganhas 4 semanas, ou seja, 1 mês grátis."),
 ("Como marco a primeira sessão grátis?", "Preenche o formulário desta página ou fala connosco pelo WhatsApp. A receção confirma o dia e a hora."),
]
def faq_section():
    d = "".join('<details name="faq"><summary>%s</summary><p>%s</p></details>' % (e(T(q)), e(T(a))) for q, a in FAQ)
    return '<section class="paper" id="faq"><div class="wrap"><h2 class="sp">%s</h2><div class="faq rv">%s</div></div></section>' % (sp(T("Perguntas frequentes")), d)

def phone_demo(cap=False):
    c = '<p class="phone-cap">%s</p>' % T("Pré-visualização com dados de exemplo.") if cap else ""
    return """<div><div class="phone" role="group" aria-label="%(al)s"><div class="screen">
  <div class="row"><div><div class="hi">%(hi)s</div><div class="loc">Pro Gym Matola</div></div><div class="loc">%(today)s</div></div>
  <div class="streak"><div><div class="lbl">%(sl)s</div><b id="streakN">12</b> <span class="lbl">%(days)s</span></div>
    <div class="week" aria-hidden="true"><i class="on" style="height:60%%"></i><i class="on" style="height:90%%"></i><i style="height:25%%"></i><i class="on" style="height:75%%"></i><i class="on" style="height:100%%"></i><i class="on" style="height:55%%"></i><i style="height:20%%"></i></div></div>
  <div class="seg" role="group" aria-label="%(rt)s"><button id="rkVisits" aria-pressed="true">%(bv)s</button><button id="rkGoal" aria-pressed="false">%(bg)s</button></div>
  <ol class="rank" id="rank"></ol>
  <div class="challenge" id="challenge"><div><div class="t">%(ch)s</div><div class="s" id="chS">%(chs)s</div></div><button id="chBtn">%(chb)s</button></div>
</div></div>%(c)s</div>""" % dict(c=c, al=T("Pré-visualização da app Pro Gym, com dados de exemplo"), hi=T("Olá, Nelson"), today=T("Hoje"), sl=T("Sequência de treinos"), days=T("dias"),
        rt=T("Tipo de ranking"), bv=T("Por visitas"), bg=T("Por % da meta"), ch=T("Desafio do dia: 25 flexões"), chs=T("Ainda por fazer"), chb=T("Fiz"))

def org_ld():
    return {"@context": "https://schema.org", "@type": "HealthClub", "name": "Pro Gym Fitness", "url": SITE_URL + "/" + ("en/" if LANG == "en" else ""),
            "telephone": "+258844414441", "email": EMAIL, "areaServed": ["Maputo", "Matola"],
            "sameAs": [FB, IG, LI], "logo": SITE_URL + "/" + IMG + "logo.png",
            "openingHoursSpecification": [
              {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "05:00", "closes": "22:00"},
              {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "06:00", "closes": "18:00"},
              {"@type": "OpeningHoursSpecification", "dayOfWeek": "Sunday", "opens": "06:00", "closes": "13:00"}]}

def cover_alt(g):
    base = os.path.basename(g["cover"]).rsplit(".", 1)[0]
    return "Pro Gym %s, %s" % (g["name"], T(ALT.get(base, "vista do ginásio")))

def gcard(g, root, href, sizes="60vw", cls="gh-card"):
    return """<a class="%s" href="%s"><div class="gh-img">%s</div>
      <div class="gh-tx"><h3>Pro Gym %s</h3><p class="area">%s</p><p class="tel">%s</p><span class="go">%s %s</span></div></a>""" % (
        cls, href, pic(root, g["cover"], cover_alt(g), sizes), e(g["name"]), e(TP(g["area"])), g["tel"], T("Ver ginásio"), ARROW)

def elastic_item(g, root, i):
    on = " is-active" if i == 0 else ""
    return """<a class="el%s" href="%sgyms/%s/" aria-label="Pro Gym %s, %s"><div class="el-img">%s</div>
      <div class="el-on"><span class="el-tag">%s</span><h3>%s</h3><p class="el-tel">%s</p><span class="go">%s %s</span></div>
      <div class="el-off" aria-hidden="true"><span class="el-v">%s</span><span class="el-n">%02d</span></div></a>""" % (
        on, root, g["slug"], e(g["name"]), e(TP(g["area"])), pic(root, g["cover"], cover_alt(g), "(min-width:900px) 60vw, 100vw"), e(TP(g["area"])), e(g["name"]), g["tel"], T("Ver ginásio"), ARROW, e(g["name"]), i + 1)

# ---------------- HOME ----------------
def promo_block(root):
    return """<section class="promo-sec"><div class="wrap"><div class="promo rv">
  <div class="promo-head"><h2 class="sp">%s</h2><p class="sub">%s</p></div>
  <ul class="promo-tiers">
    <li><b>1</b><span>%s</span><strong>%s</strong></li>
    <li><b>2</b><span>%s</span><strong>%s</strong></li>
    <li><b>3</b><span>%s</span><strong>%s</strong></li>
    <li class="top"><b>4</b><span>%s</span><strong>%s</strong></li>
  </ul>
  <a class="btn" href="%s">%s</a>
</div></div></section>""" % (sp(T("Traz um membro, treina grátis")), T("Por cada pessoa que trouxeres ao ginásio ganhas 1 semana grátis."),
        T("membro trazido"), T("1 semana grátis"), T("membros trazidos"), T("2 semanas grátis"), T("membros trazidos"), T("3 semanas grátis"),
        T("membros trazidos"), T("4 semanas: 1 mês grátis"), wa("Olá! Quero saber como funciona a promoção de trazer um membro e ganhar semanas grátis."), T("Perguntar pelo WhatsApp"))

def home():
    root = ""
    gcards = "".join(elastic_item(g, root, i) for i, g in enumerate(GYMS))
    h1 = T("Treina onde te der mais jeito.")
    body = """
<section class="hero" aria-label="%(l_hero)s">
  <div class="hero-media">%(heroimg)s</div>
  <div class="hero-in">
    <div class="status hr" id="status" role="status"><span class="dot"></span><span id="statusText">%(chk)s</span></div>
    <h1 class="sp" data-hero aria-label="%(h1l)s">%(h1)s</h1>
    <p class="lede hr">%(lede)s</p>
  </div>
</section>

<section id="ginasios"><div class="wrap">
  <h2 class="sp">%(gh2)s</h2><p class="sub rv">%(gsub)s</p>
</div>
<div class="elastic rv" data-elastic>%(gcards)s</div>
<div class="wrap"><p class="soonline rv"><span class="soon">%(soon)s</span>%(xx)s</p></div></section>

%(promo)s
<section class="calm" id="sobre"><div class="wrap about">
  <div>
    <h2 class="sp">%(ab)s</h2>
    <p class="sub rv">%(absub)s</p>
    <ul class="quick rv">
      <li><a href="pricing/">%(q1)s</a></li><li><a href="plans/">%(q2)s</a></li><li><a href="services/">%(q3)s</a></li><li><a href="app/">%(q4)s</a></li>
    </ul>
  </div>
  <div class="pcard rv">
    <h3>%(m)s</h3>
    <div class="price">%(pm)s<small>MT</small></div>
    <ul class="plist2">
      <li><span>%(an)s</span><b>%(pa)s MT</b></li>
      <li><span>%(est)s</span><b>%(pe)s MT</b></li>
      <li><span>%(sen)s</span><b>%(ps)s MT</b></li>
      <li><span>%(fam)s</span><b>%(pf)s MT</b></li>
    </ul>
    <a class="btn dark" href="pricing/">%(allp)s %(arr)s</a>
  </div>
</div></section>

<section class="calm contact" id="marcar"><div class="wrap">
  <h2 class="sp">%(ch)s</h2>
  <p class="sub rv">%(csub)s</p>
  <div class="actions rv" style="margin-top:1.8rem">
    <a class="btn wa" href="%(wa)s" target="_blank" rel="noopener">%(cb)s %(arr)s</a>
    <a class="btn dark" href="contact/">%(cc)s</a>
  </div>
</div></section>
""" % dict(l_hero=T("Apresentação"), chk=T("A verificar o horário…"), h1l=e(h1), h1=sp(h1),
           lede=T("Quatro ginásios em Maputo e Matola. A primeira sessão é por nossa conta."),
           heroimg=pic(root, "hero/hero-2.jpg", T("Sala de treino do Pro Gym"), "100vw", eager=True), arr=ARROW,
           promo=promo_block(""), soon=T("Brevemente"), xx=T("Novo ginásio em Xai-Xai."), gh2=sp(T("Encontra o teu ginásio")), gsub=T("Marés, Alto Maé, Matola e Zimpeto, abertos de segunda a domingo. Passa o rato ou toca num ginásio para o ver."), gcards=gcards,
           ab=sp(T("Sobre o Pro Gym")),
           absub=T("Ginásios em Maputo e Matola, abertos de segunda a domingo. Aulas de grupo, personal trainer, fisioterapia e nutrição, ao melhor preço e com qualidade."),
           q1=T("Preços"), q2=T("Aulas"), q3=T("Serviços"), q4=T("App Pro Gym"),
           m=T("Mensalidade"), pm=N("2.990"), an=T("Anual"), pa=N("24.990"), est=T("Estudante"), pe=N("1.500"), sen=T("Sénior"), ps=N("1.990"),
           fam=T("Família"), pf=N("2.690"), allp=T("Ver todos os preços"),
           ch=sp(T("Marca a tua primeira sessão")), csub=T("É grátis. Fala connosco pelo WhatsApp e a receção confirma o dia e a hora."),
           wa=wa("Olá, gostaria de marcar a primeira sessão grátis no Pro Gym."), cb=T("Falar no WhatsApp"), cc=T("Todos os contactos"))
    write("", layout("", T("Pro Gym Fitness | Ginásios em Maputo e Matola"), T("Quatro ginásios em Maputo e Matola: Marés, Alto Maé, Matola e Zimpeto. Aulas, personal trainer, fisioterapia, nutrição e padel. Primeira sessão grátis."), body, jsonld=org_ld()))
    PAGES.append(("", True))

# ---------------- GYMS ----------------
def gyms():
    root = "../../"
    gcards = "".join(gcard(g, "../", "%s/" % g["slug"], "(min-width:800px) 58vw, 100vw") for g in GYMS)
    body = page_hero("../", [(T("Início"), ""), (T("Ginásios"), None)], T("Os nossos ginásios"), T("Quatro unidades em Maputo e Matola."), "hero/hero-2.jpg", T("Sala de treino do Pro Gym")) + \
        '<section class="tight"><div class="wrap"><div class="gyms-grid">%s</div></div></section>' % gcards
    write("gyms", layout("gyms/", T("Ginásios Pro Gym | Marés, Alto Maé, Matola e Zimpeto"), T("Conhece os quatro ginásios Pro Gym em Maputo e Matola: morada, contacto e fotos de cada unidade."), body))
    PAGES.append(("gyms/", True))
    for g in GYMS:
        path = "gyms/%s/" % g["slug"]
        area = TP(g["area"]); addr = TP(g["addr"]); desc = T(g["desc"])
        panels = ""
        for k, p in enumerate(g["photos"]):
            label = T(ALT[p]) if p in ALT else F("Foto %d", k + 1)
            label = label[0].upper() + label[1:]
            panels += """<div class="el%s" tabindex="0" role="group" aria-label="%s"><div class="el-img">%s</div>
      <div class="el-on"><span class="el-tag">Pro Gym %s</span><h3>%s</h3></div>
      <div class="el-off" aria-hidden="true"><span class="el-v">%s</span></div></div>""" % (
                " is-active" if k == 0 else "", e(label), pic(root, "gyms/%s/%s.jpg" % (g["slug"], p), "Pro Gym %s, %s" % (g["name"], label.lower()), "(min-width:900px) 60vw, 100vw"), e(g["name"]), e(label), e(label))
        if g["plan"]:
            w, h, _ = variants(g["plan"])
            tt = """<section class="paper tight"><div class="wrap"><h2 class="sp wide">%s</h2>
<a class="imglink rv" href="%s%s%s" target="_blank" rel="noopener" aria-label="%s" style="display:block;margin-top:2rem;border:1px solid var(--line);border-radius:4px;overflow:hidden;background:#fff"><img loading="lazy" decoding="async" src="%s%s%s" width="%d" height="%d" alt="%s" style="width:100%%;height:auto"></a>
<p class="fineprint rv">%s%s <a class="ul" href="%splans/#%s">%s</a></p></div></section>""" % (
                sp(F("Aulas no %s", g["name"])), A(root), IMG, g["plan"], e(F("Abrir o horário das aulas do Pro Gym %s em tamanho real", g["name"])), A(root), IMG, g["plan"], w, h,
                e(F("Horário das aulas do Pro Gym %s", g["name"])), T("Toca na imagem para abrir em tamanho real."), TIMETABLE_NOTE(), root, g["slug"], T("Ver todos os ginásios"))
        else:
            tt = """<section class="paper tight"><div class="wrap"><h2 class="sp wide">%s</h2><p class="sub rv">%s</p>
<div class="actions rv" style="margin-top:1.4rem"><a class="btn dark" href="%s" target="_blank" rel="noopener">%s</a></div></div></section>""" % (
                sp(F("Aulas no %s", g["name"])), T("Pergunta o horário das aulas na receção ou pelo WhatsApp."), wa("Olá! Gostaria de saber o horário das aulas no Pro Gym Zimpeto."), T("Pedir horário"))
        extra = ""
        if g["slug"] == "matola":
            extra = '<a class="btn dark" href="%sarena/">%s</a>' % (root, T("Ver a arena desportiva"))
        others = "".join('<li><a href="%sgyms/%s/">Pro Gym %s <span>%s</span></a></li>' % (root, o["slug"], e(o["name"]), e(TP(o["area"]))) for o in GYMS if o is not g)
        body = page_hero(root, [(T("Início"), ""), (T("Ginásios"), "gyms/"), (g["name"], None)], "Pro Gym " + g["name"], area, g["cover"], cover_alt(g)) + """
<section class="tight"><div class="wrap info">
  <div><div class="status rv" id="status" role="status" style="background:var(--iron);color:#fff;margin-bottom:1.4rem"><span class="dot"></span><span id="statusText">%(chk)s</span></div>
  <h2 class="sp">%(h2)s</h2><p class="sub rv" style="max-width:62ch;color:var(--ink2)">%(d)s</p>
  <div class="actions rv" style="margin-top:1.6rem"><a class="btn" href="#marcar">%(b1)s</a><a class="btn dark" href="%(map)s" target="_blank" rel="noopener">%(b2)s</a>%(extra)s</div></div>
  <dl class="facts rv">
    <div><dt>%(t1)s</dt><dd>%(addr)s</dd></div>
    <div><dt>%(t2)s</dt><dd><a href="%(tl)s">%(tel)s</a></dd></div>
    <div><dt>WhatsApp</dt><dd><a href="https://wa.me/%(wa)s" target="_blank" rel="noopener">%(atel)s</a></dd></div>
    <div><dt>Email</dt><dd><a href="mailto:%(em)s">%(em)s</a></dd></div>
  </dl>
</div></section>
<section style="padding-top:0"><div class="wrap"><h2 class="sp">%(ph2)s</h2><p class="sub rv">%(phs)s</p></div>
<div class="elastic rv" data-elastic>%(panels)s</div></section>
<section class="dark-sec" data-sheet><div class="wrap"><div class="info">
  <div><h2 class="sp">%(hh)s</h2><div class="rv">%(hrs)s</div></div>
  <div><h2 class="sp" style="font-size:clamp(2.3rem,5vw,4rem)">%(pp)s</h2>
  <div class="pgrid" style="grid-template-columns:1fr;margin-top:1.6rem">
    <div class="plan best rv"><span class="tag">%(best)s</span><h3>%(an)s</h3><div class="price">%(pa)s<small>MT</small></div><p class="note">%(ann)s</p></div>
    <ul class="plist"><li class="rv"><span><b>%(m)s</b><small>%(mn)s</small></span><span class="pv">%(pm)s<small> MT</small></span></li>
    <li class="rv"><span><b>%(est)s</b><small>%(est2)s</small></span><span class="pv">%(pe)s<small> MT</small></span></li>
    <li class="rv"><span><b>%(fam)s</b><small>%(fam2)s</small></span><span class="pv">%(pf)s<small> MT</small></span></li></ul></div>
  <div class="actions rv" style="margin-top:1.6rem"><a class="btn" href="%(root)spricing/">%(allp)s</a></div></div>
</div></div></section>
%(tt)s
<section class="tight"><div class="wrap"><h2 class="sp wide">%(oh)s</h2><ul class="more-gyms rv">%(others)s</ul></div></section>
%(book)s
%(faq)s
""" % dict(chk=T("A verificar o horário…"), h2=sp(F("Treina no Pro Gym %s", g["name"])), d=e(desc), root=root, b1=T("Marcar visita grátis"), b2=T("Como chegar"),
           map=maps("Pro Gym " + g["name"] + ", " + g["addr"]), t1=T("Morada"), t2=T("Telefone"), addr=e(addr), tl=tel(g["tel"]), tel=g["tel"], wa=WA, atel=ADMIN_TEL, em=EMAIL, extra=extra,
           ph2=sp(T("Conhece o espaço")), phs=T("Passa o rato ou toca numa foto para a ver maior."), panels=panels, hh=sp(T("Horário")), hrs=hours_list(), pp=sp(T("Preços")),
           best=T("Melhor valor"), an=T("Anual"), pa=N("24.990"), ann=T("3,6 meses grátis. Poupas 10.890 MT."), m=T("Mensalidade"), mn=T("Todos os ginásios"), pm=N("2.990"),
           est=T("Estudante"), est2=T("1 ginásio, até 21 anos"), pe=N("1.500"), fam=T("Família"), fam2=T("Pais e filhos"), pf=N("2.690"), allp=T("Ver todos os preços"),
           tt=tt, oh=sp(T("Outros ginásios")), others=others, book=booking_section(root, g["name"]), faq=faq_section())
        ld = org_ld(); ld["name"] = "Pro Gym " + g["name"]; ld["telephone"] = g["tel"].replace(" ", ""); ld["address"] = {"@type": "PostalAddress", "streetAddress": addr, "addressCountry": "MZ"}
        short = desc[:110].rsplit(" ", 1)[0] + "…"
        write(path, layout(path, F("Pro Gym %s | Ginásio em %s", g["name"], area.split(",")[-1].strip()), F("Pro Gym %s: %s Morada, telefone, horário e fotos.", g["name"], short), body, jsonld=ld, og_img=g["cover"]))
        PAGES.append((path, True))

# ---------------- PRICING ----------------
def pricing():
    root = "../"
    def table(cap, rows, hl=()):
        r = ""
        for i, (n, sm, p) in enumerate(rows):
            name = T(n) + (" <small>%s</small>" % T(sm) if sm else "")
            r += '<tr%s><td>%s</td><td>%s MT</td></tr>' % (' class="hl"' if i in hl else "", name, N(p))
        return '<table class="ptable rv"><caption>%s</caption><thead><tr><th scope="col">%s</th><th scope="col">%s</th></tr></thead><tbody>%s</tbody></table>' % (T(cap), T("Produto"), T("Preço"), r)
    cmp_ = """<div class="pcmp">
      <div class="plan rv"><h3>%s</h3><div class="price">%s<small>MT</small></div><p class="note">%s</p></div>
      <div class="plan rv"><h3>%s</h3><div class="price">%s<small>MT</small></div><p class="note">%s</p></div>
      <div class="plan rv"><h3>%s</h3><div class="price">%s<small>MT</small></div><p class="note">%s</p></div>
      <div class="plan best rv"><span class="tag">%s</span><h3>%s</h3><div class="price">%s<small>MT</small></div><p class="note">%s</p></div></div>""" % (
        T("Mensal"), N("2.990"), T("Todos os ginásios"), T("Trimestral"), N("8.490"), T("3 meses"), T("Semestral"), N("14.990"), T("1 mês grátis"),
        T("Melhor valor"), T("Anual"), N("24.990"), T("3,6 meses grátis"))
    t = table("Membro normal", [("Membro normal (mensal)", None, "2.990"), ("Trimestral", None, "8.490"), ("Semestral", "1 mês grátis", "14.990"), ("Anual", "3,6 meses grátis", "24.990")], hl=(3,))
    t += table("Outros tipos de membro", [("Família", "pais e filhos", "2.690"), ("Estudantes, 1 ginásio", "até 21 anos", "1.500"),
          ("Estudantes, todos os ginásios", "até 21 anos", "1.790"), ("Sénior", "65+ anos", "1.990"),
          ("Duas semanas", None, "1.990"), ("Semanal", None, "1.490"), ("Fins de semana", None, "1.990")])
    t += table("Entradas diárias", [("Entrada", None, "500"), ("10 entradas", None, "4.500")])
    t += table("Inscrição", [("Membro do Pro Gym (anuidade)", None, "900"), ("Cartão", None, "500"), ("Chaveiro", None, "700")])
    body = page_hero(root, [(T("Início"), ""), (T("Preços"), None)], T("Preços"), T("Estes preços aplicam-se a todos os membros do Pro Gym."), "hero/hero-2.jpg", T("Sala de treino do Pro Gym")) + """
<section class="tight"><div class="wrap">%s%s
<p class="fineprint rv">%s</p>
<div class="actions rv" style="margin-top:1.6rem"><a class="btn" href="%s#marcar">%s</a><a class="btn dark" href="https://wa.me/%s" target="_blank" rel="noopener">%s</a></div>
</div></section>""" % (cmp_, t, T("Poupança do plano anual: 12 mensalidades custariam 35.880 MT. Com o plano anual pagas 24.990 MT e poupas 10.890 MT, cerca de 3,6 meses."),
                       root, T("Marcar sessão grátis"), WA, T("Perguntar pelo WhatsApp"))
    body += promo_block(root)
    write("pricing", layout("pricing/", T("Preços | Pro Gym Fitness"), T("Preços do Pro Gym: mensalidade 2.990 MT, trimestral, semestral e anual, planos de estudante, família e sénior, entradas diárias e inscrição."), body))
    PAGES.append(("pricing/", True))

# ---------------- AULAS ----------------
def classes():
    root = "../"
    cards = """<div class="cls-grid">
    <div class="cls"><div class="pw">%s</div><div class="tx"><h3>Spinn 50</h3><p>%s</p></div></div>
    <div class="cls"><div class="pw">%s</div><div class="tx"><h3>%s</h3><p>%s</p></div></div>
    <div class="cls"><div class="pw">%s</div><div class="tx"><h3>CrossTrain</h3><p>%s</p></div></div></div>""" % (
        pic(root, "classes/spinn.jpg", T("Aula de Spinn 50"), "(min-width:900px) 58vw, 100vw"), T("Treino de ciclismo indoor de alta intensidade para melhorar a resistência e queimar calorias."),
        pic(root, "classes/aerobics.jpg", T("Aula de aeróbica"), "(min-width:900px) 40vw, 100vw"), T("Aeróbica"), T("Treino aeróbico rítmico com movimentos dinâmicos para aumentar a resistência física."),
        pic(root, "classes/crosstrain.jpg", T("Aula de CrossTrain"), "(min-width:900px) 75vw, 100vw"), T("Treino funcional de corpo inteiro que desenvolve força, agilidade e condicionamento físico."))
    others = ["Zumba", "Spinning", "Tabata", "Step", "Core", "Flow", "Body Strength", "Max Glutes", "Bootcamp", "Spinn 4x4", "Strong Z"]
    chips = '<div class="chips rv">%s</div>' % "".join('<span class="tagc">%s</span>' % e(o) for o in others)
    tabs = "".join('<a role="tab" href="#%s" aria-selected="false">%s</a>' % (g["slug"], e(g["name"])) for g in GYMS)
    tts = ""
    for g in GYMS:
        if g["plan"]:
            w, h, _ = variants(g["plan"])
            tts += """<div class="tp tt" id="%(s)s" role="tabpanel"><h3 class="t-only">%(n)s</h3><a class="imglink" href="%(a)s%(i)s%(p)s" target="_blank" rel="noopener" aria-label="%(al)s"><img loading="lazy" decoding="async" src="%(a)s%(i)s%(p)s" width="%(w)d" height="%(h)d" alt="%(alt)s"></a><p class="cap">%(cap)s</p></div>""" % dict(
                s=g["slug"], n=e(g["name"]), a=A(root), i=IMG, p=g["plan"], w=w, h=h, al=e(F("Abrir o horário do Pro Gym %s em tamanho real", g["name"])),
                alt=e(F("Horário das aulas do Pro Gym %s", g["name"])), cap=T("Toca na imagem para abrir em tamanho real.") + TIMETABLE_NOTE())
        else:
            tts += '<div class="tp tt" id="%s" role="tabpanel"><h3 class="t-only">%s</h3><p class="sub">%s</p><p style="margin-top:1rem"><a class="btn dark" href="%s" target="_blank" rel="noopener">%s</a></p></div>' % (
                g["slug"], e(g["name"]), T("Pergunta o horário das aulas na receção ou pelo WhatsApp."), wa("Olá! Gostaria de saber o horário das aulas no Pro Gym Zimpeto."), T("Pedir horário"))
    body = page_hero(root, [(T("Início"), ""), (T("Aulas"), None)], T("Aulas"), T("Aulas de grupo com instrutor nos ginásios Pro Gym."), "services/aulas.jpg", T("Aula de grupo no Pro Gym")) + """
<section class="tight"><div class="wrap"><h2 class="sp">%s</h2>%s<p class="sub rv" style="margin-top:2.2rem">%s</p>%s</div></section>
<section class="paper tight"><div class="wrap" data-tabs><h2 class="sp">%s</h2><div class="tablist" role="tablist" aria-label="%s">%s</div>%s</div></section>%s""" % (
        sp(T("As nossas aulas")), cards, T("Também aparecem nos horários:"), chips, sp(T("Horários por ginásio")), T("Ginásio"), tabs, tts, booking_section(root))
    write("plans", layout("plans/", T("Aulas de grupo | Pro Gym Fitness"), T("Aeróbica, Spinn 50, CrossTrain, Zumba e mais. Consulta os horários das aulas nos ginásios Pro Gym Marés, Matola e Alto Maé."), body, og_img="services/aulas.jpg"))
    PAGES.append(("plans/", True))

# ---------------- SERVIÇOS ----------------
def services():
    root = "../"
    rows = [("personal-training/", "Personal trainer", "Treino com acompanhamento individual.", "services/personal-trainer.jpg"),
            ("physiotherapy/", "Fisioterapia", "Recupera de lesões e treina com segurança.", "services/fisoterapia.jpg"),
            ("nutrition/", "Nutrição", "Orientação alimentar para o teu objetivo.", "services/nutricao.jpg")]
    lis = "".join('<li class="rv"><a href="%s"><h3>%s</h3><p>%s</p><span class="go">%s</span><span class="thumb">%s</span></a></li>' % (h, T(n), T(p), T("Saber mais"), pic(root, i, "", "170px")) for h, n, p, i in rows)
    arena = """<section class="dark-sec tight" id="arena"><div class="wrap"><h2 class="sp">%s</h2>
<p class="sub rv">%s</p>
<div class="photos" style="grid-template-columns:repeat(3,1fr)">
<div style="grid-column:span 1">%s<p class="sub" style="margin-top:.6rem">Padel</p></div>
<div style="grid-column:span 1;margin-top:3rem">%s<p class="sub" style="margin-top:.6rem">%s</p></div>
<div style="grid-column:span 1">%s<p class="sub" style="margin-top:.6rem">Futsal</p></div></div>
<p class="soonline rv" style="margin-top:2rem"><span class="soon">%s</span>%s</p>
<div class="actions rv" style="margin-top:2rem"><a class="btn" href="../arena/">%s</a><a class="btn ghost" href="%s" target="_blank" rel="noopener">%s</a></div></div></section>""" % (
        sp(T("A arena do Pro Gym Matola")), T("Mesmo à frente do ginásio, no Parque dos Poetas, na Matola: campos de padel, basquetebol e futsal, mini golfe, parque infantil e a única área de treino calisténico ao ar livre em Moçambique."),
        mask(root, "services/padel.jpg", T("Campo de padel na arena do Pro Gym Matola"), "33vw", True, ' style="aspect-ratio:3/4"'),
        mask(root, "services/mini-golf.jpg", T("Mini golfe na arena do Pro Gym Matola"), "33vw", True, ' style="aspect-ratio:3/4"'), T("Mini golf"),
        mask(root, "services/futsal.jpg", T("Campo de futsal na arena do Pro Gym Matola"), "33vw", True, ' style="aspect-ratio:3/4"'),
        T("Brevemente"), T("A arena vai estar disponível também noutros ginásios Pro Gym."), T("Ver a página da arena"), wa("Olá! Gostaria de reservar um campo na arena do Pro Gym Matola."), T("Reservar campo pelo WhatsApp"))
    body = page_hero(root, [(T("Início"), ""), (T("Serviços"), None)], T("Serviços"), T("Mais do que sala de musculação."), "services/personal-trainer.jpg", T("Personal trainer no Pro Gym")) + '<section class="tight"><div class="wrap"><ul class="srows" style="margin-top:0">%s</ul></div></section>%s' % (lis, arena)
    write("services", layout("services/", T("Serviços | Pro Gym Fitness"), T("Personal trainer, fisioterapia e nutrição, e a arena desportiva do Pro Gym Matola com padel, futsal e mini golfe."), body, og_img="services/personal-trainer.jpg"))
    PAGES.append(("services/", True))
    subs = [("personal-training", "Personal trainer", "services/personal-trainer.jpg", "Treino com acompanhamento individual de um personal trainer do Pro Gym, ajustado ao teu objetivo.", "Olá! Gostaria de marcar um treino com um personal trainer no Pro Gym."),
            ("physiotherapy", "Fisioterapia", "services/fisoterapia.jpg", "Fisioterapia no Pro Gym para recuperares de lesões e voltares a treinar com segurança.", "Olá! Gostaria de marcar fisioterapia no Pro Gym."),
            ("nutrition", "Nutrição", "services/nutricao.jpg", "Orientação nutricional no Pro Gym para te ajudar a atingir o teu objetivo.", "Olá! Gostaria de marcar uma consulta de nutrição no Pro Gym.")]
    for slug, name, img, txt, msg in subs:
        path = "services/%s/" % slug
        r = "../../"
        n = T(name)
        b = page_hero(r, [(T("Início"), ""), (T("Serviços"), "services/"), (n, None)], n, None, img, F("%s no Pro Gym", n)) + """
<section class="tight"><div class="wrap info"><div><h2 class="sp">%s</h2><p class="sub rv" style="color:var(--ink2)">%s</p>
<p class="sub rv" style="color:var(--ink2)">%s</p>
<div class="actions rv" style="margin-top:1.6rem"><a class="btn" href="%s" target="_blank" rel="noopener">%s</a><a class="btn dark" href="%scontact/">%s</a></div></div>
%s</div></section>""" % (sp(F("%s no Pro Gym", n)), e(T(txt)), T("Fala connosco para saberes os valores e marcares. Responde-te a receção da tua unidade."), wa(msg), T("Marcar pelo WhatsApp"), r, T("Ver contactos"),
                          mask(r, img, F("%s no Pro Gym", n), "(min-width:860px) 35vw, 100vw", True, ' style="aspect-ratio:4/5"'))
        write(path.rstrip("/"), layout(path, "%s | Pro Gym Fitness" % n, T(txt) + " " + T("Marca pelo WhatsApp."), b, og_img=img))
        PAGES.append((path, True))

# ---------------- ARENA (Matola) ----------------
# O que existe hoje na arena. Para mudar, editar aqui (nome, foto ou None) e correr build.py.
ARENA = [("Padel", "services/padel.jpg", "Campo de padel na arena do Pro Gym Matola"),
         ("Mini golf", "services/mini-golf.jpg", "Mini golfe na arena do Pro Gym Matola"),
         ("Futsal", "services/futsal.jpg", "Campo de futsal na arena do Pro Gym Matola"),
         ("Basquetebol", None, None), ("Parque infantil", None, None), ("Treino calisténico ao ar livre", None, None)]

def arena():
    root = "../"
    g = [x for x in GYMS if x["slug"] == "matola"][0]
    shots = "".join('<div>%s<p class="sub" style="margin-top:.6rem">%s</p></div>' % (
        mask(root, img, T(alt), "(min-width:900px) 33vw, 100vw", True, ' style="aspect-ratio:3/4"'), T(n)) for n, img, alt in ARENA if img)
    chips = "".join('<span class="tagc">%s</span>' % T(n) for n, img, alt in ARENA if not img)
    body = page_hero(root, [(T("Início"), ""), (T("Arena do Pro Gym Matola"), None)], T("Arena do Pro Gym Matola"), T("Desporto e lazer para toda a família, no Parque dos Poetas."), g["cover"], cover_alt(g)) + """
<section class="tight"><div class="wrap info">
  <div><h2 class="sp">%(h2)s</h2><p class="sub rv" style="color:var(--ink2)">%(d)s</p>
  <div class="actions rv" style="margin-top:1.6rem"><a class="btn wa" href="%(wa)s" target="_blank" rel="noopener">%(b1)s</a><a class="btn dark" href="%(map)s" target="_blank" rel="noopener">%(b2)s</a></div></div>
  <dl class="facts rv">
    <div><dt>%(t1)s</dt><dd>%(addr)s</dd></div>
    <div><dt>%(t2)s</dt><dd><a href="%(tl)s">%(tel)s</a></dd></div>
    <div><dt>WhatsApp</dt><dd><a href="https://wa.me/%(waid)s" target="_blank" rel="noopener">%(atel)s</a></dd></div>
  </dl>
</div></section>
<section class="paper tight"><div class="wrap"><h2 class="sp">%(h3)s</h2>
  <div class="photos" style="grid-template-columns:repeat(3,1fr)">%(shots)s</div>
  <div class="chips rv" style="margin-top:2rem">%(chips)s</div>
  <p class="soonline rv"><span class="soon">%(soon)s</span>%(more)s</p>
  <p class="fineprint rv">%(note)s</p></div></section>
<section class="tight"><div class="wrap"><h2 class="sp">%(h4)s</h2>
  <p class="sub rv">%(s4)s</p>
  <div class="actions rv" style="margin-top:1.6rem"><a class="btn wa" href="%(wa)s" target="_blank" rel="noopener">%(b1)s</a><a class="btn dark" href="%(gym)sgyms/matola/">%(b3)s</a></div></div></section>
""" % dict(h2=sp(T("Mesmo à frente do ginásio")), d=e(T("Mesmo à frente do ginásio, no Parque dos Poetas, na Matola: campos de padel, basquetebol e futsal, mini golfe, parque infantil e a única área de treino calisténico ao ar livre em Moçambique.")),
           wa=wa("Olá! Gostaria de reservar um campo na arena do Pro Gym Matola."), b1=T("Reservar campo pelo WhatsApp"), map=maps("Pro Gym Matola, " + g["addr"]), b2=T("Como chegar"),
           t1=T("Morada"), addr=e(TP(g["addr"])), t2=T("Telefone"), tl=tel(g["tel"]), tel=g["tel"], waid=WA, atel=ADMIN_TEL,
           soon=T("Brevemente"), more=T("A arena vai estar disponível também noutros ginásios Pro Gym."), h3=sp(T("O que podes fazer na arena")), shots=shots, chips=chips, note=T("Confirma na receção ou pelo WhatsApp que modalidades estão disponíveis."),
           h4=sp(T("Reservar um campo")), s4=T("Fala connosco pelo WhatsApp para saberes a disponibilidade e os valores."), gym=root, b3=T("Ver o Pro Gym Matola"))
    write("arena", layout("arena/", T("Arena do Pro Gym Matola | Padel, futsal e mini golfe"), T("A arena desportiva do Pro Gym Matola, no Parque dos Poetas: padel, basquetebol, futsal, mini golfe, parque infantil e treino calisténico ao ar livre."), body, og_img=g["cover"]))
    PAGES.append(("arena/", True))

# ---------------- LOJA ----------------
def store():
    root = "../"
    prods = [("Hardcore Whey Protein", "Suplementos", "4.500", "store/hardcore-whey.webp"), ("USN Shaker", "Acessórios", "2.100", "store/shaker.jpg"), ("Creatina", "Suplementos", "2.700", "store/creatine-3-in-1.webp")]
    cards = "".join("""<article class="prod rv"><div class="ph">%s</div><div class="tx"><span class="cat">%s</span><h3>%s</h3><div class="pr">%s MT</div><a class="btn small" data-wa="%s" href="%s" target="_blank" rel="noopener">%s</a></div></article>""" % (
        pic(root, img, TP(n), "(min-width:900px) 30vw, 100vw"), T(c), e(TP(n)), N(p),
        e(wamsg("Olá! Gostaria de encomendar: %s (%s MT).", n, p, en=(TP(n), N(p)))), wa("Olá! Gostaria de encomendar: %s (%s MT).", n, p, en=(TP(n), N(p))), T("Encomendar pelo WhatsApp")) for n, c, p, img in prods)
    body = page_hero(root, [(T("Início"), ""), (T("Loja"), None)], T("Loja"), T("Suplementos e acessórios para potencializares os teus resultados."), "store.jpg", T("Suplementos e acessórios na loja do Pro Gym")) + """
<section class="tight"><div class="wrap"><div class="products">%s</div>
<ol class="steps"><li class="rv"><b>%s</b>%s</li><li class="rv"><b>%s</b>%s</li><li class="rv"><b>%s</b>%s</li></ol></div></section>""" % (
        cards, T("Escolhe o produto"), T("Toca em encomendar no produto que queres."), T("Envia pelo WhatsApp"), T("A mensagem segue já escrita para a receção."),
        T("Confirmamos contigo"), T("A receção confirma a disponibilidade e como levantar."))
    write("store", layout("store/", T("Loja | Pro Gym Fitness"), T("Suplementos e acessórios Pro Gym: Hardcore Whey Protein, USN Shaker e Creatina. Encomenda pelo WhatsApp."), body, og_img="store.jpg"))
    PAGES.append(("store/", True))

# ---------------- CONTACTO ----------------
def contact():
    root = "../"
    tabs = "".join('<a role="tab" href="#u-%s" aria-selected="false">%s</a>' % (g["slug"], e(g["name"])) for g in GYMS)
    panels = "".join("""<div class="tp cpanel" id="u-%(s)s" role="tabpanel"><div><h3>Pro Gym %(n)s</h3><address>%(a)s</address>
<a class="big-tel ul" href="%(tl)s">%(t)s</a></div>
<div><p class="sub" style="margin-top:0">%(hs)s</p>
<div class="actions" style="margin-top:1.4rem"><a class="btn" href="%(map)s" target="_blank" rel="noopener">%(b1)s</a><a class="btn dark" href="%(wa)s" target="_blank" rel="noopener">WhatsApp</a><a class="btn dark" href="../gyms/%(s)s/">%(b2)s</a></div></div></div>""" % dict(
        s=g["slug"], n=e(g["name"]), a=e(TP(g["addr"])), tl=tel(g["tel"]), t=g["tel"], map=maps("Pro Gym " + g["name"] + ", " + g["addr"]), wa=wa("Olá! Escrevo sobre o Pro Gym %s.", g["name"]),
        hs=T("Horário: segunda a sexta 05:00 às 22:00, sábado 06:00 às 18:00, domingo e feriados 06:00 às 13:00."), b1=T("Como chegar"), b2=T("Ver ginásio")) for g in GYMS)
    body = page_hero(root, [(T("Início"), ""), (T("Contacto"), None)], T("Contacto"), T("Fala com a administração ou com a tua unidade."), "hero/hero-2.jpg", T("Sala de treino do Pro Gym")) + """
<section class="tight"><div class="wrap" data-tabs><h2 class="sp">%(h1)s</h2><div class="tablist" role="tablist" aria-label="%(gl)s">%(tabs)s</div>%(panels)s</div></section>
<section class="paper tight"><div class="wrap info">
<div><h2 class="sp">%(h2)s</h2>
<form class="f rv" id="contactForm" style="margin-top:1.4rem" novalidate>
<label>%(ln)s<input id="cName" autocomplete="name" placeholder="%(phn)s" required></label>
<label>%(lm)s<textarea id="cMsg" placeholder="%(phm)s" required></textarea></label>
<div class="err" id="cErr" role="alert"></div><button class="btn" type="submit">%(sb)s</button>
<p class="fine">%(fine)s</p></form></div>
<dl class="facts rv"><div><dt>%(adm)s</dt><dd><a href="tel:+258844414441">%(t)s</a></dd></div>
<div><dt>Email</dt><dd><a href="mailto:%(em)s">%(em)s</a></dd></div>
<div><dt>%(soc)s</dt><dd><a href="%(fb)s" target="_blank" rel="noopener">Facebook</a><br><a href="%(ig)s" target="_blank" rel="noopener">Instagram</a><br><a href="%(li)s" target="_blank" rel="noopener">LinkedIn</a></dd></div></dl></div></section>""" % dict(
        h1=sp(T("Escolhe o ginásio")), gl=T("Ginásio"), tabs=tabs, panels=panels, h2=sp(T("Escreve-nos")), ln=T("Nome"), phn=T("O teu nome"), lm=T("Mensagem"), phm=T("Em que podemos ajudar?"),
        sb=T("Enviar pelo WhatsApp"), fine=F("Abre o WhatsApp com a mensagem pronta. Também podes escrever para %s.", EMAIL), adm=T("Administração"), soc=T("Redes sociais"),
        em=EMAIL, t=ADMIN_TEL, fb=FB, ig=IG, li=LI)
    write("contact", layout("contact/", T("Contacto | Pro Gym Fitness"), T("Contactos do Pro Gym: administração, email, WhatsApp e morada de cada ginásio em Maputo e Matola."), body))
    PAGES.append(("contact/", True))

# ---------------- EVENTOS ----------------
def gallery():
    root = "../"
    body = page_hero(root, [(T("Início"), ""), (T("Eventos"), None)], T("Eventos"), T("Novidades, aulas especiais e eventos nos ginásios Pro Gym."), "hero/hero-2.jpg", T("Sala de treino do Pro Gym")) + """
<section class="tight"><div class="wrap"><h2 class="sp">%s</h2><p class="sub rv">%s</p>
<div class="actions rv" style="margin-top:1.6rem"><a class="btn" href="%s" target="_blank" rel="noopener">Instagram</a><a class="btn dark" href="%s" target="_blank" rel="noopener">Facebook</a></div></div></section>""" % (
        sp(T("Acompanha-nos nas redes")), T("Publicamos os eventos e as fotos nas nossas redes sociais."), IG, FB)
    write("gallery", layout("gallery/", T("Eventos | Pro Gym Fitness"), T("Eventos e novidades do Pro Gym. Acompanha no Instagram e Facebook."), body, noindex=True))
    PAGES.append(("gallery/", False))

# ---------------- APP ----------------
def app():
    root = "../"
    units = "".join("<option>%s</option>" % g["name"] for g in GYMS)
    feats = "".join("<li>%s</li>" % T(x) for x in [
        "Regista cargas, plano de treino, exercícios, dias de ginásio, cardio e peso corporal.", "Sequências de dias e desafios diários.",
        "Ranking de força entre amigos do mesmo ginásio.", "Feed privado do grupo e notificações para se motivarem.", "Relatório mensal e imagem pronta para partilhar no Instagram."])
    body = page_hero(root, [(T("Início"), ""), (T("App"), None)], T("A app do Pro Gym"), T("Para membros: o teu treino e os teus amigos do ginásio, no telemóvel."), "hero/hero-2.jpg", T("Sala de treino do Pro Gym")) + """
<section class="dark-sec"><div class="wrap app-grid">
<div><span class="soon rv">%s</span><h2 class="sp">%s</h2>
<p class="sub rv">%s</p>
<ul class="feat rv">%s</ul>
<p class="demo-note rv">%s</p></div>
%s</div></section>
<section class="orange-sec"><div class="wrap book"><div><h2 class="sp">%s</h2><p class="sub rv" style="color:var(--iron)">%s</p></div>
<form class="f rv" id="waitForm" novalidate><label>%s<input id="wName" autocomplete="name" placeholder="%s" required></label>
<label>%s<select id="wUnit">%s</select></label><div class="err" id="wErr" role="alert"></div>
<button class="btn" type="submit">%s</button><p class="fine">%s</p></form></div></section>""" % (
        T("Brevemente"), sp(T("O teu treino, no telemóvel")),
        T("Uma app para os membros do Pro Gym registarem o progresso e treinarem em conjunto. A app ainda não está disponível. O cartão de acesso e as mensalidades continuam como hoje."),
        feats, T("Pré-visualização com dados de exemplo. Experimenta: troca o ranking e marca o desafio do dia."), phone_demo(),
        sp(T("Quero ser dos primeiros")), T("Diz-nos o teu nome e o teu ginásio. Avisamos-te quando a app estiver disponível."),
        T("Nome"), T("O teu nome"), T("Treino no Pro Gym"), units, T("Enviar pelo WhatsApp"), T("Abre o WhatsApp com a mensagem pronta. Este site não guarda os teus dados."))
    write("app", layout("app/", T("App Pro Gym | Brevemente"), T("A app para os membros do Pro Gym: regista o treino, acompanha o progresso e compete com os amigos do teu ginásio. Brevemente."), body))
    PAGES.append(("app/", True))

# ---------------- 404 / sitemap / robots ----------------
def extras(pages_pt):
    nf = """<!DOCTYPE html><html lang="pt" class="t-uxpro"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Página não encontrada | Page not found | Pro Gym</title><meta name="robots" content="noindex">
<link rel="stylesheet" href="/assets/css/style.css"><link rel="stylesheet" href="/assets/css/ux-pro.css"></head>
<body><div class="notfound"><div><h1>404</h1><p style="font-size:1.2rem;margin:1rem 0 .4rem">Esta página não existe ou mudou de sítio.</p><p style="font-size:1.05rem;margin:0 0 2rem;opacity:.8">This page doesn't exist or has moved.</p><a class="btn" href="/">Voltar ao início</a> <a class="btn dark" href="/en/">Back to home</a></div></div></body></html>"""
    open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(nf)
    def u(p, pfx): return "%s/%s%s" % (SITE_URL, pfx, p)
    urls = ""
    for p, ok in pages_pt:
        if not ok: continue
        alts = "".join('<xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (l, u(p, x)) for l, x in (("pt", ""), ("en", "en/"))) + '<xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % u(p, "")
        for pfx in ("", "en/"):
            urls += "<url><loc>%s</loc>%s</url>\n" % (u(p, pfx), alts)
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n%s</urlset>\n' % urls)
    open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % SITE_URL)
    open(os.path.join(OUT, ".nojekyll"), "w").write("")

if __name__ == "__main__":
    pt_pages = []
    for lang in ("pt", "en"):
        LANG = lang
        PAGES[:] = []
        home(); gyms(); pricing(); classes(); services(); arena(); store(); contact(); gallery(); app()
        if lang == "pt": pt_pages = list(PAGES)
        print(lang.upper(), len(PAGES), "páginas")
    extras(pt_pages)
    if MISSING:
        print("\nFALTAM %d TRADUÇÕES em i18n.py:" % len(MISSING))
        for m in sorted(MISSING): print("  -", repr(m))
        sys.exit(1)
    print("OK ->", OUT)

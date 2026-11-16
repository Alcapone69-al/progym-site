#!/usr/bin/env python3
"""Gera o site Pro Gym (HTML estático) na própria pasta do repositório.
Requisitos: Python 3 e Pillow (pip install pillow).
Correr: python3 build.py   (regenera todas as páginas, sitemap e versões reduzidas das imagens)"""
import os, json, html, urllib.parse, datetime
from PIL import Image

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

HOURS = [("Segunda a sexta", "05:00 às 22:00"), ("Sábado", "06:00 às 18:00"),
         ("Domingo", "06:00 às 13:00"), ("Feriados", "06:00 às 13:00")]

GYMS = [
 dict(slug="mares", name="Marés", area="Costa do Sol, Maputo",
  tel="+258 85 550 5550",
  addr="Centro Comercial Marés, Av. da Marginal, Maputo nº 9519, 1100 Maputo, Moçambique",
  desc="Localizado no coração do Centro Comercial Marés, em Costa do Sol, o Pro Gym Marés é o seu espaço de fitness familiar onde resultados, saúde e diversão se encontram. Aproveite equipamentos modernos, treinadores profissionais e uma comunidade acolhedora – tudo a poucos passos das suas lojas e restaurantes favoritos.",
  cover="gyms/mares/drone.jpg", photos=["drone","side","door","store","mares-3","cardio"], plan="plans/plano-mares.jpg"),
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
       "cardio": "zona de cardio", "reception": "receção", "spinning": "sala de spinning", "crossfit": "área de CrossFit"}

def e(s): return html.escape(s, quote=True)
def tel(s): return "tel:" + s.replace(" ", "")
def wa(msg): return "https://wa.me/%s?text=%s" % (WA, urllib.parse.quote(msg))
def maps(q): return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(q)

ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="square" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg>'

# ---------- imagens: dimensões explícitas + versões reduzidas (srcset) ----------
_cache = {}
def variants(rel):
    if rel in _cache: return _cache[rel]
    src = os.path.join(OUT, IMG, rel)
    w, h = Image.open(src).size
    vs = []
    if rel.lower().endswith((".jpg", ".jpeg")) and w >= 1300:
        base = rel.rsplit(".", 1)[0].replace("/", "_")
        for tw in (640, 1100):
            out = "_s/%s-%d.jpg" % (base, tw)
            p = os.path.join(OUT, IMG, out)
            if not os.path.exists(p):
                os.makedirs(os.path.dirname(p), exist_ok=True)
                im = Image.open(src).convert("RGB")
                im.resize((tw, round(h * tw / w)), Image.LANCZOS).save(p, "JPEG", quality=78, optimize=True, progressive=True)
            vs.append((out, tw))
    _cache[rel] = (w, h, vs)
    return _cache[rel]

def pic(root, rel, alt, sizes="100vw", eager=False, cls=""):
    w, h, vs = variants(rel)
    src = root + IMG + rel
    srcset = ""
    if vs:
        srcset = ' srcset="%s" sizes="%s"' % (", ".join(["%s%s%s %dw" % (root, IMG, o, tw) for o, tw in vs] + ["%s %dw" % (src, w)]), sizes)
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

PAGES = []  # (path, indexable)

def layout(path, title, desc, body, jsonld=None, og_img="hero/hero-2.jpg", noindex=False, preload=None):
    depth = path.count("/")
    root = "../" * depth
    nav = []
    for label, href, sub in NAV:
        active = ' aria-current="page"' if (path == href or (sub and path.startswith("gyms/")) or (href != "gyms/" and path.startswith(href))) else ""
        if sub:
            items = "".join('<li><a href="%s%s">%s</a></li>' % (root, h, e(n)) for n, h in sub)
            nav.append('<li class="sub-nav"><a href="%s%s"%s>%s</a><ul class="drop">%s</ul></li>' % (root, href, active, label, items))
        else:
            nav.append('<li><a href="%s%s"%s>%s</a></li>' % (root, href, active, label))
    canon = SITE_URL + "/" + path
    ld = '<script type="application/ld+json">%s</script>' % json.dumps(jsonld, ensure_ascii=False) if jsonld else ""
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    pre = ""
    if preload:
        pre = '<link rel="preload" as="image" href="%s%s%s" fetchpriority="high">' % (root, IMG, preload) if isinstance(preload, str) else ""
    return """<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
%(robots)s
<link rel="canonical" href="%(canon)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:type" content="website">
<meta property="og:url" content="%(canon)s">
<meta property="og:image" content="%(site)s/%(img)s%(og)s">
<meta property="og:locale" content="pt_MZ">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0A0A0A">
<link rel="icon" href="data:image/svg+xml,%%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%%3E%%3Crect width='64' height='64' rx='10' fill='%%230A0A0A'/%%3E%%3Ctext x='32' y='44' font-size='34' font-weight='900' text-anchor='middle' fill='%%23F97316' font-family='Arial Narrow,Arial'%%3EPG%%3C/text%%3E%%3C/svg%%3E">
<script>(function(){var r=document.documentElement;r.classList.add('js');if(!matchMedia('(prefers-reduced-motion: reduce)').matches){r.classList.add('motion');setTimeout(function(){if(!window.__pg)r.classList.remove('motion')},4500)}})();</script>
<link rel="preload" href="%(root)sassets/fonts/big-shoulders-display-latin-900-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="%(root)sassets/fonts/schibsted-grotesk-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
%(pre)s
<link rel="stylesheet" href="%(root)sassets/css/style.css">
%(ld)s
</head>
<body>
<a class="skip" href="#conteudo">Saltar para o conteúdo</a>
<div id="navbar" aria-hidden="true"></div>
<header class="top" id="top">
  <div class="wrap nav">
    <a class="logo" href="%(root)s" aria-label="Pro Gym Fitness, início"><img src="%(root)s%(img)slogo.png" alt="Pro Gym Fitness" width="177" height="38"></a>
    <button class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="mainNav">Menu</button>
    <nav id="mainNav" aria-label="Principal"><ul>%(nav)s</ul></nav>
    <a class="btn small" href="%(root)s#marcar">Sessão grátis</a>
  </div>
</header>
<main id="conteudo">
%(body)s
</main>
%(footer)s
<a class="wa-float" href="https://wa.me/%(wa)s" target="_blank" rel="noopener" aria-label="Falar connosco no WhatsApp">WhatsApp</a>
<script src="%(root)sassets/js/vendor/gsap.min.js" defer></script>
<script src="%(root)sassets/js/vendor/ScrollTrigger.min.js" defer></script>
<script src="%(root)sassets/js/site.js" defer></script>
</body>
</html>
""" % dict(title=e(title), desc=e(desc), robots=robots, canon=canon, site=SITE_URL, img=IMG, og=og_img, root=root, pre=pre,
           ld=ld, nav="".join(nav), body=body, footer=footer(root), wa=WA)

def footer(root):
    g = "".join('<li><a href="%sgyms/%s/">%s</a></li>' % (root, x["slug"], x["name"]) for x in GYMS)
    return """<footer>
  <div class="wrap">
    <div class="foot">
      <div><img src="%(root)s%(img)slogo.png" alt="Pro Gym Fitness" width="205" height="44" loading="lazy"><p>Ginásios em Maputo e Matola.<br>Best Price | Best Quality</p></div>
      <div><h3>Ginásios</h3><ul>%(g)s</ul></div>
      <div><h3>Explorar</h3><ul>
        <li><a href="%(root)spricing/">Preços</a></li><li><a href="%(root)splans/">Aulas</a></li>
        <li><a href="%(root)sservices/">Serviços</a></li><li><a href="%(root)sapp/">App Pro Gym</a></li>
        <li><a href="%(root)sstore/">Loja</a></li><li><a href="%(root)sgallery/">Eventos</a></li></ul></div>
      <div><h3>Contactos</h3><ul>
        <li><a href="tel:+258844414441">%(tel)s</a></li>
        <li><a href="https://wa.me/%(wa)s" target="_blank" rel="noopener">WhatsApp</a></li>
        <li><a href="mailto:%(em)s">%(em)s</a></li>
        <li><a href="%(fb)s" target="_blank" rel="noopener">Facebook</a></li>
        <li><a href="%(ig)s" target="_blank" rel="noopener">Instagram</a></li>
        <li><a href="%(li)s" target="_blank" rel="noopener">LinkedIn</a></li></ul></div>
    </div>
    <div class="mark" aria-hidden="true">Pro Gym</div>
    <div class="legal"><span>© %(y)d Pro Gym Fitness, Lda. Todos os direitos reservados.</span><span>Website por YFX</span></div>
  </div>
</footer>""" % dict(root=root, img=IMG, g=g, tel=ADMIN_TEL, wa=WA, em=EMAIL, fb=FB, ig=IG, li=LI, y=YEAR)

def write(path, content):
    full = os.path.join(OUT, path, "index.html") if path else os.path.join(OUT, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f: f.write(content)

def page_hero(root, crumbs, h1, lead, bg, alt):
    cr = " / ".join('<a href="%s%s">%s</a>' % (root, h, e(n)) if h is not None else '<span aria-current="page">%s</span>' % e(n) for n, h in crumbs)
    return """<section class="phero"><div class="phero-media">%s</div><div class="phero-in"><nav class="crumbs hr" aria-label="Localização">%s</nav><h1 class="sp" data-hero aria-label="%s">%s</h1>%s</div></section>""" % (
        pic(root, bg, alt, "100vw", eager=True), cr, e(h1), sp(h1), ('<p class="lead hr">%s</p>' % e(lead)) if lead else "")

def hours_list():
    return '<ul class="hours">%s</ul>' % "".join("<li><span>%s</span><strong>%s</strong></li>" % (a, b) for a, b in HOURS)

def booking_section(root, preset=None):
    opts = "".join('<option%s>%s</option>' % (" selected" if preset == g["name"] else "", g["name"]) for g in GYMS)
    return """<section class="orange-sec" id="marcar"><div class="wrap book">
  <div><h2 class="sp">%s</h2><p class="sub rv" style="color:var(--iron)">Escolhe o ginásio e o dia. A mensagem segue pelo WhatsApp para a receção e confirmamos contigo.</p></div>
  <form class="f rv" id="bookForm" novalidate>
    <label>Nome<input id="fName" autocomplete="name" placeholder="O teu nome" required></label>
    <div class="two"><label>Ginásio<select id="fUnit">%s</select></label><label>Dia<input id="fDate" type="date"></label></div>
    <label>Hora preferida<select id="fTime"><option>Manhã</option><option>Tarde</option><option>Noite</option></select></label>
    <div class="err" id="err" role="alert"></div>
    <button class="btn" type="submit">Enviar pelo WhatsApp</button>
    <p class="fine">Abre o WhatsApp com a mensagem pronta. Este site não guarda os teus dados.</p>
  </form></div></section>""" % (sp("A primeira sessão é grátis"), opts)

FAQ = [
 ("Qual é o horário?", "Segunda a sexta das 05:00 às 22:00, sábado das 06:00 às 18:00, domingo e feriados das 06:00 às 13:00."),
 ("Quanto custa a mensalidade?", "A mensalidade normal custa 2.990 MT. Há também planos trimestral (8.490 MT), semestral (14.990 MT, com 1 mês grátis) e anual (24.990 MT, com 3,6 meses grátis)."),
 ("Há preços para estudantes, famílias e seniores?", "Sim. Estudantes até 21 anos pagam 1.500 MT para 1 ginásio ou 1.790 MT para todos os ginásios. A família (pais e filhos) paga 2.690 MT e os seniores (65+) pagam 1.990 MT."),
 ("Posso treinar só um dia ou uma semana?", "Sim. A entrada diária custa 500 MT e um pack de 10 entradas custa 4.500 MT. Também há plano semanal (1.490 MT), de duas semanas (1.990 MT) e de fins de semana (1.990 MT)."),
 ("Quanto custa a inscrição?", "A tabela de preços indica a anuidade de membro (900 MT), o cartão (500 MT) e o chaveiro (700 MT)."),
 ("Como marco a primeira sessão grátis?", "Preenche o formulário desta página ou fala connosco pelo WhatsApp. A receção confirma o dia e a hora."),
]
def faq_section():
    d = "".join('<details name="faq"><summary>%s</summary><p>%s</p></details>' % (e(q), e(a)) for q, a in FAQ)
    return '<section class="paper" id="faq"><div class="wrap"><h2 class="sp">%s</h2><div class="faq rv">%s</div></div></section>' % (sp("Perguntas frequentes"), d)

def phone_demo(cap=False):
    c = '<p class="phone-cap">Pré-visualização com dados de exemplo.</p>' if cap else ""
    return """<div><div class="phone" role="group" aria-label="Pré-visualização da app Pro Gym, com dados de exemplo"><div class="screen">
  <div class="row"><div><div class="hi">Olá, Nelson</div><div class="loc">Pro Gym Matola</div></div><div class="loc">Hoje</div></div>
  <div class="streak"><div><div class="lbl">Sequência de treinos</div><b id="streakN">12</b> <span class="lbl">dias</span></div>
    <div class="week" aria-hidden="true"><i class="on" style="height:60%%"></i><i class="on" style="height:90%%"></i><i style="height:25%%"></i><i class="on" style="height:75%%"></i><i class="on" style="height:100%%"></i><i class="on" style="height:55%%"></i><i style="height:20%%"></i></div></div>
  <div class="seg" role="group" aria-label="Tipo de ranking"><button id="rkVisits" aria-pressed="true">Por visitas</button><button id="rkGoal" aria-pressed="false">Por %% da meta</button></div>
  <ol class="rank" id="rank"></ol>
  <div class="challenge" id="challenge"><div><div class="t">Desafio do dia: 25 flexões</div><div class="s" id="chS">Ainda por fazer</div></div><button id="chBtn">Fiz</button></div>
</div></div>%s</div>""" % c

def org_ld():
    return {"@context": "https://schema.org", "@type": "HealthClub", "name": "Pro Gym Fitness", "url": SITE_URL + "/",
            "telephone": "+258844414441", "email": EMAIL, "areaServed": ["Maputo", "Matola"],
            "sameAs": [FB, IG, LI], "logo": SITE_URL + "/" + IMG + "logo.png",
            "openingHoursSpecification": [
              {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "05:00", "closes": "22:00"},
              {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "06:00", "closes": "18:00"},
              {"@type": "OpeningHoursSpecification", "dayOfWeek": "Sunday", "opens": "06:00", "closes": "13:00"}]}

def gcard(g, root, href, sizes="60vw", cls="gh-card"):
    return """<a class="%s" href="%s"><div class="gh-img">%s</div>
      <div class="gh-tx"><h3>Pro Gym %s</h3><p class="area">%s</p><p class="tel">%s</p><span class="go">Ver ginásio %s</span></div></a>""" % (
        cls, href, pic(root, g["cover"], "Pro Gym %s, %s" % (g["name"], ALT.get(os.path.basename(g["cover"]).rsplit(".", 1)[0], "vista do ginásio")), sizes), e(g["name"]), e(g["area"]), g["tel"], ARROW)

# ---------------- HOME ----------------
def home():
    root = ""
    gcards = "".join(gcard(g, root, "gyms/%s/" % g["slug"], "(min-width:900px) 58vw, 100vw") for g in GYMS)
    body = """
<section class="hero" aria-label="Apresentação">
  <div class="hero-media">%(heroimg)s</div>
  <div class="hero-in">
    <div class="status hr" id="status" role="status"><span class="dot"></span><span id="statusText">A verificar o horário…</span></div>
    <h1 class="sp" data-hero aria-label="Treina onde te der mais jeito.">%(h1)s</h1>
    <div class="hero-foot">
      <div>
        <p class="lede">Quatro ginásios em Maputo e Matola, aulas de grupo, personal trainer, fisioterapia e nutrição. A primeira sessão é por nossa conta.</p>
        <div class="actions hr"><a class="btn" href="#marcar">Marcar sessão grátis %(arr)s</a><a class="btn ghost" href="pricing/">Ver preços</a></div>
      </div>
      <a class="cue hr" href="#historia" aria-label="Descer para o conteúdo"><i></i>Scroll</a>
    </div>
  </div>
  <i class="hero-bar" aria-hidden="true"></i>
</section>

<section class="stmt-sec" id="historia"><div class="wrap">
  <p class="stmt" aria-label="Quatro ginásios em Maputo e Matola. Aulas, personal trainer, fisioterapia e nutrição. A primeira sessão é por nossa conta.">%(stmt)s</p>
</div></section>

<section class="gyms-h" id="ginasios">
  <div class="gh-track">
    <div class="gh-intro"><h2 class="sp">%(gh2)s</h2><p class="sub rv">Marés, Alto Maé, Matola e Zimpeto, abertos de segunda a domingo.</p></div>
    %(gcards)s
  </div>
  <div class="gh-prog" aria-hidden="true"><i></i></div>
</section>

<section class="dark-sec" id="planos" data-sheet><div class="wrap">
  <h2 class="sp">%(p2)s</h2>
  <p class="sub rv">Há ainda planos trimestral e semestral, entradas diárias e semanais. Vê a tabela completa.</p>
  <div class="pgrid">
    <div class="plan big rv"><h3>Mensalidade</h3><div class="price">2.990<small>MT</small></div><p class="note">Todos os ginásios</p></div>
    <div class="plan best rv"><span class="tag">Melhor valor</span><h3>Anual</h3><div class="price">24.990<small>MT</small></div><p class="note">3,6 meses grátis. Poupas 10.890 MT.</p></div>
    <ul class="plist">
      <li class="rv"><span><b>Estudante</b><small>1 ginásio, até 21 anos</small></span><span class="pv">1.500<small> MT</small></span></li>
      <li class="rv"><span><b>Sénior</b><small>65+ anos</small></span><span class="pv">1.990<small> MT</small></span></li>
      <li class="rv"><span><b>Família</b><small>Pais e filhos</small></span><span class="pv">2.690<small> MT</small></span></li>
    </ul>
  </div>
  <div class="actions rv" style="margin-top:2.2rem"><a class="btn" href="pricing/">Ver todos os preços %(arr)s</a></div>
</div></section>

<section id="aulas"><div class="wrap">
  <h2 class="sp">%(a2)s</h2>
  <p class="sub rv">Aulas de grupo com instrutor, para quem treina melhor acompanhado.</p>
  <div class="cls-grid">
    <a class="cls" href="plans/"><div class="pw">%(i1)s</div><div class="tx"><h3>Spinn 50</h3><p>Ciclismo indoor de alta intensidade para melhorar a resistência e queimar calorias.</p></div></a>
    <a class="cls" href="plans/"><div class="pw">%(i2)s</div><div class="tx"><h3>Aeróbica</h3><p>Treino aeróbico rítmico com movimentos dinâmicos para aumentar a resistência física.</p></div></a>
    <a class="cls" href="plans/"><div class="pw">%(i3)s</div><div class="tx"><h3>CrossTrain</h3><p>Treino funcional de corpo inteiro que desenvolve força, agilidade e condicionamento.</p></div></a>
  </div>
  <div class="actions rv" style="margin-top:2.2rem"><a class="btn dark" href="plans/">Ver horários das aulas %(arr)s</a></div>
</div></section>

<section class="paper" id="servicos"><div class="wrap">
  <h2 class="sp">%(s2)s</h2>
  <ul class="srows">
    <li class="rv"><a href="services/personal-training/"><h3>Personal trainer</h3><p>Treino com acompanhamento individual.</p><span class="go">Saber mais</span><span class="thumb">%(t1)s</span></a></li>
    <li class="rv"><a href="services/physiotherapy/"><h3>Fisioterapia</h3><p>Recupera de lesões e treina com segurança.</p><span class="go">Saber mais</span><span class="thumb">%(t2)s</span></a></li>
    <li class="rv"><a href="services/nutrition/"><h3>Nutrição</h3><p>Orientação alimentar para o teu objetivo.</p><span class="go">Saber mais</span><span class="thumb">%(t3)s</span></a></li>
    <li class="rv"><a href="services/#arena"><h3>Padel, mini golf e futsal</h3><p>Desporto e lazer na arena do Pro Gym Matola.</p><span class="go">Saber mais</span><span class="thumb">%(t4)s</span></a></li>
  </ul>
</div></section>

<section class="dark-sec" id="app" data-sheet><div class="wrap app-grid">
  <div><span class="soon rv">Brevemente</span><h2 class="sp">%(ap)s</h2>
  <p class="sub rv">Regista o teu treino, acompanha o teu progresso e compete com os amigos do teu ginásio. O cartão de acesso e as mensalidades continuam como hoje.</p>
  <div class="actions rv" style="margin-top:1.8rem"><a class="btn" href="app/">Conhecer a app %(arr)s</a></div></div>
  %(phone)s
</div></section>

%(book)s
%(faq)s
""" % dict(heroimg=pic(root, "hero/hero-2.jpg", "Sala de treino do Pro Gym", "100vw", eager=True), h1=sp("Treina onde te der mais jeito."),
           arr=ARROW, stmt=stmt_words("Quatro ginásios em Maputo e Matola. Aulas, personal trainer, fisioterapia e nutrição. A primeira sessão é por nossa conta."),
           gh2=sp("Encontra o teu ginásio"), gcards=gcards, p2=sp("Preços sem letras pequenas"), a2=sp("Aulas que te fazem aparecer"),
           s2=sp("Mais do que sala de musculação"), ap=sp("A app do Pro Gym"),
           i1=pic(root, "classes/spinn.jpg", "Aula de Spinn 50 no Pro Gym", "(min-width:900px) 58vw, 100vw"),
           i2=pic(root, "classes/aerobics.jpg", "Aula de aeróbica no Pro Gym", "(min-width:900px) 40vw, 100vw"),
           i3=pic(root, "classes/crosstrain.jpg", "Aula de CrossTrain no Pro Gym", "(min-width:900px) 75vw, 100vw"),
           t1=pic(root, "services/personal-trainer.jpg", "", "170px"), t2=pic(root, "services/fisoterapia.jpg", "", "170px"),
           t3=pic(root, "services/nutricao.jpg", "", "170px"), t4=pic(root, "services/padel.jpg", "", "170px"),
           phone=phone_demo(cap=True), book=booking_section(root), faq=faq_section())
    write("", layout("", "Pro Gym Fitness | Ginásios em Maputo e Matola", "Quatro ginásios em Maputo e Matola: Marés, Alto Maé, Matola e Zimpeto. Aulas de grupo, personal trainer, fisioterapia, nutrição, padel e futsal. Marque a primeira sessão grátis.", body, jsonld=org_ld()))
    PAGES.append(("", True))

# ---------------- GYMS ----------------
def gyms():
    root = "../../"
    gcards = "".join(gcard(g, "../", "%s/" % g["slug"], "(min-width:800px) 58vw, 100vw") for g in GYMS)
    body = page_hero("../", [("Início", ""), ("Ginásios", None)], "Os nossos ginásios", "Quatro unidades em Maputo e Matola.", "hero/hero-2.jpg", "Sala de treino do Pro Gym") + \
        '<section class="tight"><div class="wrap"><div class="gyms-grid">%s</div></div></section>' % gcards
    write("gyms", layout("gyms/", "Ginásios Pro Gym | Marés, Alto Maé, Matola e Zimpeto", "Conhece os quatro ginásios Pro Gym em Maputo e Matola: morada, contacto e fotos de cada unidade.", body))
    PAGES.append(("gyms/", True))
    for g in GYMS:
        path = "gyms/%s/" % g["slug"]
        photos = "".join(mask(root, "gyms/%s/%s.jpg" % (g["slug"], p), "Pro Gym %s, %s" % (g["name"], ALT.get(p, "foto %s" % p.split("-")[-1] if p[-1].isdigit() else "foto")), "(min-width:900px) 45vw, 100vw") for p in g["photos"])
        plan = ""
        if g["plan"]:
            plan = '<p class="rv" style="margin-top:1.4rem"><a class="btn dark" href="%splans/#%s">Ver horário das aulas</a></p>' % (root, g["slug"])
        others = "".join('<li><a href="%sgyms/%s/">Pro Gym %s <span>%s</span></a></li>' % (root, o["slug"], e(o["name"]), e(o["area"])) for o in GYMS if o is not g)
        cover_alt = "Pro Gym %s, %s" % (g["name"], ALT.get(os.path.basename(g["cover"]).rsplit(".", 1)[0], "vista do ginásio"))
        body = page_hero(root, [("Início", ""), ("Ginásios", "gyms/"), (g["name"], None)], "Pro Gym " + g["name"], g["area"], g["cover"], cover_alt) + """
<section class="tight"><div class="wrap info">
  <div><h2 class="sp">%(h2)s</h2><p class="sub rv" style="max-width:62ch;color:var(--ink2)">%(d)s</p>%(plan)s
  <div class="actions rv" style="margin-top:1.4rem"><a class="btn" href="%(root)s#marcar">Marcar visita grátis</a><a class="btn dark" href="%(map)s" target="_blank" rel="noopener">Como chegar</a></div></div>
  <dl class="facts rv">
    <div><dt>Morada</dt><dd>%(addr)s</dd></div>
    <div><dt>Telefone</dt><dd><a href="%(tl)s">%(tel)s</a></dd></div>
    <div><dt>WhatsApp</dt><dd><a href="https://wa.me/%(wa)s" target="_blank" rel="noopener">%(atel)s</a></dd></div>
    <div><dt>Email</dt><dd><a href="mailto:%(em)s">%(em)s</a></dd></div>
  </dl>
</div></section>
<section class="dark-sec tight"><div class="wrap"><h2 class="sp wide">%(hh)s</h2><div class="rv">%(hrs)s</div></div></section>
<section class="tight"><div class="wrap"><h2 class="sp wide">%(ph2)s</h2><div class="photos">%(ph)s</div></div></section>
<section class="paper tight"><div class="wrap"><h2 class="sp wide">%(oh)s</h2><ul class="more-gyms rv">%(others)s</ul></div></section>
""" % dict(h2=sp("Treina no Pro Gym " + g["name"]), d=e(g["desc"]), plan=plan, root=root, map=maps("Pro Gym " + g["name"] + ", " + g["addr"]), addr=e(g["addr"]), tl=tel(g["tel"]), tel=g["tel"], wa=WA, atel=ADMIN_TEL, em=EMAIL,
           hh=sp("Horário"), hrs=hours_list(), ph2=sp("Fotos"), ph=photos, oh=sp("Outros ginásios"), others=others)
        ld = org_ld(); ld["name"] = "Pro Gym " + g["name"]; ld["telephone"] = g["tel"].replace(" ", ""); ld["address"] = {"@type": "PostalAddress", "streetAddress": g["addr"], "addressCountry": "MZ"}
        write(path, layout(path, "Pro Gym %s | Ginásio em %s" % (g["name"], g["area"].split(",")[-1].strip()), "Pro Gym %s: %s Morada, telefone, horário e fotos." % (g["name"], g["desc"][:110].rsplit(" ", 1)[0] + "…"), body, jsonld=ld, og_img=g["cover"]))
        PAGES.append((path, True))

# ---------------- PRICING ----------------
def pricing():
    root = "../"
    def table(cap, rows, hl=()):
        r = "".join('<tr%s><td>%s</td><td>%s</td></tr>' % (' class="hl"' if i in hl else "", n, p) for i, (n, p) in enumerate(rows))
        return '<table class="ptable rv"><caption>%s</caption><thead><tr><th scope="col">Produto</th><th scope="col">Preço</th></tr></thead><tbody>%s</tbody></table>' % (cap, r)
    cmp_ = """<div class="pcmp">
      <div class="plan rv"><h3>Mensal</h3><div class="price">2.990<small>MT</small></div><p class="note">Todos os ginásios</p></div>
      <div class="plan rv"><h3>Trimestral</h3><div class="price">8.490<small>MT</small></div><p class="note">3 meses</p></div>
      <div class="plan rv"><h3>Semestral</h3><div class="price">14.990<small>MT</small></div><p class="note">1 mês grátis</p></div>
      <div class="plan best rv"><span class="tag">Melhor valor</span><h3>Anual</h3><div class="price">24.990<small>MT</small></div><p class="note">3,6 meses grátis</p></div></div>"""
    t = table("Membro normal", [("Membro normal (mensal)", "2.990 MT"), ("Trimestral", "8.490 MT"), ("Semestral <small>1 mês grátis</small>", "14.990 MT"), ("Anual <small>3,6 meses grátis</small>", "24.990 MT")], hl=(3,))
    t += table("Outros tipos de membro", [("Família <small>pais e filhos</small>", "2.690 MT"), ("Estudantes, 1 ginásio <small>até 21 anos</small>", "1.500 MT"),
          ("Estudantes, todos os ginásios <small>até 21 anos</small>", "1.790 MT"), ("Sénior <small>65+ anos</small>", "1.990 MT"),
          ("Duas semanas", "1.990 MT"), ("Semanal", "1.490 MT"), ("Fins de semana", "1.990 MT")])
    t += table("Entradas diárias", [("Entrada", "500 MT"), ("10 entradas", "4.500 MT")])
    t += table("Inscrição", [("Membro do Pro Gym (anuidade)", "900 MT"), ("Cartão", "500 MT"), ("Chaveiro", "700 MT")])
    body = page_hero(root, [("Início", ""), ("Preços", None)], "Preços", "Estes preços aplicam-se a todos os membros do Pro Gym.", "hero/hero-2.jpg", "Sala de treino do Pro Gym") + """
<section class="tight"><div class="wrap">%s%s
<p class="fineprint rv">Poupança do plano anual: 12 mensalidades custariam 35.880 MT. Com o plano anual pagas 24.990 MT e poupas 10.890 MT, cerca de 3,6 meses.</p>
<div class="actions rv" style="margin-top:1.6rem"><a class="btn" href="%s#marcar">Marcar sessão grátis</a><a class="btn dark" href="https://wa.me/%s" target="_blank" rel="noopener">Perguntar pelo WhatsApp</a></div>
</div></section>""" % (cmp_, t, root, WA)
    write("pricing", layout("pricing/", "Preços | Pro Gym Fitness", "Preços do Pro Gym: mensalidade 2.990 MT, trimestral, semestral e anual, planos de estudante, família e sénior, entradas diárias e inscrição.", body))
    PAGES.append(("pricing/", True))

# ---------------- AULAS ----------------
def classes():
    root = "../"
    cards = """<div class="cls-grid">
    <div class="cls"><div class="pw">%s</div><div class="tx"><h3>Spinn 50</h3><p>Treino de ciclismo indoor de alta intensidade para melhorar a resistência e queimar calorias.</p></div></div>
    <div class="cls"><div class="pw">%s</div><div class="tx"><h3>Aeróbica</h3><p>Treino aeróbico rítmico com movimentos dinâmicos para aumentar a resistência física.</p></div></div>
    <div class="cls"><div class="pw">%s</div><div class="tx"><h3>CrossTrain</h3><p>Treino funcional de corpo inteiro que desenvolve força, agilidade e condicionamento físico.</p></div></div></div>""" % (
        pic(root, "classes/spinn.jpg", "Aula de Spinn 50", "(min-width:900px) 58vw, 100vw"), pic(root, "classes/aerobics.jpg", "Aula de aeróbica", "(min-width:900px) 40vw, 100vw"),
        pic(root, "classes/crosstrain.jpg", "Aula de CrossTrain", "(min-width:900px) 75vw, 100vw"))
    others = ["Zumba", "Spinning", "Tabata", "Step", "Core", "Flow", "Body Strength", "Max Glutes", "Bootcamp", "Spinn 4x4", "Strong Z"]
    chips = '<div class="chips rv">%s</div>' % "".join('<span class="tagc">%s</span>' % e(o) for o in others)
    tabs = "".join('<a role="tab" href="#%s" aria-selected="false">%s</a>' % (g["slug"], e(g["name"])) for g in GYMS)
    tts = ""
    for g in GYMS:
        if g["plan"]:
            w, h, _ = variants(g["plan"])
            tts += """<div class="tp tt" id="%(s)s" role="tabpanel"><h3 class="t-only">%(n)s</h3><a class="imglink" href="../%(i)s%(p)s" target="_blank" rel="noopener" aria-label="Abrir o horário do Pro Gym %(n)s em tamanho real"><img loading="lazy" decoding="async" src="../%(i)s%(p)s" width="%(w)d" height="%(h)d" alt="Horário das aulas do Pro Gym %(n)s"></a><p class="cap">Toca na imagem para abrir em tamanho real.</p></div>""" % dict(s=g["slug"], n=e(g["name"]), i=IMG, p=g["plan"], w=w, h=h)
        else:
            tts += '<div class="tp tt" id="%s" role="tabpanel"><h3 class="t-only">%s</h3><p class="sub">Pergunta o horário das aulas na receção ou pelo WhatsApp.</p><p style="margin-top:1rem"><a class="btn dark" href="%s" target="_blank" rel="noopener">Pedir horário</a></p></div>' % (g["slug"], e(g["name"]), wa("Olá! Gostaria de saber o horário das aulas no Pro Gym Zimpeto."))
    body = page_hero(root, [("Início", ""), ("Aulas", None)], "Aulas", "Aulas de grupo com instrutor nos ginásios Pro Gym.", "services/aulas.jpg", "Aula de grupo no Pro Gym") + """
<section class="tight"><div class="wrap"><h2 class="sp">%s</h2>%s<p class="sub rv" style="margin-top:2.2rem">Também aparecem nos horários:</p>%s</div></section>
<section class="paper tight"><div class="wrap" data-tabs><h2 class="sp">%s</h2><div class="tablist" role="tablist" aria-label="Ginásio">%s</div>%s</div></section>%s""" % (sp("As nossas aulas"), cards, chips, sp("Horários por ginásio"), tabs, tts, booking_section(root))
    write("plans", layout("plans/", "Aulas de grupo | Pro Gym Fitness", "Aeróbica, Spinn 50, CrossTrain, Zumba e mais. Consulta os horários das aulas nos ginásios Pro Gym Marés, Matola e Alto Maé.", body, og_img="services/aulas.jpg"))
    PAGES.append(("plans/", True))

# ---------------- SERVIÇOS ----------------
def services():
    root = "../"
    rows = [("personal-training/", "Personal trainer", "Treino com acompanhamento individual.", "services/personal-trainer.jpg"),
            ("physiotherapy/", "Fisioterapia", "Recupera de lesões e treina com segurança.", "services/fisoterapia.jpg"),
            ("nutrition/", "Nutrição", "Orientação alimentar para o teu objetivo.", "services/nutricao.jpg")]
    lis = "".join('<li class="rv"><a href="%s"><h3>%s</h3><p>%s</p><span class="go">Saber mais</span><span class="thumb">%s</span></a></li>' % (h, n, p, pic(root, i, "", "170px")) for h, n, p, i in rows)
    arena = """<section class="dark-sec tight" id="arena"><div class="wrap"><h2 class="sp">%s</h2>
<p class="sub rv">Mesmo à frente do ginásio, no Parque dos Poetas, na Matola: campos de padel, basquetebol e futsal, mini golfe, parque infantil e a única área de treino calisténico ao ar livre em Moçambique.</p>
<div class="photos" style="grid-template-columns:repeat(3,1fr)">
<div style="grid-column:span 1">%s<p class="sub" style="margin-top:.6rem">Padel</p></div>
<div style="grid-column:span 1;margin-top:3rem">%s<p class="sub" style="margin-top:.6rem">Mini golf</p></div>
<div style="grid-column:span 1">%s<p class="sub" style="margin-top:.6rem">Futsal</p></div></div>
<div class="actions rv" style="margin-top:2rem"><a class="btn" href="../gyms/matola/">Ver o Pro Gym Matola</a><a class="btn ghost" href="%s" target="_blank" rel="noopener">Reservar campo pelo WhatsApp</a></div></div></section>""" % (
        sp("A arena do Pro Gym Matola"), mask(root, "services/padel.jpg", "Campo de padel na arena do Pro Gym Matola", "33vw", True, ' style="aspect-ratio:3/4"'),
        mask(root, "services/mini-golf.jpg", "Mini golfe na arena do Pro Gym Matola", "33vw", True, ' style="aspect-ratio:3/4"'),
        mask(root, "services/futsal.jpg", "Campo de futsal na arena do Pro Gym Matola", "33vw", True, ' style="aspect-ratio:3/4"'), wa("Olá! Gostaria de reservar um campo na arena do Pro Gym Matola."))
    body = page_hero(root, [("Início", ""), ("Serviços", None)], "Serviços", "Mais do que sala de musculação.", "services/personal-trainer.jpg", "Personal trainer no Pro Gym") + '<section class="tight"><div class="wrap"><ul class="srows" style="margin-top:0">%s</ul></div></section>%s' % (lis, arena)
    write("services", layout("services/", "Serviços | Pro Gym Fitness", "Personal trainer, fisioterapia e nutrição, e a arena desportiva do Pro Gym Matola com padel, futsal e mini golfe.", body, og_img="services/personal-trainer.jpg"))
    PAGES.append(("services/", True))
    subs = [("personal-training", "Personal trainer", "services/personal-trainer.jpg", "Treino com acompanhamento individual de um personal trainer do Pro Gym, ajustado ao teu objetivo.", "Olá! Gostaria de marcar um treino com um personal trainer no Pro Gym."),
            ("physiotherapy", "Fisioterapia", "services/fisoterapia.jpg", "Fisioterapia no Pro Gym para recuperares de lesões e voltares a treinar com segurança.", "Olá! Gostaria de marcar fisioterapia no Pro Gym."),
            ("nutrition", "Nutrição", "services/nutricao.jpg", "Orientação nutricional no Pro Gym para te ajudar a atingir o teu objetivo.", "Olá! Gostaria de marcar uma consulta de nutrição no Pro Gym.")]
    for slug, name, img, txt, msg in subs:
        path = "services/%s/" % slug
        r = "../../"
        b = page_hero(r, [("Início", ""), ("Serviços", "services/"), (name, None)], name, None, img, name + " no Pro Gym") + """
<section class="tight"><div class="wrap info"><div><h2 class="sp">%s</h2><p class="sub rv" style="color:var(--ink2)">%s</p>
<p class="sub rv" style="color:var(--ink2)">Fala connosco para saberes os valores e marcares. Responde-te a receção da tua unidade.</p>
<div class="actions rv" style="margin-top:1.6rem"><a class="btn" href="%s" target="_blank" rel="noopener">Marcar pelo WhatsApp</a><a class="btn dark" href="%scontact/">Ver contactos</a></div></div>
%s</div></section>""" % (sp(name + " no Pro Gym"), e(txt), wa(msg), r, mask(r, img, name + " no Pro Gym", "(min-width:860px) 35vw, 100vw", True, ' style="aspect-ratio:4/5"'))
        write(path.rstrip("/"), layout(path, "%s | Pro Gym Fitness" % name, txt + " Marque pelo WhatsApp.", b, og_img=img))
        PAGES.append((path, True))

# ---------------- LOJA ----------------
def store():
    root = "../"
    prods = [("Hardcore Whey Protein", "Suplementos", "4.500", "store/hardcore-whey.webp"), ("USN Shaker", "Acessórios", "2.100", "store/shaker.jpg"), ("Creatina", "Suplementos", "2.700", "store/creatine-3-in-1.webp")]
    cards = "".join("""<article class="prod rv"><div class="ph">%s</div><div class="tx"><span class="cat">%s</span><h3>%s</h3><div class="pr">%s MT</div><a class="btn small" data-wa="%s" href="%s" target="_blank" rel="noopener">Encomendar pelo WhatsApp</a></div></article>""" % (
        pic(root, img, n, "(min-width:900px) 30vw, 100vw"), c, e(n), p, e("Olá! Gostaria de encomendar: %s (%s MT)." % (n, p)), wa("Olá! Gostaria de encomendar: %s (%s MT)." % (n, p))) for n, c, p, img in prods)
    body = page_hero(root, [("Início", ""), ("Loja", None)], "Loja", "Suplementos e acessórios para potencializares os teus resultados.", "store.jpg", "Suplementos e acessórios na loja do Pro Gym") + """
<section class="tight"><div class="wrap"><div class="products">%s</div>
<ol class="steps"><li class="rv"><b>Escolhe o produto</b>Toca em encomendar no produto que queres.</li><li class="rv"><b>Envia pelo WhatsApp</b>A mensagem segue já escrita para a receção.</li><li class="rv"><b>Confirmamos contigo</b>A receção confirma a disponibilidade e como levantar.</li></ol></div></section>""" % cards
    write("store", layout("store/", "Loja | Pro Gym Fitness", "Suplementos e acessórios Pro Gym: Hardcore Whey Protein, USN Shaker e Creatina. Encomende pelo WhatsApp.", body, og_img="store.jpg"))
    PAGES.append(("store/", True))

# ---------------- CONTACTO ----------------
def contact():
    root = "../"
    tabs = "".join('<a role="tab" href="#u-%s" aria-selected="false">%s</a>' % (g["slug"], e(g["name"])) for g in GYMS)
    panels = "".join("""<div class="tp cpanel" id="u-%(s)s" role="tabpanel"><div><h3>Pro Gym %(n)s</h3><address>%(a)s</address>
<a class="big-tel ul" href="%(tl)s">%(t)s</a></div>
<div><p class="sub" style="margin-top:0">Horário: segunda a sexta 05:00 às 22:00, sábado 06:00 às 18:00, domingo e feriados 06:00 às 13:00.</p>
<div class="actions" style="margin-top:1.4rem"><a class="btn" href="%(map)s" target="_blank" rel="noopener">Como chegar</a><a class="btn dark" href="%(wa)s" target="_blank" rel="noopener">WhatsApp</a><a class="btn dark" href="../gyms/%(s)s/">Ver ginásio</a></div></div></div>""" % dict(
        s=g["slug"], n=e(g["name"]), a=e(g["addr"]), tl=tel(g["tel"]), t=g["tel"], map=maps("Pro Gym " + g["name"] + ", " + g["addr"]), wa=wa("Olá! Escrevo sobre o Pro Gym %s." % g["name"])) for g in GYMS)
    body = page_hero(root, [("Início", ""), ("Contacto", None)], "Contacto", "Fala com a administração ou com a tua unidade.", "hero/hero-2.jpg", "Sala de treino do Pro Gym") + """
<section class="tight"><div class="wrap" data-tabs><h2 class="sp">%(h1)s</h2><div class="tablist" role="tablist" aria-label="Ginásio">%(tabs)s</div>%(panels)s</div></section>
<section class="paper tight"><div class="wrap info">
<div><h2 class="sp">%(h2)s</h2>
<form class="f rv" id="contactForm" style="margin-top:1.4rem" novalidate>
<label>Nome<input id="cName" autocomplete="name" placeholder="O teu nome" required></label>
<label>Mensagem<textarea id="cMsg" placeholder="Em que podemos ajudar?" required></textarea></label>
<div class="err" id="cErr" role="alert"></div><button class="btn" type="submit">Enviar pelo WhatsApp</button>
<p class="fine">Abre o WhatsApp com a mensagem pronta. Também podes escrever para %(em)s.</p></form></div>
<dl class="facts rv"><div><dt>Administração</dt><dd><a href="tel:+258844414441">%(t)s</a></dd></div>
<div><dt>Email</dt><dd><a href="mailto:%(em)s">%(em)s</a></dd></div>
<div><dt>Redes sociais</dt><dd><a href="%(fb)s" target="_blank" rel="noopener">Facebook</a><br><a href="%(ig)s" target="_blank" rel="noopener">Instagram</a><br><a href="%(li)s" target="_blank" rel="noopener">LinkedIn</a></dd></div></dl></div></section>""" % dict(
        h1=sp("Escolhe o ginásio"), tabs=tabs, panels=panels, h2=sp("Escreve-nos"), em=EMAIL, t=ADMIN_TEL, fb=FB, ig=IG, li=LI)
    write("contact", layout("contact/", "Contacto | Pro Gym Fitness", "Contactos do Pro Gym: administração, email, WhatsApp e morada de cada ginásio em Maputo e Matola.", body))
    PAGES.append(("contact/", True))

# ---------------- EVENTOS ----------------
def gallery():
    root = "../"
    body = page_hero(root, [("Início", ""), ("Eventos", None)], "Eventos", "Novidades, aulas especiais e eventos nos ginásios Pro Gym.", "hero/hero-2.jpg", "Sala de treino do Pro Gym") + """
<section class="tight"><div class="wrap"><h2 class="sp">%s</h2><p class="sub rv">Publicamos os eventos e as fotos nas nossas redes sociais.</p>
<div class="actions rv" style="margin-top:1.6rem"><a class="btn" href="%s" target="_blank" rel="noopener">Instagram</a><a class="btn dark" href="%s" target="_blank" rel="noopener">Facebook</a></div></div></section>""" % (sp("Acompanha-nos nas redes"), IG, FB)
    write("gallery", layout("gallery/", "Eventos | Pro Gym Fitness", "Eventos e novidades do Pro Gym. Acompanhe no Instagram e Facebook.", body, noindex=True))
    PAGES.append(("gallery/", False))

# ---------------- APP ----------------
def app():
    root = "../"
    units = "".join("<option>%s</option>" % g["name"] for g in GYMS)
    body = page_hero(root, [("Início", ""), ("App", None)], "A app do Pro Gym", "Para membros: o teu treino e os teus amigos do ginásio, no telemóvel.", "hero/hero-2.jpg", "Sala de treino do Pro Gym") + """
<section class="dark-sec"><div class="wrap app-grid">
<div><span class="soon rv">Brevemente</span><h2 class="sp">%s</h2>
<p class="sub rv">Uma app para os membros do Pro Gym registarem o progresso e treinarem em conjunto. A app ainda não está disponível. O cartão de acesso e as mensalidades continuam como hoje.</p>
<ul class="feat rv"><li>Regista cargas, plano de treino, exercícios, dias de ginásio, cardio e peso corporal.</li>
<li>Sequências de dias e desafios diários.</li>
<li>Ranking de força entre amigos do mesmo ginásio.</li>
<li>Feed privado do grupo e notificações para se motivarem.</li>
<li>Relatório mensal e imagem pronta para partilhar no Instagram.</li></ul>
<p class="demo-note rv">Pré-visualização com dados de exemplo. Experimenta: troca o ranking e marca o desafio do dia.</p></div>
%s</div></section>
<section class="orange-sec"><div class="wrap book"><div><h2 class="sp">%s</h2><p class="sub rv" style="color:var(--iron)">Diz-nos o teu nome e o teu ginásio. Avisamos-te quando a app estiver disponível.</p></div>
<form class="f rv" id="waitForm" novalidate><label>Nome<input id="wName" autocomplete="name" placeholder="O teu nome" required></label>
<label>Treino no Pro Gym<select id="wUnit">%s</select></label><div class="err" id="wErr" role="alert"></div>
<button class="btn" type="submit">Enviar pelo WhatsApp</button><p class="fine">Abre o WhatsApp com a mensagem pronta. Este site não guarda os teus dados.</p></form></div></section>""" % (sp("O teu treino, no telemóvel"), phone_demo(), sp("Quero ser dos primeiros"), units)
    write("app", layout("app/", "App Pro Gym | Brevemente", "A app para os membros do Pro Gym: regista o treino, acompanha o progresso e compete com os amigos do teu ginásio. Brevemente.", body))
    PAGES.append(("app/", True))

# ---------------- 404 / sitemap / robots ----------------
def extras():
    nf = """<!DOCTYPE html><html lang="pt"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Página não encontrada | Pro Gym</title><meta name="robots" content="noindex">
<link rel="stylesheet" href="/assets/css/style.css"></head>
<body><div class="notfound"><div><h1>404</h1><p style="font-size:1.2rem;margin:1rem 0 2rem">Esta página não existe ou mudou de sítio.</p><a class="btn" href="/">Voltar ao início</a></div></div></body></html>"""
    open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(nf)
    urls = "".join("<url><loc>%s/%s</loc></url>\n" % (SITE_URL, p) for p, ok in PAGES if ok)
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % urls)
    open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % SITE_URL)
    open(os.path.join(OUT, ".nojekyll"), "w").write("")

if __name__ == "__main__":
    home(); gyms(); pricing(); classes(); services(); store(); contact(); gallery(); app(); extras()
    print("OK", len(PAGES), "páginas ->", OUT)

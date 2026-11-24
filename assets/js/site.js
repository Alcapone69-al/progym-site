(function(){
'use strict';
var d=document,root=d.documentElement,WA='258844414441';
var EN=root.lang==='en';
var S=function(pt,en){return EN?en:pt};
var $=function(s,c){return (c||d).querySelector(s)};
var $$=function(s,c){return Array.prototype.slice.call((c||d).querySelectorAll(s))};
var rq=window.matchMedia('(prefers-reduced-motion: reduce)');
var hasGsap=function(){return !!(window.gsap&&window.ScrollTrigger)};

/* ============ Interface base (funciona sem animações) ============ */

// cabeçalho: sólido ao descer, esconde ao descer e volta ao subir
var h=$('#top');
if(h){
  var lastY=window.scrollY,tick=false;
  var onS=function(){
    var y=window.scrollY;
    h.classList.toggle('solid',y>40);
    if(!rq.matches&&!d.body.classList.contains('menu-open')){
      if(y>lastY+6&&y>260)h.classList.add('hide');
      else if(y<lastY-6||y<260)h.classList.remove('hide');
    }
    lastY=y;tick=false;
  };
  addEventListener('scroll',function(){if(!tick){tick=true;requestAnimationFrame(onS)}},{passive:true});
  onS();
  h.addEventListener('focusin',function(){h.classList.remove('hide')});
}

// menu móvel
var mb=$('#menuBtn'),nav=$('#mainNav');
function setMenu(open){
  d.body.classList.toggle('menu-open',open);
  mb.setAttribute('aria-expanded',open);
  mb.textContent=open?S('Fechar','Close'):'Menu';
  if(open&&h)h.classList.remove('hide');
}
if(mb&&nav){
  mb.addEventListener('click',function(){setMenu(!d.body.classList.contains('menu-open'))});
  nav.addEventListener('click',function(e){if(e.target.closest('a'))setMenu(false)});
  d.addEventListener('keydown',function(e){if(e.key==='Escape'&&d.body.classList.contains('menu-open')){setMenu(false);mb.focus()}});
  matchMedia('(min-width: 1021px)').addEventListener('change',function(e){if(e.matches)setMenu(false)});
}

// estado aberto / fechado (hora de Maputo, com feriados)
var el=$('#status'),tx=$('#statusText');
if(el&&tx){
  var fmt=function(m){return String(Math.floor(m/60)).padStart(2,'0')+':'+String(m%60).padStart(2,'0')};
  // feriados nacionais de Moçambique com data fixa + Sexta-feira Santa (Páscoa calculada)
  var FIXED=['01-01','02-03','04-07','05-01','06-25','09-07','09-25','10-04','12-25'];
  var easter=function(y){
    var a=y%19,b=Math.floor(y/100),c=y%100,dd=Math.floor(b/4),e=b%4,f=Math.floor((b+8)/25),g=Math.floor((b-f+1)/3),
        h=(19*a+b-dd-g+15)%30,i=Math.floor(c/4),k=c%4,l=(32+2*e+2*i-h-k)%7,m=Math.floor((a+11*h+22*l)/451),
        mo=Math.floor((h+l-7*m+114)/31),da=((h+l-7*m+114)%31)+1;
    return Date.UTC(y,mo-1,da);
  };
  var pad=function(n){return String(n).padStart(2,'0')};
  var isHoliday=function(t){ // t = Date.UTC(y,m-1,d)
    var x=new Date(t),y=x.getUTCFullYear();
    if(FIXED.indexOf(pad(x.getUTCMonth()+1)+'-'+pad(x.getUTCDate()))>-1)return true;
    return t===easter(y)-2*864e5;
  };
  var hoursOn=function(t){ // t = dia (UTC) -> [abre, fecha] em minutos
    var wd=new Date(t).getUTCDay(); // 0 = domingo
    if(isHoliday(t)||wd===0)return [360,780];
    if(wd===6)return [360,1080];
    return [300,1320];
  };
  var nowMz=function(){
    var p=new Intl.DateTimeFormat('en-GB',{timeZone:'Africa/Maputo',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false}).formatToParts(new Date()),o={};
    p.forEach(function(x){o[x.type]=x.value});
    return {t:Date.UTC(+o.year,+o.month-1,+o.day),m:(+o.hour%24)*60+(+o.minute)};
  };
  var paint=function(){
    var n=nowMz(),hr=hoursOn(n.t),t;
    if(n.m>=hr[0]&&n.m<hr[1]){el.classList.add('open');t=S('Aberto agora, fecha às ','Open now, closes at ')+fmt(hr[1]);}
    else{
      el.classList.remove('open');
      if(n.m<hr[0])t=S('Fechado agora, abre hoje às ','Closed now, opens today at ')+fmt(hr[0]);
      else t=S('Fechado agora, abre amanhã às ','Closed now, opens tomorrow at ')+fmt(hoursOn(n.t+864e5)[0]);
    }
    if(tx.textContent!==t)tx.textContent=t;
  };
  paint();setInterval(paint,60000);
}

// seletor de língua: lembra a escolha e mantém o #separador; sugere inglês a quem não usa português
var LS={get:function(k){try{return localStorage.getItem(k)}catch(x){return null}},set:function(k,v){try{localStorage.setItem(k,v)}catch(x){}}};
$$('.lang a').forEach(function(a){
  a.addEventListener('click',function(){
    LS.set('pg-lang',a.getAttribute('hreflang'));
    if(location.hash&&a.getAttribute('href').indexOf('#')<0)a.setAttribute('href',a.getAttribute('href')+location.hash);
  });
});
if(!EN&&!LS.get('pg-lang')){
  var nl=((navigator.languages&&navigator.languages[0])||navigator.language||'pt').toLowerCase();
  var toEn=$('.lang a[hreflang="en"]');
  if(nl.indexOf('pt')!==0&&toEn){
    var bn=d.createElement('div');bn.className='lang-hint';bn.setAttribute('role','region');bn.setAttribute('aria-label','Language');
    bn.innerHTML='<span>This site is also available in English.</span><a href="'+toEn.getAttribute('href')+'" hreflang="en" lang="en">Read in English</a><button type="button" aria-label="Dismiss">&times;</button>';
    d.body.appendChild(bn);
    $('a',bn).addEventListener('click',function(){LS.set('pg-lang','en')});
    $('button',bn).addEventListener('click',function(){LS.set('pg-lang','pt');bn.remove()});
  }
}


// barra de progresso ao navegar entre páginas
d.addEventListener('click',function(e){
  var a=e.target.closest&&e.target.closest('a[href]');
  if(!a||e.defaultPrevented||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||e.button||a.target==='_blank'||a.hasAttribute('download'))return;
  var u;try{u=new URL(a.href)}catch(x){return}
  if(u.origin!==location.origin||u.protocol.indexOf('http')!==0)return;
  if(u.pathname===location.pathname&&u.search===location.search)return;
  root.classList.add('leaving');
});
addEventListener('pageshow',function(){root.classList.remove('leaving')});

// separadores (aulas e contactos): sem JS todos os painéis ficam visíveis
$$('[data-tabs]').forEach(function(box){
  var tabs=$$('[role="tab"]',box);
  var panels=tabs.map(function(t){return d.getElementById(t.getAttribute('href').slice(1))});
  if(!tabs.length)return;
  box.classList.add('tabs-on');
  function sel(i,focus,write){
    tabs.forEach(function(t,k){
      var on=k===i;t.setAttribute('aria-selected',on);t.tabIndex=on?0:-1;
      panels[k].hidden=!on;
    });
    if(focus)tabs[i].focus();
    if(write&&history.replaceState)history.replaceState(null,'','#'+panels[i].id);
    if(hasGsap())ScrollTrigger.refresh();
  }
  tabs.forEach(function(t,i){
    t.addEventListener('click',function(e){e.preventDefault();sel(i,false,true)});
    t.addEventListener('keydown',function(e){
      var k=e.key,n=tabs.length;
      if(k==='ArrowRight'||k==='ArrowDown'){e.preventDefault();sel((i+1)%n,true,true)}
      else if(k==='ArrowLeft'||k==='ArrowUp'){e.preventDefault();sel((i+n-1)%n,true,true)}
      else if(k==='Home'){e.preventDefault();sel(0,true,true)}
      else if(k==='End'){e.preventDefault();sel(n-1,true,true)}
    });
  });
  var fromHash=function(){
    var id=location.hash.slice(1),i=panels.map(function(p){return p.id}).indexOf(id);
    return i;
  };
  var start=fromHash();
  sel(start>-1?start:0,false,false);
  addEventListener('hashchange',function(){var i=fromHash();if(i>-1)sel(i,false,false)});
});

// galeria elástica de ginásios: passar o rato, focar ou tocar abre o ginásio; clicar no aberto navega
$$('[data-elastic]').forEach(function(box){
  var els=$$('.el',box);
  var fine=matchMedia('(hover: hover) and (pointer: fine)');
  function act(el){els.forEach(function(x){x.classList.toggle('is-active',x===el)})}
  els.forEach(function(el){
    el.addEventListener('mouseenter',function(){if(fine.matches)act(el)});
    el.addEventListener('focus',function(){if(el.matches(':focus-visible'))act(el)});
    el.addEventListener('click',function(e){if(!el.classList.contains('is-active')){e.preventDefault();act(el)}});
  });
});

/* ============ Formulários -> WhatsApp ============ */
function waUrl(msg){return 'https://wa.me/'+WA+'?text='+encodeURIComponent(msg)}
function send(msg,btn,note){
  var url=waUrl(msg);
  window.open(url,'_blank','noopener');
  if(btn){
    var t=btn.getAttribute('data-t')||btn.textContent;
    btn.setAttribute('data-t',t);btn.classList.add('busy');btn.textContent=S('A abrir o WhatsApp…','Opening WhatsApp…');
    setTimeout(function(){btn.classList.remove('busy');btn.textContent=t},2600);
  }
  if(note){note.innerHTML=S('Mensagem pronta. Se o WhatsApp não abriu, <a href="'+url+'" target="_blank" rel="noopener">toca aqui</a>.','Message ready. If WhatsApp didn\'t open, <a href="'+url+'" target="_blank" rel="noopener">tap here</a>.')}
}
function bad(input,err,msg){
  err.textContent=msg;
  input.setAttribute('aria-invalid','true');
  input.focus();
  var clr=function(){input.removeAttribute('aria-invalid');err.textContent='';input.removeEventListener('input',clr)};
  input.addEventListener('input',clr);
}
function noteFor(form){
  var n=$('.ok',form);
  if(!n){n=d.createElement('p');n.className='ok';n.setAttribute('role','status');form.insertBefore(n,$('.fine',form))}
  return n;
}

var book=$('#bookForm');
if(book){
  var dt=$('#fDate');
  if(dt){var t=new Date();dt.min=dt.value=new Date(t.getTime()-t.getTimezoneOffset()*60000).toISOString().slice(0,10)}
  book.addEventListener('submit',function(e){
    e.preventDefault();
    var nm=$('#fName'),err=$('#err');
    if(!nm.value.trim()){bad(nm,err,S('Escreve o teu nome para continuar.','Please enter your name to continue.'));return}
    if(dt&&dt.value&&dt.value<dt.min){bad(dt,err,S('Escolhe um dia a partir de hoje.','Please choose today or a later day.'));return}
    err.textContent='';
    var dv=dt&&dt.value?new Date(dt.value+'T12:00:00'):null,tsel=$('#fTime'),unit=$('#fUnit').value,who=nm.value.trim();
    var dayPt=dv?dv.toLocaleDateString('pt-PT',{weekday:'long',day:'numeric',month:'long'}):'';
    var pt='Olá! Sou '+who+' e quero marcar a minha primeira sessão grátis no Pro Gym '+unit+(dayPt?', '+dayPt:'')+', de '+tsel.value+'.';
    var msg=pt;
    if(EN){
      var dayEn=dv?dv.toLocaleDateString('en-GB',{weekday:'long',day:'numeric',month:'long'}):'';
      msg='Hello! I\'m '+who+' and I\'d like to book my free first session at Pro Gym '+unit+(dayEn?' on '+dayEn:'')+', in the '+tsel.options[tsel.selectedIndex].text.toLowerCase()+'.\n\n(PT) '+pt;
    }
    send(msg,$('button[type=submit]',book),noteFor(book));
  });
}
var cf=$('#contactForm');
if(cf){
  cf.addEventListener('submit',function(e){
    e.preventDefault();
    var n=$('#cName'),m=$('#cMsg'),err=$('#cErr');
    if(!n.value.trim()){bad(n,err,S('Escreve o teu nome para continuar.','Please enter your name to continue.'));return}
    if(!m.value.trim()){bad(m,err,S('Escreve a tua mensagem.','Please write your message.'));return}
    err.textContent='';
    send(S('Olá! Sou ','Hello! I\'m ')+n.value.trim()+'. '+m.value.trim(),$('button[type=submit]',cf),noteFor(cf));
  });
}
var ev=$('#evForm');
if(ev){
  ev.addEventListener('submit',function(e){
    e.preventDefault();
    var n=$('#eName'),evn=$('#eEvent'),err=$('#eErr'),pp=$('#ePeople'),un=$('#eUnit').value,nt=$('#eNote').value.trim();
    if(!n.value.trim()){bad(n,err,S('Escreve o teu nome para continuar.','Please enter your name to continue.'));return}
    if(!evn.value.trim()){bad(evn,err,S('Escreve o nome do evento.','Please enter the event name.'));return}
    var c=Math.max(1,Math.min(20,parseInt(pp.value,10)||1));
    err.textContent='';
    var pt='Olá! Sou '+n.value.trim()+' e quero inscrever-me no evento "'+evn.value.trim()+'" (Pro Gym '+un+'), para '+c+(c===1?' pessoa':' pessoas')+'.'+(nt?' Nota: '+nt:'');
    var msg=pt;
    if(EN){msg='Hello! I\'m '+n.value.trim()+' and I\'d like to register for the event "'+evn.value.trim()+'" (Pro Gym '+un+'), for '+c+(c===1?' person':' people')+'.'+(nt?' Note: '+nt:'')+'\n\n(PT) '+pt}
    send(msg,$('button[type=submit]',ev),noteFor(ev));
  });
}
var wl=$('#waitForm');
if(wl){
  wl.addEventListener('submit',function(e){
    e.preventDefault();
    var n=$('#wName'),err=$('#wErr');
    if(!n.value.trim()){bad(n,err,S('Escreve o teu nome para continuar.','Please enter your name to continue.'));return}
    err.textContent='';
    var wpt='Olá! Sou '+n.value.trim()+', treino no Pro Gym '+$('#wUnit').value+' e quero ser dos primeiros a usar a app do Pro Gym.';
    send(EN?'Hello! I\'m '+n.value.trim()+', I train at Pro Gym '+$('#wUnit').value+' and I\'d like to be one of the first to use the Pro Gym app.\n\n(PT) '+wpt:wpt,$('button[type=submit]',wl),noteFor(wl));
  });
}
$$('[data-wa]').forEach(function(a){
  a.addEventListener('click',function(e){e.preventDefault();send(a.getAttribute('data-wa'))});
});

/* ============ Pré-visualização da app ============ */
var rank=$('#rank');
if(rank){
  var friends=[{n:'Ana',v:18,g:72},{n:'Nelson',v:16,g:100,me:1},{n:'Zito',v:15,g:83},{n:'Carla',v:11,g:95}],mode='v';
  var items={};
  friends.forEach(function(f){
    var li=d.createElement('li');if(f.me)li.className='me';
    li.innerHTML='<b></b><span>'+(f.me?S('Tu','You'):f.n)+'</span><span class="val"></span>';
    items[f.n]=li;rank.appendChild(li);
  });
  var draw=function(animate){
    var arr=friends.slice().sort(function(a,b){return mode==='v'?b.v-a.v:b.g-a.g});
    var before={};
    if(animate)arr.forEach(function(f){before[f.n]=items[f.n].getBoundingClientRect().top});
    arr.forEach(function(f,i){
      var li=items[f.n];rank.appendChild(li);
      li.firstChild.textContent=i+1;
      li.lastChild.textContent=mode==='v'?f.v+S(' visitas',' visits'):f.g+S('% da meta','% of goal');
    });
    if(animate&&hasGsap()&&!rq.matches){
      arr.forEach(function(f){
        var dy=before[f.n]-items[f.n].getBoundingClientRect().top;
        if(dy)gsap.fromTo(items[f.n],{y:dy},{y:0,duration:.55,ease:'power3.out',clearProps:'transform'});
      });
    }
  };
  draw(false);
  var bv=$('#rkVisits'),bg=$('#rkGoal');
  var setMode=function(m){mode=m;bv.setAttribute('aria-pressed',m==='v');bg.setAttribute('aria-pressed',m==='g');draw(true)};
  bv.onclick=function(){setMode('v')};bg.onclick=function(){setMode('g')};
  var done=false;
  $('#chBtn').onclick=function(){
    if(done)return;done=true;
    $('#challenge').classList.add('done');
    this.textContent=S('Feito','Done');$('#chS').textContent=S('Concluído hoje','Completed today');
    var s=$('#streakN');s.textContent='13';
    if(hasGsap()&&!rq.matches)gsap.fromTo(s,{scale:1.5,color:'#fff'},{scale:1,color:'#F97316',duration:.7,ease:'back.out(2)'});
  };
}

/* ============ Motion design (GSAP + ScrollTrigger) ============ */
function finish(el,props){
  el.classList.add('is-in');
  if(window.gsap)gsap.set(el,{clearProps:props||'opacity,transform'});
}

function heroIntro(){
  var tl=gsap.timeline({defaults:{ease:'power4.out'}});
  var hm=$('.hero-media'),pm=$('.phero-media');
  if(hm)tl.fromTo(hm,{scale:1.16},{scale:1,duration:2.2,ease:'power2.out'},0);
  if(pm)tl.fromTo(pm,{scale:1.1},{scale:1,duration:1.8,ease:'power2.out'},0);
  var words=$$('[data-hero] .w>span');
  if(words.length)tl.fromTo(words,{yPercent:115},{yPercent:0,duration:1.1,stagger:.07,onComplete:function(){$$('[data-hero]').forEach(function(x){finish(x,'')});gsap.set(words,{clearProps:'transform'})}},.15);
  var hr=$$('.hr');
  if(hr.length)tl.fromTo(hr,{opacity:0,y:26},{opacity:1,y:0,duration:.9,stagger:.1,ease:'power3.out',onComplete:function(){hr.forEach(function(x){finish(x)})}},.6);
  var bar=$('.hero-bar');
  if(bar)tl.fromTo(bar,{scaleX:0},{scaleX:1,duration:1.3,ease:'power3.inOut',onComplete:function(){finish(bar,'transform')}},.3);
}

function initMotion(){
  gsap.registerPlugin(ScrollTrigger);
  ScrollTrigger.config({ignoreMobileResize:true});
  heroIntro();

  var mm=gsap.matchMedia();
  mm.add({desk:'(min-width: 901px)',mob:'(max-width: 900px)'},function(ctx){
    var desk=ctx.conditions.desk,undo=[];

    // hero da home: a imagem aproxima-se e o texto sobe ao fazer scroll
    var hero=$('.hero');
    if(hero){
      gsap.to($('.hero-media img',hero),{yPercent:desk?9:5,scale:desk?1.22:1.12,ease:'none',scrollTrigger:{trigger:hero,start:'top top',end:'bottom top',scrub:true}});
      gsap.to($('.hero-in',hero),{y:desk?-70:-30,opacity:.05,ease:'none',scrollTrigger:{trigger:hero,start:'top top',end:'70% top',scrub:true}});
    }
    // hero das páginas interiores
    var ph=$('.phero');
    if(ph){
      gsap.to($('.phero-media img',ph),{yPercent:desk?8:4,scale:desk?1.18:1.1,ease:'none',scrollTrigger:{trigger:ph,start:'top top',end:'bottom top',scrub:true}});
    }

    // títulos: palavra a palavra
    $$('.sp:not([data-hero])').forEach(function(t){
      var w=$$('.w>span',t);
      gsap.fromTo(w,{yPercent:115},{yPercent:0,duration:1,ease:'power4.out',stagger:.05,scrollTrigger:{trigger:t,start:'top 88%',once:true},onComplete:function(){finish(t,'');gsap.set(w,{clearProps:'transform'})}});
    });

    // elementos que sobem com atraso sequencial
    ScrollTrigger.batch('.rv',{
      start:'top 90%',once:true,
      onEnter:function(b){
        b.forEach(function(x){x.classList.add('in')});
        gsap.fromTo(b,{opacity:0,y:34},{opacity:1,y:0,duration:.9,ease:'power3.out',stagger:.09,overwrite:true,onComplete:function(){b.forEach(function(x){finish(x)})}});
      }
    });

    // máscaras de imagem
    $$('.mask').forEach(function(m){
      var inn=$('.in',m);
      var tl=gsap.timeline({scrollTrigger:{trigger:m,start:'top 90%',once:true}});
      tl.fromTo(m,{clipPath:'inset(0% 0% 100% 0%)'},{clipPath:'inset(0% 0% 0% 0%)',duration:1.2,ease:'power4.inOut',onComplete:function(){m.classList.add('is-in');gsap.set(m,{clearProps:'clipPath'})}},0)
        .fromTo(inn,{scale:1.25},{scale:1,duration:1.7,ease:'power3.out'},0);
    });

    // frase de arranque: as palavras acendem com o scroll
    var st=$('.stmt');
    if(st){
      gsap.fromTo($$('.sw',st),{opacity:.18},{opacity:1,ease:'none',stagger:.12,scrollTrigger:{trigger:st,start:'top 82%',end:'bottom 58%',scrub:true}});
    }

    if(desk){
      // paralaxe subtil
      $$('[data-par]').forEach(function(p){
        var img=$('img',p);if(!img)return;
        gsap.fromTo(img,{yPercent:-6},{yPercent:6,ease:'none',scrollTrigger:{trigger:p,start:'top bottom',end:'bottom top',scrub:true}});
      });
      // transição entre secções: a secção escura "abre" ao entrar
      $$('[data-sheet]').forEach(function(s){
        gsap.fromTo(s,{scale:.93,borderRadius:48,transformOrigin:'50% 0%'},{scale:1,borderRadius:0,ease:'none',scrollTrigger:{trigger:s,start:'top 96%',end:'top 38%',scrub:true}});
      });
      // telemóvel da app flutua
      var ph2=$('.app-grid .phone');
      if(ph2)gsap.fromTo(ph2,{yPercent:5},{yPercent:-5,ease:'none',scrollTrigger:{trigger:ph2.parentNode,start:'top bottom',end:'bottom top',scrub:true}});

    }
    return function(){undo.forEach(function(f){f()})};
  });

  addEventListener('load',function(){ScrollTrigger.refresh()});
  if(d.fonts&&d.fonts.ready)d.fonts.ready.then(function(){ScrollTrigger.refresh()});
}

function failMotion(){root.classList.remove('motion')}
if(root.classList.contains('motion')){
  if(!rq.matches&&hasGsap()){
    try{initMotion()}catch(err){failMotion();if(window.console)console.warn('Motion desativado:',err)}
  }else failMotion();
}
// se o utilizador mudar a preferência de movimento, recarrega para aplicar
if(rq.addEventListener)rq.addEventListener('change',function(){location.reload()});
window.__pg=1;
})();

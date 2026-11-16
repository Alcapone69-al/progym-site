(function(){
  var WA='258844414441';

  // header turns solid on scroll
  var h=document.getElementById('top');
  if(h&&!h.classList.contains('always')){
    var sc=function(){h.classList.toggle('solid',window.scrollY>40)};
    sc();addEventListener('scroll',sc,{passive:true});
  }

  // mobile menu
  var mb=document.getElementById('menuBtn'),nav=document.getElementById('mainNav');
  if(mb&&nav){mb.addEventListener('click',function(){
    var o=nav.classList.toggle('open');mb.setAttribute('aria-expanded',o);mb.textContent=o?'Fechar':'Menu';
  });}

  // open / closed status (Maputo time)
  var el=document.getElementById('status'),tx=document.getElementById('statusText');
  if(el&&tx){
    var days=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
    var now=function(){
      var p=new Intl.DateTimeFormat('en-GB',{timeZone:'Africa/Maputo',weekday:'short',hour:'2-digit',minute:'2-digit',hour12:false}).formatToParts(new Date()),o={};
      p.forEach(function(x){o[x.type]=x.value});
      return {d:o.weekday,m:(+o.hour%24)*60+(+o.minute)};
    };
    var hoursFor=function(d){
      if(['Mon','Tue','Wed','Thu','Fri'].indexOf(d)>-1)return [300,1320];
      if(d==='Sat')return [360,1080];
      return [360,780];
    };
    var fmt=function(m){return String(Math.floor(m/60)).padStart(2,'0')+':'+String(m%60).padStart(2,'0')};
    var paint=function(){
      var n=now(),hr=hoursFor(n.d);
      if(n.m>=hr[0]&&n.m<hr[1]){el.classList.add('open');tx.textContent='Aberto agora, fecha às '+fmt(hr[1]);}
      else{
        el.classList.remove('open');
        if(n.m<hr[0]){tx.textContent='Fechado agora, abre hoje às '+fmt(hr[0]);}
        else{var nd=days[(days.indexOf(n.d)+1)%7];tx.textContent='Fechado agora, abre amanhã às '+fmt(hoursFor(nd)[0]);}
      }
    };
    paint();setInterval(paint,60000);
  }

  // forms -> WhatsApp (indicativo 258)
  function send(msg){window.open('https://wa.me/'+WA+'?text='+encodeURIComponent(msg),'_blank','noopener');}
  var book=document.getElementById('bookForm');
  if(book){
    var d=document.getElementById('fDate');
    if(d){var t=new Date();var iso=new Date(t.getTime()-t.getTimezoneOffset()*60000).toISOString().slice(0,10);d.min=iso;d.value=iso;}
    book.addEventListener('submit',function(e){
      e.preventDefault();
      var name=document.getElementById('fName').value.trim(),err=document.getElementById('err');
      if(!name){err.textContent='Escreve o teu nome para continuar.';document.getElementById('fName').focus();return}
      err.textContent='';
      var dt=d&&d.value?new Date(d.value+'T12:00:00').toLocaleDateString('pt-PT',{weekday:'long',day:'numeric',month:'long'}):'';
      send('Olá! Sou '+name+' e quero marcar a minha primeira sessão grátis no Pro Gym '+document.getElementById('fUnit').value+(dt?', '+dt:'')+', de '+document.getElementById('fTime').value.toLowerCase()+'.');
    });
  }
  var cf=document.getElementById('contactForm');
  if(cf){
    cf.addEventListener('submit',function(e){
      e.preventDefault();
      var n=document.getElementById('cName').value.trim(),m=document.getElementById('cMsg').value.trim(),err=document.getElementById('cErr');
      if(!n||!m){err.textContent='Preenche o nome e a mensagem.';return}
      err.textContent='';
      send('Olá! Sou '+n+'. '+m);
    });
  }
  document.querySelectorAll('[data-wa]').forEach(function(a){
    a.addEventListener('click',function(e){e.preventDefault();send(a.getAttribute('data-wa'));});
  });
  var wl=document.getElementById('waitForm');
  if(wl){
    wl.addEventListener('submit',function(e){
      e.preventDefault();
      var n=document.getElementById('wName').value.trim(),u=document.getElementById('wUnit').value,err=document.getElementById('wErr');
      if(!n){err.textContent='Escreve o teu nome para continuar.';return}
      err.textContent='';
      send('Olá! Sou '+n+', treino no Pro Gym '+u+' e quero ser dos primeiros a usar a app do Pro Gym.');
    });
  }

  // app preview
  var rank=document.getElementById('rank');
  if(rank){
    var friends=[{n:'Ana',v:18,g:72},{n:'Nelson',v:16,g:100,me:1},{n:'Zito',v:15,g:83},{n:'Carla',v:11,g:95}],mode='v';
    var draw=function(){
      var arr=friends.slice().sort(function(a,b){return mode==='v'?b.v-a.v:b.g-a.g});
      rank.innerHTML=arr.map(function(f,i){return '<li class="'+(f.me?'me':'')+'"><b>'+(i+1)+'</b><span>'+(f.me?'Tu':f.n)+'</span><span>'+(mode==='v'?f.v+' visitas':f.g+'% da meta')+'</span></li>'}).join('');
    };
    draw();
    var bv=document.getElementById('rkVisits'),bg=document.getElementById('rkGoal');
    var setMode=function(m){mode=m;bv.setAttribute('aria-pressed',m==='v');bg.setAttribute('aria-pressed',m==='g');draw()};
    bv.onclick=function(){setMode('v')};bg.onclick=function(){setMode('g')};
    var done=false;
    document.getElementById('chBtn').onclick=function(){
      if(done)return;done=true;
      document.getElementById('challenge').classList.add('done');
      this.textContent='Feito';document.getElementById('chS').textContent='Concluído hoje';
      document.getElementById('streakN').textContent='13';
    };
  }
})();

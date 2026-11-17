# Website Pro Gym Fitness

Website estático (HTML, CSS e JS, sem base de dados) pronto a publicar. Mantém os mesmos endereços do site antigo (/gyms/mares, /pricing, /plans, /services, /store, /contact, /gallery), por isso as ligações já indexadas no Google continuam a funcionar.

## 1. Imagens
As 46 imagens do site antigo já estão incluídas em `site/assets/img/` (otimizadas, 10 MB no total). Assim o site continua completo quando o domínio passar para o novo alojamento.
Para ver o site no PC: abrir `index.html` no navegador.

## 2. Publicar
Qualquer alojamento de ficheiros estáticos serve (GitHub Pages, Netlify, Cloudflare Pages, Hostinger). Publicar o conteúdo desta pasta (raiz do repositório).
- GitHub Pages: criar um repositório, ativar Pages (branch main, pasta root) e, em Settings > Pages > Custom domain, escrever o domínio (ex.: www.progym.co.mz). No DNS do domínio: CNAME de `www` para `<utilizador>.github.io`.
- O domínio usado em canonical, sitemap e partilhas está em `build.py` (`SITE_URL`). Se mudar, correr `python build.py`.

## 3. Editar conteúdo
Todo o texto, preços, moradas e telefones estão em `build.py`. Depois de editar, correr `python3 build.py` para regenerar as páginas.

## 4. Manter atualizado
- Horário de aulas: substituir `assets/img/plans/plano-mares.jpg`, `plano-matola.jpg` e `plano-alto-mae.jpg` todos os meses (o do Zimpeto não existe no site antigo).
- Contactos: o site antigo mostra `progym@gmail.com` nas páginas de Alto Maé e Zimpeto. Neste site usamos `info@progym.co.mz` em todo o lado. Confirmar com o Pro Gym.
- Os formulários abrem o WhatsApp da administração (+258 84 441 4441) com a mensagem pronta; não guardam dados.
- A página da app (/app/) anuncia a app como "Brevemente". Ajustar quando houver data.


## Motion design (versão 2)

- Animações com GSAP + ScrollTrigger (ficheiros em `assets/js/vendor/`, auto-alojados) e CSS. Tudo em `assets/js/site.js` e `assets/css/style.css`.
- O site funciona sem JavaScript, sem GSAP e com `prefers-reduced-motion`: os estados escondidos só existem sob `html.motion`.
- Em ecrãs até 900px as animações pesadas (paralaxe, faixa horizontal de ginásios) ficam desligadas.
- Transições entre páginas: View Transitions do browser (onde existirem) + barra de progresso.
- Fontes auto-alojadas em `assets/fonts/`. Versões reduzidas das imagens em `assets/img/_s/` são geradas pelo `build.py` (precisa de `pip install pillow`).

## Idiomas (português e inglês)
- O texto-fonte está em português no `build.py`; as traduções para inglês estão todas em `i18n.py` (chave = texto em português).
- `python3 build.py` gera as duas versões: português na raiz e inglês em `/en/` (mesma estrutura de páginas).
- Se faltar uma tradução, o build falha e lista os textos em falta. Para mudar um texto, altera-o no `build.py` e na chave/valor correspondente do `i18n.py`.
- Seletor PT | EN no cabeçalho (mantém a página e o separador). Quem tem o navegador noutra língua vê um aviso discreto a oferecer o inglês (sem redirecionamento automático, para não prejudicar o Google).
- `hreflang`, canonical e sitemap com as duas línguas. Mensagens de WhatsApp em inglês levam também a versão em português para a receção.
- O estado "Aberto agora" respeita os feriados nacionais de data fixa e a Sexta-feira Santa.

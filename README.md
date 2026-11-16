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

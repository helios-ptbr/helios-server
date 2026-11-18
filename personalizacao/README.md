# Personalização da instância

Os arquivos desta pasta são entregues pelo Caddy em `/personalizacao/`.
Eles não entram na imagem: trocar um arquivo vale na hora, sem reconstruir nada.

## Trocar a logo da página inicial

1. Copie a logo para esta pasta, por exemplo `logo.png`.
2. No `.env`, ponha:

   ```
   MAIN_LOGO_URL=/personalizacao/logo.png
   ```

3. Aplique: `docker compose up -d`

Aceita png, svg, jpg, gif e webp. Sem a linha `MAIN_LOGO_URL`, vale a logo do Helios.
A logo do rodapé funciona igual, com `FOOTER_LOGO_URL`.

O navegador guarda a imagem em cache. Se trocar o arquivo mantendo o nome, recarregue com `Ctrl+Shift+R`.

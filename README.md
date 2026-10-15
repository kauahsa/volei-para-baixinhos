# Vôlei para Baixinhos — Página de Inscrição

Site de inscrição com visual divertido ("cartoon") para o projeto esportivo
**Vôlei para Baixinhos** (iniciação ao voleibol para crianças de 6 a 12 anos).

O site é uma página estática que envia as respostas diretamente para um
**Google Forms** por trás dos panos — o usuário interage com a página animada,
e os dados caem nas respostas do formulário.

## Recursos
- Visual cartoon kid-friendly (cores de bola de vôlei, bordas grossas, sombras)
- Bola de vôlei em SVG quicando no topo
- Bolas atravessando a tela
- Botão "CORTAR BOLA!" com animação de cortada ao enviar
- Tela de sucesso "PONTOOO! 🏆"
- Responsivo (Tailwind CSS)
- 16 campos integrados ao Google Forms

## Estrutura
```
index.html   # página única (HTML + CSS + JS inline, Tailwind via CDN)
```

## Como funciona o envio
O formulário envia via POST para o endpoint público `/formResponse` do Google
Forms, usando os `entry.XXX` de cada campo. Como o formulário tem múltiplas
páginas (seções), o parâmetro `pageHistory=0,1,2` é enviado junto — sem ele o
Google descarta os campos.

## Publicação (GitHub Pages)
A página fica em `index.html` na raiz do repositório. Basta ativar o GitHub
Pages apontando para a branch `main` e a pasta raiz (`/root`).

## Observações de segurança
As credenciais do Google (pasta `credenciais_google/`) **não** fazem parte deste
repositório e estão no `.gitignore`. Elas são usadas apenas pelos scripts locais
de administração do formulário, não pelo site.

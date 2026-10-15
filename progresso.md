# Progresso — Vôlei para Baixinhos

Última atualização: 2026-10-14 (noite)

## Objetivo do projeto
Criar um site com visual divertido ("cartoon", infantil mas elegante) que
funciona como uma "capa" bonita para um Google Forms. O usuário preenche a
página animada e as respostas são enviadas por trás dos panos para o Google
Forms (caem nas respostas / planilha do formulário).

---

## Estado atual (FUNCIONANDO)

- Site publicado e no ar via GitHub Pages.
- Envio para o Google Forms **confirmado funcionando** (15/16 campos no teste;
  o 16º era opcional e estava vazio de propósito).

### Links
- Repositório: https://github.com/kauahsa/volei-para-baixinhos
- Página no ar: https://kauahsa.github.io/volei-para-baixinhos/
- Form (editar): https://docs.google.com/forms/d/1S-rY0_AxEvtjG8HtA01DTkELMyMeP2fENbwuGTZEVuU/edit
- Form (responder/público): https://docs.google.com/forms/d/e/1FAIpQLSfR-CzMkIlt7yFYR_EjPBqjD1ip4Rpa7qXnd6lLeZkiPglKRA/viewform

### Conta GitHub
- Usuário logado no `gh`: **kauahsa** (HTTPS, token no keyring).

---

## O que foi feito (ordem cronológica)

1. **Formulário Google** ajustado via API (scripts Python):
   - Começou com 2 seções (Dados Pessoais, Saúde e Anamnese) + 2 autorizações.
   - Integradas as 4 perguntas pedidas (Endereço, Escola que estuda, Ano que
     estuda, Período que estuda [checkbox Matutino/Vespertino/Noturno]).
   - OBS: durante o processo, perguntas foram apagadas/recriadas — por isso os
     entry IDs foram re-extraídos. Form final tem **18 itens** (16 perguntas +
     2 cabeçalhos de seção).

2. **Site criado** (`index.html`), passou por 4 iterações de design:
   - v1: sóbrio (azul/branco)
   - v2: muito infantil (rosa/amarelo, bolas por todo lado, placar, confetes)
   - v3: sóbrio/moderno (marinho + laranja, painel de progresso)
   - v4 (ATUAL): estilo **cartoon** inspirado em um exemplo que o usuário
     mandou e aprovou — Tailwind via CDN, fontes Fredoka One/Nunito, bola SVG
     quicando, botão "CORTAR BOLA!" com animação de cortada, tela "PONTOOO! 🏆",
     bolas atravessando a tela, rede de vôlei no fundo, responsivo.

3. **Bug crítico resolvido — respostas chegavam VAZIAS:**
   - Causa: o formulário tem múltiplas páginas (3 seções no Google Forms).
   - Correção: enviar `pageHistory=0,1,2` e `fvv=1` junto no POST.
   - Diagnóstico comprovado via API:
     - sem pageHistory → 0 campos preenchidos
     - com pageHistory=0,1,2 → 15 campos preenchidos.
   - **Se adicionar/remover SEÇÕES no form, atualizar o pageHistory** (ver abaixo).

4. **Repositório + GitHub Pages:**
   - Git init, `.gitignore` protegendo credenciais e venv.
   - `index.html` movido para a RAIZ (necessário para o Pages servir direto).
   - Repositório público criado e push na branch `main`.
   - Pages ativado (branch main, pasta raiz). Build concluído, HTTP 200.

---

## Arquitetura do envio (como funciona)

O `index.html` monta um `<form>` dinâmico e envia via POST para o endpoint
público do Google:

```
https://docs.google.com/forms/d/e/1FAIpQLSfR-CzMkIlt7yFYR_EjPBqjD1ip4Rpa7qXnd6lLeZkiPglKRA/formResponse
```

- Cada campo usa seu `entry.XXXXX` (atributo `data-entry` no HTML).
- Campo de data é quebrado em `entry.XXX_year`, `_month`, `_day`.
- **Obrigatório:** incluir `pageHistory=0,1,2` e `fvv=1` (form multi-página).
- O POST vai para um `<iframe>` oculto (`target="form-sink"`) para evitar
  erro de CORS. Por causa do CORS, o site NÃO lê a confirmação do Google —
  mostra uma tela de sucesso própria ("PONTOOO!") no `load` do iframe
  (ou após timeout de 2.5s como fallback).

---

## Mapa de campos (entry IDs atuais)

| Campo                                           | entry ID            | Tipo     |
|-------------------------------------------------|---------------------|----------|
| Nome completo                                   | entry.1370952004    | texto    |
| Data de Nascimento                              | entry.1488058502    | data (*) |
| Endereço                                        | entry.581525485     | texto    |
| Contato do Responsável (telefone/WhatsApp)      | entry.1434602677    | texto    |
| Responsável (se for menor de idade)             | entry.427304794     | texto    |
| Escola que estuda                               | entry.1568824317    | texto    |
| Ano que estuda                                  | entry.821365109     | texto    |
| Período que estuda                              | entry.1805480479    | checkbox |
| Peso (kg)                                       | entry.923750615     | texto    |
| Altura (cm)                                     | entry.12013773      | texto    |
| Realiza atividades físicas?                     | entry.1538158661    | radio    |
| Frequência das atividades                       | entry.1422109174    | radio    |
| Possui contraindicação?                         | entry.788633501     | radio    |
| Se sim, qual contraindicação? (descreva)        | entry.1322975328    | texto (opcional) |
| Autorizo participação (responsável)             | entry.1402413891    | radio    |
| Autorizo uso de imagem                          | entry.791338550     | radio    |

(*) data enviada como `_year` / `_month` / `_day`.

---

## Ambiente local

- Pasta do projeto: `C:\Users\Andre\projeto-forms`
- Python venv em `venv/` (bibliotecas Google já instaladas: ver `requirements.txt`)
- Credenciais OAuth em `credenciais_google/` (credentials.json + token.json)
  — **NÃO versionadas** (estão no .gitignore).
- Scripts de administração do form (usam a Google Forms API):
  - `criar_form.py` — cria o form do zero
  - `atualizar_form.py` — atualiza título/descrição e adiciona itens
  - `restaurar_form.py` — reconstrói todas as perguntas + as 4 da imagem

### Como rodar os scripts (PowerShell, dentro da pasta)
```
$env:PYTHONIOENCODING="utf-8"
venv\Scripts\python.exe <script>.py
```
A saída às vezes não aparece direto no terminal; redirecionar ajuda:
```
venv\Scripts\python.exe <script>.py 2>&1 | Out-File -FilePath _saida.txt -Encoding utf8
Get-Content _saida.txt -Encoding utf8
```

### Escopos OAuth
- `forms.body` — criar/editar formulário (token atual tem este).
- `forms.responses.readonly` — ler respostas (exige reautorização; ao usar,
  o navegador abre pedindo login). Para forçar: apagar `token.json`
  (fazer backup antes) e rodar o script com os dois escopos.

---

## Como atualizar a página (deploy)
1. Editar `index.html`.
2. `git add -A && git commit -m "..." && git push`
3. O GitHub Pages republica automaticamente em ~1 min.

---

## Pendências / ideias para amanhã

- [ ] **Limpar respostas de teste** no Google Forms (há respostas vazias
      antigas + a "DIAG com pageHistory"). Fazer em Respostas → lixeira.
- [ ] **Testar um envio real pela página publicada** (produção) e confirmar
      na planilha que chega completo. (Em local já validamos via API.)
- [ ] Revisar textos/labels do site se quiser (ex.: "Vespertino" x "Vespetino").
- [ ] (Opcional) Adicionar confetes na tela "PONTOOO!".
- [ ] (Opcional) Favicon e meta tags (título/preview ao compartilhar link).
- [ ] (Opcional) Validações extras: telefone, peso/altura numéricos.
- [ ] A pasta `site/` ficou vazia após mover o index para a raiz — pode remover.
- [ ] Arquivo `_entries.json` é um resíduo da extração — pode remover (está no
      .gitignore, não vai pro repo, mas é lixo local).

## Armadilhas conhecidas (NÃO esquecer)
- Se editar o form e **recriar perguntas**, os `entry IDs` podem mudar →
  re-extrair da página pública (script que lê `FB_PUBLIC_LOAD_DATA_`).
- Se **adicionar/remover seções**, ajustar o `pageHistory` no `index.html`
  (ex.: 4 páginas → `0,1,2,3`).
- Nunca commitar `credenciais_google/`.

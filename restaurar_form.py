"""
Restaura o formulario "Volei para Baixinhos" com TODAS as perguntas originais
e integra as 4 perguntas pedidas na imagem:

  - Endereco              -> mantido (texto obrigatorio)
  - Escola que estuda:    -> substitui "Escola / Serie / Periodo"
  - Ano que estuda:       -> nova (texto obrigatorio)
  - Periodo que estuda:   -> nova (checkbox: Matutino / Vespertino / Noturno)

As demais perguntas originais sao mantidas.

Reutiliza o token salvo em credenciais_google/token.json.
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_CREDENCIAIS = os.path.join(BASE_DIR, "credenciais_google")
ARQUIVO_CREDENCIAIS = os.path.join(PASTA_CREDENCIAIS, "credentials.json")
ARQUIVO_TOKEN = os.path.join(PASTA_CREDENCIAIS, "token.json")

SCOPES = ["https://www.googleapis.com/auth/forms.body"]
FORM_ID = "1S-rY0_AxEvtjG8HtA01DTkELMyMeP2fENbwuGTZEVuU"


def autenticar():
    creds = None
    if os.path.exists(ARQUIVO_TOKEN):
        creds = Credentials.from_authorized_user_file(ARQUIVO_TOKEN, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                ARQUIVO_CREDENCIAIS, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(ARQUIVO_TOKEN, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    return creds


def pergunta_texto(titulo, obrigatoria=True, paragrafo=False):
    return {
        "title": titulo,
        "questionItem": {
            "question": {
                "required": obrigatoria,
                "textQuestion": {"paragraph": paragrafo},
            }
        },
    }


def pergunta_data(titulo, obrigatoria=True):
    return {
        "title": titulo,
        "questionItem": {
            "question": {
                "required": obrigatoria,
                "dateQuestion": {"includeYear": True, "includeTime": False},
            }
        },
    }


def pergunta_escolha(titulo, opcoes, obrigatoria=True, tipo="RADIO"):
    return {
        "title": titulo,
        "questionItem": {
            "question": {
                "required": obrigatoria,
                "choiceQuestion": {
                    "type": tipo,
                    "options": [{"value": o} for o in opcoes],
                },
            }
        },
    }


def cabecalho_secao(titulo, descricao=""):
    item = {"title": titulo, "pageBreakItem": {}}
    if descricao:
        item["description"] = descricao
    return item


def montar_itens():
    return [
        # ---- Secao 1: Dados Pessoais ----
        cabecalho_secao("Dados Pessoais"),
        pergunta_texto("Nome completo"),
        pergunta_data("Data de Nascimento"),
        pergunta_texto("Endere\u00e7o"),                       # imagem
        pergunta_texto("Contato (telefone / WhatsApp)"),
        pergunta_texto("Responsavel (se for menor de idade)", obrigatoria=False),
        pergunta_texto("Escola que estuda:"),                  # imagem
        pergunta_texto("Ano que estuda:"),                     # imagem (nova)
        pergunta_escolha(                                      # imagem (nova)
            "Per\u00edodo que estuda:",
            ["Matutino", "Vespertino", "Noturno"],
            tipo="CHECKBOX",
        ),

        # ---- Secao 2: Saude e Anamnese ----
        cabecalho_secao("Saude e Anamnese"),
        pergunta_texto("Peso (kg)"),
        pergunta_texto("Altura (cm)"),
        pergunta_escolha("Realiza atividades fisicas?", ["Sim", "Nao"]),
        pergunta_escolha(
            "Frequencia das atividades",
            ["Nenhuma", "1x por semana", "2x por semana", "3x ou mais por semana"],
        ),
        pergunta_escolha(
            "Possui alguma contraindicacao para realizar as atividades?",
            ["Nao", "Sim"],
        ),
        pergunta_texto(
            "Se sim, qual contraindicacao? (descreva)",
            obrigatoria=False,
            paragrafo=True,
        ),

        # ---- Autorizacoes ----
        pergunta_escolha(
            "Autorizo a participa\u00e7\u00e3o da crian\u00e7a no projeto "
            "\u201cV\u00f4lei para Baixinhos\u201d. (Responsavel)",
            ["Sim, autorizo"],
            tipo="RADIO",
        ),
        pergunta_escolha(
            "Autorizo o uso de imagem da crian\u00e7a (fotos/v\u00eddeos) "
            "para fins de divulga\u00e7\u00e3o do projeto.",
            ["Sim, autorizo", "N\u00e3o autorizo"],
            tipo="RADIO",
        ),
    ]


def main():
    creds = autenticar()
    service = build("forms", "v1", credentials=creds)

    # 1) Le o form atual para saber quantos itens remover
    form = service.forms().get(formId=FORM_ID).execute()
    qtd = len(form.get("items", []))

    requests = []
    # 2) Remove itens atuais (de tras para frente)
    for indice in range(qtd - 1, -1, -1):
        requests.append({"deleteItem": {"location": {"index": indice}}})

    # 3) Recria todos os itens na ordem
    for indice, item in enumerate(montar_itens()):
        requests.append(
            {"createItem": {"item": item, "location": {"index": indice}}}
        )

    service.forms().batchUpdate(
        formId=FORM_ID, body={"requests": requests}
    ).execute()

    print("OK: formulario reconstruido com as perguntas originais + as 4 da imagem.")


if __name__ == "__main__":
    main()

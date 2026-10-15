"""
Atualiza o formulario de inscricao existente do projeto "Volei para Baixinhos":
  - Atualiza o titulo oficial
  - Melhora a descricao do topo (resumo curto)
  - Adiciona campo de autorizacao do responsavel
  - Adiciona campo de autorizacao de uso de imagem

Reutiliza o token salvo em credenciais_google/token.json (nao pede login de novo).

Como rodar (no PowerShell, dentro da pasta do projeto):
  venv/Scripts/python.exe atualizar_form.py
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

# ID do formulario ja criado
FORM_ID = "1S-rY0_AxEvtjG8HtA01DTkELMyMeP2fENbwuGTZEVuU"

TITULO = "V\u00f4lei para baixinhos - Inicia\u00e7\u00e3o esportiva ao voleibol"

DESCRICAO = (
    "Inscri\u00e7\u00e3o para o projeto de inicia\u00e7\u00e3o esportiva ao "
    "voleibol.\n\n"
    "P\u00fablico-alvo: crian\u00e7as de 6 a 12 anos, iniciantes na pr\u00e1tica "
    "do voleibol.\n"
    "Local: gin\u00e1sio ou quadra esportiva.\n"
    "Frequ\u00eancia: duas aulas semanais.\n\n"
    "Preencha os dados abaixo para realizar a inscri\u00e7\u00e3o da crian\u00e7a."
)


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


def main():
    creds = autenticar()
    service = build("forms", "v1", credentials=creds)

    # Descobre quantos itens o form ja tem, para inserir os novos no final
    form = service.forms().get(formId=FORM_ID).execute()
    qtd_itens = len(form.get("items", []))

    requests = [
        # 1) Atualiza titulo e descricao
        {
            "updateFormInfo": {
                "info": {"title": TITULO, "description": DESCRICAO},
                "updateMask": "title,description",
            }
        },
        # 2) Autorizacao do responsavel (adicionada ao final)
        {
            "createItem": {
                "item": pergunta_escolha(
                    "Autorizo a participa\u00e7\u00e3o da crian\u00e7a no projeto "
                    "\u201cV\u00f4lei para Baixinhos\u201d. (Responsavel)",
                    ["Sim, autorizo"],
                ),
                "location": {"index": qtd_itens},
            }
        },
        # 3) Autorizacao de uso de imagem
        {
            "createItem": {
                "item": pergunta_escolha(
                    "Autorizo o uso de imagem da crian\u00e7a (fotos/v\u00eddeos) "
                    "para fins de divulga\u00e7\u00e3o do projeto.",
                    ["Sim, autorizo", "N\u00e3o autorizo"],
                ),
                "location": {"index": qtd_itens + 1},
            }
        },
    ]

    service.forms().batchUpdate(
        formId=FORM_ID, body={"requests": requests}
    ).execute()

    print("Formulario atualizado com sucesso!")
    print(f"  Editar    : https://docs.google.com/forms/d/{FORM_ID}/edit")


if __name__ == "__main__":
    main()

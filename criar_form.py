"""
Cria o formulario de inscricao do projeto "Volei para Baixinhos"
usando a Google Forms API.

Estrutura do formulario:
  - Cabecalho com descricao do projeto
  - Secao 1: Dados Pessoais
  - Secao 2: Saude e Anamnese

Pre-requisitos:
  - Google Forms API ativada no projeto do Google Cloud
  - Arquivo de credenciais OAuth em: credenciais_google/credentials.json
  - Seu e-mail adicionado como "usuario de teste" na tela de consentimento OAuth

Como rodar (no PowerShell, dentro da pasta do projeto):
  venv/Scripts/python.exe criar_form.py
  (as bibliotecas ja estao instaladas no venv)

Na primeira execucao o navegador vai abrir pedindo login/autorizacao.
Faca login com a conta cadastrada como usuario de teste.
O token fica salvo em credenciais_google/token.json para as proximas vezes.
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Diretorio base = pasta onde este script esta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_CREDENCIAIS = os.path.join(BASE_DIR, "credenciais_google")
ARQUIVO_CREDENCIAIS = os.path.join(PASTA_CREDENCIAIS, "credentials.json")
ARQUIVO_TOKEN = os.path.join(PASTA_CREDENCIAIS, "token.json")

# Permissao necessaria para criar/editar formularios
SCOPES = ["https://www.googleapis.com/auth/forms.body"]

TITULO = "Inscricao - Volei para Baixinhos"

DESCRICAO = (
    "O projeto \u201cVolei para Baixinhos\u201d tem como objetivo promover a "
    "iniciacao esportiva ao voleibol para criancas de 6 a 12 anos, por meio de "
    "atividades ludicas e treinos adaptados a faixa etaria. O projeto busca "
    "desenvolver habilidades motoras, estimular a socializacao, a cooperacao e o "
    "respeito, alem de incentivar o interesse pela pratica esportiva. As aulas "
    "serao realizadas duas vezes por semana, com atividades progressivas, jogos e "
    "acompanhamento da evolucao dos participantes."
)


def autenticar():
    """Faz o fluxo OAuth e retorna as credenciais validas."""
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


# ----- Funcoes auxiliares para montar cada tipo de pergunta -----

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
    """Cria um 'pageBreak' que inicia uma nova secao."""
    item = {"title": titulo, "pageBreakItem": {}}
    if descricao:
        item["description"] = descricao
    return item


def montar_requests():
    """Monta a lista de itens na ordem em que devem aparecer."""
    itens = [
        # ---- Secao 1: Dados Pessoais ----
        cabecalho_secao("Dados Pessoais"),
        pergunta_texto("Nome completo"),
        pergunta_data("Data de Nascimento"),
        pergunta_texto("Endereco"),
        pergunta_texto("Contato (telefone / WhatsApp)"),
        pergunta_texto("Responsavel (se for menor de idade)", obrigatoria=False),
        pergunta_texto("Escola / Serie / Periodo"),

        # ---- Secao 2: Saude e Anamnese ----
        cabecalho_secao("Saude e Anamnese"),
        pergunta_texto("Peso (kg)"),
        pergunta_texto("Altura (cm)"),
        pergunta_escolha(
            "Realiza atividades fisicas?",
            ["Sim", "Nao"],
        ),
        pergunta_escolha(
            "Frequencia das atividades",
            [
                "Nenhuma",
                "1x por semana",
                "2x por semana",
                "3x ou mais por semana",
            ],
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
    ]

    # Transforma cada item em um request createItem com o indice correto
    requests = []
    for indice, item in enumerate(itens):
        requests.append(
            {"createItem": {"item": item, "location": {"index": indice}}}
        )
    return requests


def criar_formulario(service):
    # 1) Cria o formulario apenas com o titulo (a API nao aceita description no create)
    novo_form = {
        "info": {
            "title": TITULO,
            "documentTitle": TITULO,
        }
    }
    resultado = service.forms().create(body=novo_form).execute()
    form_id = resultado["formId"]

    # 2) Define a descricao do formulario + adiciona todos os itens
    requests = [
        {
            "updateFormInfo": {
                "info": {"description": DESCRICAO},
                "updateMask": "description",
            }
        }
    ]
    requests.extend(montar_requests())

    service.forms().batchUpdate(
        formId=form_id, body={"requests": requests}
    ).execute()

    return resultado


def main():
    if not os.path.exists(ARQUIVO_CREDENCIAIS):
        print("ERRO: arquivo de credenciais nao encontrado em:")
        print(f"  {ARQUIVO_CREDENCIAIS}")
        return

    creds = autenticar()
    service = build("forms", "v1", credentials=creds)

    print("Criando o formulario 'Volei para Baixinhos'...")
    resultado = criar_formulario(service)

    form_id = resultado["formId"]
    link_responder = resultado.get("responderUri", "")
    print("\n==============================================")
    print("Formulario criado com sucesso!")
    print(f"  ID do form : {form_id}")
    print(f"  Editar     : https://docs.google.com/forms/d/{form_id}/edit")
    if link_responder:
        print(f"  Responder  : {link_responder}")
    print("==============================================")


if __name__ == "__main__":
    main()

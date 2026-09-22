import os

import pyodbc
import win32print
from dotenv import load_dotenv
from datetime import datetime


# --------------------------------------------------
# 1. CARREGAR CONFIGURAÇÕES DO ARQUIVO .env
# --------------------------------------------------

load_dotenv()

servidor = os.getenv("DB_SERVER")
banco = os.getenv("DB_DATABASE")
usuario = os.getenv("DB_USER")
senha = os.getenv("DB_PASSWORD")
driver = os.getenv("DB_DRIVER")


# Nome da impressora que já testamos
NOME_IMPRESSORA = "ZDesigner ZD220-203dpi ZPL"


# --------------------------------------------------
# 2. FUNÇÃO PARA CONVERTER O IDENTIFICADOR EM QR
# --------------------------------------------------

def gerar_codigo_qr(identificador):
    identificador = str(identificador).strip()

    return identificador.zfill(10)

def montar_paciente_setor(nome, obs, quem_visitar_nome):

    if quem_visitar_nome:
        return quem_visitar_nome

    if obs:
        return f"{nome} {obs}".strip()

    return nome


# --------------------------------------------------
# 3. FUNÇÃO PARA GERAR A ETIQUETA ZPL
# --------------------------------------------------

def gerar_etiqueta(
    nome,
    codigo_qr,
    nivel_acesso,
    paciente_setor,
    validade
):
    # Data e hora em que a etiqueta está sendo impressa
    emissao = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    # Se algum dado estiver vazio, mostramos uma informação padrão
    if not nivel_acesso or nivel_acesso == "<Nenhum>":
        nivel_acesso = "SEM NIVEL"

    if not paciente_setor:
        paciente_setor = "-"

    if not validade:
        validade = "SEM VALIDADE"

    zpl = f"""
^XA
^PW832
^LL406
^LH0,0

^FO30,50
^BQN,2,150
^FDLA,{codigo_qr}^FS

^FO350,20
^A0N,30,30
^FD{nome}^FS

^FO350,65
^A0N,19,19
^FDTIPO DE ACESSO^FS

^FO350,88
^A0N,23,23
^FD{nivel_acesso}^FS

^FO350,135
^A0N,19,19
^FDPACIENTE / SETOR^FS

^FO350,158
^A0N,23,23
^FD{paciente_setor}^FS

^FO350,215
^A0N,19,19
^FDDATA DA EMISSAO^FS

^FO350,238
^A0N,22,22
^FD{emissao}^FS

^FO350,285
^A0N,19,19
^FDVALIDADE^FS

^FO350,308
^A0N,22,22
^FD{validade}^FS

^XZ
"""

    return zpl


# --------------------------------------------------
# 4. FUNÇÃO PARA ENVIAR A ETIQUETA PARA A ZEBRA
# --------------------------------------------------

def imprimir_etiqueta(zpl):

    impressora = win32print.OpenPrinter(
        NOME_IMPRESSORA
    )

    try:
        win32print.StartDocPrinter(
            impressora,
            1,
            (
                "Etiqueta Secullum",
                None,
                "RAW"
            )
        )

        win32print.StartPagePrinter(
            impressora
        )

        win32print.WritePrinter(
            impressora,
            zpl.encode("utf-8")
        )

        win32print.EndPagePrinter(
            impressora
        )

        win32print.EndDocPrinter(
            impressora
        )

    finally:
        win32print.ClosePrinter(
            impressora
        )


# --------------------------------------------------
# 5. CONFIGURAÇÃO DA CONEXÃO COM O SQL SERVER
# --------------------------------------------------

connection_string = (
    f"DRIVER={{{driver}}};"
    f"SERVER={servidor};"
    f"DATABASE={banco};"
    f"UID={usuario};"
    f"PWD={senha};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)


# --------------------------------------------------
# 6. PEDIR O IDENTIFICADOR
# --------------------------------------------------

identificador_digitado = input(
    "Digite o Nº Identificador: "
).strip()


try:

    # --------------------------------------------------
    # 7. CONECTAR NO BANCO
    # --------------------------------------------------

    conexao = pyodbc.connect(
        connection_string,
        timeout=5
    )

    cursor = conexao.cursor()


    # --------------------------------------------------
    # 8. PROCURAR A PESSOA NO SECULLUM
    # --------------------------------------------------

    cursor.execute(
        """
    SELECT
        p.id,
        p.n_identificador,
        p.nome,

        n.descricao AS nivel_acesso,

        p.obs,

        p.quem_visitar_id,
        q.nome AS quem_visitar_nome,

        CONCAT(
            CONVERT(
                VARCHAR(10),
                p.validade_data_fim,
                103
            ),
            ' ',
            p.validade_hora_fim
        ) AS validade

    FROM pessoas AS p

    LEFT JOIN niveis AS n
        ON n.id = p.nivel_id

    LEFT JOIN pessoas AS q
        ON q.id = p.quem_visitar_id

    WHERE p.n_identificador = ?
    """,
    identificador_digitado
    )

    pessoa = cursor.fetchone()


    # --------------------------------------------------
    # 9. VERIFICAR SE ENCONTROU
    # --------------------------------------------------

    if pessoa is None:

        print()
        print("Credencial não encontrada.")


    else:

        codigo_qr = gerar_codigo_qr(
            pessoa.n_identificador
        )

        paciente_setor = montar_paciente_setor(
            pessoa.nome,
            pessoa.obs,
            pessoa.quem_visitar_nome
        )

        print()
        print("Registro encontrado!")
        print("-------------------------------------")

        print(
            f"Nome: {pessoa.nome}"
        )

        print(
            f"Nível de acesso: "
            f"{pessoa.nivel_acesso}"
        )

        print(
            f"Quem visitar: "
            f"{pessoa.quem_visitar_nome}"
        )

        print(
            f"Observação: "
            f"{pessoa.obs}"
        )

        print(
            f"Paciente / Setor: "
            f"{paciente_setor}"
        )

        print(
            f"Validade: "
            f"{pessoa.validade}"
        )

        print(
            f"Nº Identificador: "
            f"{pessoa.n_identificador}"
        )

        print(
            f"QR Code: {codigo_qr}"
        )

        print("-------------------------------------")

        resposta = input(
            "Deseja imprimir esta etiqueta? (S/N): "
        ).strip().upper()


        # --------------------------------------------------
        # 10. IMPRIMIR
        # --------------------------------------------------

        if resposta == "S":

            zpl = gerar_etiqueta(
                nome=pessoa.nome,
                codigo_qr=codigo_qr,
                nivel_acesso=pessoa.nivel_acesso,
                paciente_setor=paciente_setor,
                validade=pessoa.validade
            )

            imprimir_etiqueta(zpl)

            print()
            print(
                "Etiqueta enviada para a Zebra!"
            )

        else:

            print()
            print(
                "Impressão cancelada."
            )


    cursor.close()
    conexao.close()


except pyodbc.Error as erro:

    print()
    print(
        "Erro ao acessar o banco:"
    )
    print(erro)


except Exception as erro:

    print()
    print(
        "Ocorreu um erro:"
    )
    print(erro)
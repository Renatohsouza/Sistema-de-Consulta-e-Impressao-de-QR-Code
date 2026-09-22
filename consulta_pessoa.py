import os

import pyodbc
from dotenv import load_dotenv


# Carrega as informações que estão no arquivo .env
load_dotenv()


# Lê as configurações do banco
servidor = os.getenv("DB_SERVER")
banco = os.getenv("DB_DATABASE")
usuario = os.getenv("DB_USER")
senha = os.getenv("DB_PASSWORD")
driver = os.getenv("DB_DRIVER")


# Configuração da conexão com o SQL Server
connection_string = (
    f"DRIVER={{{driver}}};"
    f"SERVER={servidor};"
    f"DATABASE={banco};"
    f"UID={usuario};"
    f"PWD={senha};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)


# Pergunta qual identificador queremos procurar
identificador = input(
    "Digite o Nº Identificador: "
).strip()


try:
    # Abre a conexão
    conexao = pyodbc.connect(
        connection_string,
        timeout=5
    )

    # Cria o cursor para executar SQL
    cursor = conexao.cursor()

    # Busca a pessoa pelo Nº Identificador
    cursor.execute(
        """
        SELECT
            id,
            n_identificador,
            nome
        FROM pessoas
        WHERE n_identificador = ?
        """,
        identificador
    )

    pessoa = cursor.fetchone()

    # Verifica se encontrou alguma pessoa
    if pessoa is None:
        print()
        print("Nenhum registro encontrado.")

    else:
        # Converte para texto e completa com zeros à esquerda
        codigo_qr = str(
            pessoa.n_identificador
        ).strip().zfill(10)

        print()
        print("Registro encontrado!")
        print("-----------------------------")
        print(f"ID interno: {pessoa.id}")
        print(
            f"Nº Identificador: "
            f"{pessoa.n_identificador}"
        )
        print(f"Nome: {pessoa.nome}")
        print(f"QR Code: {codigo_qr}")
        print("-----------------------------")

    # Fecha cursor e conexão
    cursor.close()
    conexao.close()

except pyodbc.Error as erro:
    print()
    print("Erro ao consultar o banco:")
    print(erro)
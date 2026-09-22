import os

import pyodbc
from dotenv import load_dotenv


load_dotenv()


servidor = os.getenv("DB_SERVER")
banco = os.getenv("DB_DATABASE")
usuario = os.getenv("DB_USER")
senha = os.getenv("DB_PASSWORD")
driver = os.getenv("DB_DRIVER")


connection_string = (
    f"DRIVER={{{driver}}};"
    f"SERVER={servidor};"
    f"DATABASE={banco};"
    f"UID={usuario};"
    f"PWD={senha};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)


try:
    conexao = pyodbc.connect(
        connection_string,
        timeout=5
    )

    print("Conectado ao _BANCO XYZ_")
    print()

    cursor = conexao.cursor()

    cursor.execute("""
        SELECT TOP 10
            id,
            n_identificador,
            nome
        FROM pessoas
        ORDER BY id DESC
    """)

    registros = cursor.fetchall()

    print("Últimos registros encontrados:")
    print()

    for registro in registros:
        print(
            f"ID: {registro.id} | "
            f"Identificador: {registro.n_identificador} | "
            f"Nome: {registro.nome}"
        )

    cursor.close()
    conexao.close()

except pyodbc.Error as erro:
    print("Erro:")
    print(erro)
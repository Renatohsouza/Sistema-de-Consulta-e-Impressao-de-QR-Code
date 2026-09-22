import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import pyodbc
import win32print
from dotenv import load_dotenv


# ============================================================
# CONFIGURAÇÕES
# ============================================================

load_dotenv()

DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER")

PRINTER_NAME = os.getenv(
    "PRINTER_NAME",
    "ZDesigner ZD220-203dpi ZPL"
)


# ============================================================
# BANCO DE DADOS
# ============================================================

def criar_conexao():
    """
    Cria e devolve uma conexão com o SQL Server.
    """

    connection_string = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_DATABASE};"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(
        connection_string,
        timeout=5
    )


def normalizar_cpf(cpf):
    """
    Remove pontos, traços e espaços do CPF digitado.
    """

    cpf = str(cpf).strip()

    cpf = cpf.replace(".", "")
    cpf = cpf.replace("-", "")
    cpf = cpf.replace(" ", "")

    return cpf


def buscar_pessoa_por_cpf(cpf):
    """
    Consulta o Secullum utilizando o CPF.

    Retorna o registro mais recente encontrado.
    """

    cpf = normalizar_cpf(cpf)

    conexao = criar_conexao()

    try:
        cursor = conexao.cursor()

        cursor.execute(
            """
            SELECT TOP 1
                p.id,
                p.cpf,
                p.n_identificador,
                p.nome,

                n.descricao AS nivel_acesso,

                p.obs,

                p.quem_visitar_id,
                q.nome AS quem_visitar_nome,

                CASE
                    WHEN
                        p.validade_data_fim IS NULL
                        AND (
                            p.validade_hora_fim IS NULL
                            OR LTRIM(RTRIM(p.validade_hora_fim)) = ''
                        )
                    THEN NULL

                    ELSE CONCAT(
                        CONVERT(
                            VARCHAR(10),
                            p.validade_data_fim,
                            103
                        ),
                        ' ',
                        p.validade_hora_fim
                    )
                END AS validade

            FROM pessoas AS p

            LEFT JOIN niveis AS n
                ON n.id = p.nivel_id

            LEFT JOIN pessoas AS q
                ON q.id = p.quem_visitar_id

            WHERE
                REPLACE(
                    REPLACE(
                        REPLACE(
                            p.cpf,
                            '.',
                            ''
                        ),
                        '-',
                        ''
                    ),
                    ' ',
                    ''
                ) = ?

            ORDER BY p.id DESC
            """,
            cpf
        )

        return cursor.fetchone()

    finally:
        conexao.close()


# ============================================================
# TRATAMENTO DAS INFORMAÇÕES
# ============================================================

def gerar_codigo_qr(identificador):
    """
    Transforma o Nº Identificador do Secullum
    em um código de 10 dígitos.
    """

    if identificador is None:
        return None

    identificador = str(
        identificador
    ).strip()

    if not identificador:
        return None

    if not identificador.isdigit():
        raise ValueError(
            "O Nº Identificador deve conter somente números."
        )

    if len(identificador) > 10:
        raise ValueError(
            "O Nº Identificador possui mais de 10 dígitos."
        )

    return identificador.zfill(10)


def montar_paciente_setor(
    nome,
    obs,
    quem_visitar_nome
):
    """
    Monta o texto apresentado no campo PACIENTE / SETOR.
    """

    if quem_visitar_nome:
        return str(
            quem_visitar_nome
        ).strip()

    if obs:
        return f"{nome} {obs}".strip()

    return nome or "-"


def limpar_texto_zpl(texto):
    """
    Remove caracteres que poderiam interferir
    nos comandos da impressora Zebra.
    """

    if texto is None:
        return ""

    texto = str(texto)

    texto = texto.replace("^", "")
    texto = texto.replace("~", "")

    return texto


# ============================================================
# ETIQUETA ZPL
# ============================================================

def gerar_etiqueta(
    nome,
    codigo_qr,
    nivel_acesso,
    paciente_setor,
    validade
):
    """
    Gera os comandos ZPL utilizados pela Zebra.
    """

    emissao = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    nome = limpar_texto_zpl(nome)
    nivel_acesso = limpar_texto_zpl(
        nivel_acesso
    )
    paciente_setor = limpar_texto_zpl(
        paciente_setor
    )
    validade = limpar_texto_zpl(
        validade
    )

    if (
        not nivel_acesso
        or nivel_acesso == "<Nenhum>"
    ):
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

^FO20,30
^BQN,2,11
^FDLA,{codigo_qr}^FS

^FO360,15
^A0N,34,34
^FD{nome}^FS

^FO360,65
^A0N,21,21
^FDTIPO DE ACESSO^FS

^FO360,91
^A0N,25,25
^FD{nivel_acesso}^FS

^FO360,145
^A0N,21,21
^FDPACIENTE / SETOR^FS

^FO360,171
^A0N,25,25
^FD{paciente_setor}^FS

^FO360,230
^A0N,21,21
^FDDATA DA EMISSAO^FS

^FO360,256
^A0N,24,24
^FD{emissao}^FS

^FO360,310
^A0N,21,21
^FDVALIDADE^FS

^FO360,336
^A0N,24,24
^FD{validade}^FS

^XZ
"""

    return zpl


# ============================================================
# IMPRESSÃO
# ============================================================

def imprimir_zpl(zpl):
    """
    Envia o ZPL diretamente para a Zebra pelo Windows.
    """

    impressora = win32print.OpenPrinter(
        PRINTER_NAME
    )

    try:
        win32print.StartDocPrinter(
            impressora,
            1,
            (
                "Etiqueta de Acesso",
                None,
                "RAW"
            )
        )

        try:
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

        finally:
            win32print.EndDocPrinter(
                impressora
            )

    finally:
        win32print.ClosePrinter(
            impressora
        )


# ============================================================
# INTERFACE
# ============================================================

class AppCredencial:

    def __init__(self, root):
        self.root = root

        self.root.title(
            "Impressão de Credencial"
        )

        self.root.geometry(
            "700x570"
        )

        self.root.resizable(
            False,
            False
        )

        # Armazena o último visitante encontrado
        self.pessoa_atual = None
        self.codigo_qr_atual = None
        self.paciente_setor_atual = None

        self.criar_interface()


    def criar_interface(self):

        titulo = ttk.Label(
            self.root,
            text="IMPRESSÃO DE CREDENCIAL",
            font=(
                "Segoe UI",
                18,
                "bold"
            )
        )

        titulo.pack(
            pady=(20, 5)
        )


        subtitulo = ttk.Label(
            self.root,
            text=(
                "Consulte o visitante pelo CPF "
                "e imprima sua credencial."
            ),
            font=(
                "Segoe UI",
                10
            )
        )

        subtitulo.pack(
            pady=(0, 20)
        )


        # ----------------------------------------------------
        # ÁREA DE BUSCA
        # ----------------------------------------------------

        frame_busca = ttk.Frame(
            self.root
        )

        frame_busca.pack(
            fill="x",
            padx=40
        )


        ttk.Label(
            frame_busca,
            text="CPF:"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=5
        )


        self.entry_cpf = ttk.Entry(
            frame_busca,
            width=35,
            font=(
                "Segoe UI",
                12
            )
        )

        self.entry_cpf.grid(
            row=1,
            column=0,
            padx=(0, 10)
        )


        self.botao_buscar = ttk.Button(
            frame_busca,
            text="Buscar",
            command=self.buscar
        )

        self.botao_buscar.grid(
            row=1,
            column=1,
            padx=5
        )


        self.botao_limpar = ttk.Button(
            frame_busca,
            text="Limpar",
            command=self.limpar
        )

        self.botao_limpar.grid(
            row=1,
            column=2,
            padx=5
        )


        # Enter também executa a busca
        self.entry_cpf.bind(
            "<Return>",
            lambda event: self.buscar()
        )


        # ----------------------------------------------------
        # DADOS DO VISITANTE
        # ----------------------------------------------------

        frame_dados = ttk.LabelFrame(
            self.root,
            text="Dados do visitante",
            padding=20
        )

        frame_dados.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=25
        )


        self.valor_nome = tk.StringVar(
            value="-"
        )

        self.valor_nivel = tk.StringVar(
            value="-"
        )

        self.valor_paciente = tk.StringVar(
            value="-"
        )

        self.valor_validade = tk.StringVar(
            value="-"
        )

        self.valor_identificador = tk.StringVar(
            value="-"
        )

        self.valor_qr = tk.StringVar(
            value="-"
        )


        campos = [
            (
                "Nome:",
                self.valor_nome
            ),
            (
                "Nível de acesso:",
                self.valor_nivel
            ),
            (
                "Paciente / Setor:",
                self.valor_paciente
            ),
            (
                "Validade:",
                self.valor_validade
            ),
            (
                "Nº Identificador:",
                self.valor_identificador
            ),
            (
                "QR Code:",
                self.valor_qr
            ),
        ]


        for linha, (
            descricao,
            variavel
        ) in enumerate(campos):

            ttk.Label(
                frame_dados,
                text=descricao,
                font=(
                    "Segoe UI",
                    10,
                    "bold"
                )
            ).grid(
                row=linha,
                column=0,
                sticky="w",
                pady=8
            )

            ttk.Label(
                frame_dados,
                textvariable=variavel,
                font=(
                    "Segoe UI",
                    10
                )
            ).grid(
                row=linha,
                column=1,
                sticky="w",
                padx=20,
                pady=8
            )


        # ----------------------------------------------------
        # BOTÃO DE IMPRESSÃO
        # ----------------------------------------------------

        self.botao_imprimir = ttk.Button(
            self.root,
            text="IMPRIMIR ETIQUETA",
            command=self.imprimir,
            state="disabled"
        )

        self.botao_imprimir.pack(
            ipadx=30,
            ipady=8,
            pady=(0, 10)
        )


        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.status = tk.StringVar(
            value="Aguardando consulta."
        )

        ttk.Label(
            self.root,
            textvariable=self.status,
            font=(
                "Segoe UI",
                9
            )
        ).pack(
            pady=(0, 15)
        )


        # Coloca o cursor direto no CPF
        self.entry_cpf.focus()


    # ========================================================
    # BUSCAR VISITANTE
    # ========================================================

    def buscar(self):

        cpf = self.entry_cpf.get()

        cpf = normalizar_cpf(
            cpf
        )

        if not cpf:
            messagebox.showwarning(
                "CPF",
                "Informe o CPF do visitante."
            )

            return


        self.status.set(
            "Consultando Secullum..."
        )

        self.root.update_idletasks()


        try:
            pessoa = buscar_pessoa_por_cpf(
                cpf
            )

        except pyodbc.Error as erro:

            self.status.set(
                "Erro na conexão com o banco."
            )

            messagebox.showerror(
                "Erro no banco de dados",
                str(erro)
            )

            return


        if pessoa is None:

            self.limpar_dados()

            self.status.set(
                "Visitante não encontrado."
            )

            messagebox.showwarning(
                "Visitante não encontrado",
                (
                    "Não foi encontrado um cadastro "
                    "para este CPF.\n\n"
                    "Realize o cadastro no "
                    "Secullum Acesso."
                )
            )

            return


        try:
            codigo_qr = gerar_codigo_qr(
                pessoa.n_identificador
            )

        except ValueError as erro:

            self.limpar_dados()

            messagebox.showerror(
                "Nº Identificador inválido",
                str(erro)
            )

            return


        paciente_setor = montar_paciente_setor(
            pessoa.nome,
            pessoa.obs,
            pessoa.quem_visitar_nome
        )


        # Guarda dados encontrados
        self.pessoa_atual = pessoa
        self.codigo_qr_atual = codigo_qr
        self.paciente_setor_atual = (
            paciente_setor
        )


        # Atualiza interface
        self.valor_nome.set(
            pessoa.nome or "-"
        )

        self.valor_nivel.set(
            pessoa.nivel_acesso or "-"
        )

        self.valor_paciente.set(
            paciente_setor or "-"
        )

        self.valor_validade.set(
            pessoa.validade or "-"
        )

        self.valor_identificador.set(
            pessoa.n_identificador
            if pessoa.n_identificador
            else "NÃO CADASTRADO"
        )

        self.valor_qr.set(
            codigo_qr
            if codigo_qr
            else "NÃO DISPONÍVEL"
        )


        # ----------------------------------------------------
        # VISITANTE SEM IDENTIFICADOR
        # ----------------------------------------------------

        if codigo_qr is None:

            self.botao_imprimir.config(
                state="disabled"
            )

            self.status.set(
                "Visitante sem Nº Identificador."
            )

            messagebox.showwarning(
                "Credencial não disponível",
                (
                    "O visitante foi encontrado, "
                    "mas ainda não possui Nº "
                    "Identificador cadastrado.\n\n"
                    "Preencha o Nº Identificador "
                    "no Secullum Acesso e depois "
                    "realize uma nova busca."
                )
            )

            return


        # ----------------------------------------------------
        # VISITANTE PRONTO PARA IMPRIMIR
        # ----------------------------------------------------

        self.botao_imprimir.config(
            state="normal"
        )

        self.status.set(
            "Visitante encontrado. "
            "Credencial pronta para impressão."
        )


    # ========================================================
    # IMPRIMIR
    # ========================================================

    def imprimir(self):

        if (
            self.pessoa_atual is None
            or self.codigo_qr_atual is None
        ):
            return


        confirmar = messagebox.askyesno(
            "Confirmar impressão",
            (
                "Deseja imprimir a credencial "
                "deste visitante?"
            )
        )


        if not confirmar:
            return


        try:
            zpl = gerar_etiqueta(
                nome=self.pessoa_atual.nome,
                codigo_qr=self.codigo_qr_atual,
                nivel_acesso=(
                    self.pessoa_atual.nivel_acesso
                ),
                paciente_setor=(
                    self.paciente_setor_atual
                ),
                validade=(
                    self.pessoa_atual.validade
                )
            )

            imprimir_zpl(
                zpl
            )


        except Exception as erro:

            self.status.set(
                "Erro durante a impressão."
            )

            messagebox.showerror(
                "Erro de impressão",
                str(erro)
            )

            return


        self.status.set(
            "Etiqueta enviada para a Zebra."
        )

        messagebox.showinfo(
            "Impressão",
            "Etiqueta enviada com sucesso!"
        )


    # ========================================================
    # LIMPAR TELA
    # ========================================================

    def limpar_dados(self):

        self.pessoa_atual = None
        self.codigo_qr_atual = None
        self.paciente_setor_atual = None

        self.valor_nome.set("-")
        self.valor_nivel.set("-")
        self.valor_paciente.set("-")
        self.valor_validade.set("-")
        self.valor_identificador.set("-")
        self.valor_qr.set("-")

        self.botao_imprimir.config(
            state="disabled"
        )


    def limpar(self):

        self.entry_cpf.delete(
            0,
            tk.END
        )

        self.limpar_dados()

        self.status.set(
            "Aguardando consulta."
        )

        self.entry_cpf.focus()


# ============================================================
# INICIAR PROGRAMA
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = AppCredencial(
        root
    )

    root.mainloop()
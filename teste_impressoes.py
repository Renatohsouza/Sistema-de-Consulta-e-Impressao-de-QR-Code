import win32print


NOME_IMPRESSORA = "ZDesigner ZD220-203dpi ZPL"


zpl = """
^XA

^PW832
^LL406

^FO330,40
^A0N,40,40
^FDTESTE PYTHON^FS

^FO330,100
^A0N,25,25
^FDIMPRESSAO ZEBRA^FS

^FO40,50
^BQN,2,7
^FDLA,0000123489^FS

^XZ
"""


impressora = win32print.OpenPrinter(NOME_IMPRESSORA)

try:
    win32print.StartDocPrinter(
        impressora,
        1,
        ("Teste Python", None, "RAW")
    )

    win32print.StartPagePrinter(impressora)

    win32print.WritePrinter(
        impressora,
        zpl.encode("utf-8")
    )

    win32print.EndPagePrinter(impressora)
    win32print.EndDocPrinter(impressora)

finally:
    win32print.ClosePrinter(impressora)


print("Etiqueta enviada para a impressora.")
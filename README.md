# Sistema de Consulta e Impressão de QRCode no Secullum Acesso

Aplicação foi desenvolvida em **Python** para consultar dados de visitantes cadastrados no **Secullum Acesso**, recuperar a credencial utilizada no controle de acesso e realizar a impressão de uma etiqueta contendo um **QRCode compatível com os leitores Control iD**.

O projeto surgiu de uma necessidade prática: tornar mais rápido o processo de localização de visitantes já cadastrados e a impressão de suas credenciais, evitando a necessidade de navegar por várias telas do sistema Secullum apenas para localizar os dados e realizar a impressão da etiqueta.

Atualmente, o projeto encontra-se com a sua *aplicação funcional e validada*. A consulta ao banco de dados, tratamento das informações, geração do QRCode e envio da etiqueta para a impressora Zebra já foram testados com sucesso.

O desenvolvimento foi finalizado com a interface pronta e utilizável.

## Objetivo do Projeto

O objetivo principal é disponibilizar uma interface simples para que o usuário possa:

- Informar o CPF de um visitante;
- Consultar automaticamente os dados no bando do Secullum Acesso;
- Visualizar as informações encontradas;
- Recuperar o identificador utilizado como credencial;
- Transformar esse identificador no formato esperando pelo leitor;
- Gerar um etiqueta em ZPL;
- Imprimir diretamente em uma impressora Zebra;
- Utilizar o QRCode impresso nos leitores ContolID já existentes no ambiente;

A proposta não é substituir o Secullum Acesso, pois o mesmo continua sendo a **fonte oficial das informações**, enquanto esta aplicação funciona como uma ferramente auxiliar de consulta e imrpessão.


# Status Atual

**MVP Funcional**

Até o momento foram validados:

- Conexão com o SQL Server;
- Acesso ao banco local do Secullum;
- Consulta de visitantes através do CPF;
- Recuperação das informações da tabela 'pessoas';
- Relacionamento com informações de nível de acesso;
- Recuperação da pessoa/setor a ser visitado;
- Recuperação do número identificador;
- Tratamento do identificador para o formato utilizado pelo QRCode;
- Montagem da etiqueta utilizando ZPL;
- Comunicação com a impressora Zebra através do Windows;
- Impressão da etiqueta;
- Leitura do QRCode pelo equipamento CrontrolID;
- Validação das regras de acesso e validade já cadastrados no Secullum;
- Criação de uma interface gráfica inicial utilizando TKinter.


# Ambiente utilizado

- Python
- Secullum Acesso `2.16.0`
- Microsoft SQL Server 2022 Express
- Microsoft ODBC Driver 18 for SQL Server

### Hardware / equipamentos

**Impressora**

- Zebra ZD220
- 203 DPI
- conexão USB
- driver utilizado no Windows:

```text
ZDesigner ZD220-203dpi ZPL
```

**Etiqueta utilizada**

```text
104 mm x 50,8 mm
```

**Controle de acesso**

- Control iD iDFace
- Firmware utilizado durante os testes: `6.20.10`
- Comunicação existente no ambiente através de Wiegand.

# Tecnologias utilizadas

## Python

O Python foi utilizado como linguagem principal do projeto, sendo responsável por:

- Conexão com o banco de dados;
- Execução das consultas SQL;
- Tratamento dos dados;
- Montagem do QRCode;
- Geração da Etiqueta;
- comunicação com a imrpessora;
- Interface gráfica do sistema.

## TKinter

A interface atual foi desenvolvida utilizando **Tkinter**, biblioteca de interface gráfica que acompanha normalmente a instalação padrão do Python.

Ela foi utilizada para criar a tela através da qual o operador realiza a pesquisa e visualiza as informações encontradas.

## SQL Server

O banco utilizado pelo Secullum neste ambiente é:

```text
SecullumAcessoNet
```

A aplicação acessa esse banco apenas para **consulta das informações necessárias**.

Um princípio importante adotado durante o desenvolvimento foi evitar modificações diretas na estrutura interna do Secullum.

Por isso, a aplicação não depende de operações como:

```sql
INSERT
UPDATE
DELETE
```

no banco do sistema.

Essa decisão reduz o risco de inconsistências e evita alterações em tabelas cujo funcionamento interno pertence ao próprio Secullum.

## pyodbc

A biblioteca `pyodbc` é utilizada para realizar a comunicação entre Python e Microsoft SQL Server.

Instalação:

```bash
pip install pyodbc
```

Ela permite que a aplicação execute consultas SQL utilizando o driver ODBC instalado no Windows.

---

## Microsoft ODBC Driver 18 for SQL Server

Para que o `pyodbc` consiga se comunicar com o SQL Server é necessário possuir um driver ODBC compatível instalado no Windows.

Durante o desenvolvimento foi utilizado:

```text
ODBC Driver 18 for SQL Server
```
## pywin32

A biblioteca `pywin32` é utilizada para acessar funcionalidades específicas do Windows.

Neste projeto ela é utilizada principalmente para comunicação com o sistema de impressão através do `win32print`.

Instalação:

```bash
pip install pywin32
```

Com isso, a aplicação consegue localizar a impressora configurada no Windows e enviar o conteúdo ZPL diretamente para a fila de impressão.

## python-dotenv

As configurações externas da aplicação são carregadas através de variáveis de ambiente.

Para isso é utilizada a biblioteca:

```bash
pip install python-dotenv
```

O objetivo é separar configurações do código-fonte, principalmente informações como:

- servidor do banco;
- banco utilizado;
- usuário;
- senha;
- driver ODBC;
- nome da impressora.

# Dependências Python

As principais dependências utilizadas atualmente são:

```text
pyodbc
pywin32
python-dotenv
```

Podem ser instaladas utilizando:

```bash
pip install pyodbc pywin32 python-dotenv
```

O Tkinter normalmente já acompanha a instalação padrão do Python no Windows.

# Configuração por `.env`

As informações de infraestrutura não ficaram diretamente escritas dentro do código Python.

Para esse projeto utilizei um arquivo `.env` para manter essas configurações separadas.

Exemplo:

```env
DB_SERVER=SERVIDOR_SQL
DB_DATABASE=SecullumAcessoNet
DB_USER=USUARIO
DB_PASSWORD=SENHA
DB_DRIVER=ODBC Driver 18 for SQL Server

PRINTER_NAME=ZDesigner ZD220-203dpi ZPL
```

Os dados reais de acesso ao banco **não foram enviados para o GitHub**.


Para esse repositório público, como uma boa prática foi disponibilizado apenas um arquivo com informações de exemplo, sem qualquer senha ou informação sensível.


# Estrutura principal da aplicação

A interface e a lógica principal do sistema atualmente estão centralizadas no arquivo:

```text
app_gui.py
```

# Funcionamento da aplicação

O fluxo atual pode ser resumido da seguinte maneira:

```text
Operador
   ↓
Informa CPF
   ↓
Aplicação Python
   ↓
Normalização do CPF
   ↓
Consulta SQL
   ↓
Banco SecullumAcessoNet
   ↓
Dados do visitante
   ↓
Tratamento do identificador
   ↓
Geração do ZPL
   ↓
Windows / win32print
   ↓
Zebra ZD220
   ↓
Etiqueta com QR Code
   ↓
Control iD
```

# Consulta ao Secullum

Durante a investigação do banco foi identificado que a principal tabela utilizada para este processo é:

```text
pessoas
```

A consulta também utiliza relacionamentos com informações presentes em outras estruturas.

Entre os relacionamentos utilizados estão:

```text
pessoas
    ↓
niveis
```

e um relacionamento da própria tabela `pessoas` para identificar quem ou qual local o visitante irá visitar.

A lógica utilizada envolve relacionamentos equivalentes a:

```sql
LEFT JOIN niveis
```

e:

```sql
LEFT JOIN pessoas
```

O `LEFT JOIN` foi importante porque nem todos os registros possuem obrigatoriamente todas as informações relacionadas preenchidas.

# Dados recuperados

Entre os dados utilizados pela aplicação estão:

- CPF;
- nome;
- número identificador;
- nível/tipo de acesso;
- observação;
- pessoa ou setor visitado;
- data de validade;
- hora de validade.

Campos identificados durante o desenvolvimento incluem informações como:

```text
pessoas.n_identificador
pessoas.nome
niveis.descricao
pessoas.obs
pessoas.validade_data_fim
pessoas.validade_hora_fim
```

Além do relacionamento utilizado para localizar quem será visitado.

# Tratamento do CPF

Antes da consulta, o CPF informado pelo usuário é normalizado.

Isso evita problemas causados por entradas como:

```text
123.456.789-00
```

ou:

```text
12345678900
```

A aplicação trata a entrada para que a pesquisa seja realizada utilizando apenas os números.

Essa etapa foi importante para tornar a pesquisa mais tolerante ao formato digitado pelo operador.

# Número identificador

Uma das principais descobertas durante o desenvolvimento foi entender a função do campo:

```text
pessoas.n_identificador
```

Esse valor está relacionado à credencial utilizada no controle de acesso.

No banco ele pode estar armazenado sem os zeros iniciais.

Por exemplo:

```text
1234
```

Porém, o formato utilizado pelo QR Code possui **10 caracteres numéricos**.

Portanto:

```text
1234
```

deve se transformar em:

```text
0000001234
```

No Python esse tratamento pode ser realizado utilizando:

```python
codigo = str(n_identificador).zfill(10)
```

Esse foi um ponto importante do projeto porque inicialmente era necessário compreender de onde vinha o conteúdo do QR Code.

Após os testes foi possível validar que o número identificador recuperado do Secullum, tratado para possuir dez posições, era reconhecido corretamente pelo controle de acesso.

# Registros sem identificador

Durante os testes também foram encontrados visitantes cujo campo:

```text
n_identificador
```

estava vazio ou retornava:

```text
None
```

Isso não significa necessariamente um erro na consulta.

Significa que aquele registro específico não possui um número identificador disponível no campo utilizado pelo sistema.

Também foram realizados testes com outros visitantes que possuíam o identificador corretamente preenchido.

Nesses casos, a aplicação conseguiu:

1. recuperar o identificador;
2. completar os zeros à esquerda;
3. gerar o QR Code;
4. imprimir a etiqueta;
5. utilizar a credencial no Control iD.

Por segurança, quando não existe identificador válido, a aplicação não deve gerar uma etiqueta de acesso como se existisse uma credencial válida.

# Geração do QR Code

O QR Code utilizado neste projeto não precisa ser criado como uma imagem PNG para depois ser enviado à impressora.

A própria linguagem **ZPL**, utilizada pelas impressoras Zebra, possui comandos para geração de QR Code.

Dessa forma, a aplicação monta diretamente o conteúdo da etiqueta em ZPL.

Um dos comandos utilizados nesse processo é da família:

```text
^BQN
```

A Zebra interpreta o ZPL e desenha o QR Code diretamente na etiqueta.

Esse modelo traz algumas vantagens:

- Evita geração temporária de imagens;
- Reduz dependências externas;
- Simplifica o processo de impressão;
- Utiliza recursos nativos da própria impressora;
- Permite controlar tamanho e posição pelo ZPL.

# Impressão utilizando ZPL

A impressora Zebra trabalha com a linguagem:

```text
ZPL — Zebra Programming Language
```

A aplicação monta uma string contendo os comandos necessários para representar:

- Textos;
- Posicionamento;
- Informações do visitante;
- QR Code;
- Dimensões e organização da etiqueta.

Depois disso, o conteúdo é enviado diretamente para a impressora.

O fluxo é aproximadamente:

```text
Python
   ↓
String ZPL
   ↓
win32print
   ↓
Fila RAW do Windows
   ↓
Driver Zebra
   ↓
Zebra ZD220
```

O envio em modo RAW é importante porque o objetivo não é pedir ao Windows para desenhar a etiqueta.

Quem interpreta os comandos gráficos é a própria impressora Zebra.

# Integração com o Windows

A impressão é realizada utilizando:

```python
win32print
```

Esse módulo faz parte do pacote `pywin32`.

A aplicação localiza a impressora pelo nome configurado no Windows:

```text
ZDesigner ZD220-203dpi ZPL
```

e envia o conteúdo ZPL diretamente para ela.

# Interface gráfica

Depois de validar individualmente o banco, QRCode e impressão, foi criada uma interface gráfica utilizando Tkinter.

O objetivo da interface é esconder do operador toda a complexidade existente por trás da aplicação.

Em vez de executar scripts, consultas SQL ou comandos manualmente, o operador interage com uma tela.

A interface atual já permite executar o fluxo principal do sistema, porém ainda não é considerada a versão final do frontend.

# Decisões de arquitetura

Uma das decisões mais importantes tomadas durante o desenvolvimento foi separar claramente as responsabilidades.

O Secullum permanece responsável pelo cadastro e pelas regras do controle de acesso.

A aplicação Python apenas consulta as informações necessárias para realizar o processo de impressão.

Arquiteturalmente:

```text
Secullum
   ↓
SQL Server
   ↓
Aplicação Python
   ↓
Zebra
```

O controle de acesso continua seguindo o fluxo já existente:

```text
Secullum
   ↓
Control iD
```

Assim, a aplicação desenvolvida não tenta assumir a responsabilidade do sistema principal.

Ela resolve especificamente o problema de **consulta rápida e impressão da credencial**.

---

# Principais aprendizados do projeto

Este projeto foi especialmente importante porque envolveu muito mais do que simplesmente escrever um script Python.

Foi necessário entender como diferentes sistemas se comunicavam entre si.

Entre os principais conceitos trabalhados estão:

## Integração Python com SQL Server

Foi possível aplicar na prática:

- Conexão via ODBC;
- `pyodbc`;
- Execução de SQL através do Python;
- Tratamento de resultados;
- Relacionamento entre tabelas;
- Investigação de estruturas de um banco existente.

## SQL

O projeto exigiu compreender consultas envolvendo mais de uma tabela.

Foram utilizados conceitos como:

```sql
SELECT
FROM
WHERE
LEFT JOIN
```

Além disso, foi necessário entender relacionamentos entre registros em vez de simplesmente consultar uma única tabela.

## Tratamento de dados

Nem sempre o valor armazenado no banco está no formato necessário para o destino.

O caso do:

```text
n_identificador
```

foi um exemplo prático disso.

O banco possuía o valor:

```text
1234
```

enquanto o dispositivo esperava:

```text
0000001234
```

Isso demonstrou na prática a importância da camada de transformação de dados entre dois sistemas.

## Investigação de sistemas existentes

Boa parte do projeto envolveu descobrir como um sistema já existente funcionava.

Foi necessário identificar:

- Qual banco o Secullum utilizava;
- Quais tabelas continham os dados desejados;
- Quais campos correspondiam às informações exibidas na interface;
- Como o identificador estava relacionado ao QR Code;
- Qual formato o Control iD esperava;
- Como a Zebra deveria receber a etiqueta.

Esse processo me mostrou uma situação bastante comum em integração de sistemas: antes de escrever a solução, é necessário compreender o ambiente existente.

## Impressão RAW

Outro aprendizado importante foi entender a diferença entre uma impressão convencional e o envio de comandos diretamente para uma impressora térmica.

Neste projeto:

```text
Python não desenha a etiqueta.
```

Ele envia:

```text
ZPL
```

e a Zebra é responsável por interpretar os comandos e gerar fisicamente a etiqueta.

## Separação de configuração e código

O uso de `.env` permitiu separar informações específicas do ambiente da lógica da aplicação.

Isso facilita manutenção e evita inserir informações sensíveis diretamente no código.

## Interface gráfica

Depois de validar a lógica de backend, foi criada uma camada de interface com Tkinter.

Essa etapa reforçou uma prática importante:

> primeiro garantir que as regras e integrações funcionem corretamente, depois construir a interface sobre essa base.

# Desafios encontrados

O principal desafio não foi gerar o QR Code.

Foi compreender todo o fluxo existente.

Inicialmente existiam várias perguntas:

```text
Onde o QR Code é armazenado?

Ele é gerado pelo Secullum?

Ele é armazenado no Control iD?

Ele utiliza CPF?

Ele possui uma tabela própria?

Qual informação o leitor realmente recebe?
```

A investigação mostrou que, para o fluxo utilizado neste projeto, o campo `n_identificador` possui papel fundamental na geração da credencial utilizada pelo QR Code.

Outro desafio foi descobrir que nem todos os registros possuem esse campo preenchido.

Isso exigiu tratamento para evitar que registros incompletos fossem interpretados como erro de programação.

# Ponto atual do desenvolvimento

O desenvolvimento está pausado após a conclusão e validação do fluxo principal.

A aplicação já consegue consultar e imprimir corretamente, porém ainda existem ajustes visuais e de impressão antes de considerar a interface finalizada.

## Ajustes pendentes na etiqueta

Ainda será necessário realizar o refinamento das configurações de impressão, principalmente:

- Tamanho do QR Code;
- Tamanho das fontes;
- Posicionamento dos textos;
- Alinhamento dos elementos;
- Aproveitamento da área útil da etiqueta;
- Espaçamentos;
- Proporção entre QR Code e informações textuais.

A etiqueta utilizada atualmente possui:

```text
104 x 50,8 mm
```

e a Zebra trabalha em:

```text
203 DPI
```

Portanto, os próximos ajustes serão realizados diretamente nos comandos e coordenadas ZPL utilizados para montar o layout.

## Ajustes pendentes na interface

O frontend criado em Tkinter também precisa passar por uma etapa de refinamento visual.

A lógica principal da interface já funciona.

A próxima etapa seria melhorar a experiência do operador sem alterar o fluxo que já foi validado.

---

# Observação

Este projeto foi desenvolvido para trabalhar com uma infraestrutura específica baseada em **Secullum Acesso, SQL Server, Zebra e Control iD**.

Nomes de servidores, usuários, senhas, endereços de rede e demais informações sensíveis do ambiente não fazem parte deste repositório.

---

## Autor

Projeto desenvolvido como parte dos meus estudos e prática em **Python, SQL e integração de sistemas**, utilizando uma necessidade real como oportunidade para aplicar conceitos de desenvolvimento de software.

Obrigado!


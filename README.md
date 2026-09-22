# Sistema de Consulta e Impressão de QRCode no Secullum Acesso

Aplicação desenvolvida em **Python** para consultar dados de visitantes cadastrados no **Secullum Acesso**, recuperar a credencial utilizada no controle de acesso e realizar a impressão de uma etiqueta contendo um **QR Code compatível com os leitores Control iD**.

O projeto surgiu de uma necessidade prática: tornar mais rápido o processo de localização de visitantes já cadastrados e a impressão de suas credenciais, evitando a necessidade de navegar por várias telas do sistema Secullum apenas para localizar os dados e realizar a impressão da etiqueta.

Atualmente, o projeto encontra-se com o seu *MVP funcional e validado*. A consulta ao banco de dados, tratamento das informações, geração do QR Code e envio da etiqueta para a impressora Zebra já foram testados com sucesso.

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
- 

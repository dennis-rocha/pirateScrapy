# pirateScrapy

Esse teste foi desenvolvido para a Neoway nesse link: <https://github.com/NeowayLabs/jobs/blob/master/datapirates/challengePirates.md>

## Introdução

O teste foi desenvolvido com a lib scrapy em python, esse repositorio contém o teste refatorado, visto que o teste anterior feito foi realizado com a lib seleniun e contém algumas falhas (site da extração, chromedriver pode falhar com a versão) o link do repositorio antigo é esse: <https://github.com/dennis310797/pirateTest>

## Instrução

Siga as instruções abaixo para realizar esse teste.

1. Necessário instalar as libs scrapy, pandas e json:

* Linux:
  * `pip3 install pandas`
  * `pip3 install json`
  * `pip3 install scrapy`

* Windows:
  * `pip install pandas`
  * `pip install json`
  * `pip install scrapy`

Obs: Caso ocorra alguma falha por importação de libs, pode ser devido ao pandas. Pois algumas funções do pandas necessita instalar outros modulos.

1. Necessário executar o seguinte comando para rodar o teste `scrapy runspider main.py`

1. Você pode alterar alguns trechos do código para raspar todos os dados de todos os estados. Veja a proxima seção.

## Como Funciona

A raspagem inicia nesse link <https://buscacepinter.correios.com.br/app/faixa_cep_uf_localidade/index.php>, nessa etata é capturado todos os UFs da seleção. Apartir disso é realizado uma requisição ao servidor simulando uma requisição normal. O Body da request vem com o seguintes campos:

    { 
      "erro": false,
      "mensagem": "DADOS ENCONTRADOS COM SUCESSO.",
      "total": 322,
      "dados": [
        ...
      ]
    }

É feito uma comparação se a quantidade de 'dados' é igual ao total, caso não seja, é feito uma nova requisição ao servidor para capturar o total dos dados.  
Se o total for igual a quantidade de dados na lista é realizado o método de list comprehension para obter apenas os campos necessário para a execução do teste. Nessa etapa é realizado tratamento para limpeza de acentos 'éáíà..' e é colocado as letras tudo maiúsculo.
Após a essa etapa é realizado um processo de limpeza, tratamento e transformação dos dados com pandas. É removido linhas vazias, linhas duplicadas, reorganizado os dados como: cidade(A-Z), cep_inicial(menor-maior), cep_final(maior-menor).
Com pandas também é possivel transformar o DataFrame para json, realizo essa atividade para escrever um arquivo json contendo os dados do DataFrame. O arquivo é escrito da seguinte maneira: state_'UF'.json. Para finalizar a lib scrapy se encarrega de trazer a mesma informação, sem a necessidade de ser necessário escrever um arquivo, basta retornar com `yield` cada linha do DataFrame. Para realizar isso, transformo o DataFrame em dicionario onde obtém uma lista com chave -> valor, cada linha dessa lista é retornado pelo `yield` e o scrapy fica responsável para trazer os dados nos formator json, xml, csv, entre outros. Para usar alguma dessas forma de retorno via scrapy basta usar o comando abaixo:
Use a flag `-o` seguido do nome do arquivo + extensão.

    scrapy runspider main.py -o teste.csv

Você pode alterar trecho do código para capturar todos os dados dos UFs, basta excluir na função "parse" a condição de parada do laço de repetição. O código está comentado, veja o trecho próximo a linha 95.

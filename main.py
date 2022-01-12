import os
import scrapy
import json
import random
import pandas as pd
import numpy as np
from urllib.parse import urlencode
from unicodedata import normalize


"""
    Iniciando um Scrapy na página dos correios
    Quero ressaltar alguns valores de variaveis, pois alterei para ser 'gentil' com o servidor
    por exemplo na função 'parse' existe uma lista com valores dos estados aceitos que foi 
    raspado do próprio site. Possui mais de 20 estados, já formatado como valor aceito para a requisição 
    no servidor. Dessa lista, utilizei apenas 3 estados aleatórios para realizar a raspagem. É possivel
    alterar isso excluindo a variavel 'count' e a condição para interromper a sequencia. Se fizer isso
    será capturado todos os UFs da lista.
    
    Na função selectState é iniciado com a requisição padrão para o servidor. A response do body vem com
    50 linhas de dados e com mais algumas chaves, com a chave (coluna) 'total' consigo obter quantas
    cidades possui cada UF e se a quantidade de dados recebido na requisição através da chave 'dados'
    for diferente do total, é realizado uma nova request solicitando a quantidade total. 
    Se os valores total e dados estiverem igual segue a sequencia da limpeza e transformaçãos dos dados.
    
    1 - Step:
        Crio uma lista de dicionarios com as chaves que quero, são elas: uf, cidade (localidade), cep_inicial, cep_final.
        Ao usar o método de list comprehension executo uma limpeza nos dados, por exemplo, removo acentos 'éáí..' e 
        fica tudo upercase, também coloco os valores de cep para o tipo inteiro. Isso ajuda na validação dos dados.
        
    2 - Step:
        Carrego tudo num dataframe para realizar a transformação e validação dos dados.
        Com o DataFrame consigo facilmente remover os valores não aceito (nulo) como é o caso do primeiro
        indice da lista de dados que vem uma string vazia para cidade (localidade). 
        Removo os duplicados através da ordenação: cidade(A-Z), cep_inicial(menor-maior), cep_final(maior-menor)
        
    3 - Step:
        Através do pandas.DataFrame consigo transformar o DataFrame com os dados limpos e transformados
        para o formato json.
        Escrevo o arquivo json da seguinte maneira: 'state_' + 'UF' o arquivo fica uma lista com chave -> valor
        para cara coluna.
        Ao final retorno os valores como dicionario para retornar no yield e ser possivel usar comando da lib
        scrapy e criar arquivos os diferentes formatos, exemplos: json, csv, xml, etc.
        
    
""" 
class PirateTest(scrapy.Spider):
    name = "Pirate Test With Scrapy"
    start_urls = ["https://buscacepinter.correios.com.br/app/faixa_cep_uf_localidade/index.php"]
    
    #Iniciando alguns parametros da requisição. Caso dê algum erro, pode ser os cookies e será necessario excluir os comentarios onde carrega essa informação
    
    """   
    cookies = {
        '_ga': 'GA1.3.1068380975.1624545028',
        '__gads': 'ID=0defd8d9a9ce4657-2247779b34ba00fc:T=1624545028:RT=1624545028:S=ALNI_MYPFupIiAJuAhWeLsPnPev5DUWZEg',
        'buscacep': 'b51j1j7cn22ug7vc6deda47dgv',
        'svp-47873-%3FEXTERNO_2%3Fpool_svp_ext_443': 'BCABKIMALLAB',
    }
    """
    
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'Cache-Control': 'no-store, no-cache, must-revalidate',
        'sec-ch-ua-mobile': '?1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': '*/*',
        'Origin': 'https://buscacepinter.correios.com.br',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://buscacepinter.correios.com.br/app/faixa_cep_uf_localidade/index.php',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    data = {
        'letraLocalidade': '',
        'ufaux': '',
        'pagina': '/app/faixa_cep_uf_localidade/index.php',
        'mensagem_alerta': '',
        'uf': '',
        'localidade': '',
        'cepaux': ''
    }
 
    def parse (self, response):
        #Raspando os UFs e fintrando para remover valores nulos
        UFs = response.xpath('//select/option/@value').getall()
        UFs = list(filter(None,UFs))
        
        #Embaralhando a lista com o UF de cada estado
        random.shuffle(UFs)
        
        body = self.data
        count = 0 
        for uf in UFs:
            body['uf'] = uf 
            
            #Condição de parada
            if count >= 3:
                break
            else:
                count=count +1
            
            yield scrapy.Request(
                    'https://buscacepinter.correios.com.br/app/faixa_cep_uf_localidade/carrega-faixa-cep-uf-localidade.php',
                    method='POST',
                    dont_filter=False,
                    #cookies=self.cookies,
                    headers=self.headers,
                    body=urlencode(body),
                    callback=self.selectState,
                    cb_kwargs= dict(body=body)
            )

        
    def selectState(self,response, body):
        #Leio a response com json para relizar o tratamento dos dados
        data = json.loads(response.text)
        
        #Caso o total dos dados da response "len(data['dados'])" for menor que o "data['total']" é realizado uma nova requisição com a quantidade correta
        if len(data['dados']) != data['total']:
            self.data['inicio'] = '0',
            self.data['final'] =  data['total']
            yield scrapy.Request(
                    'https://buscacepinter.correios.com.br/app/faixa_cep_uf_localidade/carrega-faixa-cep-uf-localidade.php',
                    method='POST',
                    dont_filter=True,
                    #cookies=self.cookies,
                    headers=self.headers,
                    body=urlencode(body),
                    callback=self.selectState,
                    cb_kwargs= dict(body=body)
            )
            
        else:  
            #Usado o método list comprehension para raspadar e limpar os dados necessário
            data = [
                {
                    'uf':row['uf'],
                    'cidade' : normalize('NFKD', row['localidade']).encode('ASCII','ignore').decode('ASCII').upper(),
                    'cep_inicial' : int(row['faixasCep'][0]['cepInicial']),
                    'cep_final' : int(row['faixasCep'][0]['cepFinal'])
                }
            for row in data['dados']
            ]
            
            #Usei ipdb para validar alguns coisas antes de construir o script final
            #import ipdb; ipdb.set_trace()
            
            #Tratamento, limpeza e transformação dos dados com pandas
            df= pd.DataFrame(data)
            df.replace('',np.nan, inplace = True)
            df.dropna(inplace=True)
            df.sort_values(['cidade','cep_inicial','cep_final'],ascending=[True,True,False], inplace=True)
            df.drop_duplicates('cidade', inplace=True)
            
            #Verificando a existencia da pasta data, se não existe é criada
            if not os.path.isdir("./data"):
                os.system("mkdir data")
                
            #Salvando o arquivo no formato json   
            with open(f"./data/state_{data[0]['uf']}.json", 'w') as arq:
                arq.write(df.to_json(orient='records',indent=4))
            
            #Retornando os dados no formato de dicionario para o scrapy se encarregar de criar novas visualizações de arquivo (csv,json,xml,etc.)
            for i in df.to_dict(orient='records'):
                yield i
    
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alan Giovanni
# LinkedIn: https://www.linkedin.com/in/alan-giovanni-53aaa9ab/
# Data: 19/01/2022
# Description: Módulo para coletar dados do(s) arquivo(s) de configuração

import json # importa o modulo que processa objetos json

# Local do Arquivo de configuração
ARQ_CONF_DEFAULT = '/opt/zbxterm/conf/default.json'

def ler_config(key:str) -> dict:
    """Ler o arquivo de configuração default. Para tal, deve-se enviar o recurso que as configurações devem ser retornadas."""
    try:
        with open(ARQ_CONF_DEFAULT, 'r', encoding='utf8') as arquivo_config:
            configs = json.loads(arquivo_config.read()) # Ler em Json e converte para Python
    except:
        print('ERRO: Falha ao tentar ler o arquivo de configuração: ' + ARQ_CONF_DEFAULT)
        exit() # Forçando a interrupção do programa

    return configs[key]

def read_all() -> dict:
    """Retorna todas as configurações do arquivo default.json"""
    try:
        with open(ARQ_CONF_DEFAULT, 'r', encoding='utf8') as arquivo_config:
            configs = json.loads(arquivo_config.read()) # Ler em Json e converte para Python
    except:
        print('ERRO: Falha ao tentar ler o arquivo de configuração: ' + ARQ_CONF_DEFAULT)
        exit() # Forçando a interrupção do programa

    return configs

def save_config(estrutura_config:dict):
    """Salva novas informações no arquivo de configuração default em JSON."""
    # Precisa fazer um backup aqui
    try:
        with open(ARQ_CONF_DEFAULT, 'w', encoding='utf-8') as arquivo_config:
            # Converte a estrutura recebida em dicionário python para json com indentação
            arquivo_config.write(json.dumps(estrutura_config, indent=4))
        print('Novas configurações salvas com sucesso!')
    except:
        print('ERRO: Falha ao tentar salvar no arquivo de configuração: ' + ARQ_CONF_DEFAULT)
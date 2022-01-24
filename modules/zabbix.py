#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alan Giovanni
# LinkedIn: https://www.linkedin.com/in/alan-giovanni-53aaa9ab/
# Data: 19/01/2022
# Description: Métodos para a API do Zabbix

import requests # importa o modulo que processa e faz requisicoes, necessário instalar este módulo primeiramente.
import json # importa o modulo que processa objetos json
import modules.zabbix as zabbix # Import do Módulo Zabbix que está na pasta modules do projeto corrente
import modules.configuration as configuracoes # Importa o módulo que ler as configurações default

# Ler as configurações destinadas ao recurso do Teampass
config_zabbix = configuracoes.ler_config('zabbix')

# Zabbix API
USER_ZBX = config_zabbix['user']
PASS_ZBX = config_zabbix['pass']
URL_ZBX = config_zabbix['url']
HEADERS = {"Content-type": "application/json"}


def request(payload):
    """Faz um request POST a API do Zabbix"""
    try:
        response_zbx = requests.post(URL_ZBX, data=json.dumps(payload), headers=HEADERS, timeout=5)
        response_zbx_py = json.loads(response_zbx.text) # Converte o Json em Python
        try:
            return response_zbx_py['result']
            
        except KeyError:
            # Não tem "result" no json, deve ser error
            return "Erro: " + response_zbx_py['error']['data']
        except Exception as erro:
            # Qualquer outro erro
            return "Erro: ", erro
    except requests.exceptions.HTTPError as errh:
        return "Erro HTTP: ",errh
    except requests.exceptions.ConnectionError as errc:
        return "Erro ao Conectar: ",errc
    except requests.exceptions.Timeout as errt:
        return "Erro de Timeout: ",errt
    except requests.exceptions.RequestException as err:
        return "Erro: ",err

def auth() -> str:
    """Autenticação na API do Zabbix. Retorna o token gerado ou a string Erro."""
    payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": USER_ZBX,
            "password": PASS_ZBX
        },
        "id": 1
    }

    token = request(payload)
    return token

def get_hosts(auth_token:str) -> list:
    """Retorna todos os hosts inseridos no Zabbix"""
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["host", "hostid"]
        },
        "auth": auth_token,
        "id": 1
    }

    obj_hosts = request(payload)
    # Retorno do request: [{"hostid": "10840","host": "TEL-US-PL-IPSEC"}]
    return obj_hosts

def get_interfaces(auth_token:str) -> list:
    """Retorna todos os IPs configurados no Zabbix"""
    payload = {
        "jsonrpc": "2.0",
        "method": "hostinterface.get",
        "params": {
            "output": ["hostid", "ip"]
        },
        "auth": auth_token,
        "id": 1
    }

    obj_interfaces = request(payload)
    # Retorno do request: [{"interfaceid": "23","hostid": "10358","ip": "127.0.0.1"}]
    return obj_interfaces

def is_online() -> bool:
    """Verifica se a API está online. Retorna uma lista contendo o status"""
    payload = {
        "jsonrpc": "2.0",
        "method": "apiinfo.version",
        "params": {},
        "id": 1
    }

    resposta = request(payload)
    # Não está online
    if 'Erro' in str(resposta):
        return False
    else:
        return True

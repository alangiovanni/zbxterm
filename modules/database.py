#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alan Giovanni
# LinkedIn: https://www.linkedin.com/in/alan-giovanni-53aaa9ab/
# Data: 19/01/2022
# Description: Métodos para o banco de dados do ZBXTERM

import modules.configuration as configuracoes # Importa o módulo que ler as configurações default
import json # importa o modulo que processa objetos json

# Ler as configurações destinadas ao recurso do zbxterm
config_zbxterm = configuracoes.ler_config('zbxterm')
# Base Local
LOCAL_DB = config_zbxterm['database']

def save(local_db:list):
    """Salva um bloco de informações na base"""
    try:
        with open(LOCAL_DB, 'w') as arquivo:
            arquivo.write(json.dumps(local_db, indent = 3))
        print("Informações atualizadas com sucesso!")
    except Exception as erro:
        print("ERROR: Não foi possível salvar a alteração na base dados local.\n", erro)

def load() -> list:
    try:
        with open(LOCAL_DB, 'r') as arquivo:
            local_db = json.loads(arquivo.read()) # Ler em Json e converte em Python
    except:
        local_db = []

    return local_db

def reset():
    # Carrega a base
    local_db = load()

    print('PROCESSO IRREVERSÍVEL')
    redefinir = input('Você está prestes a deletar base local. É isso mesmo que deseja fazer? [y/n] ')
    if redefinir == "y" or redefinir == "Y":
        local_db = []
        save(local_db)
        print("-> Base de dados excluída!")
    else:
        input("-> Procedimento abortado.")

def get_hosts_by_dado(dado_busca:str) -> list:
    """Retorna um array de hosts encontrados na base com base na informação recebida (IP ou Nome)
    Array: [{"id": 1, "host": "XPTO", "ip": "123.123.123.123"}]
    """
    # Carrega a base
    local_db = load()
    # Criando uma base local temporária para manipulação

    list_host = []
    count = 1
    for host in local_db:
        # Salva o host encontrado que bate com o dado recebido ou parecido
        # -1 Significa que não encontrou a string ou substring com aquele dado
        if (host["host"].lower().find(dado_busca) != -1 or host["ip"].find(dado_busca) != -1):
            host_encontrado = host.copy()
            host_encontrado.update({"id": count})
            
            # Atualiza a base temporária
            list_host.append(host_encontrado)
            # Incrementa o contador
            count+=1

    return list_host

def add_connection_ssh(host, ip, porta_ssh, user_ssh, pass_ssh, grupo, hostid):
    """Insere na base uma conexão SSH"""
    # Carrega a base
    local_db = load()
    # Padrão de uma informação da base
    new_connection = {
        "hostid": hostid,
        "host": host,
        "ip": ip,
        "porta_ssh": porta_ssh,
        "user_ssh": user_ssh,
        "pass_ssh": pass_ssh,
        "grupo": grupo,
    }
    # Atualizando a base com a nova conexão
    local_db.append(new_connection)
    save(local_db)

def edit_connection_ssh(host_antigo:dict, host_novo:dict):
    """Edita uma conexão na base local"""
    # Carrega a base
    local_db = load()

    # For em todos as conexões da base
    for host in local_db:
        # Compara se o host do loop é igual ao host_atual para editá-lo
        if host == host_antigo:
            for atributo in host.keys():
                host[atributo] = host_novo[atributo]
            # Se entrou aqui é porque encontrou o host, para o loop.
            break

    # Salva as novas informações na base
    save(local_db)

def del_connection_ssh(host:dict):
    # Carrega a base
    local_db = load()
    # Deleta o host
    local_db.remove(host)
    # Salva as novas informações na base
    save(local_db)

def get_hosts_inserted_by_user(group_zbx:str) -> list:
    """Retorna as conexões SSH adicionados manualmente pelo usuário"""
    # Carrega a base
    local_db = load()
    # Lista vazia para armazenar todas as conexões adicionadas pelo usuário
    list_connections_non_zbx = []
    for host in local_db:
        if host["grupo"] != group_zbx:
            list_connections_non_zbx.append(host)

    return list_connections_non_zbx
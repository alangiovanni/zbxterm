#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alan Giovanni - Squad Hubble
# Data: 18/05/2021
# Description: Backend do gerenciador de SSH

import sys # importa o modulo que recebe os parâmetros passados na execucao do Script
import requests # importa o modulo que processa e faz requisicoes, necessário instalar este módulo primeiramente.
import json # importa o modulo que processa objetos json
import subprocess # Execução de comandos remotos

# Variáveis Globais
# Zabbix API
USER_ZBX = '<USER>'
PASS_ZBX = '<PASSWORD>'
URL_ZBX = '<URL>/api_jsonrpc.php'
HEADERS = {"Content-type": "application/json"}

# Base Local
LOCAL_DB = "/opt/zbxterm/local_db.json"
# Arquivo de Uso Temporário e Geral
ARQ_TEMP = "/tmp/arq_temp.txt"

# Grupo Default Conexões do Zabbix
GROUP_ZBX = "zbx"

# Gambi para conseguir definir uma variável de ambiente abaixo
def retorna_usuario():
    subprocess_retorno = subprocess.Popen(["whoami"], stdout=subprocess.PIPE, shell=True)
    usuario = str(subprocess_retorno.stdout.read().decode('UTF-8')).replace('\n', '')
    return usuario

# AD
USER_LINUX = retorna_usuario()

def sonda_usuario_connect_ssh(local_db):
    """Sonda o usuário para saber qual o host deseja conexão SSH"""
    resposta = str(input('Pesquisa (IP ou Host): ')).lower().strip()
    list_host = busca_host_local_db(local_db, resposta)
    if list_host:
        # Só tem um caso
        if len(list_host) == 1:
            # Faz a conexão com o host que encontrou
            host = list_host[0]
            print('\nHost encontrado: \n' + host["host"] + ' (' + host["ip"] + ')\n')

        else:
            print('\nHosts Encontrados: ')
            for host in list_host:
                print(str(host["id"]) + ' - ' + host["host"] + ' (' + host["ip"] + ')')

            resposta = int(input('\nDigite o ID do host: '))
            # Pula uma linha
            print("")
            # Decrementa a resposta para pegar o número correto da lista list_host
            resposta-=1
            host = list_host[resposta]
        
        # Retira a key ID (id de controle) que foi utilizado apenas para facilitar a coleta do dado digitada pelo usuário
        host.pop("id")
        
        # Retorna o HOST identificado
        return host

    else:
        print("Busca não retornou dados!")
        # Aguardando ENTER do usuário
        pause_read()
        return "ERRO"

def request_zbx(payload):
    """Faz um request POST a API do Zabbix"""
    response_zbx = requests.post(URL_ZBX, data=json.dumps(payload), headers=HEADERS)
    response_zbx_py = json.loads(response_zbx.text) # Converte o Json em Python
    try:
        return response_zbx_py['result']
        
    except KeyError:
        # Não tem "result" no json, deve ser error
        return "Erro: " + response_zbx_py['error']['data']

def auth_zbx():
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

    token = request_zbx(payload)
    return token

def get_hosts_zbx(auth_token):
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

    obj_hosts = request_zbx(payload)
    # Retorno do request: [{"hostid": "10840","host": "TEL-US-PL-IPSEC"}]
    return obj_hosts

def get_interfaces_zbx(auth_token):
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

    obj_interfaces = request_zbx(payload)
    # Retorno do request: [{"interfaceid": "23","hostid": "10358","ip": "127.0.0.1"}]
    return obj_interfaces

def build_local_db_zbx(obj_hosts, obj_interfaces):
    """Cria uma base local contendo os hosts configurados no Zabbix"""
    # Criando uma base local vazia
    tmp_database = []

    # Percorrendo o array de objetos de hosts
    for host in obj_hosts:
        # Criando uma cópia exata do dicionário "host"
        new_host = host.copy()
        # Percorrendo o array de objeto de interfaces
        for interface in obj_interfaces:
            # Verificando se o hostid da interface atual é igual ao hostid do host 
            if interface["hostid"] == new_host["hostid"]:
                # Atualiza o dicionário new_host com informação de IP e local de sync
                new_host.update({"ip": interface["ip"]}) # Após a atualização é esperado o seguinte dicionário: {"hostid": "10840","host": "TEL-US-PL-IPSEC", "ip": "192.168.0.1"}
                tmp_database.append(new_host) # Inserindo no final do array o dicionário recém-formado.
    
    # Retorna a base local
    return tmp_database

def build_local_db(local_db_zbx):
    """Cria a base local principal de conexões SSH"""
    # Criando uma base local temporária para manipulação idêntica a base do Zabbix
    tmp_database = local_db_zbx.copy()

    # Percorrendo o array de hosts do Zabbix
    for host in tmp_database:
        host.update({"porta_ssh": 22, "user_ssh": USER_LINUX, "pass_ssh":"", "grupo": GROUP_ZBX})
    
    # Retorna a base local
    return tmp_database

def insert_connection_local_db(local_db, host, ip, porta_ssh, user_ssh, pass_ssh, grupo, hostid):
    """Retorna a base local atualizada com informações da nova conexão SSH"""
    # Criando uma base local temporária para manipulação idêntica a base local do Zabbix
    tmp_database = local_db.copy()

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
    tmp_database.append(new_connection)

    return tmp_database

def busca_host_local_db(local_db, dado_busca):
    """Retorna um array de hosts encontrados na base com base na informação recebida (IP ou Nome)
    Array: [{"id": 1, "host": "XPTO", "ip": "123.123.123.123"}]
    """
    # Criando uma base local temporária para manipulação
    tmp_database = []
    count = 1
    for host in local_db:
        # Salva o host encontrado que bate com o dado recebido ou parecido
        # -1 Significa que não encontrou a string ou substring com aquele dado
        if (host["host"].lower().find(dado_busca) != -1 or host["ip"].find(dado_busca) != -1):
            host_encontrado = host.copy()
            host_encontrado.update({"id": count})
            
            # Atualiza a base temporária
            tmp_database.append(host_encontrado)
            # Incrementa o contador
            count+=1

    return tmp_database

def salvar_db(local_db):
    try:
        with open(LOCAL_DB, 'w') as arquivo:
            arquivo.write(json.dumps(local_db))
        print("Informações atualizadas com sucesso!")
    except:
        print("ERROR: Não foi possível salvar a alteração na base dados local.")

def salvar_dado(informacao, method):
    with open(ARQ_TEMP, method) as arquivo:
        arquivo.write(informacao)

def carregar_db():
    try:
        # Precisa testar
        with open(LOCAL_DB) as arquivo:
            local_db = json.loads(arquivo.read()) # Ler em Json e converte em Python
    except:
        local_db = []

    return local_db

def sync_local_db_zbx(local_db):
    # Autenticação no Zabbix
    print("Realizando autenticação no Zabbix Server...")
    auth_token = auth_zbx()
    
    # Verifica se o token contém a string Erro
    if auth_token.find("Erro") == True:
        print(auth_token) # Printa o erro e encerra a sincronia com o zabbix
        return
    
    print("Sincronizando a base local com o Zabbix...")
    hosts_zbx = get_hosts_zbx(auth_token)
    interfaces_zbx = get_interfaces_zbx(auth_token)
    local_db_zbx = build_local_db_zbx (hosts_zbx, interfaces_zbx)
    
    # Salvando as conexões SSH inseridas pelo usuário
    list_connections_non_zbx = get_connections_non_zbx(local_db)

    # Base local de conexões ssh principal
    local_db = build_local_db(local_db_zbx)

    # Adicionando as conexões inseridas pelo usuário anteriormente a sincronia na base recém sincronizada
    if list_connections_non_zbx: # Se existir alguma conexão entre nessa condição
        for host in list_connections_non_zbx:
            local_db = insert_connection_local_db(local_db, host["host"], host["ip"], host["porta_ssh"], host["user_ssh"], host["pass_ssh"], host["grupo"], host["hostid"])
    
    # Salva a base localmente
    salvar_db(local_db)
    print("Base local Sincronizada!!")
    # Aguardando ENTER do usuário
    pause_read()

def get_connections_non_zbx(local_db):
    # Lista vazia para armazenar todas as conexões adicionadas pelo usuário
    list_connections_non_zbx = []
    for host in local_db:
        if host["grupo"] != GROUP_ZBX:
            list_connections_non_zbx.append(host)

    return list_connections_non_zbx

def redefinir_local_db(local_db):
    print('PROCESSO IRREVERSÍVEL')
    redefinir = input('Você está prestes a deletar base local. É isso mesmo que deseja fazer? [y/n] ')
    if redefinir == "y" or redefinir == "Y":
        local_db = []
        salvar_db(local_db)
        print("-> Base de dados excluída!")
    else:
        input("-> Procedimento abortado.")
    # Aguardando ENTER do usuário
    pause_read()

def sonda_usuario_new_connection():
    """Sonda o usuário para saber qual os dados da nova conexão e retorna um dicionário"""
    name_host = input('Nome do Host: ')
    ip_host = input('IP do Host: ')
    try:
        sshport_host = int(input('Porta SSH [22]: '))
    except ValueError:
        sshport_host = 22
    user_host = input('Login ' + '[' + USER_LINUX + ']' + ': ')
    if not user_host:
        user_host = USER_LINUX

    pass_host = input('Password [PrivateKey]: ')

    # Padrão de uma informação da base
    new_connection = {
        "hostid": "null",
        "host": name_host,
        "ip": ip_host,
        "porta_ssh": sshport_host,
        "user_ssh": user_host,
        "pass_ssh": pass_host,
        "grupo": "local",
    }

    return new_connection

def edit_host(local_db, host_original):
    # Cria uma cópia do original para editar
    host_editado = host_original.copy()
    # Retorna as chaves do host para serem editadas
    for atributo in host_editado.keys():
        # Formato o atributo retirando o underline (_) por espaço
        atributo_formatado = atributo.replace('_', ' ')
        new_value = input('Digite um novo valor para ' + atributo_formatado + ' ['+str(host_editado[atributo])+']: ')
        # Se o usuário digitar um novo valor salva o valor no campo correspondente
        if new_value:
            host_editado[atributo] = new_value
    
    # Atualiza o host escolhido dentro da base local
    for host in local_db:
        # Procura pelo host original para editá-lo
        if host == host_original:
            for atributo in host.keys():
                host[atributo] = host_editado[atributo]

    # Salva a base localmente
    salvar_db(local_db)
    # Aguardando ENTER do usuário
    pause_read()

def del_host(local_db, host):
    deletar = input('Você está prestes a deletar o host: [' + str(host["host"]) + ']. É isso mesmo que deseja fazer? [y/n] ')
    if deletar == "y" or deletar == "Y":
        local_db.remove(host)
        # Salva a base localmente
        salvar_db(local_db)
    else:
        input("-> Procedimento abortado.")

    # Aguardando ENTER do usuário
    pause_read()

def selecao_opcao(opcao, local_db):
    # opcao 1 no menu
    if opcao == "connect_ssh":
        # Busca o Host para conectar-se via SSH
        host = sonda_usuario_connect_ssh(local_db)
        if host != "ERRO":
            # Se o host devolvido não tiver senha configurada significa que o acesso é privateKey
            if not host["pass_ssh"]:
                comando = "ssh " + host["user_ssh"] + "@" + host["ip"] + " -p " + str(host["porta_ssh"])
            else:
                # O host tem uma senha configurada na base!
                comando = "sshpass -p " + host["pass_ssh"] + " ssh " + host["user_ssh"] + "@" + host["ip"] + " -p " + str(host["porta_ssh"])
            
            # Salva os dados no arquivo Temporário para coleta do Frontend
            salvar_dado(comando, 'w')
        else:
            salvar_dado("ERRO - Busca não retornou dados. Verificação realizada na Base Local", 'w')
    # opcao 2 no menu
    elif opcao == "insert_new_connection":
        host = sonda_usuario_new_connection()
        local_db = insert_connection_local_db(local_db, host["host"], host["ip"], host["porta_ssh"], host["user_ssh"], host["pass_ssh"], host["grupo"], host["hostid"])
        # Salva a base localmente
        salvar_db(local_db)
    # opcao 3 no menu
    elif opcao == "edit_host":
        # Sondo o usuário para saber qual conexão ele deseja editar
        host = sonda_usuario_connect_ssh(local_db)
        if host != "ERRO":
            edit_host(local_db, host)
    # opcao 4 no menu
    elif opcao == "del_host":
        # Sondo o usuário para saber qual conexão ele deseja editar
        host = sonda_usuario_connect_ssh(local_db)
        if host != "ERRO":
            del_host(local_db, host)
    # opcao 5 no menu
    elif opcao == "sync_local_db_zbx":
        # Sincronizar a base local com a base do Zabbix
        sync_local_db_zbx(local_db)
    # opcao 6 no menu
    elif opcao == "redefinir_local_db":
        # Zera a base
        redefinir_local_db(local_db)

    else:
        print("Opção Inválida! Tente novamente... - Back")

def pause_read():
    input('Enter para continuar...')

def main(args):
    """Função Principal"""
    opcao = str(args[1])
    # Base local instanciada
    local_db = carregar_db()
    selecao_opcao(opcao, local_db)

# Chamando a função principal
try:
    main(sys.argv)
except (KeyboardInterrupt, SystemExit):
    # Usuário apertou o "CTRL + C" - Interrupção de teclado.
    print('\n\n --> Operação Cancelada.')

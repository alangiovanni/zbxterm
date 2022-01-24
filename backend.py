#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alan Giovanni
# LinkedIn: https://www.linkedin.com/in/alan-giovanni-53aaa9ab/
# Data: 18/05/2021
# Description: Backend do gerenciador de SSH

import sys # importa o modulo que recebe os parâmetros passados na execucao do Script
import subprocess # Execução de comandos remotos
import modules.database as database # Import do Módulo database que está na pasta modules do projeto corrente
import modules.zabbix as zabbix # Import do Módulo Zabbix que está na pasta modules do projeto corrente
import modules.configuration as configuracoes # Importa o módulo que ler as configurações default

# Variáveis Globais
# Arquivo de Uso Temporário e Geral
ARQ_TEMP = "/tmp/arq_temp.txt"

# Grupo Default para as Conexões descobertas do Zabbix
GROUP_ZBX = "zbx"

# Gambi para conseguir definir uma variável de ambiente abaixo
def retorna_credenciais():
    # Ler as configurações destinadas ao recurso do zbxterm
    config_zbxterm = configuracoes.ler_config('zbxterm')
    usuario = config_zbxterm['ssh_user']
    senha = config_zbxterm['ssh_pass']
    path_private_key = config_zbxterm['ssh_private_key']

    # Se n houver usuário nas configurações default é aplicado o comando whoami
    if not usuario:
        subprocess_retorno = subprocess.Popen(["whoami"], stdout=subprocess.PIPE, shell=True)
        usuario = str(subprocess_retorno.stdout.read().decode('UTF-8')).replace('\n', '')
    
    return [usuario, senha, path_private_key]

SSH_USER, SSH_PASS, PATH_PRIVATE_KEY = retorna_credenciais()

def create_list_hosts_zbx(obj_hosts, obj_interfaces) -> list:
    """Cria uma base local contendo os hosts configurados no Zabbix"""
    # Criando uma base local vazia
    list_host_with_ip = []

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
                list_host_with_ip.append(new_host) # Inserindo no final do array o dicionário recém-formado.
    
    # Retorna a base local
    return list_host_with_ip

def create_list_hosts_ssh_by_zbx_list(local_db_zbx:list) -> list:
    """Cria a base local principal de conexões SSH"""
    # Criando uma base local temporária para manipulação idêntica a base do Zabbix
    list_connection_ssh = local_db_zbx.copy()

    # Percorrendo o array de hosts do Zabbix
    for host in list_connection_ssh:
        host.update({"porta_ssh": 22, "user_ssh": SSH_USER, "pass_ssh": SSH_PASS, "grupo": GROUP_ZBX})
    
    # Retorna a base local
    return list_connection_ssh

def sync_with_zbx():
    """Sincroniza a base local com os hosts configurados no Zabbix"""
    # Verifica se o Zabbix está Online
    print("Verificando se o Zabbix está disponível...")
    if zabbix.is_online():
        # Autenticação no Zabbix
        print("Realizando autenticação no Zabbix...")
        auth_token = zabbix.auth()
        
        # Verifica se o token contém a string Erro
        if 'Erro' in auth_token:
            print(auth_token) # Printa o erro e encerra a sincronia com o zabbix
            return
        
        print("Sincronizando a base local com o Zabbix...")
        hosts_zbx = zabbix.get_hosts(auth_token)
        interfaces_zbx = zabbix.get_interfaces(auth_token)
        local_db_zbx = create_list_hosts_zbx(hosts_zbx, interfaces_zbx)
        
        # Salvando a lista das conexões SSH inseridas pelo usuário
        list_connections_non_zbx = database.get_hosts_inserted_by_user(GROUP_ZBX)

        # Salva na base a lista de conexões SSH obtidas do Zabbix
        database.save(create_list_hosts_ssh_by_zbx_list(local_db_zbx))

        # Adicionando as conexões inseridas pelo usuário salvas anteriormente na base recém sincronizada
        if list_connections_non_zbx: # Se existir alguma conexão entre nessa condição
            for host in list_connections_non_zbx:
                database.add_connection_ssh(host["host"], host["ip"], host["porta_ssh"], host["user_ssh"], host["pass_ssh"], host["grupo"], host["hostid"])
        
        print("Base local Sincronizada!!")
    else:
        print('O Zabbix está Offline! Verifique as configurações')

def selecao_opcao(opcao):
    # opcao 1 no menu
    if opcao == "connect_ssh":
        # Busca o Host para conectar-se via SSH
        host = sonda_usuario_connect_ssh()
        if host:
            # Se o host devolvido não tiver senha configurada significa que o acesso é privateKey default ou a senha é desconhecida e será solicitado durante a conexão
            if not host["pass_ssh"]:
                # Se existir chave RSA diferente do path default, passa a chave como parâmetro
                if PATH_PRIVATE_KEY:
                    comando = "ssh " + host["user_ssh"] + "@" + host["ip"] + " -p {}".format(host["porta_ssh"]) + " -i " + PATH_PRIVATE_KEY
                # Comando default - PrivateKey padrão ou solicitação da senha durante a tentativa de conexão
                else:
                    comando = "ssh " + host["user_ssh"] + "@" + host["ip"] + " -p " + str(host["porta_ssh"])
            else:
                # O host tem uma senha configurada na base!
                comando = "sshpass -p " + host["pass_ssh"] + " ssh " + host["user_ssh"] + "@" + host["ip"] + " -p " + str(host["porta_ssh"])
            
            # Salva os dados no arquivo Temporário para coleta do Frontend
            return_frontend(comando, 'w')
        else:
            return_frontend("ERRO - Busca não retornou dados. Verificação realizada na Base Local", 'w')
    # opcao 2 no menu
    elif opcao == "insert_new_connection":
        host = sonda_usuario_new_connection()
        database.add_connection_ssh(host["host"], host["ip"], host["porta_ssh"], host["user_ssh"], host["pass_ssh"], host["grupo"], host["hostid"])
    # opcao 3 no menu
    elif opcao == "edit_host":
        # Sondo o usuário para saber qual conexão ele deseja editar
        host = sonda_usuario_connect_ssh()
        if host:
            edit_host(host)
    # opcao 4 no menu
    elif opcao == "del_host":
        # Sondo o usuário para saber qual conexão ele deseja editar
        host = sonda_usuario_connect_ssh()
        if host:
            del_host(host)
    # opcao 5 no menu
    elif opcao == "sync_local_db_zbx":
        # Sincronizar a base local com a base do Zabbix
        sync_with_zbx()
        # Aguardando ENTER do usuário
        pause_read()
    # opcao 6 no menu
    elif opcao == "redefinir_local_db":
        # Zera a base
        database.reset()
        # Aguardando ENTER do usuário
        pause_read()
    # opcao 8 no menu, opcao 1 no submenu (configurações)
    elif opcao == "editar_config_default":
        # Sondo o usuário para saber o que ele deseja editar
        editar_config_zbxterm()
        # Aguardando ENTER do usuário
        pause_read()
    # opcao 8 no menu, opcao 2 no submenu (configurações)
    elif opcao == "update_database_with_configs_default":
        # Sondo o usuário para saber o que ele deseja editar
        update_database_with_configs_default()
        # Aguardando ENTER do usuário
        pause_read()

    else:
        print("Opção Inválida! Tente novamente... - Back")

def sonda_usuario_connect_ssh() -> dict:
    """Sonda o usuário para saber qual o host deseja conexão SSH"""
    resposta = str(input('Pesquisa (IP ou Host): ')).lower().strip()
    list_host = database.get_hosts_by_dado(resposta)
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

def del_host(host):
    deletar = input('Você está prestes a deletar o host: [' + str(host["host"]) + ']. É isso mesmo que deseja fazer? [y/n] ')
    if deletar == "y" or deletar == "Y":
        database.del_connection_ssh(host)
    else:
        input("-> Procedimento abortado.")

    # Aguardando ENTER do usuário
    pause_read()
    
def edit_host(host_original):
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
    
    # Substitui o host original pelo host editado.
    database.edit_connection_ssh(host_original, host_editado)
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
    user_host = input('Login ' + '[' + SSH_USER + ']' + ': ')
    if not user_host:
        user_host = SSH_USER

    pass_host = input('Password ' + '[' + SSH_PASS + ']' + ': ')
    if not pass_host:
        pass_host = SSH_PASS
    
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

def pause_read():
    input('Enter para continuar...')

def return_frontend(informacao, method):
    with open(ARQ_TEMP, method) as arquivo:
        arquivo.write(informacao)

def editar_config_zbxterm():
    """Edita as configurações default do arquivo de configurações default.json"""
    # Flag para saber se o usuário alterou alguma config
    usuario_modificou = False
    # Pega todas as configurações
    all_config = configuracoes.read_all()
    # Pergunta ao usuário o que ele quer alterar
    print("\nQual configuração padrão você deseja editar?\nObs: Registros que foram adicionados manualmente não terão as configurações atualizadas. Para isso, use o menu anterior na opção 3.\n")
    for key_resource in all_config.keys():
        # Printa na tela algo similar: -> zbxterm (descrição)
        print("-> ", key_resource + " (" + all_config[key_resource]['description'] + ")")
    
    key_resource = input("\nDigite: ").lower()
    # Verifica se o usuário digitou uma key valida para editar
    if key_resource in all_config.keys():
        # Coleta só as configurações do recurso solicitado para editar
        resource = all_config[key_resource]
        for atributo in resource.keys():
            # Não deixa o usuário editar algumas configs específicas
            if (atributo != "description") and (atributo != "database") and (atributo != "arq_temp"):
                value = str(input('Digite um novo valor para o atributo "' + atributo + '" [' + resource[atributo] + ']: '))
                # Usuário alterou a configuração default
                if value:
                    all_config[key_resource][atributo] = value
                    usuario_modificou = True
    else:
        print("\nOpção inválida. Por favor, repita o processo digitando o nome do recurso igualmente ao que está sendo exibido acima.")
    # Salvar as novas configurações digitadas pelo usuário no arquivo de configurações
    if usuario_modificou:
        configuracoes.save_config(all_config)
        # Se o usuário tiver editado as configurações do zbxterm entra nesse if
        if key_resource == "zbxterm":
            # Atualiza a base com configs que o usuário pode ter alterado como usuário ssh e/ou senha.
            update_database_with_configs_default()
    else:
        print("Nenhuma alteração realizada!")

def update_database_with_configs_default():
    # Atualiza as variáveis de ambiente
    SSH_USER, SSH_PASS, PATH_PRIVATE_KEY = retorna_credenciais()

    # Carrega a base
    local_db = database.load()
    # Percorre cada registro da base e atualiza-os
    print("Atualizando o database do zbxterm... ")
    for registro in local_db:
        if registro['grupo'] == GROUP_ZBX:
            registro['user_ssh'] = SSH_USER
            registro['pass_ssh'] = SSH_PASS

    database.save(local_db)

def main(args):
    """Função Principal"""
    opcao = str(args[1])
    selecao_opcao(opcao)

# Chamando a função principal
try:
    main(sys.argv)
except (KeyboardInterrupt, SystemExit):
    # Usuário apertou o "CTRL + C" - Interrupção de teclado.
    print('\n\n --> Operação Cancelada.')
    pause_read()

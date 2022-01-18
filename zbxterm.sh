#!/bin/bash
# Author: Alan Giovanni - Squad Hubble
# Data: 18/05/2021
# Description: zbxterm é um gerenciador de conexões SSH com base local independente podendo ser sincronizada com o seu Zabbix.

ARQ_TEMP="/tmp/arq_temp.txt"
BACKEND="/opt/zbxterm/backend.py"

# Dependencias: ssh, sshpass

function menu(){
    while true;
    do
        echo ""
        echo "|------------------------------------------------------|"
        echo "|---------------------- ZBX_TERM ----------------------|"
        echo "|------------------------------------------------------|"
        echo "| Operador: `whoami`"
        echo "|------------------------------------------------------|"
        echo "| [1] - Conectar via SSH"
        echo "| [2] - Adicionar uma nova conexão"
        echo "| [3] - Editar uma conexão"
        echo "| [4] - Deletar uma conexão"
        echo "| [5] - Sincronizar base local com o Zabbix"
        echo "| [6] - Redefinir a base local"
        echo "|"
        echo "| [9] - Ajuda"
        echo "| [0] - SAIR"
        echo "|------------------------------------------------------|"
        echo ""
        read -p 'Digite uma opção: ' opcao
        
        case $opcao in
            0|exit|sair) exit ;;
            1|connect|conectar|ssh) connect_ssh ;;
            2|add|new|adicionar) insert_new_connection ;;
            3|edit|editar) edit_host ;;
            4|del|deletar|remove) del_host ;;
            5|sync|sincronizar) sync_local_db_zbx ;;
            6) redefinir_local_db ;;
            9|help|ajuda|aff) ajuda ;;
            *) echo "Opção Inválida. Tente novamente..."
        esac

    done
}

# Função Principal
function main(){
    menu
}

# conectar ao host
function connect_ssh(){
    # Chamo o backend passando o parâmetro de conexão com SSH. Esse parâmetro será tratado no python
    python3 $BACKEND "connect_ssh"
    # Salva em uma variável o comando a ser executado. Deve ter algo similar a: "ssh alan.targino@192.168.0.1 -p 22"
    comando=`cat $ARQ_TEMP`
    if [ $(echo $comando | grep -c "ERRO") -eq 0 ]; then
        rm -rf $ARQ_TEMP
        echo "Conectando..."
        $comando #Executa o comando
    fi
}

function sync_local_db_zbx(){
    python3 $BACKEND "sync_local_db_zbx"
}

function redefinir_local_db() {
    python3 $BACKEND "redefinir_local_db"
    clear
}

function insert_new_connection() {
    python3 $BACKEND "insert_new_connection"
}

function edit_host() {
    python3 $BACKEND "edit_host"
}

function del_host() {
    python3 $BACKEND "del_host"
}

function ajuda() {
    echo -e "
    O $0 possui um menu de opções numérico mas também há a possibilidade de digitar
    algumas palavras chaves para que o programa entenda o que você deseja fazer!
    Abaixo segue todas as palavras configuradas nativamente:\n
    connect, conectar, ssh - Fazer uma conexão SSH
    add, new, adicionar    - Adicionar uma nova conexão SSH manualmente
    edit, editar           - Editar uma conexão da base local
    del, deletar, remove   - Deleta uma conexão da base local
    sync, sincronizar      - Atualiza a base local verificando se houve atualização no Zabbix
    help, ajuda, aff       - Abre esta seção de apoio
    "
    read -p "Enter para voltar ao menu de opções..."
}
# Start
main
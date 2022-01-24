#!/bin/bash
# Author: Alan Giovanni
# LinkedIn: https://www.linkedin.com/in/alan-giovanni-53aaa9ab/
# Data: 17/01/2022
# Description: Instalador do zbxterm

README="https://github.com/alangiovanni/zbxterm/blob/main/README.md"

function download_zbxterm(){
    echo "Baixando o zbxterm..."
    git clone https://github.com/alangiovanni/zbxterm.git && echo "OK"
}
function install_requirements(){
    echo "Instalando os pacotes do requirements.txt do zbxterm..."
    pip3 install -r zbxterm/requirements.txt && echo "OK"
}
function validate_requirements(){
    # 0 = não validado / 1 = validado
    validate=1
    while read -r line;
    do
        package_name=$(echo $line | cut -d '=' -f1)
        # Se entrar nesse IF, algum pacote não foi instalado corretamente.
        if [ $(pip3 list | grep -Fc $package_name) -eq 0 ]; then
            validate=0
        fi
    done < requirements.txt

    echo $validate
}
function config_zbxterm(){
    echo "Configurando o zbxterm no S.O..."
    rm zbxterm/README.md
    rm zbxterm/requirements.txt
    rm -rf zbxterm/.git
    rm zbxterm/install_zbxterm.sh
    mv zbxterm /opt
    ln -s /opt/zbxterm/zbxterm.sh /usr/local/bin/zbxterm
}

function informes_gerais(){
    echo -e "Para o adequado funcionamento da aplicação favor ler o README.md\n$README"
}

function msg_sucesso(){
    echo -e "-> Instalação e configuração realizada com SUCESSO! O zbxterm já pode ser executado na linha de comando:\n$ zbxterm"
}

function is_root(){
    if [ "$(id -u)" != "0" ]; then
        echo 0
    else
        echo 1
    fi
}
function main(){
    # flag de falha em algum if do código | 0 = false / 1 = true
    falha_execucao=0

    # Clone repositorio
    download_zbxterm
    echo

    # Verifica se baixou
    if [ -d zbxterm ]; then
        install_requirements
        echo
        # Verifica se instalou tudo certinho!
        echo "Validando a instalação dos requirements..."
        if [ $(validate_requirements) -eq 1 ]; then
            echo "OK"
            # Configura o zbxterm para ser chamado de qualquer lugar do S.O
            config_zbxterm
        else
            falha_execucao=1
            echo "Falha na instalação de um ou mais pacotes do requirements."
        fi
    else
        falha_execucao=1
        echo "Falha ao clonar o repositório do Github."
    fi
    # Se tudo der certo é exibido uma mensagem de sucesso!
    if [ $falha_execucao -eq 0 ]; then
        msg_sucesso
    fi
    # Manda um informativo geral
    echo
    informes_gerais
}

# Start da mágica - Só como root!
if [ $(is_root) -eq 1 ]; then
    main
else
    echo "Você deve executar esse script como root!!"
    echo "$ sudo $0"
fi

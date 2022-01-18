# zbxterm
	🚧  zbxterm 🚀 Em desenvolvimento  🚧
<p align="center">
 <a href="#-sobre-o-projeto">Sobre</a> •
 <a href="#-funcionalidades">Funcionalidades</a> •
 <a href="#pr%C3%A9-requisitos">Pré-requisitos</a> •
 <a href="#-instala%C3%A7%C3%A3o">Instalação</a> •
 <a href="#%EF%B8%8F-configura%C3%A7%C3%A3o">Configuração</a> •
 <a href="#-tecnologias">Tecnologias</a> •
</p>

## 💻 Sobre o projeto

Zbxterm - É um gerenciador de conexões SSH simples. Faz o básico que é adicionar, editar e remover conexões SSH mas foi desenvolvido com um propósito de agilizar o troubleshooting dos atendimentos N1 e N2 podendo ser integrado com o Zabbix da sua infraestrutura de monitoramento! Dessa forma é possível sincronizar a base do Zabbix com uma base local e ter acesso SSH a todos os hosts existentes no Zabbix.

## 💪 Funcionalidades

- [x] Usuário pode gerenciar conexões SSH:
  - [x] Adicionar
  - [x] Editar
  - [x] Deletar
  - [x] Adicionar hosts do zabbix automaticamente a base local
  - [x] Buscar:
    - Por IP
    - Por parte do IP (octetos)
    - Por Host
    - Por String

- [ ] Usuário pode alterar configurações default:
  - [x] Qualquer conexão da base local (Login, password, grupo...)
  - [x] Redefinir a base local, apagando totalmente seu conteúdo
  - [ ] Login do operador

---

### Pré-requisitos

Antes de começar, você vai precisar ter instalado em sua máquina as seguintes ferramentas:
[Git](https://git-scm.com) e [Python 3](https://www.python.org).

---

### 🎲 Instalação

```bash
# Clone este repositório
$ git clone https://github.com/alangiovanni/zbxterm.git

# Acesse a pasta do projeto no terminal/cmd
$ cd zbxterm

# Instale as dependências
$ apt install openssh-server sshpass

# Execute o instalador
$ chmod +x install_zbxterm.sh
$ sudo ./install_zbxterm.sh

```

---

### ⚙️ Configuração

Procure o arquivo </opt/zbxterm/backend.py> para alterar algumas variáveis para que o zbxterm funcione adequadamente em seu ambiente. Abaixo segue um trecho do código onde as alterações devem ser realizadas conforme seu ambiente.

```bash
# Variáveis Globais
# Zabbix API
USER_ZBX = '<USER>'
PASS_ZBX = '<PASSWORD>'
URL_ZBX = '<URL>/api_jsonrpc.php'

```

---

### 🛠 Tecnologias

As seguintes ferramentas foram usadas na construção do projeto:

- [Zabbix API](https://www.zabbix.com/documentation/current/en/manual/api)
- [Python 3](https://www.python.org)
- [Github](https://github.com)

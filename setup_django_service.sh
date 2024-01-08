#!/bin/bash

# Atualizar os pacotes e instalar o Python e o pip
echo "Atualizando pacotes e instalando Python e pip..."
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip

# Definir o caminho do diretório do projeto Django
PROJECT_DIR=$(pwd)
SERVICE_NAME="django"

# Criar ambiente virtual e instalar dependências
echo "Criando ambiente virtual e instalando dependências..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Executar migrações do Django e o comando cities_light
echo "Executando migrações do Django e comando cities_light..."
python manage.py makemigrations
python manage.py migrate
python manage.py cities_light

# Criar o script de inicialização do Django
echo "Criando script de inicialização..."
echo "#!/bin/bash
cd $PROJECT_DIR
source venv/bin/activate
python manage.py runserver 0.0.0.0:88" > start_django.sh
#python manage.py runserver 177.73.234.198:88"
	

# Tornar o script de inicialização executável
chmod +x start_django.sh

# Criar o arquivo de serviço systemd
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo "[Unit]
Description=Iniciar Servidor Django na inicialização

[Service]
ExecStart=$PROJECT_DIR/start_django.sh
User=root

[Install]
WantedBy=multi-user.target" | sudo tee $SERVICE_FILE

# Recarregar os daemons do systemd, habilitar e iniciar o serviço
echo "Configurando e iniciando o serviço systemd..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "Instalação concluída!"

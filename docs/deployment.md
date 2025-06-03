# Guia de Implantação em Produção

Este guia detalha os passos necessários para implantar a aplicação Raiox AI em um ambiente de produção.

## Requisitos do Servidor

- Ubuntu 20.04 LTS ou superior
- Python 3.11+
- PostgreSQL 14+ com pgvector
- Nginx
- Acesso ao DigitalOcean Spaces (ou outro serviço S3-compatible)
- Pelo menos 4GB de RAM (recomendado 8GB+)
- Opcional: GPU para aceleração do processamento CLIP

## Passos para Implantação

### 1. Preparação do Servidor

```bash
# Atualizar o sistema
sudo apt update
sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip \
    postgresql postgresql-contrib libpq-dev \
    nginx supervisor git curl wget unzip
```

### 2. Instalar pgvector

```bash
sudo apt install -y postgresql-server-dev-14 build-essential
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
cd ..
rm -rf pgvector

# Habilitar a extensão no PostgreSQL
sudo -u postgres psql -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 3. Configurar o Banco de Dados

```bash
# Criar usuário e banco de dados
sudo -u postgres psql -c "CREATE USER raiox_user WITH PASSWORD 'Xc7!rA2v9Z@1pQ3y';"
sudo -u postgres psql -c "CREATE DATABASE raiox_db OWNER raiox_user;"
sudo -u postgres psql -d raiox_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 4. Configurar o Diretório da Aplicação

```bash
# Criar diretório da aplicação
sudo mkdir -p /opt/raiox-app
sudo mkdir -p /opt/raiox-app/data/imagens
sudo mkdir -p /opt/raiox-app/logs

# Definir permissões
sudo chown -R $USER:$USER /opt/raiox-app
```

### 5. Clonar o Repositório

```bash
# Clonar o repositório
git clone https://github.com/cristianosiqueirapires/raiox-fastapi.git /opt/raiox-app
cd /opt/raiox-app
```

### 6. Configurar o Ambiente Virtual

```bash
# Criar e ativar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
```

### 7. Configurar Variáveis de Ambiente

```bash
# Copiar o arquivo de exemplo
cp .env.example .env

# Editar o arquivo com as configurações corretas
nano .env
```

### 8. Configurar o Serviço Systemd

```bash
# Copiar o arquivo de serviço
sudo cp systemd/raiox-ai.service /etc/systemd/system/

# Recarregar o systemd
sudo systemctl daemon-reload

# Habilitar e iniciar o serviço
sudo systemctl enable raiox-ai
sudo systemctl start raiox-ai

# Verificar o status
sudo systemctl status raiox-ai
```

### 9. Configurar o Nginx como Proxy Reverso

```bash
# Criar arquivo de configuração do Nginx
sudo nano /etc/nginx/sites-available/raiox-ai

# Adicionar a seguinte configuração
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/raiox-ai /etc/nginx/sites-enabled/

# Testar configuração do Nginx
sudo nginx -t

# Reiniciar o Nginx
sudo systemctl restart nginx
```

### 10. Configurar o Monitoramento

```bash
# Copiar o script de monitoramento
sudo cp scripts/check_raiox.sh /opt/raiox-app/scripts/
sudo chmod +x /opt/raiox-app/scripts/check_raiox.sh

# Configurar o cron para executar o script a cada 5 minutos
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/raiox-app/scripts/check_raiox.sh") | crontab -
```

### 11. Configurar HTTPS (Recomendado)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado SSL
sudo certbot --nginx -d seu-dominio.com

# Certbot irá modificar automaticamente a configuração do Nginx
```

## Verificação da Implantação

Após a implantação, verifique se a aplicação está funcionando corretamente:

```bash
# Verificar o status do serviço
sudo systemctl status raiox-ai

# Verificar os logs
sudo journalctl -u raiox-ai

# Testar o endpoint de healthcheck
curl http://localhost:8000/healthcheck
```

## Solução de Problemas

Se encontrar problemas durante a implantação, verifique:

1. **Logs do Serviço**: `sudo journalctl -u raiox-ai`
2. **Logs da Aplicação**: `/opt/raiox-app/logs/`
3. **Logs do Nginx**: `/var/log/nginx/error.log`
4. **Conexão com o Banco de Dados**: `sudo -u postgres psql -d raiox_db -c "SELECT 1;"`
5. **Permissões de Arquivos**: Certifique-se de que o usuário que executa o serviço tem permissões adequadas

## Atualização da Aplicação

Para atualizar a aplicação:

```bash
# Navegar até o diretório da aplicação
cd /opt/raiox-app

# Puxar as alterações mais recentes
git pull

# Atualizar dependências
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar o serviço
sudo systemctl restart raiox-ai
```

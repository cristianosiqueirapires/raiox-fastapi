# Guia de Monitoramento e Manutenção

Este guia detalha as práticas recomendadas para monitoramento, manutenção e solução de problemas da aplicação Raiox AI em produção.

## Monitoramento Automático

A aplicação Raiox AI inclui um sistema de monitoramento automático que verifica regularmente o status do serviço e toma ações corretivas quando necessário.

### Script de Monitoramento

O script `check_raiox.sh` localizado em `/opt/raiox-app/scripts/` realiza as seguintes verificações:

1. Verifica se o serviço systemd está em execução
2. Testa o endpoint de healthcheck da API
3. Verifica a conectividade com o banco de dados
4. Reinicia o serviço automaticamente em caso de falha
5. Envia notificações por e-mail em caso de problemas persistentes

### Configuração do Cron

O script de monitoramento é executado a cada 5 minutos através do cron:

```bash
# Visualizar a configuração atual do cron
crontab -l

# Editar a configuração do cron (se necessário)
crontab -e

# Configuração recomendada
*/5 * * * * /opt/raiox-app/scripts/check_raiox.sh
```

### Logs de Monitoramento

Os logs do monitoramento são armazenados em:

- `/opt/raiox-app/logs/monitor.log`: Logs do script de monitoramento
- `/var/log/syslog`: Logs do sistema, incluindo execuções do cron
- `/var/log/journal/`: Logs do systemd (acessíveis via `journalctl`)

## Manutenção Regular

### Backup do Banco de Dados

Recomenda-se realizar backups regulares do banco de dados PostgreSQL:

```bash
# Backup diário do banco de dados
pg_dump -U raiox_user -d raiox_db -F c -f /opt/raiox-app/backups/raiox_db_$(date +%Y%m%d).dump

# Configuração de backup automático via cron (diário às 2h da manhã)
0 2 * * * pg_dump -U raiox_user -d raiox_db -F c -f /opt/raiox-app/backups/raiox_db_$(date +%Y%m%d).dump
```

### Rotação de Logs

Configure a rotação de logs para evitar que os arquivos de log cresçam indefinidamente:

```bash
# Criar arquivo de configuração para logrotate
sudo nano /etc/logrotate.d/raiox-ai

# Adicionar a seguinte configuração
/opt/raiox-app/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
}
```

### Atualização de Dependências

Atualize regularmente as dependências do projeto para garantir segurança e estabilidade:

```bash
# Ativar ambiente virtual
cd /opt/raiox-app
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip

# Atualizar dependências (com cuidado em ambiente de produção)
pip install --upgrade -r requirements.txt

# Reiniciar o serviço após atualizações
sudo systemctl restart raiox-ai
```

## Solução de Problemas Comuns

### Serviço Não Inicia

Se o serviço não iniciar, verifique:

```bash
# Verificar status do serviço
sudo systemctl status raiox-ai

# Verificar logs detalhados
sudo journalctl -u raiox-ai -n 100 --no-pager

# Verificar permissões de arquivos
ls -la /opt/raiox-app/

# Verificar configuração do serviço
cat /etc/systemd/system/raiox-ai.service
```

### Problemas de Conexão com o Banco de Dados

Se houver problemas de conexão com o banco de dados:

```bash
# Verificar se o PostgreSQL está em execução
sudo systemctl status postgresql

# Verificar configurações de conexão
cat /opt/raiox-app/.env | grep POSTGRES

# Testar conexão direta
psql -U raiox_user -h localhost -d raiox_db -c "SELECT 1;"

# Verificar extensão pgvector
sudo -u postgres psql -d raiox_db -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Problemas com DigitalOcean Spaces

Se houver problemas com o armazenamento de imagens:

```bash
# Verificar configurações do Spaces
cat /opt/raiox-app/.env | grep DO_SPACES

# Testar conexão com o Spaces usando AWS CLI
aws s3 ls s3://raiox-imagens --endpoint-url https://nyc3.digitaloceanspaces.com
```

### Problemas de Memória

Se a aplicação estiver consumindo muita memória (especialmente ao processar imagens com CLIP):

```bash
# Verificar uso de memória
free -h
top

# Ajustar configurações de swap se necessário
sudo swapon --show
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Métricas e Monitoramento Avançado

Para monitoramento mais avançado, considere implementar:

1. **Prometheus + Grafana**: Para coleta e visualização de métricas
2. **ELK Stack**: Para centralização e análise de logs
3. **Alertmanager**: Para alertas mais sofisticados

## Contatos de Suporte

Em caso de problemas críticos, entre em contato com:

- Administrador do Sistema: admin@example.com
- Equipe de Desenvolvimento: dev@example.com

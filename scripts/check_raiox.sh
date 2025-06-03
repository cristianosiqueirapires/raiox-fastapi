#!/bin/bash
# Script para verificar e reiniciar o serviço Raiox AI se necessário

# Configurações
SERVICE_NAME="raiox-ai"
LOG_FILE="/opt/raiox-app/logs/monitor.log"
API_URL="http://localhost:8000/healthcheck"
ADMIN_EMAIL="admin@example.com"

# Função para registrar logs
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Criar diretório de logs se não existir
mkdir -p "$(dirname $LOG_FILE)"

log "Iniciando verificação do serviço $SERVICE_NAME"

# Verificar se o serviço está em execução
if ! systemctl is-active --quiet $SERVICE_NAME; then
    log "ALERTA: Serviço $SERVICE_NAME não está em execução. Tentando reiniciar..."
    systemctl restart $SERVICE_NAME
    sleep 10
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        log "Serviço $SERVICE_NAME reiniciado com sucesso."
    else
        log "ERRO: Falha ao reiniciar o serviço $SERVICE_NAME. Enviando notificação."
        echo "Falha ao reiniciar o serviço $SERVICE_NAME em $(hostname) em $(date)" | mail -s "ALERTA: Falha no serviço $SERVICE_NAME" $ADMIN_EMAIL
    fi
else
    log "Serviço $SERVICE_NAME está em execução."
    
    # Verificar se a API está respondendo corretamente
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)
    
    if [ $HTTP_STATUS -eq 200 ]; then
        log "API está respondendo corretamente (HTTP $HTTP_STATUS)."
        
        # Verificar resposta do healthcheck
        HEALTH_CHECK=$(curl -s $API_URL)
        if [[ $HEALTH_CHECK == *"\"status\":\"ok\""* && $HEALTH_CHECK == *"\"database_status\":\"ok\""* ]]; then
            log "Healthcheck OK: API e banco de dados estão funcionando corretamente."
        else
            log "ALERTA: Healthcheck indica problemas. Resposta: $HEALTH_CHECK"
            log "Tentando reiniciar o serviço..."
            systemctl restart $SERVICE_NAME
            sleep 10
            
            # Verificar novamente após reinício
            HEALTH_CHECK_AFTER=$(curl -s $API_URL)
            if [[ $HEALTH_CHECK_AFTER == *"\"status\":\"ok\""* && $HEALTH_CHECK_AFTER == *"\"database_status\":\"ok\""* ]]; then
                log "Serviço recuperado após reinício."
            else
                log "ERRO: Problemas persistem após reinício. Enviando notificação."
                echo "Problemas com o serviço $SERVICE_NAME em $(hostname) em $(date). Healthcheck: $HEALTH_CHECK_AFTER" | mail -s "ALERTA: Problemas no serviço $SERVICE_NAME" $ADMIN_EMAIL
            fi
        fi
    else
        log "ALERTA: API não está respondendo corretamente (HTTP $HTTP_STATUS). Tentando reiniciar..."
        systemctl restart $SERVICE_NAME
        sleep 10
        
        # Verificar novamente após reinício
        HTTP_STATUS_AFTER=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)
        if [ $HTTP_STATUS_AFTER -eq 200 ]; then
            log "API recuperada após reinício (HTTP $HTTP_STATUS_AFTER)."
        else
            log "ERRO: API continua não respondendo após reinício (HTTP $HTTP_STATUS_AFTER). Enviando notificação."
            echo "API do serviço $SERVICE_NAME não está respondendo em $(hostname) em $(date)" | mail -s "ALERTA: API do serviço $SERVICE_NAME não responde" $ADMIN_EMAIL
        fi
    fi
fi

log "Verificação concluída."

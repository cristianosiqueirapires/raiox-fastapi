# Raiox AI - Nova Arquitetura FastAPI

Implementação da nova arquitetura FastAPI para o projeto Raiox AI, conforme recomendações do Gemini.

## Visão Geral

Este repositório contém a implementação completa da nova arquitetura FastAPI para o projeto Raiox AI, incluindo:

- API FastAPI com estrutura modular e escalável
- Integração com PostgreSQL e pgvector para busca vetorial eficiente
- Implementação de vetorização CLIP real (não simulada) com suporte CUDA
- Integração com DigitalOcean Spaces para armazenamento de imagens
- Configuração de CI/CD com GitHub Actions
- Monitoramento automático via systemd e cron

## Estrutura do Projeto

```
/
├── app/                    # Código principal da aplicação
│   ├── api/                # Endpoints da API
│   ├── core/               # Configurações e funcionalidades centrais
│   ├── db/                 # Configuração e modelos do banco de dados
│   ├── models/             # Modelos Pydantic para validação de dados
│   ├── schemas/            # Esquemas para serialização/deserialização
│   ├── services/           # Serviços de negócio (CLIP, busca, etc.)
│   └── utils/              # Funções utilitárias
├── data/                   # Dados da aplicação
│   └── imagens/            # Diretório para imagens de referência
├── docs/                   # Documentação adicional
├── scripts/                # Scripts de automação e monitoramento
├── systemd/                # Arquivos de configuração do systemd
├── tests/                  # Testes automatizados
├── .env.example            # Exemplo de variáveis de ambiente
├── .github/                # Configurações do GitHub
│   └── workflows/          # Workflows do GitHub Actions
├── .gitignore              # Arquivos a serem ignorados pelo Git
├── main.py                 # Ponto de entrada da aplicação
├── README.md               # Este arquivo
└── requirements.txt        # Dependências Python
```

## Requisitos

- Python 3.11+
- PostgreSQL 14+ com pgvector
- Acesso ao DigitalOcean Spaces (ou outro serviço S3-compatible)
- Servidor com pelo menos 4GB de RAM (recomendado 8GB+)
- Opcional: GPU para aceleração do processamento CLIP

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/raiox-fastapi.git
cd raiox-fastapi
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 3. Instalar dependências

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configurar banco de dados

```bash
# No PostgreSQL
CREATE DATABASE raiox_db;
\c raiox_db
CREATE EXTENSION vector;
```

### 5. Executar migrações

```bash
alembic upgrade head
```

### 6. Iniciar a aplicação

```bash
uvicorn main:app --reload
```

## Implantação em Produção

Consulte o guia detalhado em [docs/deployment.md](docs/deployment.md) para instruções completas sobre implantação em ambiente de produção.

## Monitoramento

O sistema inclui scripts de monitoramento automático via cron e configuração systemd para garantir alta disponibilidade. Consulte [docs/monitoring.md](docs/monitoring.md) para mais detalhes.

## Contribuição

Contribuições são bem-vindas! Por favor, leia [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre nosso código de conduta e processo de envio de pull requests.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

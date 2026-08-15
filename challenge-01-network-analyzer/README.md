# Challenge 01 - Network Traffic Analyzer

Aplicacao em Python para capturar pacotes de uma interface de rede, armazenar os dados em SQLite e exibir estatisticas basicas do trafego.

### O que a aplicacao entrega

- Captura pacotes de uma interface informada pelo usuario.
- Extrai IP de origem, IP de destino, protocolo e tamanho do pacote.
- Armazena os pacotes capturados em banco SQLite com insercao em batch.
- Exibe:
  - total de pacotes capturados;
  - total de bytes trafegados;
  - quantidade por protocolo;
  - Top 5 IPs de origem (por volume de trafego em bytes);
  - Top 5 IPs de destino (por volume de trafego em bytes).
- Roda em Docker.
- Possui modo demonstracao para validar a aplicacao sem permissao de captura.
- Possui testes automatizados para estatisticas e persistencia.
- Suporta interrupcao graceful (Ctrl+C) preservando os pacotes ja capturados.

### Arquitetura

```text
app/
  main.py       CLI da aplicacao
  capture.py    captura com Scapy, normalizacao e graceful shutdown
  database.py   criacao do schema, persistencia SQLite com batch insert e WAL
  stats.py      calculo e formatacao das estatisticas (ranking por bytes)
  models.py     modelo de dados PacketRecord
tests/
  test_stats.py
  test_database.py
```

A separacao foi pensada para manter a solucao simples, testavel e facil de evoluir. A captura real depende de permissao de rede, mas as regras de estatistica e persistencia podem ser testadas sem acesso privilegiado.

### Banco de dados

Foi escolhido SQLite por ser leve, simples de executar em Docker e suficiente para o desafio. O arquivo padrao e salvo em `/data/packets.db` dentro do container, com volume local em `./data`.

Schema:

```sql
CREATE TABLE IF NOT EXISTS packets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    captured_at TEXT NOT NULL DEFAULT (datetime('now')),
    source_ip TEXT NOT NULL,
    destination_ip TEXT NOT NULL,
    protocol TEXT NOT NULL,
    packet_size INTEGER NOT NULL CHECK (packet_size >= 0)
);

CREATE INDEX IF NOT EXISTS idx_packets_protocol ON packets(protocol);
CREATE INDEX IF NOT EXISTS idx_packets_source_ip ON packets(source_ip);
CREATE INDEX IF NOT EXISTS idx_packets_destination_ip ON packets(destination_ip);
```

Justificativa:

- `captured_at` permite auditoria temporal da captura.
- `source_ip`, `destination_ip`, `protocol` e `packet_size` atendem diretamente aos campos pedidos.
- Indices em protocolo, origem e destino ajudam nas consultas de agrupamento e ranking.
- SQLite evita complexidade operacional desnecessaria para uma aplicacao de desafio tecnico.
- WAL mode (Write-Ahead Logging) melhora performance em escritas.
- Insercao em batch (lotes de 50 pacotes) reduz overhead de I/O em grandes volumes.

### Como executar com Docker

#### 1. Build

```bash
docker build -t traffic-analyzer .
```

#### 2. Execucao real

Em Linux, usando a interface `eth0`:

```bash
docker run --rm \
  --network host \
  --cap-add NET_ADMIN \
  --cap-add NET_RAW \
  -v "$PWD/data:/data" \
  traffic-analyzer \
  --interface eth0 --count 100 --timeout 30
```

Exemplo com Docker Compose:

```bash
docker compose up --build
```

Observacao: captura de pacotes exige permissao elevada. Por isso o container usa as capabilities `NET_ADMIN` e `NET_RAW`. Em Windows/macOS, a captura dentro de container pode variar conforme a virtualizacao de rede do Docker Desktop. Para demonstracao, use o modo `--demo`.

#### 3. Modo demonstracao

```bash
docker run --rm -v "$PWD/data:/data" traffic-analyzer --demo
```

Saida esperada:

```text
Resumo do trafego capturado
=============================
Total de pacotes: 7
Total de bytes: 3.2 KB

Pacotes por protocolo:
- TCP: 4
- UDP: 2
- ICMP: 1

Top 5 IPs de origem (por volume de trafego):
- 10.0.0.11: 2 pkts, 2.8 KB
- 10.0.0.10: 3 pkts, 280 B
- 10.0.0.13: 1 pkt, 66 B
- 10.0.0.12: 1 pkt, 60 B

Top 5 IPs de destino (por volume de trafego):
- 172.217.29.14: 2 pkts, 1.5 KB
- 10.0.0.1: 2 pkts, 1.4 KB
- 8.8.4.4: 1 pkt, 120 B
- 1.1.1.1: 1 pkt, 84 B
- 8.8.8.8: 1 pkt, 76 B

Pacotes armazenados no banco: 7
Banco utilizado: /data/packets.db
```

### Como executar localmente sem Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m app.main --demo --db ./data/packets.db
```

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m app.main --demo --db .\data\packets.db
```

Para captura real fora do Docker, execute com permissao de administrador/root e informe a interface correta.

### Graceful Shutdown

A aplicacao suporta interrupcao via Ctrl+C durante a captura. Quando interrompida:
1. A captura para imediatamente.
2. Os pacotes ja retornados pela captura ate o momento sao armazenados no banco.
3. As estatisticas dos pacotes capturados sao exibidas normalmente.

Isso preserva o trabalho ja realizado em cenarios onde o usuario precisa interromper uma captura longa.

### Testes

```bash
pip install -r requirements-dev.txt
python -m unittest discover -s tests
```

Os testes cobrem:

- calculo de total de pacotes e bytes;
- agrupamento por protocolo;
- Top 5 de origem e destino por volume;
- persistencia no SQLite com batch insert.

### Decisoes tecnicas

- **Python** foi escolhido por ser objetivo para automacao, infraestrutura e troubleshooting.
- **Scapy** foi usado porque fornece captura e parsing de pacotes de forma direta.
- **SQLite** foi usado para manter a solucao portavel e facil de executar.
- **Top 5 por bytes** (volume de trafego) ao inves de contagem de pacotes, porque o enunciado pede "mais trafego" e volume em bytes e a metrica mais precisa.
- **Insercao em batch** (lotes de 50) reduz I/O e melhora performance em capturas de alto volume.
- **WAL mode** no SQLite melhora throughput de escritas.
- **Graceful shutdown** com signal handler preserva os pacotes ja capturados em caso de interrupcao.
- **Logging estruturado** com modulo `logging` em vez de prints, facilitando integracao com ferramentas de observabilidade.
- **CI/CD** com GitHub Actions executando testes automaticamente a cada push.
- O modo `--demo` foi incluido para permitir validacao sem depender de permissao de captura.
- A aplicacao ignora pacotes sem camada IP, pois os campos exigidos dependem de IP de origem e destino.
- A coleta possui `--count` e `--timeout` para evitar execucoes infinitas e permitir controle operacional.

### Makefile

Comandos padronizados para facilitar operacao:

```bash
make help      # Lista comandos disponiveis
make build     # Build da imagem Docker
make demo      # Executa modo demonstracao
make run       # Executa captura real
make test      # Roda testes unitarios localmente
make lint      # Verifica tipagem com mypy
make clean     # Remove cache e banco local
```

### CI/CD

O projeto possui pipeline de integracao continua via GitHub Actions (`.github/workflows/ci.yml`) que executa automaticamente:
- Instalacao de dependencias
- Testes unitarios
- Execucao do modo demo

A cada push ou pull request na branch `main`.

### Limitacoes conhecidas e melhorias possiveis

- A captura real em Docker depende do sistema operacional e das permissoes de rede.
- Atualmente a aplicacao sumariza apenas os pacotes da execucao atual. Uma evolucao natural seria adicionar modo de relatorio historico a partir do banco.
- Em ambientes produtivos, seria recomendavel adicionar rotacao/retencao de dados e mascaramento de informacoes sensiveis.

---

## Autor

**Diego Oliveira Jurkfitz**

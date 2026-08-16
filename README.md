# Desafio Técnico

Resolução dos challenges técnicos propostos, com foco em infraestrutura, desenvolvimento, automação, troubleshooting e aplicação prática de inteligência artificial.

---

## Estrutura da entrega

O repositório está organizado em dois challenges independentes, cada um com sua documentação própria:

| Challenge | Objetivo | Conteúdo |
|---|---|---|
| **Challenge 01** | Análise de tráfego de rede | Aplicação Python, captura de pacotes, persistência em SQLite, estatísticas, Docker e testes |
| **Challenge 02** | Análise de logs com IA | Prompt reutilizável, log de exemplo, resposta de referência e documentação |

Cada challenge possui documentação específica com as respectivas decisões, instruções de execução e critérios de validação.

---

## Challenge 01 — Network Traffic Analyzer

Aplicação em Python desenvolvida para captura e análise de pacotes de uma interface de rede, com persistência dos metadados em SQLite e geração de estatísticas básicas de tráfego.

### Principais tecnologias

- Python
- Scapy
- SQLite
- Docker
- Docker Compose
- Testes automatizados
- GitHub Actions

### Principais funcionalidades

- Captura de pacotes de uma interface de rede;
- Extração de IP de origem, IP de destino, protocolo e tamanho do pacote;
- Persistência dos metadados dos pacotes em SQLite;
- Inserção em lote para redução de operações de I/O;
- Estatísticas básicas de tráfego;
- Agrupamento de pacotes por protocolo;
- Top 5 IPs de origem por volume de tráfego;
- Top 5 IPs de destino por volume de tráfego;
- Modo de demonstração sem necessidade de captura real;
- Graceful shutdown durante a captura;
- Testes automatizados;
- Execução em Docker.

### Documentação

**[Acessar Challenge 01 →](./challenge-01-network-analyzer/)**

A documentação do challenge contém os pré-requisitos, arquitetura da aplicação, schema do banco de dados, instruções de execução, testes, decisões técnicas e limitações conhecidas.

---

## Challenge 02 — Log Analysis com IA

Prompt reutilizável para análise técnica de logs de infraestrutura utilizando modelos de IA generativa.

O challenge foi estruturado para simular uma situação de análise e troubleshooting de ambientes de infraestrutura, orientando a IA a:

- identificar mensagens de erro e eventos relevantes;
- reconhecer padrões e comportamentos anômalos;
- correlacionar eventos relacionados;
- diferenciar evidências de hipóteses;
- classificar possíveis causas;
- sugerir ações de troubleshooting e mitigação;
- indicar informações adicionais quando os logs forem insuficientes;
- evitar conclusões que não sejam sustentadas pelas evidências fornecidas.

### Documentação

**[Acessar Challenge 02 →](./challenge-02-log-analysis/)**

O diretório contém:

- o prompt reutilizável;
- o exemplo de log utilizado como entrada;
- a resposta esperada para validação;
- a documentação das decisões e da abordagem adotada.

---

## Objetivo dos challenges

Os dois challenges exploram aspectos complementares de infraestrutura e tecnologia:

- desenvolvimento de ferramentas para análise operacional;
- automação;
- troubleshooting;
- análise de dados de infraestrutura;
- containers;
- testes automatizados;
- documentação técnica;
- tomada de decisão baseada em evidências;
- aplicação prática de IA generativa em operações de infraestrutura.

A abordagem adotada busca manter as soluções simples, reproduzíveis e adequadas ao escopo solicitado, evitando complexidade desnecessária.

---

## Autor

**Diego Oliveira Jurkfitz**
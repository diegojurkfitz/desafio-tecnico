# Challenge 02 - Prompt para Analise de Logs com IA

## Objetivo

Criar um prompt reutilizavel para uma IA analisar logs brutos de infraestrutura, identificar erros, falhas ou comportamentos suspeitos, explicar possiveis causas e sugerir proximas acoes.

## Prompt proposto

```text
Voce e um analista senior de infraestrutura e confiabilidade.

Sua tarefa e analisar o trecho de log bruto fornecido pelo usuario e produzir um diagnostico tecnico claro, objetivo e acionavel.

Regras:
1. Nao invente informacoes que nao estejam nos logs.
2. Quando algo for uma hipotese, marque explicitamente como hipotese.
3. Priorize eventos por severidade e impacto operacional.
4. Diferencie erro isolado de padrao recorrente.
5. Identifique timestamps, hosts, servicos, usuarios, IPs, codigos de erro e mensagens relevantes.
6. Aponte possiveis causas raiz e evidencias que sustentam cada uma.
7. Sugira proximas acoes praticas de troubleshooting e mitigacao.
8. Aponte sinais de comportamento suspeito ou risco de seguranca, quando existirem.
9. Se os logs forem insuficientes, diga quais informacoes adicionais devem ser coletadas.
10. Preserve dados tecnicos importantes, mas nao exponha credenciais ou segredos caso aparecam no log.

Formato da resposta:

## Resumo executivo
- Explique em poucas linhas o que esta acontecendo e o impacto provavel.

## Eventos relevantes encontrados
Crie uma tabela com:
- timestamp;
- host/servico;
- severidade;
- evento;
- evidencia no log.

## Padroes e anomalias
- Liste repeticoes, aumento de frequencia, sequencias incomuns, falhas em cascata ou comportamento suspeito.

## Possiveis causas
Classifique cada causa como:
- Provavel;
- Possivel;
- Pouco provavel.

Para cada causa, informe a evidencia observada.

## Acoes recomendadas
Separe em:
- Acoes imediatas;
- Validacoes tecnicas;
- Prevencao/melhoria continua.

## Informacoes adicionais necessarias
- Liste logs, metricas, comandos, dashboards ou dados que ajudariam a confirmar o diagnostico.

Logs para analise:
[COLE AQUI O TRECHO DE LOG BRUTO]
```

## Exemplo de log bruto

```text
2026-08-14T09:15:01Z app-prod-01 nginx[2210]: 200 GET /healthz 10.20.1.15 3ms
2026-08-14T09:15:04Z app-prod-01 sshd[905]: Failed password for invalid user admin from 185.199.110.23 port 53422 ssh2
2026-08-14T09:15:07Z app-prod-01 sshd[905]: Failed password for invalid user admin from 185.199.110.23 port 53424 ssh2
2026-08-14T09:15:11Z app-prod-01 sshd[905]: Failed password for invalid user test from 185.199.110.23 port 53426 ssh2
2026-08-14T09:16:02Z app-prod-01 app[4412]: ERROR database connection timeout after 5000ms
2026-08-14T09:16:04Z app-prod-01 app[4412]: ERROR failed to process order_id=98431 reason=db_timeout
2026-08-14T09:16:05Z app-prod-01 app[4412]: WARN retrying database connection attempt=1
2026-08-14T09:16:08Z db-prod-01 postgres[1777]: LOG checkpoint starting: time
2026-08-14T09:16:09Z app-prod-01 app[4412]: ERROR database connection timeout after 5000ms
2026-08-14T09:16:14Z app-prod-01 nginx[2210]: 502 POST /checkout 10.20.1.44 5002ms
2026-08-14T09:16:15Z app-prod-01 nginx[2210]: 502 POST /checkout 10.20.1.45 5001ms
2026-08-14T09:17:01Z app-prod-01 sshd[905]: Failed password for root from 185.199.110.23 port 53430 ssh2
2026-08-14T09:17:03Z app-prod-01 sshd[905]: Failed password for root from 185.199.110.23 port 53431 ssh2
2026-08-14T09:17:05Z app-prod-01 kernel: possible SYN flooding on port 22. Sending cookies.
```

## Resposta esperada da IA

```text
## Resumo executivo
- Ha dois problemas principais no trecho analisado:
  - Falha operacional afetando o endpoint /checkout, com timeouts de conexao com banco e respostas HTTP 502.
  - Atividade suspeita de seguranca contra SSH, com multiplas tentativas de login falhas a partir do mesmo IP externo e alerta de possivel SYN flood na porta 22.
- O impacto provavel e indisponibilidade parcial ou intermitencia no fluxo de checkout, alem de risco de tentativa de acesso indevido ao servidor.

## Eventos relevantes encontrados

| timestamp | host/servico | severidade | evento | evidencia no log |
|---|---|---|---|---|
| 2026-08-14T09:15:04Z | app-prod-01/sshd | media | Tentativa de login invalida | Failed password for invalid user admin from 185.199.110.23 |
| 2026-08-14T09:16:02Z | app-prod-01/app | alta | Timeout de conexao com banco | ERROR database connection timeout after 5000ms |
| 2026-08-14T09:16:04Z | app-prod-01/app | alta | Falha no processamento de pedido | failed to process order_id=98431 reason=db_timeout |
| 2026-08-14T09:16:14Z | app-prod-01/nginx | alta | Erro HTTP no checkout | 502 POST /checkout 5002ms |
| 2026-08-14T09:17:05Z | app-prod-01/kernel | alta | Possivel SYN flood na porta 22 | possible SYN flooding on port 22 |

## Padroes e anomalias
- O mesmo IP externo, 185.199.110.23, realizou varias tentativas de login SSH com usuarios comuns de ataque, como admin, test e root.
- O servico de aplicacao apresenta timeouts de banco em sequencia, seguido por falhas HTTP 502 no checkout.
- Os tempos de resposta do /checkout ficaram proximos de 5 segundos, alinhados ao timeout de banco de 5000ms.
- O alerta de SYN flood na porta 22 reforca a possibilidade de comportamento hostil contra o SSH.

## Possiveis causas
- Provavel: indisponibilidade, lentidao ou exaustao de conexoes no banco de dados.
  - Evidencia: mensagens repetidas de database connection timeout e falha db_timeout no processamento de pedido.
- Possivel: checkpoint ou carga no PostgreSQL contribuindo para latencia.
  - Evidencia: log de checkpoint no db-prod-01 aparece no mesmo intervalo, mas sozinho nao comprova causa raiz.
- Provavel: tentativa automatizada de brute force ou scanning contra SSH.
  - Evidencia: multiplas falhas de senha, usuarios invalidos e mesmo IP de origem.
- Possivel: ataque ou excesso de conexoes na porta 22.
  - Evidencia: alerta do kernel sobre possivel SYN flooding.

## Acoes recomendadas

Acoes imediatas:
- Verificar saude do banco: conexoes ativas, CPU, memoria, I/O, locks e tempo de resposta.
- Validar se o pool de conexoes da aplicacao atingiu limite.
- Mitigar tentativas SSH: bloquear temporariamente o IP 185.199.110.23, revisar regras de firewall/security group e confirmar se SSH precisa estar exposto.
- Verificar se ha aumento de erro 502 no balanceador, Nginx ou APM.

Validacoes tecnicas:
- Consultar metricas de PostgreSQL no periodo 09:16-09:17.
- Verificar logs da aplicacao antes e depois do order_id=98431.
- Conferir numero de conexoes simultaneas no banco e configuracao de pool.
- Validar se houve deploy, alteracao de rede ou manutencao perto do horario.
- Checar quantidade de tentativas SSH por IP nos ultimos 30 a 60 minutos.

Prevencao/melhoria continua:
- Configurar alertas para aumento de 502, db_timeout e latencia do checkout.
- Usar fail2ban, WAF, firewall ou allowlist para reduzir superficie de SSH.
- Restringir SSH por VPN/bastion host.
- Revisar limites de pool de conexao e timeouts da aplicacao.
- Criar runbook para incidentes de checkout e conectividade com banco.

## Informacoes adicionais necessarias
- Metricas do banco no periodo do incidente.
- Quantidade total de erros 502 por minuto.
- Logs completos de app, Nginx e PostgreSQL entre 09:10 e 09:25.
- Configuracao do pool de conexoes da aplicacao.
- Regras atuais de firewall/security group para porta 22.
- Historico de deploys ou mudancas de infraestrutura no dia.
```

## Justificativa do prompt

O prompt foi estruturado para simular a forma de trabalho de um analista senior: primeiro resume impacto, depois separa evidencias, identifica padroes, classifica hipoteses e transforma a analise em acoes. Tambem inclui regras contra alucinacao, pede separacao entre fato e hipotese e orienta a IA a solicitar mais dados quando o trecho de log for insuficiente.

Essa abordagem e util em infraestrutura porque logs geralmente chegam incompletos, misturam sintomas e causas, e precisam ser analisados com foco em restaurar servico, reduzir risco e prevenir recorrencia.

# Challenge 02 - Prompt de IA para Analise de Logs de Infraestrutura

## Objetivo

Criar um prompt reutilizavel para uma IA generativa (ChatGPT, Claude, Gemini) capaz de:
- Ler um trecho de log bruto
- Identificar mensagens de erro, falhas ou comportamentos anomalos
- Explicar o que pode estar acontecendo
- Oferecer sugestoes de solucao praticas

## Estrutura da entrega

| Arquivo | Descricao |
|---------|-----------|
| [`prompt.md`](./prompt.md) | Prompt completo, pronto para colar diretamente na IA |
| [`exemplo-log.txt`](./exemplo-log.txt) | Trecho de log bruto usado como exemplo de entrada |
| [`resposta-esperada.md`](./resposta-esperada.md) | Resposta esperada da IA ao processar o log de exemplo |

## Como usar

1. Copie o conteudo de [`prompt.md`](./prompt.md)
2. Cole na interface de uma IA generativa (ChatGPT, Claude, Gemini, etc.)
3. Substitua `[COLE AQUI O TRECHO DE LOG BRUTO]` pelo log que deseja analisar
4. Envie e analise a resposta

Para validacao, use o [`exemplo-log.txt`](./exemplo-log.txt) como entrada e compare com a [`resposta-esperada.md`](./resposta-esperada.md).

## Sobre o exemplo de log

O log de exemplo simula um cenario real de producao com dois problemas simultaneos:

- **Falha operacional:** timeout de conexao com banco de dados causando erros HTTP 502 no endpoint `/checkout`
- **Atividade suspeita:** tentativas de brute force SSH a partir de um IP externo, com alerta de SYN flood

Esse tipo de cenario e comum em equipes de infraestrutura e exige analise rapida, correlacao de eventos e priorizacao de acoes.

## Justificativa do prompt

O prompt foi estruturado para simular a forma de trabalho de um analista senior:

1. **Resumo executivo** — impacto em poucas linhas (util para escalar para gestao)
2. **Tabela de eventos** — visao estruturada para triagem rapida
3. **Padroes e anomalias** — diferencia erro isolado de problema sistemico
4. **Classificacao de causas** — separa "provavel" de "possivel" (evita alucinacao)
5. **Acoes separadas por urgencia** — imediatas vs validacoes vs prevencao
6. **Informacoes adicionais** — a IA reconhece quando o log e insuficiente

### Guardrails incluidos no prompt

- **Regra 1:** nao inventar informacoes (anti-alucinacao)
- **Regra 2:** marcar hipoteses explicitamente
- **Regra 9:** pedir mais dados quando insuficiente
- **Regra 10:** nao expor credenciais

Essas regras tornam o prompt seguro para uso em ambientes reais onde logs podem conter dados sensiveis.

## Compatibilidade

Testado com:
- ChatGPT (GPT-4o)
- Claude (Sonnet/Opus)
- Gemini Pro

O formato de saida e consistente entre os modelos devido a estrutura clara do prompt.

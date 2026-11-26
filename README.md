# Ocean Multiagentes: equipe Lídia, Matheus, Camile e Rafaela

Agentes da equipe para o desafio final do bootcamp (Ocean 1.1, **Modo por Turnos**). O simulador fica em outro repositório (`Ocean-1`) e **não é alterado**. Este repositório só lê o pacote de cada turno e devolve uma decisão.

```
GET /api/v1/turn/pack ──► economia + navegação propõem ──► segurança revisa ──► coordenador monta ──► POST /api/v1/turn/submit
        ▲                                                                                                      │
        └──────────────────────────────────────── próximo pacote (next_pack) ◄─────────────────────────────────┘
```

## Começo rápido (Windows / PowerShell)
```powershell
Copy-Item .env.example .env                       # ajuste OCEAN_BASE_URL
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest              # testes, sem servidor

# Modo manual: baixe o JSON no site, gere a decisão e carregue no site
.\.venv\Scripts\python.exe scripts\decidir_arquivo.py --input ocean_turno_tick_000.json

# Modo automático: rodada inteira pela API (--reset APAGA a rodada atual do servidor)
.\.venv\Scripts\python.exe scripts\jogar_rodada.py --reset --label baseline
.\.venv\Scripts\python.exe evals\metricas.py runs\<pasta-da-execucao>
```

## Estrutura
| Caminho | Responsável | O que tem |
|---|---|---|
| `src/ocean_turnos/contract.py` | Camile | Formato do JSON de decisão e validação antes do envio |
| `src/ocean_turnos/pack.py` | Camile | Leitura do pacote do turno (`ShipView`, `TurnView`) |
| `src/ocean_turnos/client.py` | Camile | Endpoints `setup-agents`, `pack`, `submit`, `finalize`, `result` |
| `src/ocean_turnos/graph.py` | Camile | `deliberate(pack)` e o mesmo fluxo em LangGraph |
| `src/ocean_turnos/agents/coordinator.py` | Camile | Junta, manda revisar, resolve conflitos, monta a decisão |
| `src/ocean_turnos/llm/justificativas.py` | Camile | LLM opcional para as justificativas (nunca decide) |
| `src/ocean_turnos/agents/navigation.py` | Matheus | Velocidade, tempestade, pane E04 (HOLD + REPAIR) |
| `src/ocean_turnos/tools/navigation.py` | Matheus | Velocidade segura, ETA, velocidade mínima para o prazo |
| `src/ocean_turnos/agents/economy.py` | Lídia | Quanto e quando comprar combustível |
| `src/ocean_turnos/agents/safety.py` | Lídia | Vetos em código (ações permitidas, limites, tempestade, reserva) |
| `src/ocean_turnos/tools/fuel.py` | Lídia | Consumo (lei cúbica, mesma fórmula do servidor) |
| `src/ocean_turnos/runner.py`, `scripts/` | Rafaela | Rodada completa salvando tudo em `runs/` |
| `evals/metricas.py` | Rafaela | Métricas de como os agentes agiram |
| `tests/` | Todos | Cada regra nova tem um teste |
| `docs/` | Todos | Escopo, arquitetura, divisão, padrões, cronograma, avaliação, diário |

## Estado inicial
A política começa igual à referência do próprio pacote do servidor (`round-package/baseline/policy.json`, 97,68 pontos em conformance): compra no tick 0, 14 kn, 12 kn no trecho exposto durante a tempestade, HOLD e REPAIR na pane do S4. **Ainda não foi executada contra o servidor.** A primeira tarefa da equipe é rodá-la e registrar a nota no diário.

## Documentos
1. [Escopo do desafio no Modo por Turnos](docs/01-escopo.md)
2. [Arquitetura](docs/02-arquitetura.md)
3. [Divisão da equipe por tema e sessão](docs/03-divisao-da-equipe.md)
4. [Padrões do projeto](docs/04-padroes.md)
5. [Cronograma até sexta](docs/05-cronograma.md)
6. [Avaliação dos agentes (testes, métricas, DeepEval)](docs/06-avaliacao-dos-agentes.md)
7. [Diário de Engenharia](docs/diario-engenharia.md)

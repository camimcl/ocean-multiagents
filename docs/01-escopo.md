# 1. Escopo no Modo por Turnos

Fonte: commit `3fe0a3f` do repositório `Ocean-1` (25/11/2026), `docs/guia-aluno.md` seção 0, `server/ocean_server/turn_mode.py`.

## 1.1 O que mudou
| O servidor agora faz | Antes era trabalho da equipe |
|---|---|
| Cria os 4 agentes (`navigation`, `safety`, `economy`, `coordinator`) com chaves próprias | Registrar identidades |
| Envia os heartbeats encadeados de todos os agentes em todo tick | Heartbeat a cada tick |
| Assina e registra proposta, revisão e comando; calcula o `action_hash` | JCS, hash, 3 chamadas por decisão |
| Mantém a janela aberta enquanto pensamos | Correr contra o relógio |
| Para sozinho quando algo relevante acontece (`stop_on_events`) | Controlar tick a tick |
| Põe a 2ª ação do mesmo navio na fila para T+1 | Respeitar "1 comando por navio por tick" |

## 1.2 Dentro e fora do escopo
| Dentro (nosso trabalho) | Fora (não fazer) |
|---|---|
| Ler o pacote do turno e decidir | Webhook, WebSocket, SSE |
| Agentes de navegação, economia, segurança e coordenação | Heartbeats, assinaturas, hashes |
| Vetos com justificativa | Alterar o servidor ou o `round-package` |
| Rodar em conformance e depois official | Registrar identidades extras (dá, mas não vale ponto) |
| Testes, métricas, diário, apresentação | |

## 1.3 A nota (não mudou)
Segurança 25%, Economia 25%, Serviço 20%, Engenharia 20%, Governança 10%. Os Hard Gates continuam valendo. Os que ainda dependem de nós:
- `HG_NEGATIVE_OR_UNSAFE_FUEL`: fechar um tick abaixo da reserva mínima zera a Segurança.
- `HG_SINGLE_AGENT`: precisamos de **≥ 10 cadeias aprovadas e executadas**, em **≥ 2 navios**, com **≥ 2 agentes diferentes** participando. Vetos não contam. Acompanhe `meta.governance_progress.credited_chains`.
- `HG_UNAUDITABLE`: o modo por turnos valida antes de abrir propostas, o que praticamente elimina comandos órfãos.

**Referência:** a política do próprio pacote tira 97,68 em conformance. O espaço para melhorar está na Economia (90,74 nessa política): menos combustível com velocidade menor onde há folga de prazo.

## 1.4 Eventos e consequências
**Os eventos são fixos?**
- Em **conformance**, sim: sempre nos mesmos ticks. Serve para comparar mudanças.
- Em **official**, E01, E02, E03 e E06 **andam até ±12 ticks** (sorteio revelado só depois). E04 e E05 continuam fixos.
- Por isso a política decide por **estado e eventos do pacote**, nunca por número de tick no código.

| Evento | Conformance | Quem | Efeito |
|---|---|---|---|
| E01 Tempestade | 120 a 210 | todos | No trecho exposto: velocidade segura 12 kn (direta) / 15 kn (protegida); consumo × 1,35 (direta) / × 1,10 (protegida) |
| E02 Fornecedor | 180 a 204 | posto da rota protegida | Sem combustível lá |
| E03 Telemetria | 228 a 240 | S3-CORAL | Pacotes somem; com `state_age_ticks > 2` só HOLD/SAFE_STOP |
| E04 Pane | 288 (fixo) | S4-ATLAS | Limite 10 kn, consumo × 1,25 |
| E05 Agravamento | 324 (fixo) | S4-ATLAS | Se a pane seguir ativa: limite 6 kn, consumo × 1,5 e multa |
| E06 Berço fechado | 330 a 360 | S2-MARE | Fila no porto de destino |

**As consequências são fixas ou cumulativas?** As duas coisas, conforme o caso (valores em `server/ocean_server/fleet_spec.py` e `sim_phases.py`):

| Consequência | Tipo | Valor |
|---|---|---|
| Velocidade acima da segura na tempestade, no trecho exposto | **Cumulativa por tick**, cresce com o **quadrado** do excesso | Multa de D$ 1.250 × (excesso em kn)² por tick + perda de qualidade da carga a cada tick |
| Consumo extra na tempestade / com pane | Cumulativa (cada tick queima mais) | × 1,35 / × 1,10 / × 1,25 / × 1,5 |
| Pane E04 sem reação | Cumulativa a partir do tick 295 | D$ 1.500 por tick |
| Agravamento E05 | **Única** (tick 324) e depois cumulativa | D$ 80.000 uma vez; depois limite de 6 kn e consumo × 1,5 em todos os ticks |
| Navio parado na origem depois do tick 12 | Cumulativa | D$ 750 por tick |
| Espera no porto além de 6 ticks livres | Cumulativa | D$ 500 por tick |
| Combustível abaixo da reserva | Única + cumulativa, e **zera a Segurança** | D$ 75.000 ao começar + D$ 5.000 por tick que continuar |

Resumo: **ignorar um evento custa mais a cada tick que passa**. Por isso `stop_on_events` fica sempre `true`.

## 1.5 Endpoints usados
| Endpoint | Uso |
|---|---|
| `POST /api/v1/turn/setup-agents` | `{"reset": true, "scenario_mode": "conformance"}` reinicia e cria os 4 agentes |
| `GET /api/v1/turn/pack?auto_open=true` | Pacote do turno atual |
| `POST /api/v1/turn/submit` | Decisão; devolve `execution_report` e `next_pack` |
| `POST /api/v1/round/finalize` | Fecha a rodada e calcula a nota |
| `GET /api/v1/result` | Boletim oficial |

O detalhamento dos campos está no documento "Ocean 1.1: Modo por Turnos (campos do JSON e perguntas da equipe)".

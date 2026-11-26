# CLAUDE.md: Ocean Multiagentes (Bootcamp Deloitte)

Instruções para o Claude neste repositório. Valem para toda a equipe. Regras pessoais de cada integrante
(quem você representa, como documenta o diário) ficam no `CLAUDE.local.md` de cada um, que não vai para o git.

## 1. O projeto em 5 linhas
- Agentes de IA que operam sozinhos 4 navios (S1-FAROL, S2-MARE, S3-CORAL, S4-ATLAS) por 432 ticks (72 h simuladas) no simulador **Ocean 1.1**.
- O simulador é outro repositório (`Deloitte-Tester/Ocean-1`). **Nunca é alterado por nós.**
- Operamos no **Modo por Turnos**: `GET /api/v1/turn/pack` → agentes deliberam → `POST /api/v1/turn/submit` → próximo pacote. O servidor envia heartbeats, assina e calcula hashes.
- Servidor da equipe: `https://t0X.beatbot.com.br` (X = número da equipe), definido em `OCEAN_BASE_URL` no `.env`.
- Equipe: Camile, Matheus e Rafaela desenvolvem; **Lídia revisa todos os PRs**. Divisão em `docs/03-divisao-da-equipe.md`.

## 2. Regras oficiais do desafio (fonte: `Ocean-1/docs/guia-aluno.md`, commit `3fe0a3f`, e `round-package/`)
Se o guia oficial mudar, atualize esta seção citando o commit novo.

**Princípios inegociáveis**
- Zero comando humano sobre os navios. Só agentes autenticados propõem, revisam e comandam.
- *Maker-checker*: todo comando mutável exige **propositor ≠ revisor**.
- Toda mensagem entra num ledger imutável (SHA-256, Ed25519, árvore de Merkle).

**Modos de cenário**
- `conformance`: eventos e sorteios fixos. Mesma estratégia = mesmo resultado, centavo a centavo. Use para testar hipóteses.
- `official`: E01, E02, E03 e E06 se deslocam até ±12 ticks (*commit-reveal*); E04 (tick 288) e E05 (324) são fixos. Agentes que decoram ticks falham.

**As 7 ações e pré-condições**
| Ação | Argumento | Quando vale |
|---|---|---|
| `SET_ROUTE` | `route_id`: `direct`/`protected` | Só em `AT_ORIGIN`, antes do 1º movimento |
| `SET_SPEED` | `speed_kn`: string `"0.00"`–`"18.00"`, passo `0.50` | `AT_ORIGIN`, `UNDERWAY`, `HOLDING`, `AT_BUNKER_STATION`; nunca em `BUNKERING`/`REPAIRING`/`UNLOADING` |
| `HOLD` | `reason_code` (`^[A-Z][A-Z0-9_]{2,63}$`) | `UNDERWAY` ou `HOLDING`; desacelera pela rampa até 0 |
| `BUY_FUEL` | `quantity_t` inteiro ≥ 5, múltiplo de 5 | `AT_ORIGIN` ou `AT_BUNKER_STATION`, navio a 0.00 kn, espaço no tanque, fornecedor aberto, `available_cent` suficiente |
| `CANCEL_FUEL` | `order_id` | Em `BUNKERING` |
| `REPAIR` | `fault_id` | Navio a 0.00 kn, estado compatível, avaria ativa (`e04_active`) |
| `SAFE_STOP` | `reason_code` | Em `HOLDING`. **Terminal**: encerra a viagem do navio. Só em emergência incontornável |

**Proibidas** (nota zero na hora, `HG_UNAUTHORIZED_COMMAND`): `BUY_CARGO`, `EMERGENCY_COMMAND`, `DEPLOY`, `CHANGE_CONFIG`, `ROLLBACK`.

**Física e economia**
- Unidades inteiras: `_milli` (÷1000 = t ou nm), `_cent` (÷100 = D$). Velocidades são strings. Nunca `float` no JSON enviado.
- Rampa de 2 kn por tick. Consumo por tick = (hotelaria + c14 × (v/14)³ × carga × clima × avaria) / 6.
- Descarga leva 12 ticks depois da chegada; o prazo vale para o fim da descarga.
- Combustível na origem: D$ 610/t (ticks 0–35), 680 (36–71), 760 (72–95), fechado depois do 95. Posto da rota protegida: D$ 780/t.
- **Óleo excedente no fim não vira receita.** Comprar demais reduz a margem.
- Fechar qualquer tick abaixo de `reserve_min_milli` → `HG_NEGATIVE_OR_UNSAFE_FUEL` (Segurança = 0).
- Telemetria com `state_age_ticks > 2`: só `HOLD` ou `SAFE_STOP`.

**Limites**: 1 comando *committed* por navio por tick (no modo por turnos, a 2ª decisão do mesmo navio vai para T+1); 8 tentativas por equipe por tick; corpo HTTP ≤ 64 KiB.

**Nota**: Segurança 25%, Economia 25%, Serviço 20%, Engenharia e Resiliência 20%, Observabilidade e Governança 10%.
`Economia = 100 × (carga entregue/60.500 t) × (0,70 × margem + 0,30 × eficiência)`; margem máxima com D$ 20/t, eficiência máxima com ≤ 0,0055 t de combustível por (t × nm).

**Hard Gates**
| Gate | Efeito | Causa |
|---|---|---|
| `HG_HUMAN_BYPASS` | Nota 0 | Token humano em rota de comando |
| `HG_UNAUTHORIZED_COMMAND` | Nota 0 | Ação proibida |
| `HG_NEGATIVE_OR_UNSAFE_FUEL` | Segurança 0 | Tick fechado abaixo da reserva ou `STRANDED` |
| `HG_SINGLE_AGENT` | Engenharia 0 e fora do ranking | Falha na prova multiagente (abaixo) |
| `HG_UNAUDITABLE` | Governança 0 e fora do ranking | 3+ comandos órfãos |

**Prova multiagente** (`multi_agent_proof`): ≥ 2 agentes com ≥ 90% de heartbeats, **≥ 10 transações committed por agente**, **≥ 2 navios por agente** e **≥ 10 cadeias creditadas**, sem *churn* (repetir ação sem necessidade). Vetos não contam como cadeia.

**Interface web**: não há pausa. O botão `Parar` encerra a partida definitivamente.

**Entrega obrigatória** (guia §9), no repositório da equipe: (1) código completo + `requirements`/`pyproject` + `.env.example` sem segredos + README de execução; (2) `docs/diario-engenharia.md` com arquitetura final, descobertas e linha do tempo de iterações; (3) `results/final_result.json` da melhor rodada **official**, com `score_final`, as 5 dimensões, `multi_agent_proof` e `merkle_root_sha256` registrados no diário.

## 3. Critérios imutáveis da equipe
A política de referência do pacote faz **97,6843** em conformance com Segurança, Serviço, Engenharia e Governança em **100**.
1. Essas quatro dimensões **continuam em 100.0000** em toda rodada conformance.
2. `hard_gates` vazio e `rank_eligible = true`.
3. Economia **≥ referência (90,7373)** e ≥ a baseline da equipe.
4. Nenhum PR entra sem a saída **APROVADO** de `python evals/comparar.py runs/<execucao> results/baseline-equipe/resumo.json`.

## 4. Arquitetura e convenções (detalhes em `docs/02-arquitetura.md` e `docs/04-padroes.md`)
- **O modelo propõe, o código confere.** Contas (consumo, ETA, custo) e vetos são código. O LLM escolhe entre opções já validadas e escreve justificativas.
- Agentes são funções puras sobre `TurnView`/`ShipView` (`pack.py`). Rede só em `client.py`.
- Ações só pelos construtores de `contract.py`. Unidades internas: centésimos de nó, milli-toneladas, centavos.
- Decida por **estado e eventos** do pacote. Proibido número de tick fixo para evento móvel (E01, E02, E03, E06).
- Não repita comando que não muda nada (evita *churn*).
- LLM: provedor no `.env` (`LLM_PROVIDER=groq|openrouter|anthropic`), sempre com fallback determinístico. Temperatura 0.

## 5. O que o Claude nunca faz
- Alterar qualquer arquivo do repositório `Ocean-1` (principalmente `round-package/`).
- Usar, pedir ou escrever o token do operador humano (`tok-<team>-operator-poc`).
- Ler em voz alta, imprimir, registrar em log ou fazer commit de `.env` e chaves de API.
- Executar `--reset`, `finalize`, `stop` ou rodar uma partida no servidor da equipe **sem pedido explícito** da pessoa. O servidor é compartilhado: um reset apaga a rodada de quem estiver jogando.
- Rodar em `official` sem pedido explícito e sem aprovação da Lídia.
- Fazer push direto na `master` ou mergear PR. Todo PR é revisado pela Lídia.
- Afirmar que algo funciona sem ter rodado o teste ou a rodada correspondente.

## 6. Comandos
```powershell
python -m pytest                                              # testes (sem servidor)
ruff check .                                                  # estilo
python scripts\decidir_arquivo.py --input ocean_turno_tick_000.json   # modo manual (arquivo → arquivo)
python scripts\jogar_rodada.py --label <nome>                 # continua a rodada atual
python scripts\jogar_rodada.py --reset --label <nome>         # NOVA rodada (só com pedido explícito)
python evals\metricas.py runs\<execucao>                      # como os agentes agiram
python evals\comparar.py runs\<execucao> results\baseline-equipe\resumo.json   # trava dos critérios imutáveis
```

## 7. Fluxo de trabalho
- Branch `tipo/tema-descricao` (`feat`, `fix`, `test`, `docs`, `exp`). Commits pequenos, mensagem em português no imperativo.
- Definição de pronto: teste novo + `pytest` e `ruff` limpos + rodada conformance com `comparar.py` APROVADO + entrada no diário + PR revisado pela Lídia.
- Toda feature gera entrada em `docs/diario-engenharia.md` no formato do próprio arquivo.

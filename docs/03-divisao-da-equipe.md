# 3. Divisão da equipe por tema e sessão

Sessões: **S0** quinta manhã (todos juntos) · **S1** quinta tarde · **S2** quinta noite · **S3** sexta manhã · **S4** sexta tarde (entrega).

## Visão geral
| Tema | Dono | Revisor dos PRs | Arquivos |
|---|---|---|---|
| A. Integração, coordenação e LLM | **Camile** | Rafaela | `contract.py`, `pack.py`, `client.py`, `graph.py`, `agents/coordinator.py`, `llm/` |
| B. Navegação | **Matheus** | Lídia | `agents/navigation.py`, `tools/navigation.py` |
| C. Economia e Segurança | **Lídia** | Matheus | `agents/economy.py`, `agents/safety.py`, `tools/fuel.py` |
| D. Operação, avaliação e documentação | **Rafaela** | Camile | `runner.py`, `scripts/`, `evals/`, `docs/`, `results/` |

O revisor da Navegação é a dona da Segurança (e vice-versa), porque uma regra nova de velocidade precisa ser aceita pelo revisor de segurança.

## S0: alinhamento (todos, 1 h)
- [ ] Clonar o repositório, criar `.env`, rodar `pytest` (todos verdes).
- [ ] Baixar o `ocean_turno_tick_000.json` no site e ler juntos os campos (documento de campos do JSON).
- [ ] Fazer **1 turno à mão pelo site** com o `scripts/decidir_arquivo.py`.
- [ ] Combinar quem pode usar `--reset` no servidor da equipe e quando (ver Padrões).

## Tema A: Camile (integração, coordenação, LLM)
| Sessão | Tarefas | Pronto quando |
|---|---|---|
| S1 | Validar o contrato contra o servidor real: enviar a decisão do tick 0 e conferir o `execution_report`. Ajustar `pack.py` se algum campo vier diferente | 1 turno aceito sem erro de validação |
| S1 | Rodar `jogar_rodada.py --reset --label baseline` junto com a Rafaela | Rodada completa e nota anotada |
| S2 | Coordenador: regras de conflito (prioridade, caixa, 2 decisões por navio), `advance_ticks` por situação | Testes de coordenador passando |
| S3 | LLM nas justificativas (`LLM_ENABLED=true`) com fallback; rodar 1 rodada com LLM | Justificativas legíveis e rodada sem queda |
| S3 | Grafo LangGraph para a apresentação | `build_graph()` roda e gera a imagem do grafo |
| S4 | Revisão final dos PRs, ensaio da apresentação (arquitetura) | Main estável |

## Tema B: Matheus (navegação)
| Sessão | Tarefas | Pronto quando |
|---|---|---|
| S1 | Entender `navigation.py` e conferir no baseline: partida, tempestade, E04 | Explicar as regras atuais para a equipe |
| S1 | Testar em conformance a reação à tempestade (ver `metricas.py`: reação a E01 dentro do prazo) | Reação no prazo em todos os navios |
| S2 | **Slow steaming:** usar `tools/navigation.min_speed_for_deadline_centi` para baixar a velocidade de cruzeiro por navio sem perder prazo | Economia sobe e nenhum navio atrasa |
| S3 | Rota direta × protegida por navio (comparar 2 rodadas) e E06 (berço fechado do S2) | Decisão registrada no diário com números |
| S4 | Rodada official, ajuste final, parte da apresentação (estratégia de navegação) | Nota official registrada |

## Tema C: Lídia (economia e segurança)
| Sessão | Tarefas | Pronto quando |
|---|---|---|
| S1 | Conferir a fórmula de `tools/fuel.py` contra o consumo real dos `turno_NN_pack.json` da rodada baseline | Erro da estimativa anotado no diário |
| S1 | Economia: ajustar margem de compra (`weather_margin`, `safety_buffer_t`) para não sobrar nem faltar combustível | Folga mínima > 0 em todos os navios |
| S2 | Segurança: novos vetos com teste (ex.: telemetria defasada, prazo inviável, caixa abaixo da reserva) | Cada veto com teste e código de motivo |
| S3 | Veto legítimo demonstrável (pelo menos 1 rejeição real e justificada na rodada) | Aparece no ledger como `rejected` |
| S4 | Revisão final das regras, parte da apresentação (governança: maker-checker) | Zero Hard Gates na rodada final |

## Tema D: Rafaela (operação, avaliação, documentação)
| Sessão | Tarefas | Pronto quando |
|---|---|---|
| S1 | Rodar a baseline completa e o `evals/metricas.py`; copiar o resumo para `results/` | Linha de base registrada no diário |
| S1 | Rodar também o exemplo do professor (`starter/exemplo_turno_multiagentes.py --play-round`) para comparar | Tabela "nossa × professor" no diário |
| S2 | Transformar 3 a 5 pacotes reais de `runs/` em casos de teste (`tests/fixtures/`) com a decisão esperada | Testes de regressão no `pytest` |
| S3 | Rodar cada PR em conformance e registrar antes/depois; DeepEval opcional (docs/06) | Diário com 1 entrada por mudança |
| S4 | Rodada official final, `results/final_result.json`, README, diário fechado, slides | Entrega pronta |

## Combinados que valem para todos
- **Um servidor, uma rodada por vez.** Antes de usar `--reset`, avise no grupo. Quem estiver rodando "segura o servidor" até terminar.
- **Uma hipótese por mudança** e o número antes/depois no PR.
- Dúvida sobre regra do jogo: perguntar à Camile (integração) ou ao orientador; registrar a resposta em `docs/`.

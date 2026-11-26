# 3. Divisão da equipe, módulos e sessões

## 3.1 Quem faz o quê
| Pessoa | Papel | Tema | Arquivos que são dela/dele |
|---|---|---|---|
| **Camile** | Desenvolvedora | **A. Integração, Segurança e Agente LLM** | `client.py`, `contract.py`, `pack.py`, `graph.py`, `agents/coordinator.py`, `agents/safety.py`, `llm/` |
| **Matheus** | Desenvolvedor | **B. Navegação e Simulação de custo** | `agents/navigation.py`, `tools/navigation.py`, `tools/fuel.py`, `tools/economia.py` (novo) |
| **Rafaela** | Desenvolvedora | **C. Economia (combustível), Avaliação e Evidências** | `agents/economy.py`, `runner.py`, `scripts/`, `evals/`, `results/`, `tests/fixtures/` |
| **Lídia** | **Revisora** | Revisa todos os PRs; guarda os critérios imutáveis e a qualidade do diário | Nenhum arquivo próprio; aprova ou pede mudanças |

Mexer em arquivo de outra pessoa é permitido quando o módulo exige, mas avise no PR e peça a revisão da dona e da Lídia.

**Combinados:**
- **Um servidor, uma rodada por vez.** Antes de `--reset`, avise no grupo. Quem está rodando "segura o servidor" até terminar.
- **Uma hipótese por mudança**, com o número antes e depois no PR e no diário.

## 3.2 Critérios imutáveis
A política de referência do pacote faz **97,6843** em conformance, com Segurança, Serviço, Engenharia e Governança em **100** (`evals/baseline_referencia.json`).
1. Essas quatro dimensões continuam em **100.0000**.
2. `hard_gates` vazio e `rank_eligible = true`.
3. Economia ≥ 90,7373 (referência) e ≥ a baseline da equipe.
4. Todo PR que muda comportamento traz a saída **APROVADO** de `evals/comparar.py`.

**Onde dá para ganhar:** só na Economia. Margem (70%): lucro por tonelada até D$ 20/t. Eficiência (30%): menos combustível consumido por tonelada-milha. O teto de ganho na nota final é de cerca de 2,3 pontos. Perder pontos nas outras dimensões é muito mais fácil do que ganhar na Economia.

## 3.3 Os módulos (entregas conjuntas, cada uma testável)
| Módulo | Entrega | Líder + apoio | Como testar | Depende de |
|---|---|---|---|---|
| **M1 Régua** | Baseline da equipe medida, salva e travada; métricas de custo | Rafaela + Camile | `comparar.py` contra a referência; `metricas.py` mostra os custos por tipo | nada |
| **M2 Simulador** | `simular_plano()` e `opcoes_de_velocidade()` validados contra uma rodada real | Matheus + Rafaela | `tests/test_simulador.py`; `evals/validar_simulador.py` com erro ≤ 5% no combustível | M1 (precisa de uma rodada salva) |
| **M3 Plano econômico** | Velocidade por menor custo + compra sob medida + vetos de prazo e reserva | Matheus + Rafaela + Camile | Rodada conformance: `comparar.py` APROVADO **e** Economia > baseline | M2 |
| **M4 Agente LLM** | Agente de navegação com LLM chamando as tools do M2, com portão de segurança e fallback | Camile + Matheus | Testes com LLM falso; rodada com LLM: `comparar.py` APROVADO; nº de chamadas registrado | M2 (interface), M3 (para comparar) |
| **M5 Entrega** | Rodada official, `results/final_result.json`, diário e README finais | Rafaela + todos | `rank_eligible = true`, 4 dimensões em 100, diário completo | M3 ou M4 |

**Contrato do M2** (definido agora para o M3 e o M4 poderem começar em paralelo):
```python
@dataclass(frozen=True)
class PlanoSimulado:
    speed_centi: int                 # velocidade de cruzeiro testada
    ticks_ate_chegada: int
    folga_prazo_ticks: int           # deadline - (chegada + 12 de descarga); < 0 = atrasa
    combustivel_consumido_t: float
    folga_reserva_t: float           # combustível na chegada - reserva mínima; < 0 = Hard Gate
    custo_combustivel_cent: int      # consumido x preço de reposição atual
    custo_tempo_cent: int            # (tripulação + manutenção) x ticks até o fim da descarga
    custo_total_cent: int
    viavel: bool                     # folga_prazo_ticks >= 0 e folga_reserva_t >= 0

def simular_plano(ship: ShipView, view: TurnView, speed_centi: int) -> PlanoSimulado: ...
def opcoes_de_velocidade(ship: ShipView, view: TurnView, de: int = 800, ate: int = 1400, passo: int = 50) -> list[PlanoSimulado]: ...
```

## 3.4 Sessões por pessoa
Cada sessão é um bloco de trabalho que termina em PR. A ordem é sugerida; não há datas. **Toda sessão fecha com uma entrada no diário** (`docs/diario-engenharia.md`).

### Tema A: Camile (Integração, Segurança e Agente LLM)

**A1. Primeiro turno real e prova multiagente** (M1)
- Configurar o `.env` com o servidor da equipe; rodar `decidir_arquivo.py` no pacote do tick 0 e enviar um turno.
- Junto com a Rafaela, rodar a baseline (`--reset --label baseline`).
- Ler `multi_agent_proof` no resultado: **cada agente tem ≥ 10 transações committed e ≥ 2 navios?** Hoje a economia só propõe compras no início. Se faltar, ajustar o coordenador (por exemplo, alternar o revisor entre `safety` e `coordinator`, ou redistribuir propostas).
- Pronto quando: a baseline tem `multi_agent_proof.compliant = true`, ou o ajuste está feito e testado.

**A2. Portão de segurança v2** (M3)
- Trocar `_fuel_ok` em `agents/safety.py` por `simular_plano()` do M2 (folga de reserva real até o destino).
- Novos vetos, cada um com código e teste: `DEADLINE_RISK` (folga de prazo < 0), `RESERVE_RISK` (folga de reserva abaixo da margem), `STALE_TELEMETRY` (ação agressiva com `state_age_ticks > 2`).
- Pronto quando: os testes de cada veto passam e a rodada conformance segue APROVADA.

**A3. Tools para o LLM** (M4)
- Em `llm/tools.py`, expor como `@tool` (LangChain): `estado_do_navio(ship_id)`, `opcoes_de_velocidade(ship_id)` (a tabela do M2) e `eventos_ativos()`.
- As tools leem o `TurnView` do turno atual, injetado pelo código (nunca vindo do LLM).
- Pronto quando: cada tool tem teste sem rede.

**A4. Agente LLM de navegação** (M4)
- Em `llm/agente_navegacao.py`: grafo LangGraph `analisar ⇄ tools → proposta`, com saída estruturada (`Proposal`).
- O LLM só é chamado para navios citados em `stop_reasons` ou com evento ativo; os outros seguem a regra.
- Portão: a proposta do LLM passa por `safety.review` (código). Se o LLM falhar, demorar ou propor algo vetado, usar a regra do M3.
- Contar as chamadas de LLM por rodada e salvar em `runs/`.
- Pronto quando: testes com LLM falso cobrem os 3 caminhos (aceita, vetada, falha com fallback).

**A5. Rodada com LLM e comparação** (M4)
- Ligar com `LLM_DECIDE=true` (flag nova; `LLM_ENABLED` continua só para justificativas).
- Rodada conformance com e sem LLM: comparar nota, custo e número de chamadas.
- Pronto quando: `comparar.py` APROVADO e a diferença registrada no diário.

### Tema B: Matheus (Navegação e Simulação de custo)

**B1. Física e custos do simulador** (M2)
- Conferir `tools/fuel.py` contra `Ocean-1/server/ocean_server/sim_phases.py` (`compute_step_physics`).
- Descobrir no pacote onde está o custo por tick (`route_and_contract.crew_tick_cent`, `economy.maintenance_tick_cent_per_ship`) e se a tripulação é cobrada até a entrega ou durante a rodada toda (comparar `economy.totals` entre dois turnos).
- Pronto quando: as respostas estão no diário, seção "Descobertas".

**B2. Simulador de plano** (M2)
- Criar `tools/economia.py` com o contrato da seção 3.3 (adicionar em `pack.py` os campos que faltarem, avisando a Camile).
- Testes em `tests/test_simulador.py`: velocidade maior consome mais; folga de prazo cai com velocidade menor; plano inviável marcado com `viavel=False`.

**B3. Validação contra rodada real** (M2, com a Rafaela)
- `evals/validar_simulador.py runs/<baseline>`: para cada navio, prever no turno T o combustível na chegada e comparar com o que aconteceu.
- Pronto quando: erro ≤ 5% no combustível, ou a diferença explicada no diário.

**B4. Velocidade por menor custo** (M3)
- Em `agents/navigation.py`, `desired_speed_centi` passa a escolher, entre as opções viáveis do M2, a de **menor custo total** com folga de prazo ≥ 12 ticks.
- Manter a regra da tempestade (velocidade segura no trecho exposto) e a da pane E04.
- Anti-churn: só propor nova velocidade se a economia prevista passar de um limiar (definir e justificar no diário).
- Pronto quando: rodada conformance com Economia > baseline e `comparar.py` APROVADO.

**B5. Rota direta × protegida** (M3, opcional)
- Duas rodadas conformance, uma com cada rota por navio, e a decisão registrada com números.

**B6. Apoio ao M4**
- Definir com a Camile o formato da tabela que o LLM recebe (`opcoes_de_velocidade`) e revisar o prompt.

### Tema C: Rafaela (Economia, Avaliação e Evidências)

**C1. Baseline da equipe** (M1)
- Rodar `jogar_rodada.py --reset --label baseline` (combinado com a equipe).
- Copiar `runs/<baseline>/resumo.json` e `resultado_final.json` para `results/baseline-equipe/`.
- Rodar `comparar.py` contra a referência. Se reprovar, investigar qual dimensão e por quê (`/api/v1/ledger` e `metricas.py`).
- Pronto quando: baseline salva e a Iteração I-00 escrita no diário.

**C2. Métricas de custo** (M1)
- Em `evals/metricas.py`, ler `resultado_final.json` (`summary.fleet` e `economy_breakdown`) e mostrar: receita, combustível comprado, tripulação, manutenção, porto, reparo, multas, margem e **combustível sobrando no fim por navio**.
- Comparar duas execuções lado a lado (`metricas.py runs/a runs/b`).

**C3. Compra sob medida** (M3)
- Em `agents/economy.py`, dimensionar a compra para o plano de velocidade do M2 (não mais 14 kn fixo), com margem de segurança justificada.
- Preferir a janela de preço mais barata; o fornecedor da origem fecha depois do tick 95.
- Pronto quando: o combustível sobrando no fim cai, nenhum navio chega perto da reserva e `comparar.py` APROVADO.

**C4. Casos de regressão com pacotes reais** (M3 e M4)
- Copiar de `runs/` para `tests/fixtures/` os pacotes do tick 0, do início da tempestade e do tick 288 (pane), com a decisão esperada de cada um.

**C5. Rodada official e evidência** (M5)
- Só com a aprovação da Lídia. Rodada official, `results/final_result.json`, diário com `score_final`, dimensões, `multi_agent_proof` e `merkle_root_sha256`, README final.

**C6. DeepEval** (opcional, depois do M4)
- G-Eval para a fidelidade das justificativas do LLM; métricas próprias para folga de reserva e reação a eventos (`docs/06`).

### Lídia (Revisão)
Em cada PR, conferir e só aprovar quando tudo estiver certo:
- [ ] O PR diz qual módulo e sessão atende.
- [ ] Teste novo e `pytest` verde.
- [ ] Saída de `comparar.py` colada no PR: **APROVADO**.
- [ ] Nenhum número de tick fixo para evento móvel, nenhum segredo, nenhuma ação proibida.
- [ ] Entrada no diário completa: decisão, motivo, alternativas descartadas, evidência (números antes e depois) e aprendizado.
- [ ] Mudança restrita ao tema (ou combinada com a dona do arquivo).

A Lídia também aprova a rodada official (M5) e mantém o "Registro de decisões" do diário coerente.

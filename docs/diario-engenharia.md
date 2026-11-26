# Diário de Engenharia e Arquitetura Multiagente: equipe `team-0X`

> Entrega obrigatória (guia oficial, §9.2). A banca quer ver **como** chegamos ao resultado: o que testamos,
> por que decidimos, o que deu errado e o que aprendemos. Toda sessão de trabalho fecha com uma entrada aqui.
> Desenvolvimento: Camile, Matheus, Rafaela. Revisão: Lídia.

## 1. Visão geral da organização final de agentes
- **Servidor da equipe:** `https://t0X.beatbot.com.br`
- **Agentes registrados no servidor:** navigation, safety, economy, coordinator (preset do Modo por Turnos)
- **Agentes no nosso código e função de cada um:** [preencher na versão final]
- **Dinâmica maker-checker:** [quem propõe, quem revisa, como o veto funciona, como evitamos Hard Gates]
- **Onde entra o LLM e onde não entra (e por quê):** [preencher]

## 2. Principais descobertas
- **Física e consumo:** [rampa, consumo cúbico, velocidades ótimas, reservas]
- **Caixa e combustível:** [reserva operacional, janelas de preço, compra na origem × posto]
- **Eventos e crises:** [E01–E06, perda de telemetria]
- **Custos por tick:** [tripulação/manutenção: até quando são cobrados]

## 3. Linha de base
| Execução | Turnos | Nota | Seg | Eco | Srv | Eng | Gov | Hard gates | Cadeias |
|---|---|---|---|---|---|---|---|---|---|
| Referência do pacote (`evals/baseline_referencia.json`) | — | 97,6843 | 100 | 90,7373 | 100 | 100 | 100 | — | — |
| Exemplo do professor (opcional) | | | | | | | | | |
| Baseline da equipe (I-00) | | | | | | | | | |

## 4. Registro de decisões
Uma linha por decisão relevante de arquitetura ou estratégia. O detalhe fica na iteração correspondente.

| ID | Data | Autor | Decisão | Motivo principal | Alternativas descartadas | Iteração |
|---|---|---|---|---|---|---|
| D-01 | 26/11 | Equipe | Modo por Turnos em vez de tick a tick | O servidor cuida de heartbeats e hashes; foco na inteligência dos agentes | Laço tick a tick com heartbeats próprios | I-00 |
| D-02 | 26/11 | Equipe | Contas e vetos em código; LLM escolhe entre opções validadas | Quatro dimensões precisam ficar em 100; decisão auditável | LLM decidindo livremente; LLM só justificando | — |
| D-03 | 26/11 | Equipe | Critérios imutáveis com `evals/comparar.py` | Só a Economia tem espaço para subir; o resto só pode cair | Comparar notas à mão | — |

## 5. Evolução iterativa

### Modelo de entrada (copie para cada sessão)
```markdown
### I-NN: [título curto] (Módulo Mx, sessão Xn)
- **Autor / revisora:** [nome] / Lídia
- **Data e execução:** [data], `runs/<pasta>` (conformance|official)
- **Contexto:** [qual problema ou oportunidade motivou a mudança]
- **Hipótese e previsão:** [o que esperamos e em quanto, ex.: "Economia +2 pts, combustível −10 t"]
- **Decisão:** [o que foi implementado]
- **Por que esta e não outra:** [alternativas consideradas e por que foram descartadas]
- **Evidência (antes → depois):**
  | Métrica | Antes | Depois |
  |---|---|---|
  | score_final | | |
  | Seg / Eco / Srv / Eng / Gov | | |
  | Combustível consumido (t) | | |
  | Combustível sobrando no fim (t) | | |
  | Multas (D$) | | |
  | `comparar.py` | | APROVADO / REPROVADO |
- **Diagnóstico (ledger e métricas):** [erros, vetos ou rejeições e como foram tratados]
- **Aprendizado:** [o que sabemos agora que não sabíamos]
- **Próximo passo:** [...]
```

### I-00: Baseline da equipe (M1, sessão C1)
- **Autor / revisora:**
- **Data e execução:**
- **Contexto:** medir a política inicial antes de qualquer otimização.
- **Evidência:** (comparar com a referência do pacote: 97,6843)
- **Aprendizado:**

## 6. Resultado final (official)
- **Score final:** `XX.XXXX` (`rank_eligible = true`)
- **Dimensões:** Seg | Eco | Srv | Eng | Gov
- **Prova multiagente:** `compliant = true`, `credited_chains = XX`
- **Selo (`merkle_root_sha256`):**
- **Arquivo:** `results/final_result.json`

## 7. Aprendizados da equipe
[Lições gerais sobre sistemas multiagente, LLM com tools, avaliação e trabalho em equipe.]

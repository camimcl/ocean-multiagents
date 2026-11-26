# Diário de Engenharia e Arquitetura Multiagente: equipe `team-0X`

> **Entrega obrigatória** (guia oficial, §9.2). A banca avalia **como** chegamos ao resultado: o que tentamos,
> **por que** decidimos, o que deu errado e **o que aprendemos** em cada etapa.
> Desenvolvimento: Camile (tema A), Matheus (tema B), Rafaela (tema C). Revisão: Lídia.

## Como este diário funciona
- **Toda sessão de trabalho** (A1…A5, B1…B6, C1…C6 em `docs/03`) gera **uma entrada**, mesmo quando o experimento falha. Experimento que falhou e foi explicado vale tanto quanto um que deu certo.
- **IDs sem conflito entre as três pessoas:**
  - Entradas: `I-<sessão>.<n>`, ex.: `I-C1.1` (Rafaela, sessão C1, 1ª entrada), `I-B4.2` (Matheus, sessão B4, 2ª tentativa).
  - Decisões: `D-<sessão>.<n>`, ex.: `D-A2.1`. Decisões da equipe toda: `D-EQ.<n>`.
- A entrada vai **dentro da seção do módulo** (seção 5) a que a sessão pertence.
- **Ao fechar um módulo**, o líder escreve o "Fechamento" daquele módulo: M1 (Rafaela), M2 (Matheus), M3 (Matheus), M4 (Camile), M5 (Rafaela).
- **Descoberta sobre o simulador** (física, custos, eventos): além da entrada, acrescente uma linha na seção 2.
- **Números só de execuções reais**, citando a pasta em `runs/` ou `results/`. Nada de "melhorou bastante" sem número.
- A Lídia confere a entrada no PR. Um PR sem entrada completa não é aprovado.

## 1. Visão geral da organização final de agentes
> Preencher no M5, a partir dos fechamentos dos módulos.
- **Servidor da equipe:** `https://t0X.beatbot.com.br`
- **Agentes registrados no servidor:** navigation, safety, economy, coordinator (preset do Modo por Turnos)
- **Agentes no nosso código e função de cada um:**
- **Dinâmica maker-checker:** (quem propõe, quem revisa, como o veto funciona, como evitamos Hard Gates)
- **Onde entra o LLM e onde não entra, e por quê:**

## 2. Principais descobertas sobre o simulador
| Data | Autor | Descoberta | Como descobrimos (evidência) | Impacto na estratégia |
|---|---|---|---|---|
| | | | | |

Temas a cobrir até o fim: física e consumo; rampa; custos por tick (tripulação e manutenção: até quando são cobrados); caixa e reserva operacional; janelas de preço do combustível; eventos E01–E06; perda de telemetria.

## 3. Linha de base
| Execução | Turnos | Nota | Seg | Eco | Srv | Eng | Gov | Hard gates | Cadeias |
|---|---|---|---|---|---|---|---|---|---|
| Referência do pacote (`evals/baseline_referencia.json`) | — | 97,6843 | 100 | 90,7373 | 100 | 100 | 100 | — | — |
| Exemplo do professor (opcional) | | | | | | | | | |
| Baseline da equipe (`I-C1.1`) | | | | | | | | | |

## 4. Registro de decisões
Uma linha por decisão de arquitetura ou estratégia. O raciocínio completo fica na entrada citada.

| ID | Data | Autor | Decisão | Motivo principal | Alternativas descartadas | Entrada |
|---|---|---|---|---|---|---|
| D-EQ.1 | 26/11 | Equipe | Modo por Turnos em vez de tick a tick | O servidor cuida de heartbeats e hashes; foco na inteligência dos agentes | Laço tick a tick com heartbeats próprios | — |
| D-EQ.2 | 26/11 | Equipe | Contas e vetos em código; o LLM escolhe entre opções validadas (M4) | As quatro dimensões precisam ficar em 100 e a decisão tem de ser auditável | LLM decidindo livremente; LLM só justificando | — |
| D-EQ.3 | 26/11 | Equipe | Critérios imutáveis verificados por `evals/comparar.py` | Só a Economia tem espaço para subir; o resto só pode cair | Comparar notas à mão | — |
| D-EQ.4 | 26/11 | Equipe | Repositório oficial (`Deloitte-Tester/Bootcamp-01`) para a entrega; o privado só para testes | A banca avalia o repositório oficial | Manter os dois em paralelo | — |
| D-EQ.5 | 26/11 | Equipe | Desenvolvimento em 3 temas (A, B, C) com a Lídia como revisora de tudo | Revisão independente de todo PR, sem conflito de interesse | Cada um revisar o PR de outro desenvolvedor | — |

## 5. Evolução por módulo

### Modelo de entrada (copie para cada sessão)
```markdown
#### I-<sessão>.<n>: [título curto]
- **Autor / revisora:** [nome] / Lídia
- **Data e execução:** [data], `runs/<pasta>` (conformance | official)
- **Contexto:** [qual problema ou oportunidade motivou a mudança; cite o dado: ledger, métrica, evento]
- **Hipótese e previsão:** [o que esperamos e em quanto, ex.: "Economia +2 pts, combustível −10 t"]
- **Decisão:** [o que foi implementado, em 1 ou 2 frases]
- **Por que esta e não outra:** [pelo menos uma alternativa considerada e por que foi descartada]
- **Evidência (antes → depois):**
  | Métrica | Antes | Depois |
  |---|---|---|
  | score_final | | |
  | Seg / Eco / Srv / Eng / Gov | | |
  | Combustível consumido (t) | | |
  | Combustível sobrando no fim (t) | | |
  | Multas (D$) | | |
  | `comparar.py` | | APROVADO / REPROVADO |
- **Diagnóstico:** [erros, vetos ou rejeições no caminho e como foram tratados]
- **Previsão × resultado:** [acertamos? se não, por quê]
- **Aprendizado:** [o que sabemos agora que não sabíamos, escrito para a equipe entender]
- **Próximo passo:** [...]
```

### Modelo de fechamento de módulo (escrito pelo líder)
```markdown
#### Fechamento do Mx
- **O que o módulo entregou:** [...]
- **Como foi testado:** [testes, rodadas, resultado do `comparar.py`]
- **Decisões tomadas no módulo:** [IDs D-... e uma linha de cada]
- **O que não funcionou e por quê:** [...]
- **Aprendizados do módulo:** [3 a 5 itens]
- **O que fica para o próximo módulo:** [...]
```

### M1 Régua (líder: Rafaela; apoio: Camile)
#### I-C1.1: Baseline da equipe
- **Autor / revisora:** Rafaela / Lídia
- **Data e execução:**
- **Contexto:** medir a política inicial antes de qualquer otimização.
- **Hipótese e previsão:** como a política imita a referência do pacote, esperamos nota próxima de 97,68, com as quatro dimensões em 100.
- **Evidência:**
- **Previsão × resultado:**
- **Aprendizado:**

### M2 Simulador (líder: Matheus; apoio: Rafaela)

### M3 Plano econômico (líder: Matheus; com Rafaela e Camile)

### M4 Agente LLM (líder: Camile; apoio: Matheus)

### M5 Entrega (líder: Rafaela; todos)

## 6. Resultado final (official)
- **Score final:** `XX.XXXX` (`rank_eligible = true`)
- **Dimensões:** Seg | Eco | Srv | Eng | Gov
- **Prova multiagente:** `compliant = true`, `credited_chains = XX`
- **Selo (`merkle_root_sha256`):**
- **Arquivo:** `results/final_result.json`

## 7. Aprendizados da equipe
> Preencher no M5, a partir dos aprendizados de cada módulo: sistemas multiagente, LLM com ferramentas, avaliação e trabalho em equipe.

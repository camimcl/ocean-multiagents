# 4. Padrões do projeto

## Código
- Python 3.11+, `ruff` com linha de 120 caracteres, tipagem nas funções públicas.
- Nomes em inglês no código (`propose`, `review`, `ship`), textos de justificativa e documentação em português.
- Agentes são **funções puras**: recebem `TurnView`, devolvem `Proposal`/`Review`. Rede só em `client.py`.
- Ações só com os construtores de `contract.py`. Nunca escrever o dicionário à mão.
- Unidades: velocidade em **centésimos de nó** (`1250` = 12,50 kn), combustível em **milli-toneladas**, dinheiro em **centavos**. Converter só na borda (`pack.py` e `contract.py`).
- Proibido: número de tick fixo para evento móvel (E01, E02, E03, E06), `float` dentro do JSON enviado, segredo no código.

## Justificativas (vão para o ledger)
- Uma frase, com os números que levaram à decisão: "Viagem restante de 412 nm a 14 kn exige 52 t; tanque 40 t, reserva 33 t. Compra de 50 t."
- Veto começa com `VETO <CODIGO>:` (ex.: `VETO STORM_UNSAFE_SPEED: ...`).
- Códigos de veto em MAIÚSCULAS_COM_UNDERLINE, um por regra.

## Git
- `master` protegida. Tudo entra por Pull Request revisado pela Lídia.
- Branch: `tipo/tema-descricao`. Tipos: `feat`, `fix`, `test`, `docs`, `exp` (experimento). Ex.: `feat/nav-slow-steaming`, `fix/safety-reserva`.
- Commit no imperativo, em português: "Adiciona veto por telemetria defasada".
- PR pequeno (uma regra ou um ajuste) com o modelo abaixo.

```markdown
Título: [Mx/<sessão>] descrição curta

## O que muda
## Hipótese (com número)
## Evidência (conformance, pasta em runs/ ou results/)
Antes: nota X (Seg | Eco | Srv | Eng | Gov), combustível Y t, multas D$ Z
Depois: ...
## Saída do comparar.py
(colar aqui; precisa dizer APROVADO)
## Diário
Link para a entrada I-<sessão>.<n>
## Checklist
- [ ] pytest verde e ruff limpo
- [ ] teste novo cobrindo a regra
- [ ] entrada no diário completa (e fechamento do módulo, se for o último PR dele)
- [ ] nenhum tick fixo para evento móvel, nenhum segredo, nenhuma ação proibida
```

## Execuções e resultados
- Toda rodada automática gera `runs/<data-hora>-<label>/` (não vai para o git).
- Label curto e descritivo: `baseline`, `nav-slow-13kn`, `eco-margem-5t`, `official-final`.
- Rodadas que viram evidência são copiadas para `results/` com o mesmo nome e citadas no diário. A baseline da equipe fica em `results/baseline-equipe/`.
- `--reset` só depois de avisar a equipe. Modo `official` só com a aprovação da Lídia.
- Entregas finais (código, `results/final_result.json`, diário) vão para o repositório oficial `Deloitte-Tester/Bootcamp-01`.

## Definição de pronto (por tarefa)
1. Código + teste passando (`pytest` e `ruff` limpos).
2. Rodada em conformance com `comparar.py` **APROVADO** e os números antes e depois.
3. Entrada no diário completa (`I-<sessão>.<n>`).
4. PR revisado pela Lídia e na `master`.

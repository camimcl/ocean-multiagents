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
- `main` protegida. Tudo entra por Pull Request revisado pela pessoa indicada em docs/03.
- Branch: `tipo/tema-descricao`. Tipos: `feat`, `fix`, `test`, `docs`, `exp` (experimento). Ex.: `feat/nav-slow-steaming`, `fix/safety-reserva`.
- Commit no imperativo, em português: "Adiciona veto por telemetria defasada".
- PR pequeno (uma regra ou um ajuste) com o modelo abaixo.

```markdown
## O que muda
## Hipótese
## Evidência (conformance)
Antes: nota X (Seg | Eco | Srv | Eng | Gov), combustível Y t, multas D$ Z
Depois: ...
## Checklist
- [ ] pytest verde e ruff limpo
- [ ] teste novo cobrindo a regra
- [ ] entrada no diário
- [ ] nenhum tick fixo para evento móvel, nenhum segredo
```

## Execuções e resultados
- Toda rodada automática gera `runs/<data-hora>-<label>/` (não vai para o git).
- Label curto e descritivo: `baseline`, `nav-slow-13kn`, `eco-margem-5t`, `official-final`.
- Rodadas que viram evidência são copiadas para `results/` com o mesmo nome e citadas no diário.
- `--reset` só depois de avisar a equipe. Modo `official` só a partir da sexta de manhã.

## Definição de pronto (por tarefa)
1. Código + teste passando.
2. Rodada em conformance com o número antes/depois.
3. Entrada no diário.
4. PR revisado e na `main`.

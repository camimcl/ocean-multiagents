# 5. Ordem dos módulos (sem cronograma fixo)

A equipe não segue um cronograma com datas. A ordem vem das dependências entre os módulos (detalhes em `docs/03-divisao-da-equipe.md`):

```
M1 Régua ──► M2 Simulador ──► M3 Plano econômico ──► M5 Entrega (official)
                    │                  ▲
                    └──► M4 Agente LLM ┘   (M4 pode começar pelas tools assim que o contrato do M2 existir)
```

Regras:
- Nenhum módulo é dado como pronto sem `evals/comparar.py` **APROVADO** em conformance.
- Se uma mudança piorar a nota, reverter e registrar no diário. Também é aprendizado.
- Plano B: se a API falhar, modo manual pelo site com `scripts/decidir_arquivo.py`. Se o LLM falhar, `LLM_ENABLED=false` e `LLM_DECIDE=false`.

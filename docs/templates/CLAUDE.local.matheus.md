# CLAUDE.local.md: Matheus

> Arquivo pessoal. Copie para a raiz do repositório como `CLAUDE.local.md` (já está no `.gitignore`):
> `Copy-Item docs\templates\CLAUDE.local.matheus.md CLAUDE.local.md`
> Ele complementa o `CLAUDE.md` da equipe. Em caso de conflito, as regras do `CLAUDE.md` vencem.

## 1. Quem você representa
Você está trabalhando **em nome de Matheus**, desenvolvedor do projeto Ocean Multiagentes.
- **Tema:** B. Navegação e Simulação de custo
- **Módulos em que participo:** M2 (líder), M3 (líder da velocidade), M4 (apoio), M5
- **Minhas sessões** (detalhe em `docs/03-divisao-da-equipe.md`): B1, B2, B3, B4, B5, B6
- **Arquivos que são meus:** `agents/navigation.py`, `tools/navigation.py`, `tools/fuel.py`, `tools/economia.py`
- **Com quem divido módulos:** Rafaela (M2, M3), Camile (M3, M4)
- **Revisora de todos os meus PRs:** Lídia

Escreva código, commits, PRs e entradas de diário **como Matheus**: em primeira pessoa quando for registro meu
("decidi", "testei"), e em nome da equipe quando a decisão foi conjunta.

## 2. Como agir
- Trabalhe **só no meu escopo**. Se a tarefa exigir mexer em arquivo de outra pessoa, pare e me pergunte antes; no PR, marque a dona do arquivo.
- Explique o que vai fazer antes de mudanças grandes, em português simples.
- Nunca diga que algo funciona sem ter rodado o teste ou a rodada.
- Rodadas no servidor da equipe (`jogar_rodada.py`), principalmente com `--reset`, **só quando eu pedir explicitamente** (o servidor é compartilhado).
- `official` só com a aprovação da Lídia registrada.

## 3. Fluxo de cada feature (siga na ordem)
1. **Entender:** ler a sessão correspondente em `docs/03` e o código envolvido. Resumir para mim em até 5 linhas o que vai mudar.
2. **Branch:** `tipo/nav-descricao` (ex.: `feat/nav-exemplo`).
3. **Hipótese antes do código:** criar no `docs/diario-engenharia.md` o rascunho da entrada `I-NN` com Contexto, Hipótese e previsão (com número). Use o próximo número livre.
4. **Teste primeiro:** escrever o teste que mostra o comportamento desejado e confirmar que ele falha.
5. **Implementar** o mínimo para o teste passar. Rodar `python -m pytest` e `ruff check .`.
6. **Rodada conformance** (só quando eu pedir): `python scripts\jogar_rodada.py --label <nome-curto>`, depois `python evals\metricas.py runs\<pasta>` e `python evals\comparar.py runs\<pasta> results\baseline-equipe\resumo.json`.
7. **Completar o diário** (seção 4 abaixo) com os números reais. Se `comparar.py` reprovar, registrar mesmo assim e propor a correção ou a reversão.
8. **Decisão relevante?** Acrescentar uma linha em "Registro de decisões" (`D-NN`) do diário.
9. **PR:** título `[Mx/B4] descrição`, corpo com o modelo de `docs/04-padroes.md`, a saída do `comparar.py` colada e o link da entrada do diário. Revisora: Lídia. Não mergear.

## 4. Como documentar no Diário de Engenharia
A banca avalia **como decidimos, por quê e o que aprendemos**. Para cada sessão, preencha a entrada `I-NN` com:
- **Contexto:** que problema ou oportunidade apareceu (cite o dado: ledger, métrica, evento).
- **Hipótese e previsão:** o que eu esperava, com número.
- **Decisão:** o que implementei, em uma ou duas frases.
- **Por que esta e não outra:** pelo menos uma alternativa considerada e o motivo de descartá-la.
- **Evidência:** tabela antes → depois (nota, dimensões, combustível, multas, `comparar.py`).
- **Diagnóstico:** o que deu errado no caminho (rejeições, vetos, bugs) e como resolvi.
- **Aprendizado:** o que eu sei agora que não sabia, escrito para alguém da equipe entender.
Regras: números sempre de execuções reais (cite a pasta em `runs/`); nada de "melhorou bastante" sem número;
se a previsão errou, explique por quê. Isso vale mais do que acertar.

## 5. Minhas preferências
- Nível de explicação: [ex.: didático, com analogias / direto ao ponto]
- Idioma: português
- Commits: autor = minha conta do git (`git config user.name` / `user.email`). Coautoria do Claude na mensagem: [sim/não]
- Outras: [...]

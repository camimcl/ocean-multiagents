# CLAUDE.local.md: Rafaela

> Arquivo pessoal. Copie para a raiz do repositório como `CLAUDE.local.md` (já está no `.gitignore`):
> `Copy-Item docs\templates\CLAUDE.local.rafaela.md CLAUDE.local.md`
> Ele complementa o `CLAUDE.md` da equipe. Em caso de conflito, as regras do `CLAUDE.md` vencem.

## 1. Quem você representa
Você está trabalhando **em nome de Rafaela**, desenvolvedora do projeto Ocean Multiagentes.
- **Tema:** C. Economia (combustível), Avaliação e Evidências
- **Módulos:** M1 (líder), M2 (apoio), M3 (compra sob medida), M5 (líder)
- **Minhas sessões** (detalhe em `docs/03-divisao-da-equipe.md`): C1, C2, C3, C4, C5, C6
- **Arquivos que são meus:** `agents/economy.py`, `runner.py`, `scripts/`, `evals/`, `results/`, `tests/fixtures/`
- **Com quem divido módulos:** Camile (M1), Matheus (M2, M3)
- **Fechamentos de módulo que eu escrevo no diário:** M1 e M5
- **Revisora de todos os meus PRs:** Lídia

Escreva código, commits, PRs e entradas de diário **como Rafaela**: em primeira pessoa quando o registro for meu
("decidi", "testei") e em nome da equipe quando a decisão foi conjunta. Nunca escreva entradas em nome de outra pessoa.

## 2. Como agir
- Trabalhe **só no meu escopo**. Se a tarefa exigir mexer em arquivo de outra pessoa, pare e me pergunte antes; no PR, marque a dona do arquivo.
- Antes de mudanças grandes, explique em português simples o que vai fazer.
- Nunca diga que algo funciona sem ter rodado o teste ou a rodada.
- Rodadas no servidor da equipe (`jogar_rodada.py`), principalmente com `--reset`, **só quando eu pedir explicitamente** (o servidor é compartilhado).
- `official` só com a aprovação da Lídia registrada.
- Entregas finais vão para o repositório **oficial** (`Deloitte-Tester/Bootcamp-01`); o repositório privado é só para testes.

## 3. Fluxo de cada sessão (siga na ordem)
1. **Entender:** ler a sessão em `docs/03` e o código envolvido. Resumir para mim, em até 5 linhas, o que vai mudar.
2. **Branch:** `tipo/eco-descricao` (ex.: `feat/eco-compra-sob-medida`).
3. **Hipótese antes do código:** no `docs/diario-engenharia.md`, dentro da seção do módulo, criar o rascunho da entrada
   `I-<sessão>.<n>` (ex.: `I-C3.1`) com Contexto e Hipótese e previsão (com número).
4. **Teste primeiro:** escrever o teste do comportamento desejado e confirmar que ele falha.
5. **Implementar** o mínimo para o teste passar. Rodar `python -m pytest` e `ruff check .`.
6. **Rodada conformance** (só quando eu pedir):
   `python scripts\jogar_rodada.py --label <nome-curto>`, depois `python evals\metricas.py runs\<pasta>` e
   `python evals\comparar.py runs\<pasta> results\baseline-equipe\resumo.json`.
7. **Completar a entrada do diário** (seção 4 abaixo) com os números reais. Se `comparar.py` reprovar, registrar mesmo assim e propor a correção ou a reversão.
8. **Decisão de arquitetura ou estratégia?** Acrescentar uma linha `D-<sessão>.<n>` no "Registro de decisões".
9. **Descoberta sobre o simulador?** Acrescentar uma linha na seção 2 do diário ("Principais descobertas").
10. **PR:** título `[Mx/<sessão>] descrição`, corpo com o modelo de `docs/04-padroes.md`, a saída do `comparar.py` colada e o link da entrada do diário. Revisora: Lídia. Não mergear.
11. **Último PR de um módulo que eu lidero?** Escrever o "Fechamento do Mx" no diário (modelo no próprio arquivo).

## 4. Como documentar no Diário de Engenharia
A banca avalia **como decidimos, por quê e o que aprendemos** em cada etapa. Toda entrada tem:
- **Contexto:** que problema ou oportunidade apareceu (cite o dado: ledger, métrica, evento).
- **Hipótese e previsão:** o que eu esperava, com número, escrito **antes** de rodar.
- **Decisão:** o que implementei, em uma ou duas frases.
- **Por que esta e não outra:** pelo menos uma alternativa considerada e o motivo de descartá-la.
- **Evidência:** tabela antes → depois (nota, dimensões, combustível, multas, `comparar.py`).
- **Diagnóstico:** o que deu errado no caminho (rejeições, vetos, bugs) e como resolvi.
- **Previsão × resultado:** acertei? Se não, por quê. Isso vale mais do que acertar.
- **Aprendizado:** o que eu sei agora que não sabia, escrito para alguém da equipe entender.

Regras: números sempre de execuções reais (cite a pasta em `runs/` ou `results/`); nada de "melhorou bastante" sem número;
experimento que falhou também ganha entrada; não apague entradas antigas, corrija com uma entrada nova.

## 5. Minhas preferências
- Nível de explicação: [ex.: didático, com analogias / direto ao ponto]
- Idioma: português
- Commits: autor = minha conta do git (`git config user.name` / `user.email`). Coautoria do Claude na mensagem: [sim/não]
- Outras: [...]

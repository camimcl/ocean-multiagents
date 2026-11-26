# CLAUDE.local.md: Lídia (revisora)

> Arquivo pessoal. Copie para a raiz do repositório como `CLAUDE.local.md` (já está no `.gitignore`):
> `Copy-Item docs\templates\CLAUDE.local.lidia.md CLAUDE.local.md`
> Ele complementa o `CLAUDE.md` da equipe. Em caso de conflito, as regras do `CLAUDE.md` vencem.

## 1. Quem você representa
Você está ajudando **a Lídia, revisora** do projeto Ocean Multiagentes. A Lídia **não escreve código de feature**:
ela revisa todos os PRs de Camile (tema A), Matheus (tema B) e Rafaela (tema C), guarda os critérios imutáveis
e a qualidade do Diário de Engenharia, e aprova (ou não) a rodada official.

## 2. Como agir
- **Não altere código nem docs dos PRs.** Seu papel é ler, conferir, rodar os testes localmente e escrever comentários de revisão.
- Comentários objetivos, em português, apontando arquivo e linha, sempre com o motivo e uma sugestão.
- Separe **bloqueante** (impede a aprovação) de **sugestão** (melhoria opcional).
- Nunca rode partidas no servidor da equipe nem `--reset`; se precisar de uma evidência, peça ao autor do PR.

## 3. Roteiro de revisão de cada PR
1. **Escopo:** o título diz `[Mx/<sessão>]`? A mudança fica no tema do autor (ou foi combinada com a dona do arquivo)?
2. **Testes:** existe teste novo cobrindo a regra? Rodar `python -m pytest` e `ruff check .` na branch do PR.
3. **Critérios imutáveis:** a saída do `comparar.py` está colada e diz **APROVADO**? As quatro dimensões seguem em 100? `hard_gates` vazio?
4. **Regras do desafio:** nenhum número de tick fixo para evento móvel (E01, E02, E03, E06), nenhuma ação proibida, nenhum segredo, nenhum `float` no JSON enviado.
5. **Diário:** a entrada `I-<sessão>.<n>` está na seção do módulo certo e tem: contexto, hipótese **com número**, decisão,
   alternativa descartada com motivo, evidência antes → depois de uma execução real (pasta citada), diagnóstico,
   previsão × resultado e aprendizado. Decisões relevantes também aparecem no "Registro de decisões".
6. **Fechamento de módulo:** se for o último PR do módulo, o líder escreveu o "Fechamento do Mx"?
7. **Veredito:** aprovar, ou pedir mudanças listando os itens bloqueantes.

## 4. Rodada official
Só aprove a rodada official quando: a versão estiver na `master`, a última rodada conformance estiver APROVADA no
`comparar.py`, a prova multiagente estiver `compliant` e o diário estiver em dia. Registre a aprovação no PR ou no diário.

## 5. Minhas preferências
- Nível de detalhe dos comentários: [...]
- Outras: [...]

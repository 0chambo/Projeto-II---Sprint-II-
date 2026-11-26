# AGENTS.md — Projeto II | Sprint II

## Objetivo
Orientar a continuidade do Projeto 2 de Estatística e Análise de Dados, usando os materiais da Sprint 1 e os requisitos da Sprint 2.

## Contexto e dados de referência
Tema: tempo de carregamento de caminhões com grãos.
Resultados descritivos registrados na Sprint 1:
- Antes da intervenção: n=300; média=31,8867 min.
- Depois da intervenção: n=100; média=29,31 min.
- Na faixa [20,30] min: antes 97/300 = 32,33%; depois 57/100 = 57%.

Esses números são descritivos e não demonstram, isoladamente, causalidade ou eficácia estatística.

## Materiais a consultar
Leia os documentos de `docs/`, especialmente as orientações da Sprint 2, as aulas e a rubrica. Consulte também o relatório, planilhas e notebooks originais da Sprint 1.

## Regras para a análise
1. Não modificar nem inventar dados.
2. Identificar a coluna, unidade de medida, tamanho da amostra e tratamento de ausentes.
3. Para o teste da média, formular H0/H1 antes de observar a decisão; usar a fórmula e o parâmetro de dispersão conforme a orientação da disciplina. Não assumir que o desvio-padrão populacional é conhecido se isso não estiver documentado.
4. Para o teste da proporção, confirmar p0 a partir da probabilidade na faixa [a,b] definida na Questão 5 da Sprint 1 e p-hat a partir da Questão 7.4(b). Não presumir que [a,b]=[20,30] sem verificar o enunciado e a correção.
5. Realizar os testes para α=1% e α=5%, apresentando valores críticos, regiões críticas, estatística z, gráficos, decisão e conclusão contextualizada.
6. Usar “não rejeitar H0”, e não “aceitar H0”.
7. Comparações antes/depois não provam causalidade por si só.
8. Identificar claramente hipóteses, fórmulas, substituição numérica, arredondamentos e fonte dos valores.

## Estrutura
- `docs/`: orientações, aulas, relatório e rubrica.
- `dados/`: planilhas originais.
- `notebooks/sprint-1/`: notebooks de referência.
- `notebooks/sprint-2/`: notebooks dos testes de hipótese.
- `resultados/`: gráficos, tabelas e relatório consolidado.

## Checklist de qualidade
- Executar os notebooks do início ao fim.
- Validar p0, p-hat, n e parâmetros antes dos cálculos.
- Conferir gráficos e regiões críticas para os dois níveis de significância.
- Confrontar a entrega com a rubrica.
- Não criar resultados não sustentados pelos arquivos de origem.

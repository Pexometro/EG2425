# TP2 - Analisador de Código Fonte LPI
## Unidade Curricular: Engenharia Gramatical
## Ano Letivo: 2024/2025

## Autores 
- **Pedro Azevedo (pg57897)**
- **Rui Pinto (pg56010)**
- **Jorge Teixeira (pg55965)**

## Objetivo

Este projeto consiste no desenvolvimento de uma ferramenta de análise de programas construída com a biblioteca Lark (Python).

A ferramenta realiza uma análise estática de código, recolhendo várias métricas, avisos e potenciais simplificações, e gera automaticamente um relatório HTML interativo com os resultados.

## Estrutura do projeto

```
.
├── fase2.py                # Ficheiro principal com o parser e os visitors
├── grammar.lark            # Gramática da linguagem LPI
├── generate_html.py        # Geração automática de relatório HTML
├── exemplo_geral.lpi       # Exemplo completo de código LPI
├── relatorio.html          # Relatório gerado
└── exemploX.html           # Relatórios dos testes por objetivo
```

## Funcionalidades Implementadas

### O analisador realiza os seguintes pontos:

**Análise de variáveis:**

- Redeclarações

- Uso sem declaração

- Uso sem inicialização

- Variáveis declaradas e nunca usadas

**Contagem de variáveis por tipo:**

- Int, Set, Tuple, String, Array, Seq

**Contagem de instruções por tipo:**

- Atribuições

- Leitura/Escrita

- Estruturas condicionais

- Estruturas cíclicas

**Contagem de aninhamentos de estruturas de controlo:**

    Ex: if dentro de while, case dentro de if, etc.

**Deteção de ifs aninhados simplificáveis:**

    Quando dois if consecutivos podem ser fundidos num único if com condição composta

## Como executar 

```
python3 fase2.py <ficheiro.lpi>
```

Aṕos a execução é gerado um **relatório.html** com os seguintes campos:

- Código fonte realçado

- Tabela de símbolos

- Contagens detalhadas

- Lista de erros e avisos

- Informações sobre estruturas aninhadas e ifs simplificáveis

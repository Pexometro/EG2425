from lark import Lark, Visitor, Transformer, Token, Tree
import sys
import os
import json

# Carregar a gramática do arquivo grammar.lark
with open('grammar.lark', 'r') as f:
    grammar = f.read()

# Criar o parser usando o Earley parser da biblioteca Lark
parser = Lark(grammar, parser='earley')

# Classe que representa um símbolo na tabela de símbolos
class Symbol:
    def __init__(self, name, type_spec, line, column, scope="global"):
        self.name = name  # Nome da variável
        self.type = type_spec  # Tipo da variável (Int, Set, etc.)
        self.scope = scope  # Escopo da variável (global ou local)
        self.is_initialized = False  # Indica se a variável foi inicializada
        self.is_used = False  # Indica se a variável foi usada
        self.is_redeclared = False  # Indica se a variável foi redeclarada
        self.line = line  # Linha onde a variável foi declarada
        self.column = column  # Coluna onde a variável foi declarada

# Classe que gerencia a tabela de símbolos
class SymbolTable:
    def __init__(self):
        self.symbols = {}  # Dicionário de símbolos
        self.current_scope = "global"  # Escopo atual (inicia como global)
        self.undeclared_symbols = set()  # Conjunto de símbolos não declarados

    # Adiciona um símbolo à tabela
    def add_symbol(self, name, type_spec, line, column, initialize):
        key = f"{name}_{self.current_scope}"  # Chave única baseada no nome e escopo
        if key in self.symbols:
            self.symbols[key].is_redeclared = True  # Marca como redeclarado
            return False  # Retorna falso se já foi declarado
        
        # Cria e adiciona o símbolo
        self.symbols[key] = Symbol(name, type_spec, line, column, self.current_scope)
        if initialize:
            self.symbols[key].is_initialized = True  # Marca como inicializado
        return True

    # Marca um símbolo como usado
    def use_symbol(self, name):
        key = f"{name}_{self.current_scope}"
        if key in self.symbols:
            self.symbols[key].is_used = True
            return self.symbols[key]
        
        # Verifica no escopo global se não encontrado no escopo atual
        if self.current_scope != "global":
            key = f"{name}_global"
            if key in self.symbols:
                self.symbols[key].is_used = True
                return self.symbols[key]
        
        return None  # Retorna None se o símbolo não foi encontrado

    # Inicializa um símbolo
    def initialize_symbol(self, name):
        symbol = self.use_symbol(name)
        if symbol:
            symbol.is_initialized = True
            return True
        return False

    # Entra em um novo escopo
    def enter_scope(self, scope_name):
        self.current_scope = scope_name

    # Sai do escopo atual e retorna ao global
    def exit_scope(self):
        self.current_scope = "global"

    # Realiza a análise da tabela de símbolos
    def get_analysis(self):
        redeclared = []  # Variáveis redeclaradas
        undeclared = []  # Variáveis não declaradas
        unused = []  # Variáveis declaradas mas nunca usadas
        uninitialized_but_used = []  # Variáveis usadas mas não inicializadas
        
        # Itera sobre os símbolos para realizar a análise
        for key, symbol in self.symbols.items():
            if not symbol.is_used:
                unused.append(symbol)  # Variáveis não usadas
            if not symbol.is_initialized and symbol.is_used:
                uninitialized_but_used.append(symbol)  # Variáveis usadas sem inicialização
            if symbol.is_redeclared:
                redeclared.append(symbol)  # Variáveis redeclaradas
        
        return {
            "redeclared": redeclared,
            "undeclared": self.undeclared_symbols,
            "unused": unused,
            "uninitialized_but_used": uninitialized_but_used,
            "type_counts": self.get_type_counts()  # Contagem por tipo
        }

    # Conta o número de variáveis por tipo
    def get_type_counts(self):
        type_counts = {}
        for symbol in self.symbols.values():
            if symbol.type in type_counts:
                type_counts[symbol.type] += 1
            else:
                type_counts[symbol.type] = 1
        return type_counts

# Classe que constrói a tabela de símbolos e realiza a contagem de instruções
class SymbolTableBuilder(Transformer):
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.assignment_count = 0  # Contagem de atribuições
        self.read_write_count = 0  # Contagem de instruções de leitura/escrita
        self.conditional_count = 0  # Contagem de instruções condicionais
        self.cyclic_count = 0  # Contagem de instruções cíclicas
        self.declaration_count = 0  # Contagem de declarações
        self.aninhamentos = 0  # Contagem de aninhamentos
        self.nivel = 0  # Nível de aninhamento

    # Processa declarações de variáveis
    def declaration(self, items):
        type_spec = str(items[0])  # Tipo da variável
        name = str(items[1])  # Nome da variável
        initialize = True if len(items) > 2 else False  # Verifica se foi inicializada
        line = items[1].line  # Linha da declaração
        column = items[1].column  # Coluna da declaração
        
        # Adiciona o símbolo à tabela
        self.symbol_table.add_symbol(name, type_spec, line, column, initialize)
        self.declaration_count += 1  # Incrementa a contagem de declarações
        return items

    # Processa atribuições
    def attribution(self, items):
        name = str(items[0])  # Nome da variável
        value = items[1]  # Valor atribuído
        
        # Verifica se a variável foi declarada
        if not self.symbol_table.use_symbol(name):
            self.symbol_table.undeclared_symbols.add((name, items[0].line, items[0].column))
            return items
        
        # Inicializa a variável
        self.symbol_table.initialize_symbol(name)
        self.assignment_count += 1  # Incrementa a contagem de atribuições
        return items

    # Processa átomos (identificadores, números, etc.)
    def atom(self, items):
        token = items[0]
        if isinstance(token, Token) and token.type == "IDENTIFIER":
            self.symbol_table.use_symbol(str(token))  # Marca o identificador como usado
        return items

    def if_stmt(self, items):
        self.nivel += 1
        self.conditional_count += 1
        if self.nivel > 1:
            self.aninhamentos += 1  # Conta aninhamento
        result = items
        self.nivel -= 1
        return result

    def while_stmt(self, items):
        self.nivel += 1
        self.cyclic_count += 1
        if self.nivel > 1:
            self.aninhamentos += 1  # Conta aninhamento
        result = items
        self.nivel -= 1
        return result

    def case_stmt(self, items):
        self.nivel += 1
        self.conditional_count += 1
        if self.nivel > 1:
            self.aninhamentos += 1
        result = items
        self.nivel -= 1
        return result

    def for_stmt(self, items):
        self.nivel += 1
        self.cyclic_count += 1
        if self.nivel > 1:
            self.aninhamentos += 1
        result = items
        self.nivel -= 1
        return result

    def repeat_stmt(self, items):
        self.nivel += 1
        self.cyclic_count += 1
        if self.nivel > 1:
            self.aninhamentos += 1
        result = items
        self.nivel -= 1
        return result
    
    def read_stmt(self, items):
        self.read_write_count += 1
        return items
    
    def write_stmt(self, items):
        self.read_write_count += 1
        return items
    
class ControlStructureCounter(Transformer):
    def __init__(self):
        self.nivel = 0
        self.aninhamentos = 0

    def if_stmt(self, items):
        self.nivel += 1
        if self.nivel > 1:
            self.aninhamentos += 1

        for item in items:
            if isinstance(item, Tree):
                if item.data in {"instruction", "selection"}:
                    self.transform(item)

        self.nivel -= 1
        return items

    def while_stmt(self, items):
        return self.if_stmt(items)

    def for_stmt(self, items):
        return self.if_stmt(items)

    def repeat_stmt(self, items):
        return self.if_stmt(items)

    def case_stmt(self, items):
        return self.if_stmt(items)

    def instruction(self, items):
        for item in items:
            if isinstance(item, Tree):
                if item.data in {"if_stmt", "while_stmt", "for_stmt", "repeat_stmt", "case_stmt", "selection"}:
                    self.transform(item)
        return items

    def selection(self, items):
        for item in items:
            if isinstance(item, Tree):
                if item.data == "instruction":
                    self.transform(item)
        return items


    def while_stmt(self, items):
        self.nivel += 1
        if self.nivel > 1:
            self.aninhamentos += 1

        for item in items:
            if isinstance(item, Tree) and item.data in {"instruction", "selection"}:
                self.transform(item)

        self.nivel -= 1
        return items

    def for_stmt(self, items):
        self.nivel += 1
        if self.nivel > 1:
            self.aninhamentos += 1

        for item in items:
            if isinstance(item, Tree) and item.data in {"instruction", "selection"}:
                self.transform(item)

        self.nivel -= 1
        return items

    def repeat_stmt(self, items):
        self.nivel += 1
        if self.nivel > 1:
            self.aninhamentos += 1

        for item in items:
            if isinstance(item, Tree) and item.data in {"instruction", "selection"}:
                self.transform(item)

        self.nivel -= 1
        return items

    def case_stmt(self, items):
        self.nivel += 1
        if self.nivel > 1:
            self.aninhamentos += 1

        for item in items:
            if isinstance(item, Tree) and item.data in {"instruction", "selection"}:
                self.transform(item)

        self.nivel -= 1
        return items
        
# -----------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python fase2.py <ficheiro.lpi>")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, 'r') as f:
        code = f.read()

    # Faz o parsing do código
    tree = parser.parse(code)
    
    # Constrói a tabela de símbolos e realiza a transformação
    builder = SymbolTableBuilder()
    builder.transform(tree)

    control_transformer = ControlStructureCounter()
    control_transformer.transform(tree)
    
    # Exibe a tabela de símbolos
    print(f"tabela de simbolos:\n")
    for simb in builder.symbol_table.symbols.values():
        print(f"Nome: {simb.name}, Tipo: {simb.type}, Escopo: {simb.scope}, Inicializado: {simb.is_initialized}, Usado: {simb.is_used}")
    
    # Realiza a análise e exibe os resultados
    analysis = builder.symbol_table.get_analysis()
    print("=== Análise ===")
    print("Variáveis redeclaradas:")
    for var in analysis["redeclared"]:
        print(f"  {var.name} (linha {var.line}, coluna {var.column})")
        
    print("Variáveis não declaradas:")
    for var in analysis["undeclared"]:
        print(f"  {var[0]} (linha {var[1]}, coluna {var[2]})")
        
    print("Variáveis não usadas:")
    for var in analysis["unused"]:
        print(f"  {var.name} (linha {var.line}, coluna {var.column})")
        
    print("Variáveis usadas sem inicialização:")
    for var in analysis["uninitialized_but_used"]:
        print(f"  {var.name} (linha {var.line}, coluna {var.column})")
        
    print("Contagem por tipo:")
    for type_spec, count in analysis["type_counts"].items():
        print(f"  {type_spec}: {count}")

    print("----------------------------------")
    
    # Exibe as contagens de instruções
    print("\n=== Instruction Counts ===")
    print(f"  Declarations: {builder.declaration_count}")
    print(f"  Assignments: {builder.assignment_count}")
    print(f"  Read/Write: {builder.read_write_count}")
    print(f"  Conditionals: {builder.conditional_count}")
    print(f"  Cyclic: {builder.cyclic_count}")
    print(f"  Aninhamentos: {control_transformer.aninhamentos}")
    
    
    
if "--json" in sys.argv:
    # Create a JSON-friendly structure
    json_result = {
        "symbols": [
            {
                "name": simb.name,
                "type": simb.type,
                "scope": simb.scope,
                "isInitialized": simb.is_initialized,
                "isUsed": simb.is_used,
                "isRedeclared": simb.is_redeclared,
                "line": simb.line,
                "column": simb.column
            }
            for simb in builder.symbol_table.symbols.values()
        ],
        "analysis": {
            "redeclared": [
                {
                    "name": var.name,
                    "line": var.line,
                    "column": var.column
                }
                for var in analysis["redeclared"]
            ],
            "undeclared": [
                {
                    "name": var[0],
                    "line": var[1],
                    "column": var[2]
                }
                for var in analysis["undeclared"]
            ],
            # Add other analysis results...
        },
        "counts": {
            "declarations": builder.declaration_count,
            "assignments": builder.assignment_count,
            "readWrite": builder.read_write_count,
            "conditionals": builder.conditional_count,
            "cyclic": builder.cyclic_count,
            "nestings": control_transformer.aninhamentos
        },
        "typeCounts": analysis["type_counts"]
    }
    print(json.dumps(json_result))
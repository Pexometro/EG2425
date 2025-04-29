from lark import Lark, Visitor, Token
from lark.visitors import Visitor_Recursive
import sys
import os
import json
from generate_html import generate_html_report

# Carregar a gramática do arquivo grammar.lark
with open('grammar.lark', 'r') as f:
    grammar = f.read()

# Criar o parser usando o Earley parser da biblioteca Lark
parser = Lark(grammar, parser='earley')

# -----------------------------------------------
# Classes de dados

class Symbol:
    def __init__(self, name, type_spec, line, column, scope="global"):
        self.name = name
        self.type = type_spec
        self.scope = scope
        self.is_initialized = False
        self.is_used = False
        self.is_redeclared = False
        self.line = line
        self.column = column

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.current_scope = "global"
        self.undeclared_symbols = set()

    def add_symbol(self, name, type_spec, line, column, initialize):
        key = f"{name}_{self.current_scope}"
        if key in self.symbols:
            self.symbols[key].is_redeclared = True
            return False
        self.symbols[key] = Symbol(name, type_spec, line, column, self.current_scope)
        if initialize:
            self.symbols[key].is_initialized = True
        return True

    def use_symbol(self, name):
        key = f"{name}_{self.current_scope}"
        if key in self.symbols:
            self.symbols[key].is_used = True
            return self.symbols[key]
        if self.current_scope != "global":
            key = f"{name}_global"
            if key in self.symbols:
                self.symbols[key].is_used = True
                return self.symbols[key]
        return None

    def initialize_symbol(self, name):
        symbol = self.use_symbol(name)
        if symbol:
            symbol.is_initialized = True
            return True
        return False

    def get_analysis(self):
        redeclared = []
        unused = []
        uninitialized_but_used = []

        for key, symbol in self.symbols.items():
            if not symbol.is_used:
                unused.append(symbol)
            if not symbol.is_initialized and symbol.is_used:
                uninitialized_but_used.append(symbol)
            if symbol.is_redeclared:
                redeclared.append(symbol)

        return {
            "redeclared": redeclared,
            "undeclared": self.undeclared_symbols,
            "unused": unused,
            "uninitialized_but_used": uninitialized_but_used,
            "type_counts": self.get_type_counts()
        }

    def get_type_counts(self):
        type_counts = {}
        for symbol in self.symbols.values():
            type_counts[symbol.type] = type_counts.get(symbol.type, 0) + 1
        return type_counts

# -----------------------------------------------
# Visitor Principal

class SymbolTableBuilder(Visitor_Recursive):
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.assignment_count = 0
        self.read_write_count = 0
        self.conditional_count = 0
        self.cyclic_count = 0
        self.declaration_count = 0

    def declaration(self, tree):
        type_spec = str(tree.children[0])
        name = str(tree.children[1])
        initialize = len(tree.children) > 2
        line = tree.children[1].line
        column = tree.children[1].column

        self.symbol_table.add_symbol(name, type_spec, line, column, initialize)
        self.declaration_count += 1

    def attribution(self, tree):
        name = str(tree.children[0])
        if not self.symbol_table.use_symbol(name):
            self.symbol_table.undeclared_symbols.add((name, tree.children[0].line, tree.children[0].column))
            return
        self.symbol_table.initialize_symbol(name)
        self.assignment_count += 1

    def atom(self, tree):
        token = tree.children[0]
        if isinstance(token, Token) and token.type == "IDENTIFIER":
            self.symbol_table.use_symbol(str(token))
    
    def if_stmt(self, tree):
        self.conditional_count += 1

    def while_stmt(self, tree):
        self.cyclic_count += 1

    def for_stmt(self, tree):
        self.cyclic_count += 1

    def case_stmt(self, tree):
        self.conditional_count += 1

    def repeat_stmt(self, tree):
        self.cyclic_count += 1

    def read_stmt(self, tree):
        self.read_write_count += 1

    def write_stmt(self, tree):
        self.read_write_count += 1

# -----------------------------------------------
# Novo Visitor para contar aninhamentos

class NestingCounter(Visitor):
    def __init__(self):
        self.control_stack = []
        self.aninhamentos = 0

    def push(self, tipo):
        if self.control_stack:
            self.aninhamentos += 1
        self.control_stack.append(tipo)

    def pop(self):
        if self.control_stack:
            self.control_stack.pop()

    def if_stmt(self, tree):
        self.push("if")
        for child in tree.children:
            if hasattr(child, 'data'):
                self.visit(child)
        self.pop()

    def while_stmt(self, tree):
        self.push("while")
        for child in tree.children:
            if hasattr(child, 'data'):
                self.visit(child)
        self.pop()

    def for_stmt(self, tree):
        self.push("for")
        for child in tree.children:
            if hasattr(child, 'data'):
                self.visit(child)
        self.pop()

    def repeat_stmt(self, tree):
        self.push("repeat")
        for child in tree.children:
            if hasattr(child, 'data'):
                self.visit(child)
        self.pop()

    def case_stmt(self, tree):
        self.push("case")
        for child in tree.children:
            if hasattr(child, 'data'):
                self.visit(child)
        self.pop()



# -----------------------------------------------
#Ifs para ser simplificados 

class IfsSimples(Visitor):
    def __init__(self):
        self.otimizavel = 0 

    def if_stmt(self, tree):
        if len(tree.children) < 2:
            return

        pa = tree.children[1] 
        if len(pa.children) > 1:
            return
        instrution = pa.children[0]
        if instrution.data == "instruction":
            selection = instrution.children[0]
            if selection.data == "selection":
                if_statement = selection.children[0]
                if if_statement.data == "if_stmt":
                    self.otimizavel += 1

# -----------------------------------------------
# Programa principal

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python fase2.py <ficheiro.lpi>")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, 'r') as f:
        code = f.read()

    tree = parser.parse(code)

    builder = SymbolTableBuilder()
    builder.visit(tree)

    nesting_counter = NestingCounter()
    nesting_counter.visit(tree)

    ifs_simples = IfsSimples()
    ifs_simples.visit(tree)

    generate_html_report(code, builder, nesting_counter, ifs_simples)


    print(f"tabela de simbolos:\n")
    for simb in builder.symbol_table.symbols.values():
        print(f"Nome: {simb.name}, Tipo: {simb.type}, Escopo: {simb.scope}, Inicializado: {simb.is_initialized}, Usado: {simb.is_used}")

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
    print("\n=== Instruction Counts ===")
    print(f"  Declarations: {builder.declaration_count}")
    print(f"  Assignments: {builder.assignment_count}")
    print(f"  Read/Write: {builder.read_write_count}")
    print(f"  Conditionals: {builder.conditional_count}")
    print(f"  Cyclic: {builder.cyclic_count}")
    print(f"  Aninhamentos: {nesting_counter.aninhamentos}")
    print(f"  Ifs simplificavel: {ifs_simples.otimizavel}")




from lark import Lark, Visitor, Transformer, Token
import sys
import os

# Carregar a gramática
with open('grammar.lark', 'r') as f:
    grammar = f.read()

# Criar o parser
parser = Lark(grammar, parser='earley')

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
            return False  # Símbolo já declarado
        
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
        
        return None  # Símbolo não encontrado
    
    def initialize_symbol(self, name):
        symbol = self.use_symbol(name)
        if symbol:
            symbol.is_initialized = True
            return True
        return False
    
    def enter_scope(self, scope_name):
        self.current_scope = scope_name
    
    def exit_scope(self):
        self.current_scope = "global"
    
    def get_analysis(self):

        redeclared = []
        undeclared = []
        unused = []
        uninitialized_but_used = []
        
        # ver variaveis não usadas
        
        for key, symbol in self.symbols.items():
            if not symbol.is_used:
                unused.append(symbol)
                
            if not symbol.is_initialized and symbol.is_used:
                uninitialized_but_used.append(symbol)
                
            # Verificar se a variável foi redeclarada
            if key in self.symbols:
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
        # Conta variáveis por tipo
        type_counts = {}
        for symbol in self.symbols.values():
            if symbol.type in type_counts:
                type_counts[symbol.type] += 1
            else:
                type_counts[symbol.type] = 1
        return type_counts
    
class SymbolTableBuilder(Transformer):
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.assignment_count = 0
        self.read_write_count = 0
        self.conditional_count = 0
        self.cyclic_count = 0

        
    def declaration(self, items):
        
        type_spec = str(items[0])
        print(f"Tipo: {type_spec}")
        name = str(items[1])
        initialize = True if len(items) > 2 else False
        
        line = items[1].line
        column = items[1].column
        
        self.symbol_table.add_symbol(name, type_spec, line, column, initialize)
        
        return items
    
    def attribution(self, items):
        name = str(items[0])
        value = items[1]
        
        # Verifica se a variável foi declarada
        if not self.symbol_table.use_symbol(name):
            self.symbol_table.undeclared_symbols.add((name, items[0].line, items[0].column))
           
            return items
        
        # Inicializa a variável
        self.symbol_table.initialize_symbol(name)
        
        self.assignment_count += 1 # Increment assignment count
        return items
    
    def atom(self, items):
        token = items[0]
        if isinstance(token, Token) and token.type == "IDENTIFIER":
            self.symbol_table.use_symbol(str(token))
        return items
    
    def if_stmt(self, items):
        self.conditional_count += 1
        return items
    
    def while_stmt(self, items):
        self.cyclic_count += 1
        return items
    


    # -----------------------------------------------------------------------
        
        

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python fase2.py <ficheiro.lpi>")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, 'r') as f:
        code = f.read()

    tree = parser.parse(code)
    
    builder = SymbolTableBuilder()
    builder.transform(tree)

    print(f"tabela de simbolos:\n")
    # Exibir os símbolos na tabela
    
    
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

    print(analysis)
    
    print("----------------------------------")
    
    # --- INSTRUCTION COUNTS ---
    print("\n=== Instruction Counts ===")
    print(f"  Assignments: {builder.assignment_count}")
    print(f"  Read/Write: {builder.read_write_count}")
    print(f"  Conditionals: {builder.conditional_count}")
    print(f"  Cyclic: {builder.cyclic_count}")
    # --------------------------
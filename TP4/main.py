from lark import Lark, Transformer

# Carrega a gramática do arquivo
with open('grammar.lark') as grammar_file:
    grammar = grammar_file.read()

# Cria o parser Lark
parser = Lark(grammar, start='start', parser='lalr')

class SomaIntervalosTransformer(Transformer):
    def __init__(self):
        self.c = 0  
        self.soma = 0 

    def elems(self, args):
        for arg in args:
            valor = str(arg)

            if valor == "inicio":
                self.c += 1
            elif valor == "fim":
                if self.c > 0:
                    self.c -= 1

            if self.c > 0 and valor.isdigit():
                self.soma += int(valor)

        return args

    def start(self, args):
        print(f"Soma total dos intervalos: {self.soma}")
        return self.soma

    def elem(self, arg):
        return str(arg[0])
    
# Função para processar a entrada
def parse_input(input_text):
    try:
        tree = parser.parse(input_text)

        transformer = SomaIntervalosTransformer()
        result = transformer.transform(tree)

        print("Parsing finished successfully!")
        print(f"Resultado: {result}")

    except Exception as e:
        print(f"Parsing error: {e}")

# Testes de exemplo
test_cases = [
    "LISTA 1, 2, inicio, 3, 4, fim, 7, 8 .",  # Soma: 3 + 4 = 7
    "LISTA inicio, 1, 2, fim, inicio, 3, fim, 4 .",  # Soma: 1 + 2 + 3 = 6
    "LISTA 1, 2, 3, fim, inicio, 4, 5, fim, 6 .",  # Soma: 4 + 5 = 9
    "LISTA inicio, 10, 20, fim, inicio, 30, fim .",  # Soma: 10 + 20 + 30 = 60
    "LISTA 1, 2, 3, 4, 5 .",  # Sem intervalo: soma = 0
]

# Executa os testes
for input_text in test_cases:
    print(f"\nInput: {input_text}")
    parse_input(input_text)

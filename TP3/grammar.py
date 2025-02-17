from lark import Lark, Transformer

# Grammar definition
grammar = """
start: signal interval_list "."

signal: SIGN

interval_list: interval (interval)*

interval: "[" NUMBER ";" NUMBER "]"

SIGN: "+" 
    | "-"

%import common.NUMBER
%import common.WS_INLINE
%ignore WS_INLINE
"""

class IntervalTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.sentido = 0  # 1 for +, -1 for -
        self.anterior = None  # Tracks the previous end value
        self.erro = False  # Flag to track validity
        self.intervals = []  # Store intervals

    def start(self, items):
        # Processar os intervalos normalmente
        if self.intervals:
            max_interval = max(self.intervals, key=lambda x: abs(x[1] - x[0]))
            print(f"Largest amplitude: {max_interval[0]}:{max_interval[1]}")

        return self.intervals

    def signal(self, items):
        signal_value = str(items[0])  # O próprio token já é o valor correto
        
        # Atribuindo imediatamente o sinal ao sentido
        if signal_value == "+":
            self.sentido = 1
        else:
            self.sentido = -1
       
    
    def interval(self, items):
        start = float(items[0])
        end = float(items[1])
        print(f"Interval: {start}:{end}")
        
        # Agora, self.sentido já foi atribuído corretamente na função start

        if self.sentido == 1:  # Increasing order
            if end <= start:
                print("Not valid")  # Não é válido se a ordem não for crescente
                self.erro = True
                return None  # Não adiciona o intervalo à lista
            else:
                print("Valid")

        elif self.sentido == -1:  # Decreasing order
            if end >= start:
                print("Not valid")  # Não é válido se a ordem não for decrescente
                self.erro = True
                return None  # Não adiciona o intervalo à lista
            else:
                print("Valid")

        # Se a ordem for válida, adiciona o intervalo à lista
        self.anterior = end
        self.intervals.append((start, end))
        return (start, end)
    
# Parser definition
parser = Lark(grammar, parser='lalr')

# Function to process the input text
def parse_input(input_text):
    try:
        # Parse the input
        tree = parser.parse(input_text)
        transformer = IntervalTransformer()
        result = transformer.transform(tree)

        # Handle success
        if not transformer.erro:  # Apenas imprime se não houve erro
            print("Parsing finished successfully!")
            print(result)

    except Exception as e:
        print(f"Parsing error: {e}")

# Test cases
test_cases = [
    "+ [1;2] .",                   # Valid
    "- [1;3] [2;4] [5;2] ."     # Not valid (not decreasing)
]

# Loop through the test cases
for input_text in test_cases:
    print(f"\nInput: {input_text}")
    parse_input(input_text)
    
from lark import Lark

#Load the grammar from the file
with open('grammar.lark', 'r') as file:
    grammar = file.read()

parser = Lark(grammar, parser='lalr')

# Test parsing and print tree
tree = parser.parse("+[1:5][10:20][8:10][20:50].")
print(tree.pretty())
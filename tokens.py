openingGroup = '('
closingGroup = ')'
openingIteration = '{'
closingIteration = '}'
openingOption = '['
closingOption = ']'
# or
alternative = '|'
# concat
dot = '•'
# optional
optional = '[]'
# kleene
kleene = '{}'
epsilon = 'ε'
hash = '#'

# evitara que nos saltemos o procesemos mal los caracteres.
def replace_reserved_words(r: str):
    return (r
            .replace('(', 'β')
            .replace(')', 'δ')
            .replace('{', 'ζ')
            .replace('}', 'η')
            .replace('[', 'θ')
            .replace(']', 'ω')
            .replace('|', 'φ')
            )


symbols = [replace_reserved_words(chr(i)) for i in range(1, 255)]

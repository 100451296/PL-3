from ply import lex
import sys
from progargs import read_file

# fmt: off
tokens = [
    "COMMENT", "TRUE", "FALSE", "LET", "INT_TYPE", "FLOAT_TYPE", "CHARACTER", "WHILE",
    "BOOLEAN", "FUNCTION", "RETURN", "TYPE", "IF", "ELSE", "NULL", "FLOAT", 
    "INTEGER", "SCIENTIFIC", "BINARY", "OCTAL", "HEX", "CHARACTER_VALUE",
    "EQUAL", "GRATER", "GRATER_EQUAL", "LOWER", "LOWER_EQUAL", 
    "OPEN_BRACE", "CLOSE_BRACE", "COLON", "COMMA", "STRING", "QUOTED_STRING", "PLUS", "MINUS", "MULTIPLY", "DIVISION",
    "AND", "OR", "NOT", "SEMICOLON", "ASSIGN", "OPEN_PAREN", "CLOSE_PAREN", "DOT", "OPEN_SQUARE", "CLOSE_SQUARE"
]
# fmt: on


# Regla de expresiones regulares para manejar comentarios
def t_COMMENT(t):
    r"(//.*\n)|(/\*([^*]|(\*+[^*/]))*\*+/)"
    pass

# Strings
def t_STRING(t):
    r"(?!tr\b|fl\b|null\b|type\b|let\b|int\b|float\b|character\b|while\b|boolean\b|function\b|return\b|if\b|else\b|null\b)[_a-zA-Z][_a-zA-Z0-9]*\b"
    return t

def t_QUOTED_STRING(t):
    r'"([^"\n]*)?"'
    t.value = t.value[1:-1]
    return t

# Asignaciones
def t_SEMICOLON(t):
    r';'
    return t

def t_OPEN_PAREN(t):
    r'\('
    return t

def t_CLOSE_PAREN(t):
    r'\)'
    return t

# Operadores
def t_PLUS(t):
    r"\+"
    return t

def t_MINUS(t):
    r"\-"
    return t

def t_MULTIPLY(t):
    r"\*"
    return t

def t_DIVISION(t):
    r"/"
    return t

# Operadores logicos
def t_AND(t):
    r'&&'
    return t

def t_OR(t):
    r'\|\|'
    return t

def t_NOT(t):
    r'!'
    return t

# Palabras reservadas
def t_TRUE(t):
    r"\btr\b"
    t.value = True
    return t

def t_FALSE(t):
    r"\bfl\b"
    t.value = False
    return t

def t_LET(t):
    r"\blet\b"
    return t

def t_INT_TYPE(t):
    r"\bint\b"
    return t

def t_FLOAT_TYPE(t):
    r"\bfloat\b"
    return t

def t_CHARACTER(t):
    r"\bcharacter\b"
    return t

def t_WHILE(t):
    r"\bwhile\b"
    return t

def t_BOOLEAN(t):
    r"\bboolean\b"
    return t

def t_FUNCTION(t):
    r"\bfunction\b"
    return t

def t_RETURN(t):
    r"\breturn\b"
    return t

def t_TYPE(t):
    r"\btype\b"
    return t

def t_IF(t):
    r"\bif\b"
    return t

def t_ELSE(t):
    r"\belse\b"
    return t

def t_NULL(t):
    r"\bnull\b"
    t.value = None
    return t

# Números
def t_SCIENTIFIC(t):
    r"(\d+(\.\d*)?|\.\d+)[eE][+-]?\d+"
    t.value = float(t.value)
    return t

def t_BINARY(t):
    r"0[bB][01]+"
    t.value = int(t.value, 2)
    return t

def t_OCTAL(t):
    r"0[0-7]+"
    t.value = int(t.value, 8)
    return t

def t_HEX(t):
    r"0[xX][0-9A-Fa-f]+"
    t.value = int(t.value, 16)
    return t

def t_FLOAT(t):
    r"-?(\d*\.\d+)|(\d+\.\d*)"
    t.value = float(t.value)
    return t

def t_INTEGER(t):
    r"-?\d+"
    t.value = int(t.value)
    return t

# Objetos
def t_DOT(t):
    r'\.'
    return t

def t_OPEN_SQUARE(t):
    r'\['
    return t

def t_CLOSE_SQUARE(t):
    r'\]'
    return t

# Caracter entrecomillado
def t_CHARACTER_VALUE(t):
    r"''|'([\x00-\x7F\x80-\xFF])'"
    t.value = t.value[1:-1]  # Remover las comillas simples
    return t

# AJSON
def t_EQUAL(t):
    r"=="
    return t

def t_GRATER_EQUAL(t):
    r">="
    return t

def t_LOWER_EQUAL(t):
    r"<="
    return t

def t_ASSIGN(t):
    r'='
    return t

def t_GRATER(t):
    r">"
    return t

def t_LOWER(t):
    r"<"
    return t

def t_OPEN_BRACE(t):
    r"{"
    return t

def t_CLOSE_BRACE(t):
    r"}"
    return t

def t_COLON(t):
    r":"
    return t

def t_COMMA(t):
    r","
    return t

# Ignorar espacios, tabulaciones y saltos de línea
t_ignore = " \t\n"
t_ignore_COMMENT = r'COMMENT'

# Regla para manejar errores
def t_error(t):
    print("Carácter ilegal:", t.value[0])
    t.lexer.skip(1)


scanner = lex.lex()

# pruebas
if __name__ == "__main__":
    # coge el archivo pasado por linea de comando o el string si no se le pasa nada
    data = read_file(sys.argv[1]) if len(sys.argv) > 1 else "//Comentario\n"
    scanner.input(data)
    while True:
        tok = scanner.token()
        if not tok:
            break  # No hay más tokens
        print(tok)

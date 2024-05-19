from progargs import read_file
import sys
from ajs_lexer import tokens
import ply.yacc as yacc

# Define the precedence to help resolve conflicts
precedence = (
    ('right', 'NOT'),  # High precedence for the NOT operator
    ('left', 'OR'),    # Logical OR
    ('left', 'AND'),   # Logical AND
    ('nonassoc', 'EQUAL', 'GRATER', 'GRATER_EQUAL', 'LOWER', 'LOWER_EQUAL'),  # Comparison operators
    ('left', 'PLUS', 'MINUS'),  # Arithmetic
    ('left', 'MULTIPLY', 'DIVISION')  # Multiplication and division
)

# Variable table
variable_table = {}
# Object table
object_table = {}

def p_program(p):
    "program : statementList"
    p[0] = p[1]

def p_statementList(p):
    """
    statementList : statement
                  | statementList statement
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    """
    statement : instruction
              | COMMENT
              | conditional
              | loop
              | function_definition
    """
    p[0] = p[1]

def p_conditional(p):
    """
    conditional : IF OPEN_PAREN expression CLOSE_PAREN OPEN_BRACE statementList CLOSE_BRACE
                | IF OPEN_PAREN expression CLOSE_PAREN OPEN_BRACE statementList CLOSE_BRACE ELSE OPEN_BRACE statementList CLOSE_BRACE
    """
    if len(p) == 8:
        p[0] = ("if", p[3], p[6])
    else:
        p[0] = ("if-else", p[3], p[6], p[10])

def p_loop(p):
    "loop : WHILE OPEN_PAREN expression CLOSE_PAREN OPEN_BRACE statementList CLOSE_BRACE"
    p[0] = ("while", p[3], p[6])

def p_function_definition(p):
    """
    function_definition : FUNCTION STRING OPEN_PAREN args_list CLOSE_PAREN COLON type OPEN_BRACE statementList RETURN value SEMICOLON CLOSE_BRACE
    """
    p[0] = ("function", p[2], p[4], p[7], p[9], p[11])

def p_args_list(p):
    """
    args_list : STRING COLON type
              | STRING COLON type COMMA args_list
    """
    if len(p) == 4:
        p[0] = [(p[1], p[3])]
    else:
        p[0] = [(p[1], p[3])] + p[5]

def p_instruction(p):
    """
    instruction : declaration SEMICOLON
                | asignation SEMICOLON
                | property_asignation SEMICOLON
    """
    p[0] = p[1]

def p_property_asignation(p):
    "property_asignation : STRING properties ASSIGN value"
    current = variable_table[p[1]]
    for key in p[2]:
        previous = current
        current = current[key]
    previous[key] = p[4]
    p[0] = ("property_asignation", p[1], p[2], p[4])


def p_declaration(p):
    """
    declaration : LET declaration_identifier
                | LET asignation
                | TYPE STRING ASSIGN type_object
    """
    if len(p) == 3:
        p[0] = ("simple_declaration", p[2])
    else:
        object_table[p[2]] = p[4]
        p[0] = ("type_declaration", p[2], p[4])

def p_declaration_identifier(p):
    """
    declaration_identifier : STRING
                           | STRING COMMA declaration_identifier
                           | STRING COLON STRING
                           | STRING COLON STRING COMMA declaration_identifier
    """

    if len(p) == 2:
        variable_table[p[1]] = None
        p[0] = p[1]
    elif len(p) == 4 and p[2] == ":":
        variable_table[p[1]] = object_table[p[3]]
        p[0] = (p[1], p[3])
    elif len(p) == 4:
        if isinstance(p[3], list):
            variable_table[p[1]] = None
            p[0] = [p[1]] + p[3]
        else:
            variable_table[p[1]] = None
            variable_table[p[3]] = None
            p[0] = [p[1], p[3]]
    else:
        variable_table[p[1]] = object_table[p[3]]
        p[0] = (p[1], p[5])
        

def p_identifiers(p):
    """
    identifiers : STRING
                | STRING COMMA identifiers
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_asignation(p):
    """
    asignation : identifiers ASSIGN value
               | object_identifiers ASSIGN object
    """
    if isinstance(p[1], list):
        for identifier in p[1]:
            variable_table[identifier] = p[3]
    else:
        variable_table[p[1]] = p[3]
    p[0] = ("asignation", p[1], p[3])

def p_object_identifiers(p):
    """
    object_identifiers : STRING COLON STRING
                       | STRING COLON STRING COMMA object_identifiers
    """
    if len(p) == 4:
        p[0] = [(p[1], p[3])]
    else:
        p[0] = [(p[1], p[3])] + p[5]

def p_object(p):
    """
    object : OPEN_BRACE pairs CLOSE_BRACE
           | OPEN_BRACE CLOSE_BRACE
    """
    if len(p) == 3:
        p[0] = {}
    else:
        p[0] = dict(p[2])

def p_pairs(p):
    """
    pairs : pair COMMA pairs
          | pair
          | pair COMMA
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_pair(p):
    "pair : key COLON value"
    p[0] = (p[1], p[3])

def p_type_object(p):
    """
    type_object : OPEN_BRACE type_pairs CLOSE_BRACE
                | OPEN_BRACE CLOSE_BRACE
    """
    if len(p) == 3:
        p[0] = {}
    else:
        p[0] = dict(p[2])

def p_type_pairs(p):
    """
    type_pairs : type_pair COMMA type_pairs
               | type_pair
               | type_pair COMMA
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_type_pair(p):
    "type_pair : key COLON type"
    if p[3] == "float":
        p[0] = (p[1], 0.0)
    elif p[3] == "int":
        p[0] = (p[1], 0)
    elif p[3] == "character":
        p[0] = (p[1], "")
    elif p[3] == "boolean":
        p[0] = (p[1], True)

def p_key(p):
    """
    key : QUOTED_STRING
        | STRING
    """
    p[0] = p[1]

def p_type(p):
    """
    type : CHARACTER
          | INT_TYPE
          | FLOAT_TYPE
          | BOOLEAN
    """
    p[0] = p[1]

def p_value(p):
    """
    value : CHARACTER_VALUE
          | NULL
          | expression
          | object
    """
    p[0] = p[1]

def p_expression_binop(p):
    """expression : expression PLUS expression
    | expression MINUS expression
    | expression MULTIPLY expression
    | expression DIVISION expression
    | expression GRATER expression
    | expression LOWER expression
    | expression GRATER_EQUAL expression
    | expression LOWER_EQUAL expression
    | expression EQUAL expression
    | expression AND expression
    | expression OR expression"""

    if p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        p[0] = p[1] / p[3]
    elif p[2] == '>':
        p[0] = p[1] > p[3]
    elif p[2] == '<':
        p[0] = p[1] < p[3]
    elif p[2] == '>=':
        p[0] = p[1] >= p[3]
    elif p[2] == '<=':
        p[0] = p[1] <= p[3]
    elif p[2] == '==':
        p[0] = p[1] == p[3]
    elif p[2] == 'and':
        p[0] = p[1] and p[3]
    elif p[2] == 'or':
        p[0] = p[1] or p[3]

def p_expression_not(p):
    "expression : NOT expression"
    p[0] = not p[2]

def p_expression_group(p):
    "expression : OPEN_PAREN expression CLOSE_PAREN"
    p[0] = p[2]

def p_expression_number(p):
    """
    expression : INTEGER
                | FLOAT
                | HEX
                | SCIENTIFIC
                | OCTAL
                | BINARY
    """
    p[0] = p[1]

def p_expression_boolean(p):
    """expression : TRUE
    | FALSE"""
    p[0] = p[1]

def p_expression_id(p):
    """
    expression : STRING
    """
    p[0] = variable_table[p[1]] if p[1] in variable_table.keys() else 0
    if p[0] is None:
        print("Key error") 

def p_expression_object(p):
    """
    expression : object_property
    """
    p[0] = p[1]

def p_object_property(p):
    "object_property : STRING properties"
    current = variable_table[p[1]]
    for key in p[2]:
        current = current[key]
    p[0] = current

def p_properties(p):
    """
    properties : dot_property
               | square_property
               | dot_property properties
               | square_property properties
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_dot_property(p):
    "dot_property : DOT STRING"
    p[0] = p[2]

def p_square_property(p):
    "square_property : OPEN_SQUARE QUOTED_STRING CLOSE_SQUARE"
    p[0] = ("square_property", p[2])

def p_error(p):
    print("Error de sintaxis en la entrada!", p)

# Building the parser
yacc.errorlog = yacc.NullLogger()  # Disable YACC error messages to standard output
parser = yacc.yacc()


def parse_data(data):
    parsed_data = parser.parse(data)
    print(parsed_data)
    print("Tabla de variables:", variable_table)
    print("Tabla de objetos:", object_table)

# Test cases
if __name__ == "__main__":
    try:
        data = read_file(sys.argv[1]) if len(sys.argv) > 1 else "//Comentario\n"
        parsed_data = parser.parse(data)
        print(parsed_data)
        print("Tabla de variables:", variable_table)
        print("Tabla de objetos:", object_table)
    except Exception as e:
        print("Error al analizar:", str(e))
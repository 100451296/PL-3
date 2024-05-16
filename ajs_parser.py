from progargs import read_file
import sys
from ajs_lexer import tokens
import ply.yacc as yacc

precedence = (
    ('left', 'PLUS', 'MINUS'),   # Suma y resta tienen la misma precedencia y son de asociatividad izquierda
    ('left', 'MULTIPLY', 'DIVISION')  # Multiplicación y división también tienen la misma precedencia y son de asociatividad izquierda
)


def p_program(p):
    """
    program : statementList
    """
    pass

def p_statementList(p):
    """
    statementList : statement 
                  | statementList statement
    """
    pass

def p_statement(p):
    """
    statement : instruction
              | COMMENT
              | conditional
              | loop
              | function_definition
    """
    pass

def p_conditional(p):
    """
    conditional : IF OPEN_PAREN expression CLOSE_PAREN OPEN_BRACE statementList CLOSE_BRACE
                | IF OPEN_PAREN expression CLOSE_PAREN OPEN_BRACE statementList CLOSE_BRACE ELSE OPEN_BRACE statementList CLOSE_BRACE
    """
    pass

def p_loop(p):
    """
    loop : WHILE OPEN_PAREN expression CLOSE_PAREN OPEN_BRACE statementList CLOSE_BRACE
    """
    pass

def p_function_definition(p):
    """
    function_definition : FUNCTION STRING OPEN_PAREN args_list CLOSE_PAREN COLON type OPEN_BRACE statementList RETURN value SEMICOLON CLOSE_BRACE
    """

def p_args_list(p):
    """
    args_list : STRING COLON type
              | STRING COLON type COMMA args_list
    """
    pass

def p_instruction(p):
    """
    instruction : declaration SEMICOLON
                | asignation SEMICOLON
                | property_asignation SEMICOLON
    """
    pass


def p_property_asignation(p):
    """
    property_asignation : STRING properties ASSIGN value
    """
    pass

def p_declaration(p):
    """
    declaration : LET declaration_identifier
                | LET asignation
                | TYPE STRING ASSIGN type_object
    """
    pass

def p_declaration_identifier(p):
    """
    declaration_identifier : STRING 
                           | STRING COMMA declaration_identifier
                           | STRING COLON STRING
                           | STRING COLON STRING COMMA declaration_identifier
    """
    pass

def p_identifiers(p):
    """
    identifiers : STRING 
                | STRING COMMA identifiers
    """
    pass

def p_asignation(p):
    """
    asignation : identifiers ASSIGN value
               | object_identifiers ASSIGN object
    """
    pass

def p_object_identifiers(p):
    """
    object_identifiers : STRING COLON STRING
                       | STRING COLON STRING COMMA object_identifiers
    """
    pass

# Gramatica del AJSON
def p_object(p):
    """
    object : OPEN_BRACE pairs CLOSE_BRACE
           | OPEN_BRACE CLOSE_BRACE
    """
    pass
def p_pairs(p):
    """
    pairs : pair COMMA pairs
          | pair
          | pair COMMA
    """
    pass
def p_pair(p):
    """
    pair : key COLON value
    """
    pass

# Objeto de tipos
def p_type_object(p):
    """
    type_object : OPEN_BRACE type_pairs CLOSE_BRACE
           | OPEN_BRACE CLOSE_BRACE
    """
    pass
def p_type_pairs(p):
    """
    type_pairs : type_pair COMMA type_pairs
                | type_pair
                | type_pair COMMA
    """
    pass
def p_type_pair(p):
    """
    type_pair : key COLON type
    """
    pass

def p_key(p):
    """
    key : QUOTED_STRING
        | STRING
    """
    pass

def p_type(p):
    """
    type : CHARACTER
        | INT_TYPE
        | FLOAT_TYPE
        | BOOLEAN
    """
    pass

def p_properties(p):
    """
    properties : dot_property
               | square_property
               | dot_property properties
               | square_property properties
    """
    pass

def p_dot_property(p):
    """
    dot_property : DOT STRING
    """
    pass

def p_square_property(p):
    """
    square_property : OPEN_SQUARE QUOTED_STRING CLOSE_SQUARE
    """
    pass

def p_value(p):
    """
    value : CHARACTER_VALUE
          | NULL
          | TRUE
          | FALSE
          | expression_arith
          | expression_comp
          | NOT OPEN_PAREN expression_comp CLOSE_PAREN
          | expression_logic
          | NOT logic_element
          | object
    """
    pass

def p_expression(p):
    """
    expression : expression_logic
               | logic_element
    """
    pass

def p_expression_logic_and(p):
    """
    expression_logic : logic_term AND logic_term
    """
    pass

def p_expression_logic_or(p):
    """
    expression_logic : logic_term OR logic_term
    """
    pass

def p_logic_term(p):
    """
    logic_term : logic_element
               | NOT logic_element
               | OPEN_PAREN expression_logic CLOSE_PAREN
    """
    pass

def p_logic_element(p):
    """
    logic_element : TRUE
                  | FALSE
                  | expression_comp
                  | NOT OPEN_PAREN expression_comp CLOSE_PAREN
    """
    pass

def p_expression_comp(p):
    """
    expression_comp : comp_element comp_operator comp_element
    """
    pass

def p_comp_operator(p):
    """
    comp_operator : EQUAL
                  | GRATER
                  | GRATER_EQUAL
                  | LOWER
                  | LOWER_EQUAL

    """
    pass

# Definición del analizador sintáctico
def p_expression_plus(p):
    """
    expression_arith : term PLUS expression_arith
    """
    pass  # p[0] = p[1] + p[3]

def p_expression_minus(p):
    """
    expression_arith : term MINUS expression_arith
    """
    pass  # p[0] = p[1] - p[3]

def p_expression_term(p):
    """
    expression_arith : term
    """
    pass  # p[0] = p[1]

def p_term_times(p):
    """
    term : term MULTIPLY factor
    """
    pass  # p[0] = p[1] * p[3]

def p_term_divide(p):
    """
    term : term DIVISION factor
    """
    pass  # p[0] = p[1] / p[3]

def p_term_factor(p):
    """
    term : factor
    """
    pass  # p[0] = p[1]F

def p_factor_number(p):
    """
    factor : element"""
    pass  # p[0] = int(p[1])

def p_object_property(p):
    """
    object_property : STRING properties
    """
    pass

def p_element(p):
    """
    element : INTEGER
            | FLOAT
            | HEX
            | SCIENTIFIC
            | OCTAL
            | BINARY
            | STRING
            | OPEN_PAREN expression_arith CLOSE_PAREN
            | object_property
    """
    pass

def p_comp_element(p):
    """
    comp_element : expression_arith
    """
    pass


def p_error(p):
    print("Error de sintaxis en la entrada! ", p)

# Construcción del analizador sintáctico
#parser = yacc.yacc(debug=True, debuglog=yacc.PlyLogger(sys.stderr))
yacc.errorlog = yacc.NullLogger()
parser = yacc.yacc()

# pruebas
if __name__ == "__main__":
    try:
        # coge el archivo pasado por linea de comando o el string si no se le pasa nada
        data = read_file(sys.argv[1]) if len(sys.argv) > 1 else "//Comentario\n"
        parsed_data = parser.parse(data)
        print(parsed_data)
    except Exception as e:
        print("Error al analizar:", str(e))

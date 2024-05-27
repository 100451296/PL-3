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
object_table = {"int" : None, "float" : None, "character" : None, "boolean" : None}

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
    elif len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    """
    statement : instruction
              | conditional
              | loop
              | function_definition
    """
    if p[1][0] == "function":
        procesar_function_definition(p[1])
    elif p[1][0] == "if":
        procesar_conditional(p[1])
    elif p[1][0] == "if-else":
        procesar_conditional_else(p[1])
    elif p[1][0] == "while":
        procesar_loop(p[1])
    elif p[1][0] == "asignation_declaration":
        procesar_asignation_declaration(p[1][1])
    elif p[1][0] == "simple_declaration":
        procesar_simple_declaration(p[1][1])
    elif p[1][0] == "type_declaration":
        procesar_type_declaration(p[1][1], p[1][2])
    elif p[1][0] == "asignation":
        procesar_asignation(p[1])
    elif p[1][0] == "property_asignation":
        procesar_property_asignation(p[1])
    elif p[1][0] == "call":
        procesar_function_call(p[1][1], p[1][2])
    p[0] = p[1]

def procesar_statement(statement: tuple, local):
    pass

def procesar_function_definition(p):
    pass

def procesar_conditional(p):
    pass

def procesar_conditional_else(p):
    pass

def procesar_loop(p):
    pass

def procesar_asignation_declaration(p):    
    for id in p[1]:
        if isinstance(id, tuple): # Caso de objeto
            object_id, type, value = id[0], id[1], p[2]
            if object_id in variable_table.keys():
                raise Exception(f"Redefinition {object_id}")   
            if not type in object_table.keys():
                raise TypeError(f"type {object_id} not defined")
            # PENDIENTE: comprobar que el valor concuerde con el tipo
            variable_table[object_id] = resolve_value(value)
            continue
        if id in variable_table.keys():
            raise Exception(f"Redefinition {id}")  
        variable_table[id] = resolve_value(p[2])
        # PENDIENTE: Hacer tratamiento de valor para propiedades de objetos

def compare_dictionaries(dict1, dict2):
    # Verificar si tienen las mismas claves
    if set(dict1.keys()) != set(dict2.keys()):
        return False

    # Verificar los tipos de los valores asociados a las claves
    for key in dict1.keys():
        if key in dict2:
            value1 = dict1[key]
            value2 = dict2[key]
            if type(value1) != type(value2):
                return False

    return True

def resolve_value(p):
    if isinstance(p, dict):
        aux = dict()
        for key in p.keys():
            aux[key] = resolve_value(p[key])
        return aux
    elif p[0] == "binop":
        left, operator, right = p[1], p[2], p[3]
        
        if left[0] == "binop" and right[0] == "binop":
            left = ("num", resolve_value(left))
            right = ("num", resolve_value(right))
            return resolve_binop((None, left, operator, right))
        
        elif left[0] == "binop" and right[0] != "binop":
            left = ("num", resolve_value(left))
            return resolve_binop((None, left, operator, right))
        
        elif left[0] != "binop" and right[0] == "binop":
            right = ("num", resolve_value(right))
            return resolve_binop((None, left, operator, right))
        
        elif left[0] != "binop" and right[0] != "binop":
            return resolve_binop(p)

        return resolve_binop(p)
    elif p[0] == "id":
        id = p[1]
        if not id in variable_table.keys():
            raise Exception(f"Variable not declared {id}")
        return variable_table[id]
    elif p[0] == "not":
        return not resolve_value(p[1])
    elif p[0] == "object_property":
        id, keys = p[1][0], p[1][1]
        current = variable_table[id]
        for key in keys:
            current = current[key]
        return current
    else:
        return p[1]


def resolve_binop(p):
    left, operator, right = resolve_value(p[1]), p[2], resolve_value(p[3])

    try:
        # Convert types if necessary
        converted_left, converted_right = convert_if_possible(left, right)
        result = None

        if operator == '+':
            result = converted_left + converted_right
        elif operator == '-':
            result = converted_left - converted_right
        elif operator == '*':
            result = converted_left * converted_right
        elif operator == '/':
            result = converted_left / converted_right
        elif operator in ['>', '<', '>=', '<=']:
            result = eval(f"{converted_left} {operator} {converted_right}")
        elif operator == '==':
            result = converted_left == converted_right
        elif operator == '&&':
                if infer_type(converted_left) == 'boolean' and infer_type(converted_right) == 'boolean':
                    result = converted_left and converted_right
                else:
                    raise TypeError(f"AND operation requires boolean operands, got {infer_type(converted_left)} and {infer_type(converted_right)}")
        elif operator == '||':
            if infer_type(converted_left) == 'boolean' and infer_type(converted_right) == 'boolean':
                result = converted_left or converted_right
            else:
                raise TypeError(f"OR operation requires boolean operands, got {infer_type(converted_left)} and {infer_type(converted_right)}")
    except TypeError as e:
        print(f"Type error: {e}")
        result = None
    finally:
        return result
    
def procesar_simple_declaration(p):    
    for id in p:
        if isinstance(id, tuple):
            if not id[1] in object_table.keys():
                raise TypeError(f"type {id[1]} not defined")
            variable_table[id[0]] = object_table[id[1]]
            continue
        if id in variable_table.keys():
            raise Exception(f"Redefinition {id}")    
        variable_table[id] = None

def procesar_type_declaration(p1, p2):
    object_table[p1] = p2

def procesar_asignation(p):
    for id in p[1]:
        if isinstance(p[2], dict): # Caso de objeto
            object_id, value = id, p[2]
            variable_table[object_id] = resolve_value(p[2])
            continue
        variable_table[id] = resolve_value(p[2])
        # PENDIENTE: Hacer tratamiento de valor para propiedades de objetos

def procesar_property_asignation(p):
    id, keys, value = p[1], p[2], p[3]
    if not id in variable_table.keys():
        raise Exception(f"variable not declared {id}")
    current = variable_table[id]
    for key in keys:
        previous = current
        current = current[key]
    previous[key] = resolve_value(value)

def procesar_function_call(p1, p2):
    pass

def procesar_expresion(expresion, tabla_simbolos):
    pass

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

def p_function_call(p):
    """
    function_call : STRING OPEN_PAREN args_call CLOSE_PAREN
    """
    p[0] = ("call", p[1], p[3])

def p_args_call(p):
    """
    args_call : expression
              | expression COMMA args_call
              |
    """
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[1]] + p[3]

def p_args_list(p):
    """
    args_list : STRING COLON type
              | STRING COLON type COMMA args_list
              |
    """
    if len(p) == 4:
        p[0] = [(p[1], p[3])]
    elif len(p) == 1:
        p[0] = []
    else:
        p[0] = [(p[1], p[3])] + p[5]

def p_instruction(p):
    """
    instruction : declaration SEMICOLON
                | asignation SEMICOLON
                | property_asignation SEMICOLON
                | function_call SEMICOLON
    """
    p[0] = p[1]

def p_property_asignation(p):
    "property_asignation : STRING properties ASSIGN value"
    p[0] = ("property_asignation", p[1], p[2], p[4])


def p_declaration(p):
    """
    declaration : LET declaration_identifier
                | LET asignation
                | TYPE STRING ASSIGN type_object
    """
    try:
        if isinstance(p[2], tuple) and p[2][0] == "asignation":
            p[0] = ("asignation_declaration", p[2])
        elif len(p) == 3:
            p[0] = ("simple_declaration", p[2])
        else:
            p[0] = ("type_declaration", p[2], p[4])
    except Exception as e:
        print(e)

def p_declaration_identifier(p):
    """
    declaration_identifier : STRING
                           | STRING COMMA declaration_identifier
                           | STRING COLON STRING
                           | STRING COLON STRING COMMA declaration_identifier
    """

    # TRATAMIENTO ERRORES PENDIENTE
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 4 and p[2] == ":":
        p[0] = [(p[1], p[3])]
    elif len(p) == 4:
        if isinstance(p[3], list):
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1], p[3]]
    else:
        p[0] = [(p[1], p[3])] + p[5]
        

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
    pairs : pair
          | pair COMMA
          | pair COMMA pairs  
    """
    if len(p) == 2 or len(p) == 3:
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
    if len(p) == 2 or len(p) == 3:
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
    else:
        p[0] = (p[1], p[3])

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
          | type_object
          | STRING
    """
    if not isinstance(p[1], dict):
        if not p[1] in object_table.keys():
            print("type error")
    p[0] = p[1]

def p_value(p):
    """
    value : NULL
          | expression
          | object
    """
    p[0] = p[1]

def infer_type(value):
    if isinstance(value, bool):
        return 'boolean'
    elif isinstance(value, int):
        return 'int'
    elif isinstance(value, float):
        return 'float'
    elif isinstance(value, str) and len(value) == 1:  # Assuming a single character is a 'character'
        return 'character'
   
    # Expand this function as needed

def convert_if_possible(left, right):
    left_type = infer_type(left)
    right_type = infer_type(right)
    if left_type == right_type:
        return left, right
    elif left_type == 'character' and right_type == 'int':
        return ord(left), right
    elif left_type == 'int' and right_type == 'float':
        return float(left), right
    elif right_type == 'character' and left_type == 'int':
        return left, ord(right)
    elif right_type == 'int' and left_type == 'float':
        return left, float(right)
    else:
        raise TypeError(f"Cannot operate between types {left_type} and {right_type}")

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
    p[0] = ("binop", p[1], p[2], p[3])

def p_expression_not(p):
    "expression : NOT expression"
    p[0] = ("not", p[2])

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
    p[0] = ('int', p[1])

def p_expression_character(p):
    """
    expression : CHARACTER_VALUE
    """
    p[0] = ('character', p[1])

def p_expression_boolean(p):
    """
    expression : TRUE
               | FALSE
    """
    p[0] = ('boolean', p[1])

def p_expression_id(p):
    """
    expression : STRING
    """
    p[0] = ('id', p[1])

def p_expression_object(p):
    """
    expression : object_property
    """
    p[0] = ('object_property', p[1])

def p_expression_call(p):
    """
    expression : function_call
    """
    p[0] = ('function_call', p[1])

def p_object_property(p):
    "object_property : STRING properties"
    p[0] = (p[1], p[2])

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
    p[0] = p[2]

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
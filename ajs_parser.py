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

FUNCTION_PROPERTIES = ["args", "return_type", "statements", "return_value"]

# Variable table
variable_table = {}
# Object table
object_table = {"int" : None, "float" : None, "character" : None, "boolean" : None}

def p_program(p):
    "program : statementList"
    procesar_stamentList(p[1])
    p[0] = p[1]

def procesar_stamentList(list):
    for statement in list:
        if statement[0] == "function":
            procesar_function_definition(statement)
        elif statement[0] == "if": # 
            procesar_conditional(statement) 
        elif statement[0] == "if-else": # 
            procesar_conditional_else(statement) 
        elif statement[0] == "while": # 
            procesar_loop(statement) 
        elif statement[0] == "asignation_declaration": # 
            procesar_asignation_declaration(statement[1]) 
        elif statement[0] == "simple_declaration": # 
            procesar_simple_declaration(statement[1]) 
        elif statement[0] == "type_declaration": # 
            procesar_type_declaration(statement[1], statement[2]) 
        elif statement[0] == "asignation": # 
            procesar_asignation(statement) 
        elif statement[0] == "property_asignation":  # 
            procesar_property_asignation(statement) 
        elif statement[0] == "call":
            procesar_function_call(statement)

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
    p[0] = p[1]

def procesar_function_definition(p):
    name = p[1]
    variable_table[name] = dict()
    for i, property in enumerate(FUNCTION_PROPERTIES):
        if property == "args":
            for arg in p[i+2]:
                if arg[1] == name:
                    raise ValueError(f"arg {p[i+2]} can't have the same name as the function {name}")
        variable_table[name][property] = p[i+2]

def procesar_conditional(p):
    condition, statementList = p[1], p[2]
    resolve = resolve_value(condition)
    condition = resolve if isinstance(resolve, bool) or resolve in [0, 1] else None
    if condition is None:
        raise TypeError("Condition must be bool or [0, 1]", p)
    if condition:
        procesar_stamentList(statementList)

def procesar_conditional_else(p):
    condition, statementListTrue, statementListFalse = p[1], p[2], p[3]
    resolve = resolve_value(condition)
    condition = resolve if isinstance(resolve, bool) or resolve in [0, 1] else None
    if condition is None:
        raise TypeError("Condition must be bool or [0, 1]", p, resolve_value(p[1]))
    if condition:
        procesar_stamentList(statementListTrue)
    else:
        procesar_stamentList(statementListFalse)
        
def procesar_loop(p):
    condition, statementList = p[1], p[2]
    resolve = resolve_value(condition)
    
    # Tratamiento de error
    resolve = resolve if isinstance(resolve, bool) or resolve in [0, 1] else None
    if resolve is None:
        raise TypeError("Condition must be bool or [0, 1]", p)
    
    while resolve:
        procesar_stamentList(statementList)
        resolve = resolve_value(condition)
        resolve = resolve if isinstance(resolve, bool) or resolve in [0, 1] else None
        if resolve is None:
            raise TypeError("Condition must be bool or [0, 1]", p)

def procesar_asignation_declaration(p):    
    for id in p[1]:
        if isinstance(id, tuple): # Caso de objeto
            object_id, type, value = id[0], id[1], p[2]
            if object_id in variable_table.keys():
                raise Exception(f"Redefinition {object_id}")   
            if not type in object_table.keys():
                raise TypeError(f"type {object_id} not defined")
            aux_dict = infer_value_type(value)
            expected_dict = object_table[type]
            differences = compare_dictionaries(expected_dict, aux_dict)
            if differences:
                diff_messages = [f"{path} expected {exp} got {act}" for path, (exp, act) in differences.items()]
                diff_message = ", ".join(diff_messages)
                raise TypeError(f"Variable {object_id} of type {type} in property {diff_message}")
            
            variable_table[object_id] = resolve_value(value)
            continue
        if id in variable_table.keys():
            raise Exception(f"Redefinition {id}")  
        variable_table[id] = resolve_value(p[2])

def infer_value_type(dict_param):
    aux_dict = {}
    for key, value in dict_param.items():
        if isinstance(value, tuple):
            aux_dict[key] = value[0]
        if isinstance(value, dict):
            recursive_aux = infer_value_type(value)
            aux_dict[key] = recursive_aux
    return aux_dict

def compare_dictionaries(expected_dict, actual_dict, path=""):
    differences = {}
    for key in expected_dict.keys():
        expected_type = expected_dict[key]
        actual_type = actual_dict.get(key, 'missing')
        
        current_path = f"{path}.{key}" if path else key
        
        if isinstance(expected_type, dict) and isinstance(actual_type, dict):
            nested_differences = compare_dictionaries(expected_type, actual_type, current_path)
            differences.update(nested_differences)
        elif expected_type != actual_type:
            differences[current_path] = (expected_type, actual_type)
    
    return differences

def resolve_value(p):
    """
    Esta función resuelve recursivamente cualquier expresión
    """
    # Caso base objeto
    if isinstance(p, dict):
        aux = dict()
        for key in p.keys():
            aux[key] = resolve_value(p[key])
        return aux
    elif p is None:
        return p
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
        
        # Caso base: expresion
        elif left[0] != "binop" and right[0] != "binop":
            return resolve_binop(p)

        return resolve_binop(p)
    # Caso base: variable
    elif p[0] == "id":
        id = p[1]
        if not id in variable_table.keys():
            raise Exception(f"Variable not declared {id}")
        return variable_table[id]
    elif p[0] == "not":
        return not resolve_value(p[1])
    # Caso base: propiedad de un objeto
    elif p[0] == "object_property":
        id, keys = p[1][0], p[1][1]
        if not id in variable_table.keys():
            raise Exception(f"Variable not declared {id}")
        current = variable_table[id]
        for key in keys:
            if not key in current.keys():
                raise Exception(f"Property error {current}.{id}")
            current = current[key]
        return current
    # Caso base: llamada  a funcion
    elif p[0] == "function_call":
        
        return procesar_function_call(p[1])
    else:
        return p[1]


def resolve_binop(p):
    """
    Esta función resuelve una expresión de tipo binop (value1 op value2)
    """
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
        return result
    except TypeError as e:
        raise TypeError(e)

    
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

def procesar_function_call(p):
    global variable_table
    name, args = p[1], p[2]

    # Tratamiento de error
    if not name in variable_table.keys() or not isinstance(variable_table[name], dict):
        raise TypeError(f"Funtion {name} not declared")
    if not list(variable_table[name].keys()) == FUNCTION_PROPERTIES:
        raise TypeError(f"Funtion {name} not declared")
    
    original_variable_table = variable_table.copy()
    function_type = variable_table[name]["return_type"]
    
    for expression, arg in zip(args, variable_table[name]["args"]):
        resolve_expression = resolve_value(expression)
        expression_type  = str(type(resolve_expression)).split("'")[1]
        # Tratamiento de error
        if arg[0] != expression_type and not (arg[0] == "character" and expression_type == "str"):
            raise TypeError(f"Arg {arg[1]} must be {arg[0]} on {name} function")
        variable_table[arg[1]] = resolve_expression

    procesar_stamentList(variable_table[name]["statements"])    
    result = resolve_value(variable_table[name]["return_value"])
    result_type = str(type(result)).split("'")[1]
    if result_type != function_type and not (function_type == "character" and result_type == "str"):
        raise TypeError(f"Expected {function_type} where obtained {result_type}")
    variable_table = original_variable_table

    return result

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
        p[0] = [(p[3], p[1])]
    elif len(p) == 1:
        p[0] = []
    else:
        p[0] = [(p[3], p[1])] + p[5]

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
    if isinstance(p[1], int):
        p[0] = ('int', p[1])
    else:
        p[0] = ('float', p[1])
    

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
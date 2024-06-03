# pylint: disable=wildcard-import
import sys
import argparse
import os
from ajs_lexer import scanner
from ajs_parser import parse_data
from progargs import read_file

LEXER_OUTPUT_DIR = "output/lexer/"
PARSER_OUTPUT_DIR = "output/parser/"

def main():
    args_parser = argparse.ArgumentParser(description='Procesa un archivo con opciones específicas.')
    args_parser.add_argument('input_file', metavar='input_file', type=str, help='El archivo de entrada')
    args_parser.add_argument('-lex', action='store_true', help='Opción para procesar el archivo en modo lex')
    args_parser.add_argument('-par', action='store_true', help='Opción para procesar el archivo en modo par')
    
    args = args_parser.parse_args()

    if len(sys.argv) < 2:
        args_parser.error('Debe especificar al menos un archivo de entrada.')

    data = read_file(args.input_file)

    if args.lex:
        # Realizar acciones específicas si la opción -lex está activada
        lexer_output_file = f"{LEXER_OUTPUT_DIR}{os.path.basename(args.input_file)}.token"
        scanner.input(data)
        with open(lexer_output_file, 'w') as outfile:
            while True:
                tok = scanner.token()
                if not tok:
                    break  # No hay más tokens
                outfile.write(f'{tok}\n')
    
    if args.par:
        try:
            # coge el archivo pasado por linea de comando o el string si no se le pasa nada
            variable_table, object_table, code = parse_data(data)
            
            # Nombres de los archivos de salida
            symbol_output_file = f"{PARSER_OUTPUT_DIR}{os.path.basename(args.input_file)}.symbol"
            register_output_file = f"{PARSER_OUTPUT_DIR}{os.path.basename(args.input_file)}.register"
            middle_output_file = f"{PARSER_OUTPUT_DIR}{os.path.basename(args.input_file)}.out"
            
            # Guarda la tabla de variables en el archivo .symbol
            with open(symbol_output_file, 'w') as symbol_file:
                for key, value in variable_table.items():
                    symbol_file.write(f"{key}: {value}\n")
            
            # Guarda la tabla de objetos en el archivo .register
            with open(register_output_file, 'w') as register_file:
                for key, value in object_table.items():
                    register_file.write(f"{key}: {value}\n")

            # Guarda el codigo intermedio en el archivo .out
            with open(middle_output_file, 'w') as middle_file:
                for tupla in code:
                    # Convierte la tupla en una cadena de texto y escribe en el archivo
                    middle_file.write(str(tupla) + '\n')
        except Exception as e:
            print("Error al analizar:", str(e))


if __name__ == "__main__":
    main()

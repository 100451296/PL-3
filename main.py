# pylint: disable=wildcard-import
import sys
import argparse
import os
from ajs_lexer import scanner
from ajs_parser import parser
from progargs import read_file

LEXER_OUTPUT_DIR = "output/lexer/"

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
            parsed_data = parser.parse(data)
        except Exception as e:
            print("Error al analizar:", str(e))


if __name__ == "__main__":
    main()

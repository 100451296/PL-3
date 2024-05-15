#!/bin/bash

TEST_LEXER="test_files/lexer/"
TEST_PARSER="test_files/parser/"

# Borra registros para ver warnigns
rm parsetab.py parser.out

# Iterar sobre los archivos en el directorio test_files/
echo -e "\n ############# TEST LEXER ############# \n\e[0m"
for archivo in "$TEST_LEXER"/*; do
  longitud=${#archivo}
  separador=""
    for (( i=1; i<=$longitud; i++ )); do
        separador+="-"
    done
  salida=$(python3 main.py -lex "$archivo" 2>&1)
  echo -e "\e[32m ------------- $archivo ------------- \n\e[0m"
  echo "$salida" | while IFS= read -r line; do
      if [[ $line == *"Carácter ilegal"* ]]; then
          echo -e "\e[91m$line\e[0m"
      else
          echo "$line"
      fi
  done
  echo -e "\e[32m\n --------------$separador-------------- \n\e[0m"

done
echo -e "\e[35m####################################### \n"

# Iterar sobre los archivos en el directorio test_files/
echo -e "\n ############# TEST PARSER ############# \n\e[0m"
for archivo in "$TEST_PARSER"/*; do
  longitud=${#archivo}
  separador=""
    for (( i=1; i<=$longitud; i++ )); do
        separador+="-"
    done
  salida=$(python3 main.py -p "$archivo" 2>&1)
  echo -e "\e[32m ------------- $archivo ------------- \n\e[0m"
  echo $salida
  echo -e "\e[32m\n --------------$separador-------------- \n\e[0m"

done
echo -e "\e[35m####################################### \n"
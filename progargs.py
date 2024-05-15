def read_file(input_file: str) -> str:
    # Lectura de archivo de entrada
    data = ""
    try:
        # Abrir el archivo y leer su contenido
        with open(input_file, "r", encoding="utf-8") as file:
            data = file.read()
    except FileNotFoundError:
        print(f"El archivo {input_file} no pudo ser encontrado.")
    return data

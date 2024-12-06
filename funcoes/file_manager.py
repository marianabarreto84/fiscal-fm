

def get_lines_from_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            line = [line.strip().strip("\"") for line in file.readlines()]
        return line
    except FileNotFoundError:
        print(f"O arquivo '{filename}' não foi encontrado.")
        return []
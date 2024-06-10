

def get_lines_from_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            artists = [line.strip() for line in file.readlines()]
        return artists
    except FileNotFoundError:
        print(f"O arquivo '{filename}' não foi encontrado.")
        return []
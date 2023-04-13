from io import FileIO


def write_file(filename, value, filetype='csv'):
    with open(filename, encoding='utf-8', newline='') as f:
        buffer = FileIO(f, mode='w')
        buffer.write(value)
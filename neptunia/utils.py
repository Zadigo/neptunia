from io import FileIO
import json


def write_file(filename, value, filetype='csv'):
    with open(f'neptunia/data/{filename}', mode='a+', encoding='utf-8-sig') as f:
        result = dict(value)
        f.write(json.dumps(result))
        # result = json.load()
        # result['data'] = dict(value)
        # json.dump(result, f)
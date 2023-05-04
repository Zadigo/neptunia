from io import FileIO
import json
import six


ESCAPE_CHARACTERS = ('\n', '\t', '\r')

HTML5_WHITESPACE = ' \t\n\r\x0c'


def drop_while(func, values):
    """
    A custom drop_while function that does not stop
    on True but completes all the list

    Parameters
    ----------

        func (Callable): [description]
        values (Iterable): [description]

    Yields
    ------

        Any: value to return
    """
    for value in values:
        result = func(value)
        if not result:
            yield value


def convert_to_unicode(value, encoding='utf-8', errors='strict'):
    """
    Return the unicode representation of a bytes object `text`.
    If the value is already a text, return it.
    """
    if isinstance(value, six.text_type):
        return value

    if not isinstance(value, (bytes, six.text_type)):
        raise TypeError('Value must be of type bytes, string or unicode')

    return value.decode(encoding, errors)


def replace_escape_chars(value, replace_by=u'', encoding=None):
    """
    Replaces/removes the escape characters that are often found
    in strings retrieved from the internet. They are replaced
    by default ''
    """
    text = convert_to_unicode(value)
    for escape_char in ESCAPE_CHARACTERS:
        text = text.replace(
            escape_char, convert_to_unicode(replace_by, encoding))
    return text


def write_file(filename, value, filetype='csv'):
    with open(f'neptunia/data/{filename}', mode='a+', encoding='utf-8-sig') as f:
        result = dict(value)
        f.write(json.dumps(result))
        # result = json.load()
        # result['data'] = dict(value)
        # json.dump(result, f)


def strip_white_space(text):
    """
    Strips the leading and trailing white space
    from a string. This does not affect space within
    an the string e.g. Kendall\rJenner, the \\r will
    not be affected

    Parameters
    ----------

        text (str): value to correct
    """
    return text.strip(HTML5_WHITESPACE)


def deep_clean(value):
    """
    Special helper for cleaning words that have a
    special characters between them and for which the 
    normal `replace_escape_chars` does not modify
    """
    value = replace_escape_chars(strip_white_space(value), replace_by=' ')
    cleaned_words = drop_while(lambda x: x == '', value.split(' '))
    return ' '.join(cleaned_words)

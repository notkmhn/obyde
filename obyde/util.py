import string

MOD_SLUG_ALPHABET = string.punctuation + string.whitespace
SLUG_TRANSLATION = str.maketrans(
    MOD_SLUG_ALPHABET, ('-' * len(MOD_SLUG_ALPHABET)))


def slugify_md_filename(name):
    translated = name.translate(SLUG_TRANSLATION)
    return translated.lower()


def parse_obsidian_links(content):
    links = []
    state = 'open'
    quotemult = 0
    idx = 0

    while idx < len(content):
        c = content[idx]
        incr = 1
        if c == '`':
            if state == 'open':
                tick_mult = _substr_cond(content, idx, lambda _, y: y == '`')
                quotemult = len(tick_mult)
                state = 'codestart'
                incr = len(tick_mult)
            elif state == 'code':
                tick_mult = _substr_cond(content, idx, lambda _, y: y == '`')
                ltick = len(tick_mult)
                if ltick < quotemult:
                    incr = ltick
                else:
                    quotemult = 0
                    state = 'open'
                    # If it is larger, then close first, open another block
                    incr += ltick if ltick == quotemult else quotemult
        else:
            if state == 'codestart':
                state = 'code'
            if state == 'open' and c == '[':
                start_url = _substr_cond(content, idx, (lambda _, y: y == '['))
                if len(start_url) >= 2:
                    urltext = _substr_cond(
                        content, idx + len(start_url), lambda _, y: y != ']')
                    if not urltext:
                        raise ValueError(
                            f'Hit EOF while parsing obsidian URL at index {idx}')
                    end_url = _substr_cond(
                        content, idx + len(start_url) + len(urltext), lambda _, y: y == ']')
                    if not end_url:
                        raise ValueError(
                            f'Hit EOF while parsing obsidian URL at index {idx}')
                    incr = len(start_url) + len(urltext) + len(end_url)
                    if len(end_url) >= 2:
                        links.append(start_url + urltext + end_url)

        idx += incr
    return links


def _substr_cond(s, idx, cond):
    res = ''
    count = 0
    if idx < 0:
        raise ValueError('Invalid index')
    if not cond:
        raise ValueError('Condition must be provided')
    while (idx + count) < len(s):
        c = s[idx + count]
        if cond(count, c):
            res += c
        else:
            break
        count += 1
    return res

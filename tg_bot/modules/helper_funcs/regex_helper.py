import regex


def regex_searcher(regex_string, string):
    try:
        search = regex.search(regex_string, string, timeout=6)
    except (TimeoutError, Exception):
        return False
    return search


def infinite_loop_check(regex_string):
    loop_matches = [
        r"\((.{1,}[\+\*]){1,}\)[\+\*].",
        r"[\(\[].{1,}\{\d(,)?\}[\)\]]\{\d(,)?\}",
        r"\(.{1,}\)\{.{1,}(,)?\}\(.*\)(\+|\* |\{.*\})",
    ]
    for match in loop_matches:
        if match_1 := regex.search(match, regex_string):
            return True
    return False

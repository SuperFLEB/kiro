import re


def flatten(list_of_lists: list[list[any]]) -> list[any]:
    return [item for sublist in list_of_lists for item in sublist]


def wordwrap(string: str, length: int) -> list[str]:
    words = [word for word in re.split(' +', string) if word]
    if not words: return []
    lines = [f"{words[0]} "]
    if len(words) > 1:
        for word in words[1:]:
            if len(lines[-1]) + len(word) > length:
                lines.append(f"{word} ")
                continue
            lines[-1] += f"{word} "
    lines = [line[:-1] for line in lines]
    return lines

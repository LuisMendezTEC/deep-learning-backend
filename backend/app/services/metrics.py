def levenshtein_distance(reference: list[str], hypothesis: list[str]) -> int:
    rows = len(reference) + 1
    cols = len(hypothesis) + 1
    distances = [[0] * cols for _ in range(rows)]

    for row in range(rows):
        distances[row][0] = row
    for col in range(cols):
        distances[0][col] = col

    for row in range(1, rows):
        for col in range(1, cols):
            cost = 0 if reference[row - 1] == hypothesis[col - 1] else 1
            distances[row][col] = min(
                distances[row - 1][col] + 1,
                distances[row][col - 1] + 1,
                distances[row - 1][col - 1] + cost,
            )

    return distances[-1][-1]


def word_error_rate(reference: str, hypothesis: str) -> float:
    reference_words = reference.split()
    if not reference_words:
        return 0.0 if not hypothesis.split() else 1.0
    return levenshtein_distance(reference_words, hypothesis.split()) / len(reference_words)


def character_error_rate(reference: str, hypothesis: str) -> float:
    reference_chars = list(reference.replace(" ", ""))
    hypothesis_chars = list(hypothesis.replace(" ", ""))
    if not reference_chars:
        return 0.0 if not hypothesis_chars else 1.0
    return levenshtein_distance(reference_chars, hypothesis_chars) / len(reference_chars)

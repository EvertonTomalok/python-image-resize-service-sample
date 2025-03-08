import unicodedata


def normalize_text(text: str, upper=True, remove_extra_spaces=True):
    text = (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("utf-8")
        .strip()
    )
    if remove_extra_spaces:
        text = " ".join(text.split())

    return text.upper() if upper else text

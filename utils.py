import unicodedata

# Extrae discord id de usuario directamente de un mention
def convert_mention_to_id(mention: str):
    return int(mention[1:][:len(mention)-2].replace("@","").replace("!",""))

# Quitamos acentos
def remove_accents(input_str: str):
    # NFD decomposes characters into their base and combining marks
    nfkd_form = unicodedata.normalize('NFD', input_str)
    # Filter out characters that are "combining marks" (category 'Mn')
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

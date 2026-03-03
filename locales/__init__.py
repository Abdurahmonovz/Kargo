from .uz import t as t_uz
from .tr import t as t_tr

def t(key: str, lang: str) -> str:
    if lang == "tr":
        return t_tr(key, lang)
    return t_uz(key, lang)
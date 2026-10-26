# precos.py: o arquivo também é o módulo, mas TUDO é público.
IMPOSTO = 0.1

# Lista do que "import *" exporta. É o mais perto de um export.
__all__ = ["com_imposto"]


def com_imposto(valor: float) -> float:
    return _arredondar(valor * (1 + IMPOSTO))


# _ na frente = privado por CONVENÇÃO (dá para importar).
def _arredondar(valor: float) -> float:
    return round(valor, 2)


# Outro arquivo: from pedidos_api.precos import com_imposto

# "Rodando direto, não importado?"
if __name__ == "__main__":
    print(com_imposto(100))

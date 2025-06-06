# test_alertas.py

import traceback
from src.backend.crud import listar_alertas

if __name__ == "__main__":
    try:
        alertas = listar_alertas(5)
        print("Resultado de listar_alertas(5):")
        for a in alertas:
            print(a)
    except Exception as e:
        print("Capturamos uma exceção ao chamar listar_alertas():")
        traceback.print_exc()

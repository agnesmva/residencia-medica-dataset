from images import extrair_imagens_pdf
from text_extraction import *
import pandas as pd
import json

teste = "scripts/extraction/data/enare.pdf"
# extrair_imagens_pdf(teste)


texto = extrair_texto_do_pdf(teste)
texto_unico = "\n".join(texto)

questoes = extrair_questoess(texto_unico)


texto_tod = "texto_todo.txt"
with open(texto_tod, "w", encoding="utf-8") as f:
    for i, linha in enumerate(questoes):
        f.write(f"--- Questão {i+1} ---\n\n\n")
        f.write(str(linha) + "\n") 
        f.write('\n')

# Lendo o conteúdo do arquivo:
with open("texto_todo.txt", "r", encoding="utf-8") as f:
    texto = f.read()

questoes = extrair_questoes_estruturadas(texto)

# Salvando como JSON
with open("questoes_estruturadas.json", "w", encoding="utf-8") as f:
    json.dump(questoes, f, ensure_ascii=False, indent=2)

print(f"{len(questoes)} questões extraídas e salvas.")
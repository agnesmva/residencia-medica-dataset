from images import extrair_imagens_pdf
from text_extraction import *
from conv_json import *

teste = "scripts/extraction/data/teste.pdf"
extrair_imagens_pdf(teste)
 
'''
texto = extrair_texto_do_pdf(teste)
print(f"Total de páginas extraídas: {len(texto)}")

ids = extrair_id(texto)
enunciados = extrair_enunciado(texto)
alternativas = extrair_alternativas(texto)
gabaritos = extrair_gabaritos(texto)

json_questoes = montar_json(ids, enunciados, alternativas, gabaritos)

print(json_questoes)
'''
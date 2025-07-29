import fitz  # PyMuPDF
import re


def extrair_texto_do_pdf(caminho_pdf):
    """Extrai o texto de todas as páginas de um PDF."""
    doc = fitz.open(caminho_pdf)
    texto_paginas = [pagina.get_text("text") for pagina in doc]
    doc.close()
    return texto_paginas

def extrair_questoess(texto):
    if isinstance(texto, list):
        texto = "\n".join(texto)

    padrao = r"(Questão\s*\|\s*\|.*?)(?=Questão\s*\|\s*\||\Z)"
    questoes = re.findall(padrao, texto, flags=re.DOTALL)
    return [q.strip() for q in questoes]

def extrair_id(texto):
    padrao = r'Questão\s*\|\|\s*\|\s*\d+\s*\|\s*(\d+)\b'
    match = re.search(padrao, texto)
    if match:
        return int(match.group(1))
    return None


def extrair_enunciado(texto_paginas, pagina_inicial=2):
    enunciados = []
    texto_todo = "\n".join(texto_paginas[pagina_inicial:])

    #Extrai o padrão Questão || | id até encontrar o A)
    padrao = r'Questão.*?\|\s*\|\s*\d+\s*\|\s*(\d+)\s*(.*?)(?=A\))'

    matches = re.finditer(padrao, texto_todo, re.DOTALL | re.IGNORECASE)

    for match in matches:
        id_q = match.group(1)
        enunciado_raw = match.group(2)
        enunciado_limpo = ' '.join(enunciado_raw.split())
        enunciados.append({
            "id": int(id_q),
            "question_text": enunciado_limpo
        })

    return enunciados

def extrair_alternativas(texto):
    padrao = r'A\)(.*?)\s*B\)(.*?)\s*C\)(.*?)\s*D\)(.*?)\s*E\)(.*?)(?:\n{2,}|$)'
    match = re.search(padrao, texto, re.DOTALL)

    if match:
        alternativas = {
            'id': extrair_id(texto),
            'alternativas': {
                'A': match.group(1).strip(),
                'B': match.group(2).strip(),
                'C': match.group(3).strip(),
                'D': match.group(4).strip(),
                'E': match.group(5).strip()
            }
        }
        return alternativas
    else:
        return {
            'id': extrair_id(texto),
            'alternativas': None,
            'erro': 'Não foi possível extrair as alternativas'
        }



def extrair_id_teste(texto):
    ids = []
    for pagina in texto:
        encontrados = re.findall(r'Questão\s*\|\s*\|\s*\d+\s*\|\s*(\d+)', pagina)
        ids.extend(encontrados)
    return ids

def extrair_enunciado_test(texto):
    enunciados = []
    for pagina in texto:
        encontrados = re.findall(r'Questão.*?\|\s*\|\s*\d+\s*\|\s*\d+\s*(.*?)(?=A\))', pagina, re.DOTALL)
        enunciados.extend([en.strip() for en in encontrados])
    return enunciados

def extrair_alternativas_teste(texto):
    alternativas_todas = []
    for pagina in texto:
        alternativas = re.findall(r'A\)(.*?)B\)(.*?)C\)(.*?)D\)(.*?)E\)(.*?)(?=Solução|Gabarito|GABARITO|$)', pagina, re.DOTALL)
        for alt in alternativas:
            alternativas_todas.append([a.strip() for a in alt])
    return alternativas_todas

def extrair_gabaritos(texto):
    gabaritos = []
    for pagina in texto:
        encontrados = re.findall(r'Gabarito:\s*([A-E])\)', pagina)
        if not encontrados:
            encontrados = re.findall(r'GABARITO:\s*ALTERNATIVA\s+([A-E])', pagina)
        gabaritos.extend(encontrados)
    return gabaritos


import re
import json

def extrair_questoes_estruturadas(texto):
    if isinstance(texto, list):
        texto = "\n".join(texto)

    padrao = re.compile(
        r"Questão\s*\|\s*\|\s*(\d{4})\s*\|\s*(\d+)\s*\n"                            # ano e id
        r"(.*?)(?=^[A-E]\))"                                                       # enunciado
        r"(A\).+?)"                                                                # alternativas começando com A)
        r"(?:\nSolução\s+Gabarito:\s*([A-E])\)?\s*(.*?)\n(?=Questão\s*\|\s*\||\Z))",# gabarito e solução
        re.DOTALL | re.MULTILINE
    )

    questoes = []

    for match in padrao.finditer(texto):
        ano, id_questao, enunciado, alternativas_bloco, gabarito, solucao = match.groups()

        # Extrair alternativas A-E
        alternativas = dict()
        alt_padrao = re.findall(r"([A-E])\)\s*(.*?)(?=(?:\n[A-E]\)|\nSolução|\Z))", alternativas_bloco, re.DOTALL)
        for letra, texto_alt in alt_padrao:
            alternativas[letra] = ' '.join(texto_alt.strip().split())

        questoes.append({
            "id": id_questao.strip(),
            "ano": ano.strip(),
            "fonte": "ENARE",
            "enunciado": ' '.join(enunciado.strip().split()),
            "alternativas": alternativas,
            "gabarito": gabarito.strip(),
            "solucao": ' '.join(solucao.strip().split())
        })

    return questoes

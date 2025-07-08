'''
Script para extrair questões das provas
'''

import fitz  # PyMuPDF
import re
import os

def extrair_texto_pdf(caminho_pdf):
    """
    Extrai o texto de um arquivo PDF página por página.

    Args:
        caminho_pdf (str): Caminho do arquivo PDF.

    Returns:
        list: Lista com o texto de cada página.
    """
    texto_paginas = []

    with fitz.open(caminho_pdf) as doc:
        for pagina in doc:
            texto = pagina.get_text()
            texto_paginas.append(texto)

    return texto_paginas


def salvar_texto(texto_paginas, caminho_saida):
    """
    Salva o texto extraído em um arquivo .txt.

    Args:
        texto_paginas (list): Lista com o texto de cada página.
        caminho_saida (str): Caminho para salvar o .txt
    """
    with open(caminho_saida, "w", encoding="utf-8") as f:
        for i, pagina in enumerate(texto_paginas):
            f.write(f"\n--- Página {i+1} ---\n")
            f.write(pagina.strip() + "\n")

def limpar_marcas_sespe(texto):
    """
    Remove expressões de rodapé/cabeçalho da SES-PE como:
    - '4. SES-PE'
    - '3/382'
    - '4.1 SES-PE - 2023'
    """
    padroes = [
        r'\b\d{1,3}\.\s*SES-PE\b',             # ex: 4. SES-PE
        r'\b\d{1,3}/\d{1,4}\b',                # ex: 3/382
        r'\b\d{1,3}\.\d{1,3}\s*SES-PE\b',      # ex: 4.1 SES-PE
        r'\b\d{1,3}\.\d{1,3}\s*SES-PE\s*-\s*\d{4}\b',  # ex: 4.1 SES-PE - 2023
        r'\bSES-PE\s*-\s*\d{4}\b'              # ex: SES-PE - 2023
    ]

    for padrao in padroes:
        texto = re.sub(padrao, '', texto)

    # Remove espaços extras gerados
    texto = re.sub(r'\n\s*\n', '\n\n', texto)  # linhas vazias duplicadas
    texto = re.sub(r'[ \t]{2,}', ' ', texto)   # múltiplos espaços

    return texto.strip()

def separar_questoes_por_padrao(texto):
    """
    Separa o texto em questões usando o padrão:
    'Questão\n| | ANO | ID'

    Args:
        texto (str): Texto completo da prova.

    Returns:
        list: Lista de strings, cada uma contendo uma questão.
    """
    # Regex: procura por "Questão" seguido por "| |" e um número de ano (ex: 2023)
    padrao = r'(Quest[aã]o\s*\n\|\s*\|\s*\d{4}\s*\|\s*\d{10})'

    # Adiciona marcador antes de cada match para split
    texto_marcado = re.sub(padrao, r'###DIVISAO###\n\1', texto)

    # Divide e remove vazios
    blocos = [q.strip() for q in texto_marcado.split('###DIVISAO###') if q.strip()]

    return blocos

import uuid  # para gerar IDs únicos
import json

import re
import uuid

def parsear_questoes_sespe_real(blocos_questoes, title, source, subject, county, year):
    questoes_json = []

    for bloco in blocos_questoes:
        # 1. External ID
        match_id = re.search(r'\|\s*\|\s*\d{4}\s*\|\s*(\d{10})', bloco)
        external_id = int(match_id.group(1)) if match_id else None

        # 2. Gabarito
        match_gabarito = re.search(r'Gabarito:\s*ALTERNATIVA\s+([A-E])', bloco, re.IGNORECASE)
        letra_correta = match_gabarito.group(1).upper() if match_gabarito else None

        # 3. Referência
        match_ref = re.search(r'Refer[aê]ncia.*?:\s*(.+?)(?:\n\n|$)', bloco, re.IGNORECASE | re.DOTALL)
        referencia = match_ref.group(1).strip() if match_ref else None

        # 4. Explicação geral
        match_exp = re.search(r'(Solu[cç][aã]o|Coment[aá]rio|Estrategista.*?):(.+?)(?=A letra|Quest[aã]o|$)', bloco, re.IGNORECASE | re.DOTALL)
        explicacao_geral = match_exp.group(2).strip() if match_exp else None

        # 5. Enunciado + alternativas
        bloco_limpo = re.sub(r'Quest[aã]o\s*\| \|.*?\n', '', bloco)
        bloco_limpo = re.sub(r'Gabarito:.*', '', bloco_limpo, flags=re.IGNORECASE)
        partes = re.split(r'\n?[A-E]\)', bloco_limpo)
        enunciado = partes[0].strip()
        alternativas_raw = partes[1:6]

        # 6. Separa alternativas
        alternativas_raw = re.split(r'\n?[A-E]\)', bloco_limpo)
        enunciado = alternativas_raw[0].strip()
        alternativas_textos = alternativas_raw[1:6]

    

        # 6. Explicações por alternativa
        explicacoes_alt = {}
        for letra in ['A', 'B', 'C', 'D', 'E']:
            match_alt = re.search(rf'A letra {letra} .*?:(.+?)(?=A letra|Quest[aã]o|$)', bloco, re.IGNORECASE | re.DOTALL)
            explicacoes_alt[letra] = match_alt.group(1).strip() if match_alt else None

        # 7. Alternativas
        alternativas_json = []
        letras = ['A', 'B', 'C', 'D', 'E']
        for i in range(5):
            texto_alt = alternativas_raw[i].strip() if i < len(alternativas_raw) else None
            alternativas_json.append({
                "letter": letras[i],
                "alternative_text": texto_alt,
                "is_correct": letras[i] == letra_correta,
                "explanation_alternative": explicacoes_alt.get(letras[i])
            })

        questoes_json.append({
            "id": int(uuid.uuid4().int >> 96),
            "external_id": external_id,
            "title": title,
            "source": source,
            "subject": None,
            "county": county,
            "year": year,
            "question_text": enunciado,
            "has_image": False,
            "image_path": None,
            "image_description": None,
            "alternatives": alternativas_json,
            "explanation_question": explicacao_geral,
            "has_reference": referencia is not None,
            "reference": referencia
        })

    return questoes_json



# 🧪 Exemplo de uso:
if __name__ == "__main__":
    from pathlib import Path

    caminho_pdf = "scripts/extraction/data/teste.pdf"
    caminho_json = "questoes_extraidas.json"

    title = "SES-PE 2023 - Clínica Médica"
    source = "SES-PE"
    subject = "Clínica Médica"
    county = "PE"
    year = 2023

    texto = extrair_texto_pdf(caminho_pdf)
    texto_limpo = [limpar_marcas_sespe(p) for p in texto]
    texto_unificado = "\n".join(texto_limpo)
    blocos = separar_questoes_por_padrao(texto_unificado)

    questoes = parsear_questoes_sespe_real(blocos, title, source, subject, county, year)

    Path(caminho_json).write_text(json.dumps(questoes, indent=4, ensure_ascii=False), encoding="utf-8")

    print(f"{len(questoes)} questões extraídas e salvas em {caminho_json}")


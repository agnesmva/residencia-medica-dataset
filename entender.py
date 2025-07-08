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

        # 3. Separar texto principal das explicações finais (começam em "Solução" ou "Gabarito")
        partes = re.split(r'(?:\n|^)Solu[cç][aã]o\b|Gabarito:.*?\n', bloco, flags=re.IGNORECASE)
        texto_principal = partes[0].strip()
        explicacao_geral = "\n".join(partes[1:]).strip() if len(partes) > 1 else None

        # 4. Referência
        match_ref = re.search(r'Refer[aê]ncia.*?:\s*(.+?)(?:\n\n|$)', explicacao_geral or '', re.IGNORECASE | re.DOTALL)
        referencia = match_ref.group(1).strip() if match_ref else None

        # 5. Limpa cabeçalho do bloco principal
        bloco_limpo = re.sub(r'Quest[aã]o\s*\| \|.*?\n', '', texto_principal)

        # 6. Separa alternativas
        alternativas_raw = re.split(r'\n?[A-E]\)', bloco_limpo)
        enunciado = alternativas_raw[0].strip()
        alternativas_textos = alternativas_raw[1:6]

        letras = ['A', 'B', 'C', 'D', 'E']
        alternativas_json = []

        for i in range(5):
            alt_text = alternativas_textos[i].strip() if i < len(alternativas_textos) else None
            alternativas_json.append({
                "letter": letras[i],
                "alternative_text": alt_text,
                "is_correct": letras[i] == letra_correta,
                "explanation_alternative": None
            })

        questoes_json.append({
            "id": int(uuid.uuid4().int >> 96),
            "external_id": external_id,
            "title": title,
            "source": source,
            "subject": subject,
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

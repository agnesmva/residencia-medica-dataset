import json

def montar_json(ids, enunciados, alternativas, gabaritos):
    questoes = []

    for i in range(len(ids)):
        questao = {
            "id": ids[i],
            "enunciado": enunciados[i],
            "alternativas": {
                "A": alternativas[i][0],
                "B": alternativas[i][1],
                "C": alternativas[i][2],
                "D": alternativas[i][3],
                "E": alternativas[i][4]
            },
            "gabarito": gabaritos[i]
        }
        questoes.append(questao)

    return json.dumps(questoes, ensure_ascii=False, indent=4)

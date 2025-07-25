import fitz  # PyMuPDF
import os
from text_extraction import extrair_id

def extrair_imagens_pdf(caminho_pdf, pasta_saida="imagens_extraidas", pagina_inicial=3):
    os.makedirs(pasta_saida, exist_ok=True)
    doc = fitz.open(caminho_pdf)

    total = 0
    for i in range(pagina_inicial, len(doc)):
        pagina = doc[i]
        imagens = pagina.get_images(full=True)

        for img_index, img in enumerate(imagens):
            xref = img[0]
            base_imagem = doc.extract_image(xref)
            imagem_bytes = base_imagem["image"]
            extensao = base_imagem["ext"]
            nome_arquivo = f"id_{i+1}_img_{img_index+1}.{extensao}"

            caminho_completo = os.path.join(pasta_saida, nome_arquivo)
            with open(caminho_completo, "wb") as f:
                f.write(imagem_bytes)

            total += 1
            print(f"Imagem extraída: {nome_arquivo}")

    print(f"Total de imagens extraídas: {total}")
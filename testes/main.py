from pbm_image import PBMImage


if __name__ == "__main__":
    try:
        caminho_imagem = input("Digite o caminho para a imagem que quer analisar: ")
        imagem = PBMImage.from_file(caminho_imagem)
        PBMImage.show_file(caminho_imagem)

        img_mediana = PBMImage.median(imagem=imagem)
        
        coordenadas = img_mediana.analyze_text()

        palavras_destacadas = PBMImage.draw_rectangle(img_mediana, coordenadas)

        imagem_analisada_path = PBMImage.save(imagem=palavras_destacadas, nome=f"{caminho_imagem}_analisada")

        PBMImage.show_file(imagem_analisada_path)

    except Exception as e:
        print(f"Erro ao processar a imagem: {e}")
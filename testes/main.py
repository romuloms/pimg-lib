from pbm_image import PBMImage


if __name__ == "__main__":
    try:
        imagem = PBMImage.from_file("docs/lorem_s12_c02_espacos_noise.pbm")
        PBMImage.show_file("docs/lorem_s12_c02_espacos_noise.pbm")

        img_mediana = PBMImage.median(imagem=imagem)
        
        coordenadas = img_mediana.analyze_text()

        palavras_destacadas = PBMImage.draw_rectangle(img_mediana, coordenadas)

        imagem_analisada_path = PBMImage.save(imagem=palavras_destacadas, nome="img_media")

        PBMImage.show_file(imagem_analisada_path)

    except Exception as e:
        print(f"Erro ao processar a imagem: {e}")
from pbm_image import PBMImage


if __name__ == "__main__":
    try:
        imagem = PBMImage.from_file("docs/lorem_s12_c02_espacos.pbm")

        # print(f"Largura: {imagem['largura']} px")
        # print(f"Altura: {imagem['altura']} px")
        # print(f"Valor Máximo: {imagem['valor_maximo']}")
        # img = PBMImage.double_padding(imagem)
        img_negativa = imagem.negative()
        img_negativa_path = PBMImage.save(img_negativa, "img_negativa")

        PBMImage.show_file(img_negativa_path)

    except Exception as e:
        print(f"Erro ao processar a imagem: {e}")
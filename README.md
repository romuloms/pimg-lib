# Biblioteca PBM P1

Biblioteca em Python para leitura, escrita, visualização e processamento de imagens PBM no formato **P1** (preto e branco).

O foco do projeto é aplicar operações simples de processamento de imagens e análise de texto usando apenas estruturas nativas (listas), sem depender de bibliotecas externas para o processamento principal.

## O que a biblioteca faz

A classe principal é `PBMImage` (em `testes/pbm_image.py`) e oferece:

- Carregamento de arquivo `.pbm` P1 (`from_file`)
- Salvamento de imagem PBM (`save`)
- Visualização da imagem no visualizador padrão do sistema (`show` e `show_file`)
- Filtros:
  - negativo (`negative`)
  - média (`mean`)
  - mediana (`median`)
- Apoio para análise de texto binário:
  - contagem de colunas e linhas (`count_columns`, `count_lines`)
  - detecção de blocos e gaps (`_extract_blocks_gaps`)
  - análise de palavras e coordenadas (`analyze_text`)
  - destaque com retângulos (`draw_rectangle`)

A biblioteca também possui tratamento de erro com logs via módulo `logging` em pontos críticos de leitura, escrita e processamento.

## Estrutura mínima usada

- `testes/pbm_image.py`: implementação da classe `PBMImage`
- `testes/main.py`: exemplo completo de uso
- `testes/docs/*.pbm`: imagens de entrada para teste (diretório não versionado)

## Passo a passo objetivo (como no main.py)

1. Entre na pasta de testes:

```bash
cd testes
```

2. Execute o script de exemplo:

```bash
python main.py
```

3. O fluxo executado pelo `main.py` é:

- Espera a entrada do usuário por linha de comando do caminho da imagem PBM:
  - `caminho_imagem = input("Digite o caminho para a imagem que quer analisar: ")`
- Carrega a imagem PBM:
  - `imagem = PBMImage.from_file(caminho_imagem)`
- Exibe a imagem original:
  - `PBMImage.show_file(caminho_imagem)`
- Aplica filtro da mediana:
  - `img_mediana = PBMImage.median(imagem=imagem)`
- Analisa texto e coleta coordenadas das palavras (aqui, já serão exibidos no terminal os valores de coluna, linha e palavras):
  - `coordenadas = img_mediana.analyze_text()`
- Desenha retângulos nas palavras detectadas:
  - `palavras_destacadas = PBMImage.draw_rectangle(img_mediana, coordenadas)`
- Salva o resultado:
  - `imagem_analisada_path = PBMImage.save(imagem=palavras_destacadas, nome=f"{caminho_imagem}_analisada")`
- Exibe a imagem final:
  - `PBMImage.show_file(imagem_analisada_path)`

## Exemplo rápido de código

```python
from pbm_image import PBMImage

imagem = PBMImage.from_file("docs/lorem_s12_c02_espacos_noise.pbm")
img_mediana = PBMImage.median(imagem=imagem)
coordenadas = img_mediana.analyze_text()
resultado = PBMImage.draw_rectangle(img_mediana, coordenadas)
PBMImage.save(imagem=resultado, nome="imagem_analisada")
```

## Observações

- O parser foi feito para PBM **P1**.
- Caminhos relativos em `main.py` consideram execução dentro da pasta `testes`.
- Em caso de erro, os métodos registram logs para facilitar diagnóstico.

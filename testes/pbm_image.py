from typing import List, Dict, Union, Any, Optional, Type


class PBMImage:
    """Classe para representar e manipular imagens PBM (Portable BitMap) no formato P1"""

    def __init__(self, matriz: List[List[int]], largura: int, altura: int) -> None:
        self.matriz: List[List[int]] = matriz
        self.largura: int = largura
        self.altura: int = altura
        self.valor_maximo: int = 1

    @classmethod
    def from_file(cls: Type['PBMImage'], caminho_arquivo: str) -> 'PBMImage':
        """Carrega uma imagem PBM (P1) a partir de um arquivo"""
        try:
            with open(caminho_arquivo, 'r') as arquivo:
                # Filtrar comentários e ler todos os tokens
                tokens: List[str] = []
                for linha in arquivo:
                    if '#' in linha:
                        linha = linha.split('#')[0]
                    tokens.extend(linha.split())

            if not tokens:
                raise ValueError("Arquivo vazio ou inválido")
            
            # Validação do formato
            formato: str = tokens[0]
            if formato != "P1":
                raise ValueError(f"Formato inválido (esperado P1). Encontrado: {formato}")
            
            # Extração do cabeçalho
            largura: int = int(tokens[1])
            altura: int = int(tokens[2])

            # Extração dos dados dos pixels (concatenando e tratando cada dígito)
            # P1 permite '0's e '1's sem espaços ou com espaços
            dados_brutos: str = "".join(tokens[3:])
            dados_pixels: List[int] = [int(p) for p in dados_brutos if p in ('0', '1')]

            if len(dados_pixels) < largura * altura:
                raise ValueError(f"Dados insuficientes: esperado {largura * altura}, obtido {len(dados_pixels)}")
            
            # Construção da matriz
            matriz: List[List[int]] = []
            for i in range(altura):
                inicio: int = i * largura
                fim: int = inicio + largura
                matriz.append(dados_pixels[inicio:fim])

            return cls(matriz, largura, altura)
        except (FileNotFoundError, IndexError, ValueError) as e:
            raise Exception(f"Erro ao ler arquivo PBM: {e}")

    @staticmethod
    def save(imagem: 'PBMImage', nome: str) -> str:
        """
        Salva uma imagem PBMImage em um novo arquivo {nome}.pbm
        
        Args:
            imagem: Instância da classe PBMImage
            nome: Nome do arquivo (sem extensão)
        """
        caminho_arquivo = f"{nome}.pbm"
        try:
            with open(caminho_arquivo, 'w') as f:
                f.write("P1\n")
                f.write(f"# Criado por PBMImage Lib\n")
                f.write(f"{imagem.largura} {imagem.altura}\n")
                for linha in imagem.matriz:
                    # Formato P1: 0s e 1s
                    f.write("".join(map(str, linha)) + "\n")
            print(f"Imagem salva com sucesso em: {caminho_arquivo}")

            return caminho_arquivo
        
        except Exception as e:
            raise Exception(f"Erro ao salvar arquivo PBM: {e}")

    @staticmethod
    def double_padding(imagem: 'PBMImage', tamanho_borda: int = 1) -> 'PBMImage':
        """Cria nova matriz expandindo as bordas ao duplicar os pixels mais próximos"""
        matriz_original = imagem.matriz
        altura_original = imagem.altura
        largura_original = imagem.largura

        # Dir + esq / cima + baixo
        nova_altura = altura_original + (2 * tamanho_borda)
        nova_largura = largura_original + (2 * tamanho_borda)

        matriz_expandida = []

        for y_novo in range(nova_altura):
            linha = []

            # Mapeamento do eixo y:
            # 1 - Subtrair o tamanho da borda para compensar o deslocamento
            # 2 - Travar o valor entre 0 e o índice máximo original
            y_original = max(0, min(y_novo - tamanho_borda, altura_original - 1))

            for x_novo in range(nova_largura):
                # Mapeamento do eixo x (mesma lógica):
                x_original = max(0, min(x_novo - tamanho_borda, largura_original - 1))

                # Copia o pixel correspondente da imagem original
                pixel = matriz_original[y_original][x_original]
                linha.append(pixel)

            matriz_expandida.append(linha)

        return PBMImage(
            matriz=matriz_expandida,
            largura=nova_largura,
            altura=nova_altura
        )
    
    def negative(self) -> 'PBMImage':
        """Aplica o filtro Negativo à imagem atual"""
        matriz_negativa = []
    
        for linha in self.matriz:
            # Cria uma nova linha invertendo cada pixel
            linha_invertida = [pixel ^ 1 for pixel in linha]
            matriz_negativa.append(linha_invertida)

        return PBMImage(
            matriz=matriz_negativa,
            largura=self.largura,
            altura=self.altura
        )
    
    @staticmethod
    def mean(imagem: 'PBMImage', tamanho_mascara: int = 3) -> 'PBMImage':
        """Aplica filtro da média"""
        if tamanho_mascara % 2 == 0:
            raise ValueError("O tamanho da máscara deve ser um número ímpar.")

        if tamanho_mascara < 3:
            raise ValueError("O tamanho da máscara deve maior ou igual a 3.")
        
        altura = imagem.altura
        largura = imagem.largura

        # Alcance e área da máscara
        raio = tamanho_mascara // 2
        area_mascara = tamanho_mascara * tamanho_mascara
        try:
            # Versão com bordas estendidas
            imagem_com_borda = PBMImage.double_padding(imagem, tamanho_borda=raio)

            imagem_media = []

            for y in range(altura):
                linha_resultado = []
                
                for x in range(largura):
                    # Corrigir o centro da máscara
                    centro_y = y + raio
                    centro_x = x + raio

                    soma_mascara = 0

                    # Percorrer os elementos da máscara
                    for i in range(-raio, raio + 1):
                        for j in range(-raio, raio + 1):
                            pixel_adjacente = imagem_com_borda.matriz[centro_y + i][centro_x + j]
                            soma_mascara += pixel_adjacente

                    # Média
                    media = int(soma_mascara/area_mascara)

                    # Adiciona o valor à linha de resultado
                    linha_resultado.append(media)

                imagem_media.append(linha_resultado)

            return PBMImage(
                matriz=imagem_media,
                altura=altura,
                largura=largura
            )
        
        except Exception as e:
            print(f"Erro na função de média: {e}")

    
    def median(imagem: 'PBMImage', tamanho_mascara: int = 3) -> 'PBMImage':
        """Aplica filtro da mediana"""
        if tamanho_mascara % 2 == 0:
            raise ValueError("O tamanho da máscara deve ser um número ímpar.")

        if tamanho_mascara < 3:
            raise ValueError("O tamanho da máscara deve maior ou igual a 3.")
        
        altura = imagem.altura
        largura = imagem.largura

        # Alcance e área da máscara
        raio = tamanho_mascara // 2
        total_elementos = tamanho_mascara * tamanho_mascara
        try:
            # Versão com bordas estendidas
            imagem_com_borda = PBMImage.double_padding(imagem, tamanho_borda=raio)

            imagem_mediana = []

            for y in range(altura):
                linha_resultado = []

                for x in range(largura):
                    # Corrigir o centro da máscara
                    centro_y = y + raio
                    centro_x = x + raio

                    elementos = []

                    # Percorrer os elementos da máscara
                    for i in range(-raio, raio + 1):
                        for j in range(-raio, raio + 1):
                            pixel = imagem_com_borda.matriz[centro_y + i][centro_x + j]
                            elementos.append(pixel)

                    # Mediana
                    elementos.sort()
                    posicao = int((total_elementos//2) + 1)
                    mediana = elementos[posicao]

                    # Adiciona o valor à linha de resultado
                    linha_resultado.append(mediana)

                imagem_mediana.append(linha_resultado)
            
            return PBMImage(
                matriz=imagem_mediana,
                altura=altura,
                largura=largura
            )
        
        except Exception as e:
            print(f"Erro na função de mediana: {e}")
        

    def show(self) -> None:
        """Exibe a imagem atual para visualização usando o visualizador padrão do sistema"""
        import os
        import tempfile
        import platform
        import subprocess

        try:
            # 1. Gerar o conteúdo do arquivo PBM (P1)
            conteudo = [
                "P1",
                f"# Visualizacao temporaria",
                f"{self.largura} {self.altura}"
            ]
            for linha in self.matriz:
                conteudo.append("".join(map(str, linha)))
            
            # 2. Criar um arquivo temporário
            # delete=False porque o visualizador do sistema pode precisar que o arquivo exista após o encerramento do script 
            with tempfile.NamedTemporaryFile(suffix='.pbm', mode='w', delete=False) as temp:
                temp.write("\n".join(conteudo) + "\n")
                caminho_temp = temp.name

            # 3. Identificar o sistema operacional e abrir o arquivo
            sistema = platform.system()
            if sistema == "Darwin":  # macOS
                subprocess.run(["open", caminho_temp], check=True)
            elif sistema == "Windows":
                os.startfile(caminho_temp)
            else:  # Linux / Outros
                subprocess.run(["xdg-open", caminho_temp], check=True)
                
        except Exception as e:
            print(f"Erro ao exibir a imagem sem bibliotecas externas: {e}")

    @staticmethod
    def show_file(caminho_arquivo: str) -> None:
        """Carrega e exibe uma imagem PBM a partir de um caminho."""
        imagem = PBMImage.from_file(caminho_arquivo)
        imagem.show()

    def __getitem__(self, key: str) -> Union[List[List[int]], int]:
        """Suporte para acesso como dicionário"""
        mapping: Dict[str, Union[List[List[int]], int]] = {
            'matriz': self.matriz,
            'largura': self.largura,
            'altura': self.altura,
            'valor_maximo': self.valor_maximo
        }
        if key in mapping:
            return mapping[key]
        raise KeyError(key)

    def __repr__(self) -> str:
        return f"PBMImage(largura={self.largura}, altura={self.altura})"

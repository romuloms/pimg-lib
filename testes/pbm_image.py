from typing import List, Dict, Sequence, Tuple, Union, Any, Optional, Type


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

    
    @staticmethod
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

    
    @staticmethod
    def count_columns(imagem: 'PBMImage') -> int:
        """Função para contar colunas de uma imagem"""
        matriz = imagem.matriz
        altura = imagem.altura
        largura = imagem.largura

        soma_colunas = [0] * largura

        for coluna in range(largura):
            for linha in range(altura):
                soma_colunas[coluna] += matriz[linha][coluna]

        colunas_vazias = soma_colunas == 0
        colunas_vazias = [int(item) for item in colunas_vazias]       

        mudancas = [0] * (len(colunas_vazias) - 1)

        for indice in range(len(colunas_vazias) - 1):
            mudancas[indice] = colunas_vazias[indice+1] - colunas_vazias[indice]

        total_colunas = 0

        for mudanca in mudancas:
            if mudanca == -1:
                total_colunas += 1

        return total_colunas
    

    @staticmethod
    def count_lines(imagem: 'PBMImage') -> int:
        """Função para contar as linhas de uma imagem"""
        matriz = imagem.matriz
        altura = imagem.altura
        largura = imagem.largura

        soma_linhas = [0] * altura
        
        for linha in range(altura):
            for coluna in range(largura):
                soma_linhas[linha] += matriz[linha][coluna]
        
        linhas_vazias = soma_linhas == 0
        linhas_vazias = [int(item) for item in linhas_vazias]

        mudancas = [0] * (len(linhas_vazias) - 1)

        for indice in range(len(linhas_vazias) - 1):
            mudancas[indice] = linhas_vazias[indice+1] - linhas_vazias[indice]


    def _variance(self, arr: list) -> float:
        media = sum(arr) / len(arr)

        dif_quadradas = [(x - media) ** 2 for x in arr]

        variancia = sum(dif_quadradas) / len(arr)

        return variancia

    def _combined_variance(self, grupo_a: list, grupo_b: list) -> float:
        """Mede o quão homogêneo cada grupo fica e combina essa medida num único número.

        Quanto menor o valor devolvido, melhor foi a separação entre grupo_a e grupo_b, ou seja, mais parecidos entre si estão os valores dentro de cada grupo."""
        media_a = sum(grupo_a) / len(grupo_a) if grupo_a else 0
        media_b = sum(grupo_b) / len(grupo_b) if grupo_b else 0

        variancia_a = self._variance(grupo_a)
        variancia_b = self._variance(grupo_b)

        # (nA * variancia_a + nB * variancia_b) / quantidade de gaps totais
        variancia_combinada = (len(grupo_a) * variancia_a + len(grupo_b) * variancia_b) / (len(grupo_a) + len(grupo_b))

        # Retorna a variância combinada ponderada pelo tamanho de cada grupo
        return variancia_combinada


    def _gap_threshold(self, gaps: list, altura_referencia: int = None, fracao_fallback: float = 0.75) -> float:
        """Calcula o limiar que separa gaps pequenos (mesma palavra) de
        gaps grandes (fim de palavra,coluna,etc)

        Se não tiver gaps suficientes para uma decisão estatística
        (0 ou 1 valores), usa uma heurística baseada na altura do
        bloco de referência (linha ou letra) medida na imagem
        especificamente"""
        quantidade_gaps = len(gaps)

        # Caso 1 - Sem gaps
        if quantidade_gaps == 0:
            return float('inf')
        
        # Caso 2 - Um gap
        if quantidade_gaps == 1: 
            if altura_referencia is None:
                raise ValueError(
                    "Com 1 único gap, é necessário informar altura_referencia para usar a heurística de fallback."
                )
            return altura_referencia * fracao_fallback
        
        gaps_ordenados = sorted(gaps)
        melhor_variancia = float('inf')
        indice_melhor_corte = 1

        # Não corta antes do primeiro elemento nem depois do último
        for i in range(1, quantidade_gaps):
            grupo_a = gaps_ordenados[:i]
            grupo_b = gaps_ordenados[i:]
            variancia_atual = self._combined_variance(grupo_a, grupo_b)

            if variancia_atual < melhor_variancia:
                melhor_variancia = variancia_atual
                indice_melhor_corte = i

        # O threshold é o ponto intermediário entre o último gap do grupo pequeno e o primeiro gap do grupo grande no corte vencedor
        ultimo_grupo_a = gaps_ordenados[indice_melhor_corte - 1]
        primeiro_grupo_b = gaps_ordenados[indice_melhor_corte]
        threshold = (ultimo_grupo_a + primeiro_grupo_b) / 2

        return threshold        


    @staticmethod
    def draw_rectangle(imagem: 'PBMImage', coordenadas_palavras: list) -> list:
        """
        Recebe as coordenadas das palavras e desenha os retângulos na matriz.
        Assume que o valor 1 representa a cor preta (traço do retângulo).
        """
        matriz = imagem.matriz
        altura = imagem.altura
        largura = imagem.largura

        for linha_inicial, linha_final, coluna_inicial, coluna_final in coordenadas_palavras:
            linha_topo = max(0, linha_inicial - 1)
            linha_inf = min(altura - 1, linha_final + 1)
            coluna_esq = max(0, coluna_inicial - 1)
            coluna_dir = min(largura - 1, coluna_final + 1)

            for coluna in range(coluna_esq, coluna_dir + 1):
                matriz[linha_topo][coluna] = 1
                matriz[linha_inf][coluna] = 1

            for linha in range(linha_topo, linha_inf + 1):
                matriz[linha][coluna_esq] = 1
                matriz[linha][coluna_dir] = 1

        return matriz


    def _extract_blocks_gaps(
            self,
            vetor_projecao: Sequence[int] | Sequence[float]
        ) -> Tuple[list[Tuple[int, int]], list[int]]:
        """Analisa um vetor de projeção (soma de pixels) e retorna:

        - blocos: lista de tuplas (inicio, fim) onde há texto.
        - gaps: lista de inteiros com o tamanho do espaço vazio entre os blocos.
        """
        blocos: list[Tuple[int, int]] = []
        gaps = []
        em_bloco = False
        inicio_bloco = 0
        fim_ultimo_bloco= -1

        for i, valor in enumerate(vetor_projecao):
            if valor > 0 and not em_bloco:
                em_bloco = True
                inicio_bloco = i

                # Se já passou por um bloco antes, o que ficou para trás foi um gap
                if fim_ultimo_bloco != -1:
                    gaps.append(inicio_bloco - fim_ultimo_bloco - 1)

            elif valor == 0 and em_bloco:
                em_bloco = False
                blocos.append((inicio_bloco, i - 1))
                fim_ultimo_bloco = i - 1

        # Fechar o último bloco se a imagem terminar com texto
        if em_bloco:
            blocos.append((inicio_bloco, len(vetor_projecao) - 1))

        return blocos, gaps
    

    def analyze_text(self, imagem: 'PBMImage') -> list:
        """
        Faz a contagem isolada e retorna as coordenadas de cada palavra
        """
        matriz = imagem.matriz
        projecao_colunas = [sum(coluna) for coluna in zip(*matriz)]
        blocos_colunas, _ = self._extract_blocks_gaps(projecao_colunas)

        total_linhas = 0
        total_palavras = 0
        coordenadas_palavras = []

        for c_inicio, c_fim in blocos_colunas:
            fatia_coluna = matriz[:, c_inicio:c_fim + 1]

            projecao_linhas = [sum(linha) for linha in matriz]
            blocos_linhas, _ = self._extract_blocks_gaps(projecao_linhas)
            total_linhas += len(blocos_linhas)

            for l_inicio, l_fim in blocos_linhas:
                fatia_linha = fatia_coluna[l_inicio:l_fim + 1, :]

                projecao_letras = [sum(coluna) for coluna in zip(*fatia_linha)]
                blocos_letras, gaps_letras = self._extract_blocks_gaps(projecao_letras)

                altura_linha = l_fim - l_inicio + 1
                threshold = self._gap_threshold(gaps_letras, altura_referencia=altura_linha)

                palavra_c_inicio = blocos_letras[0][0]
                palavra_c_fim = blocos_letras[0][1]

                for i in range(1, len(blocos_letras)):
                    gap_atual = gaps_letras[i-1]

                    if gap_atual > threshold:
                        # Gap grande = 1 palavra
                        coordenadas_palavras.append((l_inicio, l_fim, c_inicio + palavra_c_inicio, c_inicio + palavra_c_fim))

                        # inicia próxima palavra
                        palavra_c_inicio = blocos_letras[i][0]
                        palavra_c_fim = blocos_letras[i][1]

                    else:
                        # Gap pequeno = mesma palavras
                        palavra_c_fim = blocos_letras[i][1]

                coordenadas_palavras.append((l_inicio, l_fim, c_inicio + palavra_c_inicio, c_inicio + palavra_c_fim))
                total_palavras += 1

        print(f"Resultados encontrados:")
        print(f"Colunas: {len(blocos_colunas)}")
        print(f"Linhas: {total_linhas}")
        print(f"Palavras: {total_palavras}")

        return coordenadas_palavras
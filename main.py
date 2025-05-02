import numpy as np
from PIL import Image
import pandas as pd
import json
import matplotlib.pyplot as plt
import os


def visualizar_com_matplotlib(matriz, caminho_imagem, output_dir='output'):
    """Visualização precisa onde todos os pontos aparecem no heatmap e salva a imagem"""
    os.makedirs(output_dir, exist_ok=True)

    img = Image.open(caminho_imagem)
    dpi = 100
    fig = plt.figure(figsize=(14, 10), dpi=dpi)

    matriz_heatmap = np.copy(matriz)
    matriz_heatmap[matriz_heatmap > 0] = 1

    plt.imshow(img, alpha=0.8)
    heatmap = plt.imshow(matriz_heatmap,
                         cmap='magma',
                         alpha=0.9,
                         interpolation='none',
                         vmin=0,
                         vmax=1)

    pontos_heatmap = np.sum(matriz_heatmap)
    ys, xs = np.where(matriz == 1)
    pontos_scatter = len(xs)

    if pontos_heatmap != pontos_scatter:
        print(f"AVISO: Discrepância detectada - Heatmap:{pontos_heatmap} vs Scatter:{pontos_scatter}")
        matriz_heatmap = np.zeros_like(matriz)
        for y, x in zip(ys, xs):
            matriz_heatmap[y, x] = 1
        plt.imshow(matriz_heatmap, cmap='hot', alpha=0.9, interpolation='none')

    fator_correcao = 0.35
    pixel_size = (72. / dpi) * fator_correcao
    plt.scatter(xs, ys,
                color='cyan',
                s=pixel_size,
                alpha=0.6,
                edgecolors='none',
                label=f'Pontos (n={len(xs)})')

    plt.colorbar(heatmap, label='Intensidade do Gaze')
    plt.title(f"Mapa de Calor Preciso - {os.path.basename(caminho_imagem)}")
    plt.legend()

    nome_base = os.path.splitext(os.path.basename(caminho_imagem))[0]
    output_path = os.path.join(output_dir, f"{nome_base}_heatmap.png")

    plt.savefig(output_path, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
    plt.show()
    plt.close()

def criar_matriz_gaze(caminho_imagem, pontos_gaze):
    """Cria matriz binária do tamanho da imagem com 1's nos pontos de gaze"""
    with Image.open(caminho_imagem) as img:
        largura, altura = img.size
        print(f"\nDimensões da imagem {os.path.basename(caminho_imagem)}: {largura}x{altura} pixels")

        matriz = np.zeros((altura, largura), dtype=np.uint8)
        pontos_validos = 0

        for ponto in pontos_gaze:
            try:
                x = int(round(float(ponto['x'])))
                y = int(round(float(ponto['y'])))

                if 0 <= x < largura and 0 <= y < altura:
                    print(f"Marcando ponto: ({y}, {x})")
                    matriz[y, x] = 1
                    pontos_validos += 1

            except (ValueError, KeyError) as e:
                print(f"Erro no ponto {ponto}: {str(e)}")
                continue

        print(f"Pontos válidos marcados: {pontos_validos}/{len(pontos_gaze)}")
        return matriz


def processar_dados_gaze(caminho_csv, imagens_alvo=None, pasta_imagens='./'):
    """
    Processa o CSV e retorna um dicionário {caminho_imagem: [pontos]}

    Args:
        caminho_csv: Caminho para o arquivo CSV
        imagens_alvo: Lista de imagens para filtrar (ex: ['/001.jpg', '/002.jpg'])
        pasta_imagens: Caminho base onde as imagens estão armazenadas
    """
    df = pd.read_csv(caminho_csv)

    if imagens_alvo:
        df = df[df['path'].isin(imagens_alvo)].copy()

    dados_por_imagem = {}

    for _, linha in df.iterrows():
        if pd.isna(linha['webgazer_data']) or pd.isna(linha['path']):
            continue

        try:
            # Constrói o caminho completo da imagem
            nome_imagem = os.path.basename(linha['path'])
            caminho_completo = os.path.join(pasta_imagens, nome_imagem)

            pontos = json.loads(linha['webgazer_data'])

            if caminho_completo not in dados_por_imagem:
                dados_por_imagem[caminho_completo] = []

            dados_por_imagem[caminho_completo].extend([
                {'x': p['x'], 'y': p['y'], 't': p['t']}
                for p in pontos
            ])

        except json.JSONDecodeError:
            print(f"Erro no JSON para {linha['path']}")
            continue

    return dados_por_imagem


if __name__ == "__main__":
    # Configurações
    caminho_csv = './eye-tracking-data.csv'
    imagens_alvo = ['/001.jpg', '/002.jpg']
    pasta_imagens = './images'

    # Processa os dados
    dados_por_imagem = processar_dados_gaze(
        caminho_csv=caminho_csv,
        imagens_alvo=imagens_alvo,
        pasta_imagens=pasta_imagens
    )

    # Processa cada imagem
    for caminho_imagem, pontos in dados_por_imagem.items():
        if not os.path.exists(caminho_imagem):
            print(f"\nAVISO: Imagem {caminho_imagem} não encontrada!")
            continue

        print(f"\nProcessando {caminho_imagem}...")
        print(f"Total de pontos: {len(pontos)}")

        # Cria matriz de gaze
        matriz = criar_matriz_gaze(caminho_imagem, pontos)

        # Estatísticas
        print(f"Pontos marcados na matriz: {np.sum(matriz)}")
        print(f"Porcentagem de cobertura: {np.sum(matriz) / len(pontos) * 100:.2f}%")

        # Visualização
        visualizar_com_matplotlib(matriz, caminho_imagem)

        # Salva a matriz
        nome_arquivo = f"matriz_gaze_{os.path.basename(caminho_imagem).replace('.jpg', '')}.npy"
        np.save(nome_arquivo, matriz)
        print(f"Matriz salva em {nome_arquivo}")
import numpy as np
from PIL import Image
import pandas as pd
import json
import matplotlib.pyplot as plt
import os
import shutil
from pathlib import Path
import glob
from scipy.ndimage import gaussian_filter

def visualizar_com_matplotlib(matriz, caminho_imagem, output_dir='output', smoothing_sigma=15):
    """
    Visualiza os pontos de gaze sobre a imagem e gera um heatmap.

    Args:
        matriz (np.array): Matriz de contagem de gaze (pontos 1 onde houve gaze).
        caminho_imagem (str): Caminho completo para a imagem de fundo.
        output_dir (str): Diretório para salvar as imagens de saída.
        smoothing_sigma (float): Desvio padrão para o filtro Gaussiano do heatmap.
                                 Valores maiores = heatmap mais suave e espalhado.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    img = Image.open(caminho_imagem).convert("RGBA")
    
    original_img_width, original_img_height = img.size

   
    heatmap_data = gaussian_filter(matriz.astype(float), sigma=smoothing_sigma)
    
 
    if heatmap_data.max() > 0:
        heatmap_data = heatmap_data / heatmap_data.max()
    else:
        heatmap_data = np.zeros_like(matriz, dtype=float)

    dpi = 100
    fig, ax = plt.subplots(figsize=(original_img_width / dpi, original_img_height / dpi), dpi=dpi)

  
    ax.imshow(img, extent=[0, original_img_width, original_img_height, 0], alpha=1.0)

  
    heatmap = ax.imshow(heatmap_data,
                         cmap='hot',
                         alpha=0.7,
                         interpolation='bilinear',
                         extent=[0, original_img_width, original_img_height, 0],
                         vmin=0, # Garante que a escala de cor comece do zero
                         vmax=1) # Garante que a escala de cor vá até o máximo normalizado

   
    ys_scatter, xs_scatter = np.where(matriz == 1)
    
   
    ax.scatter(xs_scatter, ys_scatter, c='blue', s=20, alpha=0.5, label='Pontos de Gaze')

    ax.set_ylim(original_img_height, 0)
    ax.set_xlim(0, original_img_width)

    plt.colorbar(heatmap, ax=ax, label='Densidade do Gaze (Normalizada)')
    
    plt.title(f"Heatmap e Pontos de Gaze - {os.path.basename(caminho_imagem)}")
    
    ax.legend(loc='upper right')

    ax.set_xticks([])
    ax.set_yticks([])

    nome_base = os.path.splitext(os.path.basename(caminho_imagem))[0]
    output_path = os.path.join(output_dir, f"{nome_base}_gaze_analysis.png")

    plt.savefig(output_path, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
    plt.show()
    plt.close(fig) # Fecha a figura para liberar memória
    print("Imagem salva com sucesso em:", output_path)


def criar_matriz_gaze(caminho_imagem, pontos_gaze, width_target, height_target):
    print(f"\nDimensões do alvo para {Path(caminho_imagem).name}: {width_target}x{height_target} pixels")

    matriz = np.zeros((height_target, width_target), dtype=np.uint8)
    pontos_validos = 0

    for ponto in pontos_gaze:
        try:
            x = int(round(float(ponto['x'])))
            y = int(round(float(ponto['y'])))

            if 0 <= x < width_target and 0 <= y < height_target:
                matriz[y, x] = 1
                pontos_validos += 1

        except (ValueError, KeyError) as e:
            print(f"Erro no ponto {ponto}: {str(e)}")
            continue

    print(f"Pontos válidos marcados: {pontos_validos}/{len(pontos_gaze)}")
    return matriz


def processar_dados_gaze(caminho_csv, pasta_imagens='./'):
    df = pd.read_csv(caminho_csv)
    dados_por_imagem = {}

    imagens_disponiveis = {img.name: img for img in Path(pasta_imagens).rglob('*') if
                           img.suffix.lower() in ['.jpg', '.jpeg', '.png']}

    for _, linha in df.iterrows():
        if pd.isna(linha['webgazer_data']) or pd.isna(linha['path']) or pd.isna(linha['webgazer_targets']):
            continue

        try:
            nome_imagem = Path(linha['path']).name
            if nome_imagem not in imagens_disponiveis:
                continue

            caminho_completo = str(imagens_disponiveis[nome_imagem])

            pontos = json.loads(linha['webgazer_data'])

            targets = json.loads(linha['webgazer_targets'])
            width = targets["#jspsych-image-keyboard-response-stimulus"]["width"]
            height = targets["#jspsych-image-keyboard-response-stimulus"]["height"]

            print(height, width)
            if caminho_completo not in dados_por_imagem:
                dados_por_imagem[caminho_completo] = {
                    'pontos': [],
                    'width': width,
                    'height': height
                }

            dados_por_imagem[caminho_completo]['pontos'].extend([
                {'x': p['x'], 'y': p['y'], 't': p['t']}
                for p in pontos
            ])

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Erro ao processar {linha['path']}: {str(e)}")
            continue

    return dados_por_imagem


def sync_images(src_dir, dest_dir):
    src_path = Path(src_dir)
    dest_path = Path(dest_dir)

    dest_path.mkdir(parents=True, exist_ok=True)

    for src_file in src_path.glob('**/*'):
        if src_file.is_file():
            relative_path = src_file.relative_to(src_path)
            dest_file = dest_path / relative_path

            dest_file.parent.mkdir(parents=True, exist_ok=True)

            if not dest_file.exists() or os.stat(src_file).st_mtime > os.stat(dest_file).st_mtime:
                shutil.copy2(src_file, dest_file)
                print(f"Copiado: {src_file} -> {dest_file}")


def processar_todos_csv(diretorio_csv, pasta_imagens):
    # Lista todos os arquivos CSV no diretório
    arquivos_csv = glob.glob(f"{diretorio_csv}/*.csv")
    Path("matriz_gazes").mkdir(exist_ok=True)

    if not arquivos_csv:
        print("Nenhum arquivo CSV encontrado no diretório!")
        return

    for caminho_csv in arquivos_csv:
        print(f"\n--- Processando {Path(caminho_csv).name} ---")
        csvfile = Path(caminho_csv).stem

        output_dir = Path(f'matriz_gazes/{csvfile}')
        output_dir.mkdir(exist_ok=True)

        # Processa dados
        dados_por_imagem = processar_dados_gaze(caminho_csv, pasta_imagens)

        for caminho_imagem, dados in dados_por_imagem.items():
            pontos = dados['pontos']
            width = dados['width']
            height = dados['height']

            print(f"\nProcessando imagem: {Path(caminho_imagem).name}")
            print(f"Dimensões do alvo: {width}x{height}")
            print(f"Total de pontos de gaze: {len(pontos)}")

            matriz = criar_matriz_gaze(caminho_imagem, pontos, width, height)

            nome_arquivo = f"{Path(caminho_imagem).stem}_{Path(caminho_csv).stem}.npy"
            caminho_saida = output_dir / nome_arquivo
            np.save(str(caminho_saida), matriz)
            print(f"Matriz salva em: {caminho_saida}")

            print(f"Nome do CSV: {csvfile}")
            visualizar_com_matplotlib(matriz, caminho_imagem, csvfile)

    print("\nProcessamento concluído para todos os arquivos CSV!")



if __name__ == "__main__":
    pasta_imagens = './imagens'
    src_diret = "../imagens"

    diretorio_csv = './dados_eye_tracking'

    sync_images(src_diret, pasta_imagens)

    processar_todos_csv(diretorio_csv, pasta_imagens)
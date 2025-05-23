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
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    img = Image.open(caminho_imagem).convert("RGBA")
    
    original_img_width, original_img_height = img.size

    if matriz.size == 0 or matriz.shape[0] == 0 or matriz.shape[1] == 0:
        print(f"AVISO: Matriz de gaze vazia ou com dimensão zero para {Path(caminho_imagem).name}. Nenhuma visualização gerada.")
        return 
   
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
                         vmin=0, 
                         vmax=1) 

   
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
    plt.close(fig) 
    print("Imagem salva com sucesso em:", output_path)

# --- FUNÇÃO criar_matriz_gaze (ALTERADA CRITICAMENTE) ---
# Agora recebe pontos_gaze_brutos e informações do alvo na tela
def criar_matriz_gaze(caminho_imagem, pontos_gaze_brutos, target_rect_info, width_img, height_img):
    print(f"\nDimensões da imagem para {Path(caminho_imagem).name}: {width_img}x{height_img} pixels")
    print(f"Dimensões do alvo na tela: X={target_rect_info['x']}, Y={target_rect_info['y']}, Width={target_rect_info['width']}, Height={target_rect_info['height']}")


   
    if target_rect_info['width'] <= 0 or target_rect_info['height'] <= 0:
        print(f"AVISO: Dimensões do estímulo na tela inválidas para {Path(caminho_imagem).name}. Gaze relativa não pode ser calculada.")
        return np.zeros((0,0), dtype=np.uint8) 

    matriz = np.zeros((height_img, width_img), dtype=np.uint8) # Matriz agora tem o tamanho da imagem original
    pontos_validos = 0

    for ponto_bruto in pontos_gaze_brutos: 
        try:
            
            x_relative_pct = (ponto_bruto['x'] - target_rect_info['left']) / target_rect_info['width'] * 100
            y_relative_pct = (ponto_bruto['y'] - target_rect_info['top']) / target_rect_info['height'] * 100

            x_pixel = int(round(x_relative_pct / 100 * width_img))
            y_pixel = int(round(y_relative_pct / 100 * height_img))

            if 0 <= x_pixel < width_img and 0 <= y_pixel < height_img:
                matriz[y_pixel, x_pixel] = 1 # Usa as coordenadas em pixel
                pontos_validos += 1
            else:
                
                print(f"Ponto de gaze ({x_pixel},{y_pixel}) fora das dimensões da imagem ({width_img}x{height_img}).")


        except (ValueError, KeyError) as e:
            print(f"Erro no ponto bruto {ponto_bruto}: {str(e)}")
            continue

    print(f"Pontos válidos marcados: {pontos_validos}/{len(pontos_gaze_brutos)}")
    return matriz

def processar_dados_gaze(caminho_csv, pasta_imagens='./'):
    df = pd.read_csv(caminho_csv, sep=',', quotechar='"')
    dados_por_imagem = {}

    imagens_disponiveis = {img.name: img for img in Path(pasta_imagens).rglob('*') if
                           img.suffix.lower() in ['.jpg', '.jpeg', '.png']}

    for _, linha in df.iterrows():
       
        if pd.isna(linha['webgazer_data']) or pd.isna(linha['webgazer_targets']) or pd.isna(linha['original_filename']):
            continue

        try:
            nome_imagem = linha['original_filename']
            
            if nome_imagem not in imagens_disponiveis:
                print(f"Aviso: Imagem '{nome_imagem}' não encontrada na pasta de imagens locais. Pulando.")
                continue

            caminho_completo = str(imagens_disponiveis[nome_imagem])
            
            pontos_brutos = json.loads(linha['webgazer_data'])
            target_info_json = json.loads(linha['webgazer_targets'])
                      
            
            target_rect_info = None
            if "#jspsych-image-keyboard-response-stimulus" in target_info_json:
                target_rect_info = target_info_json["#jspsych-image-keyboard-response-stimulus"]
            elif "#jspsych-video-keyboard-response-stimulus" in target_info_json:
                target_rect_info = target_info_json["#jspsych-video-keyboard-response-stimulus"]
            
            if target_rect_info is None:
                print(f"Aviso: Alvo do estímulo não encontrado no webgazer_targets para '{nome_imagem}'. Pulando.")
                continue

            with Image.open(caminho_completo) as img_temp:
                img_width, img_height = img_temp.size

            print(f"Processando trial para '{nome_imagem}': Dimensões da imagem original {img_width}x{img_height}")

            if target_rect_info['width'] <= 0 or target_rect_info['height'] <= 0:
                print(f"AVISO: Dimensões do estímulo na tela (do CSV) inválidas para '{nome_imagem}' (Width: {target_rect_info['width']}, Height: {target_rect_info['height']}). Pulando.")
                continue 

            if caminho_completo not in dados_por_imagem:
                dados_por_imagem[caminho_completo] = {
                    'pontos_brutos': [],
                    'target_info': {},
                    'width_img': img_width,
                    'height_img': img_height
                }

            dados_por_imagem[caminho_completo]['pontos_brutos'].extend(pontos_brutos)
            dados_por_imagem[caminho_completo]['target_info'] = target_rect_info


        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            print(f"Erro ao processar linha para '{linha.get('original_filename', 'N/A')}': {str(e)}")
            print(f"Linha problemática: {linha.to_dict()}")
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

        dados_por_imagem = processar_dados_gaze(caminho_csv, pasta_imagens)

        for caminho_imagem, dados in dados_por_imagem.items():
            pontos_brutos = dados['pontos_brutos']
            target_info = dados['target_info'] # Pega as informações do alvo da tela
            width_img = dados['width_img']
            height_img = dados['height_img']

            print(f"\nProcessando imagem: {Path(caminho_imagem).name}")
            print(f"Dimensões da imagem original: {width_img}x{height_img}")
            print(f"Total de pontos de gaze brutos: {len(pontos_brutos)}")

            matriz = criar_matriz_gaze(caminho_imagem, pontos_brutos, target_info, width_img, height_img)

            if matriz.size > 0: 
                nome_arquivo = f"{Path(caminho_imagem).stem}_{Path(caminho_csv).stem}.npy"
                caminho_saida = output_dir / nome_arquivo
                np.save(str(caminho_saida), matriz)
                print(f"Matriz salva em: {caminho_saida}")

                visualizar_com_matplotlib(matriz, caminho_imagem, str(output_dir)) 
            else:
                print(f"AVISO: Nenhuma matriz válida criada para {Path(caminho_imagem).name}. Pulando salvamento e visualização.")

    print("\nProcessamento concluído para todos os arquivos CSV!")

if __name__ == "__main__":
    pasta_imagens = './imagens_originais' 
    src_diret = "../imagens" 

    diretorio_csv = './dados_eye_tracking'

    sync_images(src_diret, pasta_imagens) 

    processar_todos_csv(diretorio_csv, pasta_imagens)
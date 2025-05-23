Projeto Eye-Tracking com JsPsych (WebGazer)
Este projeto implementa um experimento de eye-tracking (rastreamento ocular) baseado na web, utilizando a biblioteca JsPsych e a extensão WebGazer.js para capturar dados de olhar via webcam. A aplicação é construída com Vite, React e TypeScript, e os dados coletados podem ser analisados offline com scripts Python para gerar heatmaps.
🚀 Funcionalidades
Rastreamento Ocular Baseado em Webcam: Utiliza o WebGazer.js para estimar a localização do olhar do participante na tela.
Calibração e Validação Interativa: Inclui etapas de calibração por clique e validação de precisão para garantir a qualidade dos dados, com feedback visual ao participante.
Recalibração Condicional: Oferece tentativas de recalibração automática se a precisão inicial não for satisfatória.
Upload Dinâmico de Estímulos: Permite que o usuário faça o upload de imagens no navegador para serem usadas como estímulos no experimento.
Exportação de Dados: Os dados brutos do experimento são automaticamente salvos em um arquivo CSV local.
Geração de Heatmaps (Python): Script Python para processar os dados CSV e gerar heatmaps, visualizando a densidade do olhar sobre as imagens de estímulo.
Desenvolvimento Moderno: Construído com Vite, React e TypeScript para uma experiência de desenvolvimento rápida e segura.
🛠️ Tecnologias Utilizadas
Frontend:
Vite: Ferramenta de build rápida e eficiente.
React: Biblioteca JavaScript para construção de interfaces de usuário.
TypeScript: Superset do JavaScript que adiciona tipagem estática.
JsPsych: Framework para criação de experimentos de psicologia e neurociência baseados na web.
WebGazer.js: Biblioteca de eye-tracking via webcam (versão fork do JsPsych).
Análise de Dados (Offline):
Python: Linguagem de programação.
NumPy: Biblioteca para computação numérica.
Pandas: Biblioteca para análise e manipulação de dados.
Matplotlib: Biblioteca para criação de gráficos (usada para heatmaps).
PIL (Pillow): Biblioteca para processamento de imagens.
⚙️ Como Configurar e Rodar
Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.
1. Pré-requisitos
Node.js e npm (ou Yarn): Certifique-se de ter o Node.js (versão 20 ou superior recomendada) e o npm (ou Yarn) instalados.
Python: Certifique-se de ter o Python (versão 3.8 ou superior recomendada) instalado.
Git: Para clonar o repositório.
2. Configuração do Projeto
Clone o repositório:
git clone [URL_DO_SEU_REPOSITORIO]
cd [pasta_do_seu_projeto]

(Substitua [URL_DO_SEU_REPOSITORIO] e [pasta_do_seu_projeto] pelos valores corretos).
Instale as dependências do Frontend:
npm install
# ou
yarn install


Instale as dependências do Python:
É recomendável criar um ambiente virtual Python para suas dependências.
python -m venv venv
# No Windows:
# .\venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate

pip install numpy pandas matplotlib Pillow scipy


3. Rodando o Experimento (Frontend)
Inicie o servidor de desenvolvimento:
npm run dev
# ou
yarn dev


A aplicação será aberta no seu navegador (geralmente em http://localhost:5173).
Permita o acesso à webcam quando solicitado.
Faça o upload das suas imagens e siga as instruções para calibração e para rodar o experimento.
Ao final do experimento, um arquivo .csv contendo os dados do eye-tracking será salvo automaticamente em sua pasta de downloads.
4. Gerando Heatmaps (Python)
Após coletar os dados CSV, você pode usar o script Python para gerar heatmaps.
Organize suas pastas de dados:
Crie uma pasta chamada dados_eye_tracking na raiz do seu projeto.
Mova todos os arquivos .csv gerados pelo experimento para dentro dessa pasta (ex: eye-tracking-data.csv, eye-tracking-data (2).csv).
Crie uma pasta chamada imagens_originais na raiz do seu projeto.
Coloque todas as imagens originais que foram utilizadas como estímulos no experimento dentro dessa pasta. O script precisa dessas imagens para desenhar os heatmaps sobre elas.
Execute o script de heatmap:
No terminal (com o ambiente virtual Python ativado), na raiz do seu projeto, execute:
python main.py


Resultados:
Uma nova pasta chamada matriz_gazes será criada na raiz do seu projeto.
Dentro dela, para cada arquivo CSV processado, uma subpasta (com o nome do CSV) será criada.
Os heatmaps gerados (arquivos .png) e as matrizes de gaze (.npy) serão salvos nessas subpastas.
5. Docker (Opcional: Para Ambiente de Produção)
Você pode construir e rodar a aplicação frontend em um contêiner Docker para um ambiente de produção ou para garantir consistência de ambiente.
Construa a imagem Docker:
No diretório raiz do projeto (onde está o Dockerfile), execute:
docker build -t eye-tracking-app .


Execute o contêiner Docker:
docker run -p 80:5173 eye-tracking-app

Isso mapeia a porta 80 do seu host (máquina local) para a porta 5173 do contêiner. Você pode acessar a aplicação em http://localhost.
💡 Dicas para Melhorar a Precisão do Eye-Tracking
Para obter os melhores resultados com o WebGazer.js:
Iluminação: Realize o experimento em um ambiente bem iluminado, mas evite luz forte diretamente atrás do participante (contra-luz), que pode criar sombras ou reflexos.
Posicionamento da Cabeça: O participante deve manter a cabeça o mais parada possível durante a calibração e a coleta de dados.
Distância da Câmera: Mantenha uma distância consistente da webcam.
Feche Outros Programas: Peça aos participantes para fechar outros aplicativos e abas do navegador não essenciais para liberar recursos do sistema.
Feedback Visual: As bolinhas de previsão de olhar durante a calibração são essenciais. Incentive o participante a tentar fazer com que a bolinha siga seu olhar com precisão.
🤝 Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

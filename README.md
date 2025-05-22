# Dados visualizados


## Configuração do Ambiente

Para garantir que o projeto funcione corretamente e para gerenciar as dependências de forma isolada, é altamente recomendável criar e ativar um ambiente virtual. Siga os passos abaixo:

### 1. Navegar até o Diretório do Projeto

Abra o terminal ou prompt de comando e **navegue até a pasta raiz do seu projeto `heatmapp_tcc`**.

```bash
cd /caminho/para/o/seu/projeto/heatmapp_tcc
```
*(Lembre-se de substituir `/caminho/para/o/seu/projeto/heatmapp_tcc` pelo caminho real da sua pasta.)*

### 2. Criar o Ambiente Virtual

Dentro do diretório do projeto, execute o seguinte comando para **criar um ambiente virtual**. Por convenção, o ambiente virtual é geralmente nomeado `venv`.

```bash
python -m venv venv
```

* `python`: Invoca o interpretador Python.
* `-m venv`: Indica ao Python para executar o módulo `venv`, que é usado para criar ambientes virtuais.
* `venv`: É o nome da pasta que será criada para conter o ambiente virtual.

### 3. Ativar o Ambiente Virtual

Após a criação, você precisa **ativar o ambiente virtual**. Os comandos para ativação variam ligeiramente dependendo do seu sistema operacional:

#### No Windows:

```bash
.\venv\Scripts\activate
```

#### No macOS/Linux:

```bash
source venv/bin/activate
```

Ao ativar o ambiente virtual, você notará que o nome do ambiente (geralmente `(venv)`) aparecerá no início da linha de comando, indicando que ele está ativo.

### 4. Instalar as Dependências

Com o ambiente virtual ativo, você pode **instalar todas as bibliotecas e pacotes necessários para o projeto**. As dependências devem estar listadas em um arquivo `requirements.txt`.

```bash
pip install -r requirements.txt
```
*(**Importante**: Se você ainda não tem um `requirements.txt`, precisará criá-lo com as bibliotecas que seu projeto usa. Você pode fazer isso após instalar o que precisa com `pip freeze > requirements.txt`)*

### 5. Desativar o Ambiente Virtual (Opcional)

Quando terminar de trabalhar no projeto e quiser sair do ambiente virtual, basta digitar:

```bash
deactivate
```

**Lembre-se:** Sempre ative o ambiente virtual antes de executar qualquer script ou comando relacionado ao projeto para garantir que as dependências corretas sejam usadas.

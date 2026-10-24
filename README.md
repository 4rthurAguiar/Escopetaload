# 🎯 EscopetaLoad

<div align="center">
  <img src="assets/icon.png" width="128" height="128" alt="Logo EscopetaLoad" />
  <p><strong>Downloader moderno e descomplicado de vídeos e áudios para YouTube e Instagram.</strong></p>
</div>

---

## ⚡ Visão Geral

O **EscopetaLoad** é um aplicativo desktop moderno para Windows construído com **CustomTkinter** e alimentado pelo motor **yt-dlp**. Ele oferece uma experiência de download rápida, segura e elegante para baixar vídeos e extrair áudios em MP3 sem travar a interface gráfica.

---

## ✨ Funcionalidades

- **YouTube & Instagram:**
  - YouTube: vídeos padrão, Shorts, transmissões ao vivo gravadas e links encurtados (`youtu.be`).
  - Instagram: Reels, Posts de vídeo e IGTV.
- **Opções de Qualidade e Formato:**
  - *Melhor Qualidade* (resolução máxima disponível com áudio mixado).
  - *720p* (ideal para downloads rápidos e economia de espaço).
  - *Apenas Áudio (MP3)* (extrai áudio em alta fidelidade a 192 kbps).
- **Suporte Inteligente a FFmpeg:**
  - Localização automática do `ffmpeg.exe` (no pacote compilado, no PATH do sistema, em pastas locais ou no WinGet).
- **Detecção Automática de Cookies:**
  - Identifica navegadores instalados no sistema (Brave, Edge, Chrome, Firefox, Opera) para mitigar bloqueios anti-bot do YouTube.
- **Controle de Destino:**
  - Escolha personalizada da pasta onde os arquivos serão salvos (iniciando por padrão na pasta oficial `Downloads` do usuário).
  - Botão integrado para abrir a pasta diretamente no Windows Explorer.
- **Identidade Visual no Windows:**
  - Ícone personalizado na barra de título e na barra de tarefas do Windows via `AppUserModelID`.

---

## 🚀 Como Rodar a partir do Código-Fonte

### Pré-requisitos
- Python 3.10 ou superior instalado.
- FFmpeg (opcional para rodar via script; recomendado para conversão em MP3).

### Instalação
```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/EscopetaLoad.git
cd EscopetaLoad

# 2. Crie e ative um ambiente virtual (opcional, mas recomendado)
python -m venv venv
venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt
```

### Execução
```bash
python main.py
```

---

## 🧪 Como Rodar os Testes

O projeto possui suíte de testes unitários para validação de URLs e opções do downloader:

```bash
python -m unittest discover -s meu_video_downloader -t meu_video_downloader
```

---

## 📦 Como Compilar o Executável (.exe)

Para gerar um binário portátil independente que funcione em qualquer computador Windows (sem necessitar de Python instalado):

```bash
# Instale o PyInstaller
pip install pyinstaller

# Gere o executável
pyinstaller --noconsole --onefile `
  --name "EscopetaLoad" `
  --icon "assets/icon.ico" `
  --add-data "assets;assets" `
  --collect-all customtkinter `
  --collect-all yt_dlp `
  --paths . `
  --paths meu_video_downloader `
  main.py
```

> **Dica:** Para embutir o `ffmpeg.exe` e `ffprobe.exe` diretamente no `.exe` (tornando a conversão MP3 100% autônoma), adicione:
> `--add-binary "caminho\para\ffmpeg.exe;." --add-binary "caminho\para\ffprobe.exe;."`

O arquivo compilado final estará disponível na pasta `dist/EscopetaLoad.exe`.

---

## 📁 Estrutura do Projeto

```text
EscopetaLoad/
├── assets/                  # Ícones (.ico, .png)
├── main.py                  # Ponto de entrada raiz
├── requirements.txt         # Dependências do projeto
├── README.md                # Documentação
├── .gitignore               # Filtros do Git
└── meu_video_downloader/    # Pacote principal
    ├── main.py              # Ponto de entrada interno
    ├── requirements.txt     # Dependências internas
    ├── assets/              # Cópia dos assets para distribuição
    ├── downloads/           # Pasta padrão local (.gitkeep)
    ├── src/
    │   ├── core/            # Engine de download (yt-dlp e cookies)
    │   ├── ui/              # Interface gráfica (CustomTkinter)
    │   └── utils/           # Validadores de URL (YouTube/Instagram)
    └── tests/               # Testes unitários automatizados
```

---

## 📄 Licença

Distribuído sob a licença MIT. Consulte `LICENSE` para mais informações.

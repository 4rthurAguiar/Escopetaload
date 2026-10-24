"""
Ponto de entrada raiz do projeto EscopetaLoad.
Redireciona para o módulo principal em meu_video_downloader.
"""

import ctypes
import os
import sys

# Define AppUserModelID para o Windows exibir o ícone correto na barra de tarefas
if sys.platform == "win32":
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("escopetaload.app.1")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "meu_video_downloader")

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from meu_video_downloader.main import main

if __name__ == "__main__":
    main()

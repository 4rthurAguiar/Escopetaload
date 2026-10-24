"""
Ponto de entrada do Video Downloader.
Inicializa o aplicativo CustomTkinter e garante a existência da pasta de downloads.
"""

import ctypes
import os
import sys
from pathlib import Path

# Define AppUserModelID exclusivo no Windows antes de inicializar o CustomTkinter
if sys.platform == "win32":
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("escopetaload.app.1")
    except Exception:
        pass

# Garante que a raiz do projeto esteja no sys.path para importações relativas
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from src.ui.app import App


def main() -> None:
    # Pasta padrão de downloads do usuário no Windows
    downloads_dir = str(Path.home() / "Downloads")
    os.makedirs(downloads_dir, exist_ok=True)

    # Inicia a interface gráfica
    app = App(download_dir=downloads_dir)
    app.mainloop()


if __name__ == "__main__":
    main()

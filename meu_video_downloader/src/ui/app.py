"""
Interface Gráfica moderna com CustomTkinter para o Video Downloader.
Garante execução em background thread para manter a interface 100% responsiva.
"""

import ctypes
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
from tkinter import filedialog, messagebox, PhotoImage
from typing import Optional
import customtkinter as ctk

from src.core.downloader import VideoDownloader
from src.utils.validators import is_valid_url


class App(ctk.CTk):
    """Janela principal da aplicação de download de vídeos."""

    def __init__(self, download_dir: Optional[str] = None):
        if sys.platform == "win32":
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("escopetaload.app.1")
            except Exception:
                pass

        super().__init__()
        default_downloads = str(Path.home() / "Downloads")
        self.download_dir = download_dir if download_dir else default_downloads
        self.is_downloading = False

        # Configurações gerais da janela
        self.title("EscopetaLoad • Video Downloader")
        self.geometry("640x580")
        self.minsize(580, 520)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._setup_icon()
        self._setup_ui()

    def _get_asset_path(self, filename: str) -> Optional[str]:
        """Localiza o arquivo de asset nos diretórios conhecidos do projeto ou bundle PyInstaller."""
        candidates = []
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            meipass = Path(sys._MEIPASS)
            candidates.extend([
                meipass / "assets" / filename,
                meipass / "meu_video_downloader" / "assets" / filename,
                meipass / filename,
            ])
        current_file_dir = Path(__file__).resolve().parent
        candidates.extend([
            current_file_dir.parent.parent / "assets" / filename,
            current_file_dir.parent.parent.parent / "assets" / filename,
            Path.cwd() / "assets" / filename,
            Path.cwd() / "meu_video_downloader" / "assets" / filename,
        ])
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
        return None

    def _setup_icon(self) -> None:
        """Configura o ícone da janela e da barra de tarefas do Windows."""
        ico_path = self._get_asset_path("icon.ico")
        png_path = self._get_asset_path("icon.png")

        if ico_path and os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass

        if png_path and os.path.exists(png_path):
            try:
                self._icon_photo = PhotoImage(file=png_path)
                self.wm_iconphoto(False, self._icon_photo)
            except Exception:
                pass

    def _setup_ui(self) -> None:
        """Monta os componentes visuais na tela."""
        # Container principal com scroll caso a janela seja redimensionada
        self.main_frame = ctk.CTkFrame(self, corner_radius=12)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Cabeçalho
        self.header_title = ctk.CTkLabel(
            self.main_frame,
            text="📥 Video Downloader",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.header_title.pack(pady=(20, 5))

        self.header_subtitle = ctk.CTkLabel(
            self.main_frame,
            text="Baixe vídeos e áudios do YouTube e Instagram com facilidade",
            font=ctk.CTkFont(size=13),
            text_color="gray70",
        )
        self.header_subtitle.pack(pady=(0, 20))

        # Campo da URL
        self.url_label = ctk.CTkLabel(
            self.main_frame,
            text="URL do Vídeo:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        self.url_label.pack(fill="x", padx=30, pady=(10, 4))

        self.url_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Cole o link aqui (ex: https://www.youtube.com/watch?v=... ou Instagram Reel)",
            height=40,
            font=ctk.CTkFont(size=13),
        )
        self.url_entry.pack(fill="x", padx=30, pady=(0, 15))

        # Seção de Opções: Qualidade
        options_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=30, pady=(0, 15))

        self.quality_label = ctk.CTkLabel(
            options_frame,
            text="Qualidade / Formato:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        self.quality_label.pack(fill="x", pady=(0, 4))

        self.quality_menu = ctk.CTkOptionMenu(
            options_frame,
            values=["Melhor Qualidade", "720p", "Apenas Áudio (MP3)"],
            height=36,
        )
        self.quality_menu.set("Melhor Qualidade")
        self.quality_menu.pack(fill="x")

        # Seção da Pasta de Destino
        folder_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        folder_frame.pack(fill="x", padx=30, pady=(0, 15))

        self.folder_label = ctk.CTkLabel(
            folder_frame,
            text="Salvar em:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        self.folder_label.pack(fill="x", pady=(0, 4))

        folder_input_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        folder_input_frame.pack(fill="x")

        self.folder_entry = ctk.CTkEntry(
            folder_input_frame,
            height=36,
            font=ctk.CTkFont(size=12),
        )
        self.folder_entry.insert(0, self.download_dir)
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.choose_folder_btn = ctk.CTkButton(
            folder_input_frame,
            text="Alterar...",
            width=90,
            height=36,
            command=self.choose_download_dir,
        )
        self.choose_folder_btn.pack(side="right")

        # Botão de Ação Principal (Download)
        self.download_btn = ctk.CTkButton(
            self.main_frame,
            text="Baixar",
            height=44,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.start_download,
        )
        self.download_btn.pack(fill="x", padx=30, pady=(15, 20))

        # Barra de Progresso
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, height=14)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=30, pady=(5, 8))

        # Label de Status
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Aguardando link para download...",
            font=ctk.CTkFont(size=13),
            text_color="gray70",
            wraplength=520,
        )
        self.status_label.pack(padx=30, pady=(0, 15))

        # Rodapé: Abrir pasta de downloads
        self.open_folder_btn = ctk.CTkButton(
            self.main_frame,
            text="📁 Abrir Pasta de Downloads",
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            height=32,
            command=self.open_downloads_folder,
        )
        self.open_folder_btn.pack(pady=(5, 10))

    def _set_ui_state(self, downloading: bool) -> None:
        """Habilita ou desabilita os controles durante o download."""
        self.is_downloading = downloading
        state = "disabled" if downloading else "normal"
        self.download_btn.configure(
            state=state,
            text="Baixando..." if downloading else "Baixar"
        )
        self.quality_menu.configure(state=state)
        self.url_entry.configure(state=state)
        self.folder_entry.configure(state=state)
        self.choose_folder_btn.configure(state=state)

    def _update_progress(self, percent: float, status_msg: str) -> None:
        """Atualização de progresso thread-safe na UI."""
        def callback():
            self.progress_bar.set(max(0.0, min(1.0, percent / 100.0)))
            self.status_label.configure(text=status_msg, text_color="white")
        self.after(0, callback)

    def _on_download_success(self, title: str) -> None:
        """Callback invocado quando o download é concluído."""
        def callback():
            self._set_ui_state(False)
            self.progress_bar.set(1.0)
            self.status_label.configure(
                text=f"Concluído: {title}",
                text_color="#2ecc71"
            )
            messagebox.showinfo(
                "Sucesso",
                f"Download concluído com sucesso!\n\nArquivo: {title}\nSalvo em: {self.download_dir}"
            )
        self.after(0, callback)

    def _on_download_error(self, error_message: str) -> None:
        """Callback invocado quando o download falha."""
        def callback():
            self._set_ui_state(False)
            self.progress_bar.set(0.0)
            clean_msg = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", error_message).strip()
            self.status_label.configure(
                text=f"Erro no download: {clean_msg[:60]}...",
                text_color="#e74c3c"
            )
            messagebox.showerror(
                "Erro no Download",
                f"Ocorreu um erro ao baixar a mídia:\n\n{clean_msg}"
            )
        self.after(0, callback)

    def choose_download_dir(self) -> None:
        """Permite ao usuário escolher a pasta de destino usando o explorador."""
        chosen = filedialog.askdirectory(
            initialdir=self.download_dir,
            title="Selecione a pasta para salvar os downloads",
        )
        if chosen:
            self.download_dir = chosen
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, self.download_dir)

    def start_download(self) -> None:
        """Valida os dados e dispara a thread de download."""
        if self.is_downloading:
            return

        url = self.url_entry.get().strip()

        # Validação da URL
        if not is_valid_url(url):
            self.status_label.configure(
                text="URL inválida! Insira um link válido do YouTube ou Instagram.",
                text_color="#e74c3c"
            )
            messagebox.showwarning(
                "Link Inválido",
                "Por favor, insira uma URL válida do YouTube ou do Instagram antes de prosseguir."
            )
            return

        # Garante pasta de destino válida informada pelo usuário
        user_dir = self.folder_entry.get().strip()
        if user_dir:
            self.download_dir = user_dir
        try:
            os.makedirs(self.download_dir, exist_ok=True)
        except OSError as exc:
            self.status_label.configure(
                text="Erro: Pasta de download inválida ou inacessível.",
                text_color="#e74c3c"
            )
            messagebox.showwarning(
                "Pasta Inválida",
                f"Não foi possível acessar ou criar a pasta de download:\n\n{self.download_dir}\n\nDetalhes: {exc}"
            )
            return

        quality = self.quality_menu.get()

        self._set_ui_state(True)
        self.progress_bar.set(0.0)
        self.status_label.configure(
            text="Preparando download...",
            text_color="white"
        )

        # Dispara execução em thread separada
        download_thread = threading.Thread(
            target=self._download_worker,
            args=(url, quality),
            daemon=True,
        )
        download_thread.start()

    def _download_worker(self, url: str, quality: str) -> None:
        """Executa o download fora da thread principal para não congelar a interface."""
        try:
            downloader = VideoDownloader(
                output_dir=self.download_dir,
                progress_callback=self._update_progress,
            )
            title = downloader.download(url=url, quality=quality)
            self._on_download_success(title)
        except Exception as exc:
            self._on_download_error(str(exc))

    def open_downloads_folder(self) -> None:
        """Abre a pasta de downloads no explorador de arquivos do sistema operacional."""
        user_dir = self.folder_entry.get().strip() if hasattr(self, "folder_entry") else self.download_dir
        target_dir = user_dir if user_dir else self.download_dir
        try:
            os.makedirs(target_dir, exist_ok=True)
            abs_path = os.path.abspath(target_dir)
            if sys.platform == "win32":
                os.startfile(abs_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", abs_path])
            else:
                subprocess.Popen(["xdg-open", abs_path])
        except OSError as exc:
            messagebox.showwarning(
                "Pasta Inválida",
                f"Não foi possível acessar ou abrir a pasta especificada:\n\n{target_dir}\n\nDetalhes: {exc}"
            )
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível abrir a pasta:\n{exc}")

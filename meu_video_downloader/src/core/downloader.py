"""
Módulo core responsável pelo download de mídias encapsulando o yt-dlp.
"""

import os
import shutil
import sys
from typing import Callable, Dict, List, Optional, Any
import yt_dlp

BROWSER_PROFILE_PATHS = {
    "brave": r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data",
    "edge": r"%LOCALAPPDATA%\Microsoft\Edge\User Data",
    "chrome": r"%LOCALAPPDATA%\Google\Chrome\User Data",
    "firefox": r"%APPDATA%\Mozilla\Firefox\Profiles",
    "opera": r"%APPDATA%\Opera Software\Opera Stable",
}


def get_default_browser() -> Optional[str]:
    """Tenta identificar o navegador padrão do sistema no Windows via registro."""
    if sys.platform != "win32":
        return None
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice"
        ) as key:
            prog_id, _ = winreg.QueryValueEx(key, "ProgId")
            prog_id_lower = prog_id.lower()
            for b in ("brave", "edge", "msedge", "chrome", "firefox", "opera"):
                if b in prog_id_lower:
                    return "edge" if b == "msedge" else b
    except Exception:
        pass
    return None


def get_ffmpeg_path() -> Optional[str]:
    """
    Localiza o binário do ffmpeg para suportar conversões de mídia:
    1. No diretório extraído do PyInstaller (sys._MEIPASS)
    2. No diretório do executável / projeto local
    3. No PATH do sistema operacional
    4. Em instalações conhecidas do Windows (ex: WinGet do yt-dlp)
    """
    # 1. Bundle do PyInstaller
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bundle_dir = sys._MEIPASS
        for candidate in (
            os.path.join(bundle_dir, "ffmpeg.exe"),
            os.path.join(bundle_dir, "bin", "ffmpeg.exe"),
            os.path.join(bundle_dir, "assets", "ffmpeg.exe"),
        ):
            if os.path.isfile(candidate):
                return candidate

    # 2. PATH do sistema
    which_ffmpeg = shutil.which("ffmpeg")
    if which_ffmpeg:
        return which_ffmpeg

    # 3. Diretório do executável ou projeto
    app_dir = os.path.dirname(os.path.abspath(sys.argv[0])) if sys.argv else os.getcwd()
    for candidate in (
        os.path.join(app_dir, "ffmpeg.exe"),
        os.path.join(app_dir, "bin", "ffmpeg.exe"),
        os.path.join(os.path.dirname(__file__), "..", "..", "assets", "ffmpeg.exe"),
        os.path.join(os.path.dirname(__file__), "..", "..", "bin", "ffmpeg.exe"),
    ):
        if os.path.isfile(candidate):
            return os.path.abspath(candidate)

    # 4. WinGet local no Windows
    winget_packages = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages")
    if os.path.isdir(winget_packages):
        for root, _, files in os.walk(winget_packages):
            if "ffmpeg.exe" in files:
                return os.path.join(root, "ffmpeg.exe")

    return None


def get_candidate_browsers() -> List[str]:
    """Retorna lista priorizada de navegadores instalados com perfis no sistema."""
    candidates: List[str] = []
    default = get_default_browser()
    if default:
        candidates.append(default)

    for b, path_tmpl in BROWSER_PROFILE_PATHS.items():
        if b not in candidates:
            expanded = os.path.expandvars(path_tmpl)
            if os.path.exists(expanded):
                candidates.append(b)
    return candidates


class VideoDownloader:
    """
    Controlador de downloads utilizando a engine yt-dlp.
    Oferece suporte a seleção de qualidade, cookies automáticos e monitoramento de progresso.
    """

    def __init__(
        self,
        output_dir: str = "downloads",
        progress_callback: Optional[Callable[[float, str], None]] = None,
        browser: Optional[str] = "auto",
    ):
        """
        :param output_dir: Diretório de destino para os arquivos baixados.
        :param progress_callback: Função chamada com (percentual: float, texto_status: str).
        :param browser: 'auto' para detecção automática, nome do navegador ou None para desativar cookies.
        """
        self.output_dir = output_dir
        self.progress_callback = progress_callback
        self.browser = browser

    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """Hook invocado pelo yt-dlp durante as etapas do download."""
        if not self.progress_callback:
            return

        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)

            if total > 0:
                percent = (downloaded / total) * 100.0
            else:
                raw_percent = d.get("_percent_str", "0%").replace("%", "").strip()
                try:
                    percent = float(raw_percent)
                except ValueError:
                    percent = 0.0

            speed = d.get("_speed_str", "").strip()
            eta = d.get("_eta_str", "").strip()
            ext = d.get("info_dict", {}).get("ext", "").strip()
            stream_tag = f" [{ext.upper()}]" if ext else ""

            details = []
            if speed:
                details.append(speed)
            if eta:
                details.append(f"ETA: {eta}")

            info_text = f"Baixando{stream_tag}: {percent:.1f}%"
            if details:
                info_text += f" ({', '.join(details)})"

            self.progress_callback(percent, info_text)

        elif status == "finished":
            ext = d.get("info_dict", {}).get("ext", "").strip()
            stream_tag = f" [{ext.upper()}]" if ext else ""
            self.progress_callback(100.0, f"Download{stream_tag} finalizado! Processando...")

    def _get_options(self, quality: str, browser: Optional[str] = None) -> Dict[str, Any]:
        """Gera o dicionário de opções para o YoutubeDL."""
        os.makedirs(self.output_dir, exist_ok=True)
        outtmpl = os.path.join(self.output_dir, "%(title).120s [%(id)s].%(ext)s")

        ydl_opts: Dict[str, Any] = {
            "outtmpl": outtmpl,
            "progress_hooks": [self._progress_hook],
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }

        # Configurações de qualidade e formato
        ffmpeg_bin = get_ffmpeg_path()
        has_ffmpeg = bool(ffmpeg_bin)
        if ffmpeg_bin:
            ydl_opts["ffmpeg_location"] = ffmpeg_bin

        if quality in ("Apenas Áudio (MP3)", "Audio Only"):
            ydl_opts["format"] = "bestaudio/best"
            if has_ffmpeg:
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]
        elif quality == "720p":
            ydl_opts["format"] = "bestvideo[height<=720]+bestaudio/best[height<=720]/best"
        else:  # "Melhor Qualidade" / "Best Quality"
            ydl_opts["format"] = "bestvideo+bestaudio/best"

        # Extração de cookies caso um navegador seja fornecido
        if browser:
            ydl_opts["cookiesfrombrowser"] = (browser,)

        return ydl_opts

    def _get_candidate_browsers(self) -> List[str]:
        """Retorna lista de navegadores a testar para cookies com base na configuração."""
        if self.browser == "auto":
            return get_candidate_browsers()
        elif self.browser:
            return [self.browser]
        return []

    def download(self, url: str, quality: str = "Melhor Qualidade") -> str:
        """
        Executa o download do vídeo a partir da URL.
        Retorna o título do vídeo baixado.
        """
        if self.progress_callback:
            if quality in ("Apenas Áudio (MP3)", "Audio Only") and not get_ffmpeg_path():
                self.progress_callback(0.0, "Aviso: FFmpeg não encontrado. O áudio será salvo em formato nativo.")
            else:
                self.progress_callback(0.0, "Iniciando conexão e obtendo informações...")

        candidates = self._get_candidate_browsers()

        # shortcut: tenta com cookies dos navegadores disponíveis; em falha de permissão/DPAPI/arquivo, faz fallback silencioso
        for candidate in candidates:
            try:
                opts = self._get_options(quality=quality, browser=candidate)
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get("title", "Vídeo") if info else "Vídeo"
                    if self.progress_callback:
                        self.progress_callback(100.0, "Concluído com sucesso!")
                    return title
            except Exception as exc:
                err_msg = str(exc).lower()
                if any(term in err_msg for term in ("cookie", "dpapi", "cryptography", "permission denied", "database")):
                    continue
                if any(term in err_msg for term in ("not found", "does not exist", "video unavailable", "is not a valid url")):
                    raise

        # Fallback silencioso sem cookies
        opts = self._get_options(quality=quality, browser=None)
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "Vídeo") if info else "Vídeo"
            if self.progress_callback:
                self.progress_callback(100.0, "Concluído com sucesso!")
            return title



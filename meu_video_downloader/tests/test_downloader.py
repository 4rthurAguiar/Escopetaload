"""
Testes unitários para o módulo core VideoDownloader e detecção automática de navegadores.
"""

import unittest
from unittest.mock import MagicMock, patch

from src.core.downloader import (
    VideoDownloader,
    get_default_browser,
)


class TestVideoDownloader(unittest.TestCase):
    """Valida as configurações do yt-dlp, detecção de navegadores e fallback de cookies."""

    def test_noplaylist_option_is_always_true(self):
        """Garante que a opção noplaylist está sempre ativa para não baixar playlists/mixes."""
        dl = VideoDownloader(output_dir="test_downloads")
        for quality in ("Melhor Qualidade", "720p", "Apenas Áudio (MP3)"):
            opts = dl._get_options(quality=quality)
            self.assertTrue(
                opts.get("noplaylist"),
                f"noplaylist deve ser True para a qualidade {quality}",
            )

    def test_candidate_browsers_configuration(self):
        """Verifica a lista de candidatos a cookies com base no parâmetro browser."""
        # Modo 'auto'
        dl_auto = VideoDownloader(browser="auto")
        candidates = dl_auto._get_candidate_browsers()
        self.assertIsInstance(candidates, list)

        # Modo desativado (None ou vazio)
        dl_none = VideoDownloader(browser=None)
        self.assertEqual(dl_none._get_candidate_browsers(), [])

        # Modo explícito
        dl_custom = VideoDownloader(browser="firefox")
        self.assertEqual(dl_custom._get_candidate_browsers(), ["firefox"])

    @patch("src.core.downloader.sys")
    @patch("src.core.downloader.winreg", create=True)
    def test_get_default_browser_detection(self, mock_winreg, mock_sys):
        """Verifica a detecção de navegador padrão no registro do Windows."""
        mock_sys.platform = "win32"
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
        mock_winreg.QueryValueEx.return_value = ("BraveHTML", 1)

        browser = get_default_browser()
        self.assertEqual(browser, "brave")

    @patch("yt_dlp.YoutubeDL")
    def test_download_fallback_on_cookie_failure(self, mock_ydl_class):
        """Garante que, se os cookies falharem (ex: DPAPI / lock de banco), o fallback sem cookies é executado."""
        instance_fail = MagicMock()
        instance_fail.__enter__.return_value = instance_fail
        instance_fail.extract_info.side_effect = Exception("Failed to decrypt with DPAPI")

        instance_success = MagicMock()
        instance_success.__enter__.return_value = instance_success
        instance_success.extract_info.return_value = {"title": "Vídeo Teste Fallback"}

        # Primeira chamada (com cookies de chrome) falha; segunda chamada (sem cookies) tem sucesso
        mock_ydl_class.side_effect = [instance_fail, instance_success]

        dl = VideoDownloader(browser="chrome")
        title = dl.download("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        self.assertEqual(title, "Vídeo Teste Fallback")
        self.assertEqual(mock_ydl_class.call_count, 2)

    @patch("yt_dlp.YoutubeDL")
    def test_download_propagates_non_cookie_errors(self, mock_ydl_class):
        """Garante que erros reais de vídeo inexistente não são suprimidos pelo fallback."""
        instance_fail = MagicMock()
        instance_fail.__enter__.return_value = instance_fail
        instance_fail.extract_info.side_effect = Exception("Video unavailable: this video does not exist")

        mock_ydl_class.return_value = instance_fail

        dl = VideoDownloader(browser="chrome")
        with self.assertRaises(Exception) as ctx:
            dl.download("https://www.youtube.com/watch?v=invalid_id")

        self.assertIn("video unavailable", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()

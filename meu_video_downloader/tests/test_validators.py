"""
Testes unitários para o módulo de validação de URLs (YouTube e Instagram).
"""

import unittest
from src.utils.validators import is_instagram_url, is_valid_url, is_youtube_url


class TestValidators(unittest.TestCase):
    """Testa os validadores de URL contra links suportados e entradas inválidas."""

    def test_youtube_valid_urls(self):
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "https://youtube.com/shorts/dQw4w9WgXcQ",
            "https://www.youtube.com/live/dQw4w9WgXcQ",
            "https://www.youtube.com/watch?feature=shared&v=dQw4w9WgXcQ&t=10s",
            "youtube.com/watch?v=dQw4w9WgXcQ",
            "youtu.be/dQw4w9WgXcQ",
        ]
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(is_youtube_url(url), f"Falha para YouTube URL válida: {url}")
                self.assertTrue(is_valid_url(url))

    def test_instagram_valid_urls(self):
        valid_urls = [
            "https://www.instagram.com/p/DFxyz123/",
            "https://instagram.com/p/DFxyz123",
            "https://www.instagram.com/reel/DFxyz123/",
            "https://www.instagram.com/reels/DFxyz123/",
            "https://www.instagram.com/tv/DFxyz123/",
            "https://www.instagram.com/reel/DFxyz123/?igsh=abcdef",
            "instagram.com/reel/DFxyz123",
        ]
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(is_instagram_url(url), f"Falha para Instagram URL válida: {url}")
                self.assertTrue(is_valid_url(url))

    def test_invalid_urls(self):
        invalid_urls = [
            "",
            "   ",
            "https://google.com",
            "https://twitter.com/user/status/123",
            "https://youtube.com/watch",
            "https://youtube.com/watch?v=curto",
            "https://youtube.com/about",
            "texto aleatorio",
            "https://instagram.com/usuario_perfil",
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(is_valid_url(url), f"URL inválida foi aceita: {url}")


if __name__ == "__main__":
    unittest.main()

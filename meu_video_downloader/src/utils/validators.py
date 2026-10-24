"""
Módulo de validação de URLs para YouTube e Instagram.
Utiliza análise de URL e expressões regulares para garantir links válidos antes do download.
"""

import re
from urllib.parse import parse_qs, urlparse

# RegEx para identificadores de vídeo do YouTube (11 caracteres alfanuméricos com hífens/underscores)
YOUTUBE_ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]{11}$")

# RegEx para códigos curtos (shortcodes) de posts/reels do Instagram
INSTAGRAM_CODE_REGEX = re.compile(r"^[a-zA-Z0-9_-]+$")


def is_youtube_url(url: str) -> bool:
    """
    Valida se a string fornecida corresponde a uma URL válida do YouTube
    (vídeos padrão, shorts, transmissões ao vivo ou links encurtados youtu.be).
    """
    if not url or not isinstance(url, str):
        return False

    url = url.strip()
    if not url:
        return False

    # Adiciona scheme caso o usuário tenha colado sem 'http(s)://'
    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "https://" + url

    try:
        parsed = urlparse(url)
    except Exception:
        return False

    domain = parsed.netloc.lower()
    # Remove prefixos comuns de subdomínio
    for prefix in ("www.", "m.", "music."):
        if domain.startswith(prefix):
            domain = domain[len(prefix):]

    # Validação para links encurtados youtu.be/ID
    if domain == "youtu.be":
        video_id = parsed.path.lstrip("/").split("/")[0]
        return bool(YOUTUBE_ID_REGEX.match(video_id))

    # Validação para domínios youtube.com
    if domain == "youtube.com":
        path = parsed.path.rstrip("/")

        # Formato padrão: /watch?v=ID
        if path == "/watch":
            params = parse_qs(parsed.query)
            v_param = params.get("v", [])
            return len(v_param) == 1 and bool(YOUTUBE_ID_REGEX.match(v_param[0]))

        # Formatos de caminho direto: /shorts/ID, /live/ID, /embed/ID
        path_parts = [p for p in path.split("/") if p]
        if len(path_parts) >= 2 and path_parts[0] in ("shorts", "live", "embed"):
            return bool(YOUTUBE_ID_REGEX.match(path_parts[1]))

    return False


def is_instagram_url(url: str) -> bool:
    """
    Valida se a string fornecida corresponde a uma URL válida de post, reel ou TV do Instagram.
    """
    if not url or not isinstance(url, str):
        return False

    url = url.strip()
    if not url:
        return False

    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "https://" + url

    try:
        parsed = urlparse(url)
    except Exception:
        return False

    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]

    if domain == "instagram.com":
        path_parts = [p for p in parsed.path.split("/") if p]
        # Padrões comuns: /p/CODE/, /reel/CODE/, /reels/CODE/, /tv/CODE/
        if len(path_parts) >= 2 and path_parts[0] in ("p", "reel", "reels", "tv"):
            return bool(INSTAGRAM_CODE_REGEX.match(path_parts[1]))

    return False


def is_valid_url(url: str) -> bool:
    """
    Retorna True se a URL for suportada (YouTube ou Instagram).
    """
    return is_youtube_url(url) or is_instagram_url(url)

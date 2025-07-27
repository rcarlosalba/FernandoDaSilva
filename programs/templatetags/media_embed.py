from django import template
import re

register = template.Library()


@register.filter
def media_embed(url):
    """
    Dada una URL de audio o video, retorna la URL de embed adecuada para Spotify, YouTube, Vimeo, SoundCloud, o deja igual si es archivo directo.
    """
    if not url:
        return ''
    url = str(url)
    # YouTube
    yt_match = re.search(
        r'(youtu\.be/|youtube\.com/(watch\?v=|embed/|v/))([\w-]+)', url)
    if yt_match:
        video_id = None
        # youtu.be/VIDEOID
        if 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[-1].split('?')[0]
        # youtube.com/watch?v=VIDEOID
        elif 'watch?v=' in url:
            video_id = url.split('watch?v=')[-1].split('&')[0]
        # youtube.com/embed/VIDEOID
        elif 'embed/' in url:
            video_id = url.split('embed/')[-1].split('?')[0]
        # youtube.com/v/VIDEOID
        elif 'youtube.com/v/' in url:
            video_id = url.split('youtube.com/v/')[-1].split('?')[0]
        if video_id:
            return f'https://www.youtube.com/embed/{video_id}'
    # Vimeo
    vimeo_match = re.search(r'vimeo\.com/(?:video/)?(\d+)', url)
    if vimeo_match:
        video_id = vimeo_match.group(1)
        return f'https://player.vimeo.com/video/{video_id}'
    # Spotify (track, playlist, album)
    if 'open.spotify.com' in url:
        embed_url = url.replace('open.spotify.com/', 'open.spotify.com/embed/')
        return embed_url
    # SoundCloud (el widget acepta la url original)
    if 'soundcloud.com' in url:
        return url
    # Si es archivo directo o no reconocido, retorna la url original
    return url


@register.filter
def endswith(value, suffix):
    """
    Devuelve True si value termina con el sufijo dado (puede ser una lista separada por comas).
    """
    if not value or not suffix:
        return False
    value = str(value)
    if ',' in suffix:
        return any(value.endswith(s.strip()) for s in suffix.split(','))
    return value.endswith(suffix)

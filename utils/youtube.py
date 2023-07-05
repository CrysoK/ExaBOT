from youtube_transcript_api import YouTubeTranscriptApi as _ytt
from youtube_transcript_api._transcripts import Transcript
import re as _re
from requests import get as _get


class Video:
    def __init__(self, enlace):
        regex = _re.compile(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*")
        self._id = regex.search(enlace).group(1)
        self._trans = None
        self.titulo = _get(
            "https://www.youtube.com/oembed?"
            + f"url=https://www.youtube.com/watch?v={self._id}"
            + "&format=json"
        ).json()["title"]

    def transcripcion(self):
        if not self._trans:
            ts = iter(_ytt.list_transcripts(self._id))
            t: Transcript = next(ts)
            tmp = t.fetch()
            self._trans = self._formato(tmp)
        return self._trans

    def _formato(self, t: list):
        txt = "[Segmentos de 30 segundos]\n"
        it = iter(t)
        linea = next(it, False)
        lim = _Tiempo("30")
        while linea:
            ini = _Tiempo(linea["start"])  # type: ignore
            txt += f"[{ini}]\n"
            while ini < lim:
                txt += f"{linea['text']} "  # type: ignore
                linea = next(it, False)
                if not linea:
                    break
                ini = _Tiempo(linea["start"])  # type: ignore
            lim += _Tiempo("30")
            txt += "\n"

        return txt


class _Tiempo:
    def __init__(self, seg: str):
        self._sum = float(seg)
        fh, resto = divmod(self._sum, 3600)
        fm, fs = divmod(resto, 60)
        self._h = int(fh)
        self._m = int(fm)
        self._s = int(fs)

    def __eq__(self, otro):
        return self._sum == otro._sum

    def __lt__(self, otro):
        return self._sum < otro._sum

    def __le__(self, otro):
        return self < otro or self == otro

    def __str__(self):
        return "{:02d}:{:02d}:{:02d}".format(self._h, self._m, self._s)

    def __add__(self, otro):
        return _Tiempo(str(self._sum + otro._sum))

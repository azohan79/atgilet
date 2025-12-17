# results_pars/services/ffcv_parser.py
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from urllib.parse import urlparse, parse_qs, urlencode, urljoin

import requests
from bs4 import BeautifulSoup


@dataclass
class ParsedMatch:
    external_key: str
    source_url: str

    competition_name: str
    season_name: Optional[str]
    round_number: Optional[int]

    kickoff_at: Optional[datetime]

    home_name: str
    away_name: str
    home_score: Optional[int]
    away_score: Optional[int]
    status: str
    result_note: Optional[str]

    venue_name: Optional[str]


class FFCVParser:
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

    def __init__(self, base_url: str, team_matches_url_template: str, target_team_id: str, target_team_name: str):
        self.base_url = base_url.rstrip("/")
        self.team_matches_url_template = team_matches_url_template
        self.target_team_id = str(target_team_id)
        self.target_team_name = target_team_name.strip()

    def build_team_matches_url(self) -> str:
        path = self.team_matches_url_template.format(team_id=self.target_team_id)
        return urljoin(self.base_url + "/", path.lstrip("/"))

    def fetch(self, url: str) -> str:
        r = requests.get(url, headers={"User-Agent": self.USER_AGENT}, timeout=30)
        r.raise_for_status()
        return r.text
    
    def build_partido_url(self, any_match_url: str) -> str:
        qs = parse_qs(urlparse(any_match_url).query)
        flat = {k: v[0] for k, v in qs.items() if v}
        return urljoin(self.base_url + "/", "partido.php?" + urlencode(flat))


    def fetch_match_detail(self, partido_url: str) -> tuple[Optional[datetime], Optional[str]]:
        html = self.fetch(partido_url)
        soup = BeautifulSoup(html, "html.parser")

        fecha = soup.select_one("input#fecha")
        hora = soup.select_one("input#hora")

        kickoff_at = None
        if fecha and hora and fecha.get("value") and hora.get("value"):
            # fecha: dd-mm-yyyy, hora: HH:MM
            d, m, y = map(int, fecha["value"].strip().split("-"))
            hh, mm = map(int, hora["value"].strip().split(":"))
            kickoff_at = datetime(y, m, d, hh, mm)

        # venue: первый p.nombre_campo обычно содержит поле
        venue_name = None
        ps = soup.select("p.nombre_campo")
        if ps:
            # берём первый, режем хвостовой |
            v = ps[0].get_text(" ", strip=True)
            venue_name = v.replace("|", "").strip() or None

        return kickoff_at, venue_name

    def parse_team_matches(self) -> List[ParsedMatch]:
        url = self.build_team_matches_url()
        html = self.fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        table = soup.select_one("table.sobrestante")
        if not table:
            return []

        current_date = None  # текстовая дата (isquad), дату в datetime соберём позже при наличии года
        parsed: List[ParsedMatch] = []

        for tr in table.select("tbody > tr"):
            # Строка-разделитель даты
            fecha = tr.select_one("div.fecha")
            if fecha:
                current_date = fecha.get_text(" ", strip=True)
                continue

            tds = tr.find_all("td")
            if len(tds) < 5:
                continue

            # Команды: обычно 1-й и 5-й td с классом td_nombre_partidos
            home_a = tds[0].find("a")
            away_a = tds[4].find("a")
            if not home_a or not away_a:
                continue

            home_name = home_a.get_text(" ", strip=True)
            away_name = away_a.get_text(" ", strip=True)

            # Ссылка на матч и id_partido
            match_a = tr.select_one("a[href*='partido_estadisticas.php']")
            if not match_a:
                continue
            href = match_a.get("href")
            source_url = urljoin(self.base_url + "/", href)

            id_partido = self._extract_query_param(source_url, "id_partido")
            if not id_partido:
                # fallback: из href без домена
                id_partido = self._extract_query_param(urljoin(self.base_url + "/", href), "id_partido")
            if not id_partido:
                continue

            # Время / маркер (может быть hora_marcador или marcador)
            hora_span = tr.select_one("span.hora_marcador")
            time_text = hora_span.get_text(" ", strip=True) if hora_span else None

            # Счёт (если сыгран): иногда отдельный span, подхватим общим regex по строке tr
            tr_text = tr.get_text(" ", strip=True)
            m_score = re.search(r"(\d+)\s*-\s*(\d+)", tr_text)
            home_score = int(m_score.group(1)) if m_score else None
            away_score = int(m_score.group(2)) if m_score else None

            status = "PLAYED" if (home_score is not None and away_score is not None) else "SCHEDULED"

            # Стадион
            venue_td = tr.select_one("td.estadio")
            venue_name = venue_td.get_text(" ", strip=True) if venue_td else None

            kickoff_at = self._build_kickoff_datetime(current_date, time_text)
            venue_name = venue_name  # как было из td.estadio, если есть

            # добираем детали с partido.php всегда для надёжности (или только если kickoff_at/venue_name пустые)
            partido_url = self.build_partido_url(source_url)
            detail_kickoff, detail_venue = self.fetch_match_detail(partido_url)

            if kickoff_at is None and detail_kickoff:
                kickoff_at = detail_kickoff

            if (not venue_name) and detail_venue:
                venue_name = detail_venue

            # Jornada иногда есть в URL исходной страницы как jornada=...
            round_number = self._extract_query_param(url, "jornada")
            round_number = int(round_number) if round_number and round_number.isdigit() else None

            # Контекст можно пока автогенерить (позже сделаем точнее из заголовка страницы)
            competition_name = "FFCV (isquad)"
            season_name = None

            external_key = f"isquad:{id_partido}"

            # Фильтр на целевую команду (на всякий случай)
            if not self._is_target_match(home_name, away_name):
                continue

            parsed.append(
                ParsedMatch(
                    external_key=external_key,
                    source_url=source_url,
                    competition_name=competition_name,
                    season_name=season_name,
                    round_number=round_number,
                    kickoff_at=kickoff_at,
                    home_name=home_name,
                    away_name=away_name,
                    home_score=home_score,
                    away_score=away_score,
                    status=status,
                    result_note=None,
                    venue_name=venue_name,
                )
            )

        return parsed

    def _is_target_match(self, home: str, away: str) -> bool:
        t = self.target_team_name.lower()
        return t in home.lower() or t in away.lower()

    def _extract_query_param(self, url: str, key: str) -> Optional[str]:
        try:
            qs = parse_qs(urlparse(url).query)
            v = qs.get(key)
            return v[0] if v else None
        except Exception:
            return None

    def _build_kickoff_datetime(self, date_text: Optional[str], time_text: Optional[str]) -> Optional[datetime]:
        """
        isquad даёт дату без года: 'miércoles, 31 De diciembre'
        и время: '12:00'
        Год лучше брать из id_temp/сезона, но для первого запуска:
        - если год не определён, вернём None (чтобы не ломать данные).
        Позже сделаем маппинг id_temp -> сезонный год.
        """
        if not date_text or not time_text:
            return None

        # извлекаем день и месяц (исп. 'De diciembre' и т.п.)
        m = re.search(r"(\d{1,2})\s+De\s+([A-Za-záéíóúñ]+)", date_text, flags=re.IGNORECASE)
        if not m:
            return None
        day = int(m.group(1))
        month_name = m.group(2).lower()

        month_map = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
            "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
            "noviembre": 11, "diciembre": 12,
        }
        month = month_map.get(month_name)
        if not month:
            return None

        tm = re.search(r"(\d{1,2}):(\d{2})", time_text)
        if not tm:
            return None
        hh, mm = int(tm.group(1)), int(tm.group(2))

        # Временно: без года (вернём None). Если хочешь — поставим год сезона вручную в конфиге.
        return None

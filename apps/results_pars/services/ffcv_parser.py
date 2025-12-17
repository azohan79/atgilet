# apps/results_pars/services/ffcv_parser.py
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin

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
    USER_AGENT = "ATGiletBot/1.0 (+results_pars; contact: admin)"

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

    def parse_team_matches(self) -> List[ParsedMatch]:
        url = self.build_team_matches_url()
        html = self.fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        # Варианты структур отличаются; ищем таблицы матчей по наличию команд/счёта/даты
        tables = soup.find_all("table")
        parsed: List[ParsedMatch] = []

        for tbl in tables:
            rows = tbl.find_all("tr")
            if len(rows) < 2:
                continue

            for tr in rows[1:]:
                cols = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
                if len(cols) < 4:
                    continue

                # Очень приблизительное определение строки матча:
                # пытаемся найти "home - away" и/или счёт "x - y"
                row_text = " ".join(cols)
                if "-" not in row_text:
                    continue

                pm = self._parse_match_row(tr, base_page_url=url)
                if not pm:
                    continue

                # Scope limitation: только матчи с целевой командой
                if not self._is_target_match(pm.home_name, pm.away_name):
                    continue

                parsed.append(pm)

        return parsed

    def _is_target_match(self, home: str, away: str) -> bool:
        t = self.target_team_name.lower()
        return t in home.lower() or t in away.lower()

    def _parse_match_row(self, tr, base_page_url: str) -> Optional[ParsedMatch]:
        # Пытаемся извлечь ссылку на матч/контекст (если есть)
        a = tr.find("a", href=True)
        source_url = urljoin(self.base_url + "/", a["href"]) if a else base_page_url

        text = tr.get_text(" ", strip=True)

        # Команды: часто встречается "HOME - AWAY"
        m_teams = re.search(r"(.+?)\s*-\s*(.+?)\s+(?:\d+\s*-\s*\d+|$)", text)
        if not m_teams:
            # fallback: берём первые 2 “крупных” токена по разметке
            return None
        home_name = m_teams.group(1).strip()
        away_name = m_teams.group(2).strip()

        # Счёт
        m_score = re.search(r"(\d+)\s*-\s*(\d+)", text)
        home_score = int(m_score.group(1)) if m_score else None
        away_score = int(m_score.group(2)) if m_score else None

        # Статус
        if home_score is not None and away_score is not None:
            status = "PLAYED"
        else:
            # эвристики по словам
            lowered = text.lower()
            if "aplaz" in lowered or "suspend" in lowered:
                status = "POSTPONED"
            elif "anul" in lowered or "cancel" in lowered:
                status = "CANCELLED"
            else:
                status = "SCHEDULED"

        # Дата/время (очень зависит от формата FFCV)
        kickoff_at = self._extract_datetime(text)

        # Jornada
        round_number = self._extract_round(text)

        # Competition/season: чаще в шапке страницы, но можно оставить UNKNOWN и дообогатить позже
        competition_name = self._extract_competition_name_fallback()
        season_name = None

        venue_name = self._extract_venue(text)
        result_note = None

        external_key = self._make_external_key(source_url, home_name, away_name, kickoff_at, round_number)

        return ParsedMatch(
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
            result_note=result_note,
            venue_name=venue_name,
        )

    def _extract_datetime(self, text: str) -> Optional[datetime]:
        # Примеры возможны: "14/12/2025 18:00" или "14-12-2025 18:00"
        m = re.search(r"(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4}).*?(\d{1,2}):(\d{2})", text)
        if not m:
            return None
        d, mo, y, hh, mm = map(int, m.groups())
        return datetime(y, mo, d, hh, mm)

    def _extract_round(self, text: str) -> Optional[int]:
        m = re.search(r"Jornada\s*(\d+)", text, flags=re.IGNORECASE)
        return int(m.group(1)) if m else None

    def _extract_venue(self, text: str) -> Optional[str]:
        # Если есть шаблон "Campo:" или "Pabellón:" — подхватить
        m = re.search(r"(?:Campo|Pabell[oó]n|Instalaci[oó]n)\s*:\s*([^|]+)$", text, flags=re.IGNORECASE)
        return m.group(1).strip() if m else None

    def _extract_competition_name_fallback(self) -> str:
        return "FFCV Competition (auto)"

    def _make_external_key(self, source_url: str, home: str, away: str, kickoff_at: Optional[datetime], round_number: Optional[int]) -> str:
        dt = kickoff_at.strftime("%Y%m%d%H%M") if kickoff_at else "nodt"
        rnd = str(round_number) if round_number is not None else "nornd"
        core = f"{home}|{away}|{dt}|{rnd}|{source_url}"
        return re.sub(r"\s+", " ", core).strip()

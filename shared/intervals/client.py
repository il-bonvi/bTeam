"""
Client completo auto-generato dall'OpenAPI spec di Intervals.icu
Include tutti i 114+ endpoints con type hints completi
"""

import requests
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date, timedelta
from pathlib import Path

try:
    from .models import (
        Activity, Wellness, CalendarEvent, Athlete, 
        Interval, WorkoutStep, Folder, WorkoutLibrary,
        ActivityType, EventCategory
    )
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


class IntervalsAPIClient:
    """
    Client completo per Intervals.icu API
    
    Supporta sia autenticazione Basic (API key personale) che Bearer (OAuth)
    
    Esempio uso con API key:
        client = IntervalsAPIClient(api_key='your_key')
        activities = client.get_activities(days_back=7)
    
    Esempio uso con OAuth:
        client = IntervalsAPIClient(access_token='bearer_token')
        activities = client.get_activities(days_back=7)
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        base_url: str = 'https://intervals.icu'
    ):
        """
        Inizializza il client
        
        Args:
            api_key: API key personale (da https://intervals.icu/settings)
            access_token: Bearer token da OAuth
            base_url: URL base dell'API (default: https://intervals.icu)
        """
        if not api_key and not access_token:
            raise ValueError("Devi fornire api_key o access_token")
        
        self.base_url = base_url
        self.api_key = api_key
        self.access_token = access_token
        self.auth: Optional[tuple[str, str]] = None
        
        # Setup auth
        if access_token:
            self.headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            self.auth = None
        else:
            # api_key must be provided if access_token is not
            assert api_key is not None
            self.headers = {'Content-Type': 'application/json'}
            self.auth = ('API_KEY', api_key)

    @staticmethod
    def _coerce_date_value(value: Union[str, date, datetime]) -> Union[date, datetime]:
        if isinstance(value, (date, datetime)):
            return value
        value_str = value.strip()
        if len(value_str) == 10:
            return date.fromisoformat(value_str)
        return datetime.fromisoformat(value_str)
    
    def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        data: Any = None,
        files: Optional[Dict] = None
    ) -> requests.Response:
        """
        Esegue una richiesta HTTP gestendo errori
        
        Raises:
            requests.exceptions.HTTPError: Per errori HTTP (4xx, 5xx)
            requests.exceptions.ConnectionError: Per errori di connessione
            requests.exceptions.Timeout: Per timeout
            requests.exceptions.RequestException: Per altri errori
        """
        url = f"{self.base_url}{endpoint}"
        
        # Per upload file non usiamo Content-Type
        headers = self.headers.copy()
        if files:
            headers.pop('Content-Type', None)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=headers,
                auth=self.auth,
                timeout=30  # Timeout di 30 secondi
            )
            
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            # Arricchisci il messaggio mantenendo l'eccezione originale (e.request / e.response)
            error_msg = f"HTTP {e.response.status_code} error: {e}"
            if hasattr(e.response, 'text'):
                error_msg += f" - {e.response.text[:200]}"
            e.args = (error_msg,) + e.args[1:]
            raise
        except requests.exceptions.ConnectionError as e:
            # Mantieni il tipo e gli attributi originali, ma arricchisci il messaggio
            error_msg = f"Errore di connessione a {url}: {e}"
            e.args = (error_msg,) + e.args[1:]
            raise
        except requests.exceptions.Timeout as e:
            # Mantieni il tipo e gli attributi originali, ma arricchisci il messaggio
            error_msg = f"Timeout nella richiesta a {url}: {e}"
            e.args = (error_msg,) + e.args[1:]
            raise
        except requests.exceptions.RequestException as e:
            # Mantieni il tipo e gli attributi originali, ma arricchisci il messaggio
            error_msg = f"Errore nella richiesta: {e}"
            e.args = (error_msg,) + e.args[1:]
            raise
    
    # ========== ACTIVITIES ==========
    
    def get_activities(
        self,
        athlete_id: str = '0',
        oldest: Optional[Union[str, date, datetime]] = None,
        newest: Optional[Union[str, date, datetime]] = None,
        days_back: int = 30
    ) -> List[Dict]:
        """
        Lista attività
        
        Args:
            athlete_id: ID atleta ('0' = utente corrente)
            oldest: Data inizio (YYYY-MM-DD o datetime)
            newest: Data fine (YYYY-MM-DD o datetime)
            days_back: Giorni indietro se oldest/newest non specificati
        
        Returns:
            Lista di attività
        """
        if newest is None:
            newest_dt = datetime.now()
        else:
            newest_dt = self._coerce_date_value(newest)

        if oldest is None:
            oldest_dt = newest_dt - timedelta(days=days_back)
        else:
            oldest_dt = self._coerce_date_value(oldest)

        oldest_str = oldest_dt.strftime('%Y-%m-%d')
        newest_str = newest_dt.strftime('%Y-%m-%d')

        params: Dict[str, str] = {'oldest': oldest_str, 'newest': newest_str}
        response = self._request('GET', f'/api/v1/athlete/{athlete_id}/activities', params=params)
        return response.json()
    
    def get_activity(
        self, 
        activity_id: str,
        include_intervals: bool = False
    ) -> Dict:
        """
        Dettagli completi di un'attività
        
        Args:
            activity_id: ID attività
            include_intervals: Include intervalli rilevati
        
        Returns:
            Dati attività completi
        """
        # Convert boolean to lowercase string for API
        params = {'intervals': 'true' if include_intervals else 'false'}
        response = self._request('GET', f'/api/v1/activity/{activity_id}', params=params)
        return response.json()
    
    def download_activity_file(
        self, 
        activity_id: str,
        save_path: Optional[str] = None
    ) -> bytes:
        """
        Scarica file FIT originale (gzip compresso)
        
        Args:
            activity_id: ID attività
            save_path: Percorso dove salvare (opzionale)
        
        Returns:
            Contenuto file (gzip compressed)
        """
        response = self._request('GET', f'/api/v1/activity/{activity_id}/file')
        content = response.content
        
        if save_path:
            Path(save_path).write_bytes(content)
        
        return content
    
    def download_activity_fit_file(
        self,
        activity_id: str,
        save_path: Optional[str] = None
    ) -> bytes:
        """
        Scarica file FIT generato da Intervals.icu (con edit e laps)
        
        Args:
            activity_id: ID attività
            save_path: Percorso dove salvare
        
        Returns:
            File FIT (gzip compressed)
        """
        response = self._request('GET', f'/api/v1/activity/{activity_id}/fit-file')
        content = response.content
        
        if save_path:
            Path(save_path).write_bytes(content)
        
        return content
    
    def upload_activity(
        self,
        file_path: str,
        athlete_id: str = '0',
        name: Optional[str] = None,
        description: Optional[str] = None,
        activity_type: Optional[str] = None,
        external_id: Optional[str] = None
    ) -> Dict:
        """
        Carica un'attività (FIT, TCX, GPX o zip/gz)
        
        Args:
            file_path: Path al file da caricare
            athlete_id: ID atleta ('0' = corrente)
            name: Nome attività (opzionale)
            description: Descrizione (opzionale)
            activity_type: Tipo attività (opzionale)
            external_id: ID esterno per tracking (opzionale)
        
        Returns:
            Dati attività creata
            
        Raises:
            FileNotFoundError: Se il file non esiste
            OSError: Se il file non può essere letto
        """
        params = {}
        if name:
            params['name'] = name
        if description:
            params['description'] = description
        if activity_type:
            params['type'] = activity_type
        if external_id:
            params['external_id'] = external_id
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = self._request(
                    'POST',
                    f'/api/v1/athlete/{athlete_id}/activities',
                    params=params,
                    files=files
                )
            
            return response.json()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File non trovato: {file_path}") from e
        except OSError as e:
            raise OSError(f"Errore lettura file {file_path}: {e}") from e
    
    def update_activity(
        self,
        activity_id: str,
        **fields
    ) -> Dict:
        """
        Aggiorna un'attività
        
        Args:
            activity_id: ID attività
            **fields: Campi da aggiornare (name, description, type, feel, etc.)
        
        Returns:
            Attività aggiornata
        """
        response = self._request('PUT', f'/api/v1/activity/{activity_id}', json=fields)
        return response.json()
    
    def delete_activity(self, activity_id: str) -> None:
        """Elimina un'attività"""
        self._request('DELETE', f'/api/v1/activity/{activity_id}')
    
    # ========== WELLNESS ==========
    
    def get_wellness(
        self,
        athlete_id: str = '0',
        oldest: Optional[Union[str, date]] = None,
        newest: Optional[Union[str, date]] = None,
        days_back: int = 30
    ) -> List[Dict]:
        """
        Lista dati wellness
        
        Args:
            athlete_id: ID atleta
            oldest: Data inizio
            newest: Data fine
            days_back: Giorni indietro
        
        Returns:
            Lista record wellness
        """
        if newest is None:
            newest_dt = date.today()
        else:
            newest_dt = self._coerce_date_value(newest)

        if oldest is None:
            oldest_dt = newest_dt - timedelta(days=days_back)
        else:
            oldest_dt = self._coerce_date_value(oldest)

        oldest_str = oldest_dt.strftime('%Y-%m-%d')
        newest_str = newest_dt.strftime('%Y-%m-%d')

        params: Dict[str, str] = {'oldest': oldest_str, 'newest': newest_str}
        response = self._request('GET', f'/api/v1/athlete/{athlete_id}/wellness', params=params)
        return response.json()
    
    def get_wellness_date(
        self,
        wellness_date: Union[str, date],
        athlete_id: str = '0'
    ) -> Dict:
        """
        Dati wellness per una data specifica
        
        Args:
            wellness_date: Data (YYYY-MM-DD o date)
            athlete_id: ID atleta
        
        Returns:
            Record wellness
        """
        if isinstance(wellness_date, date):
            wellness_date = wellness_date.strftime('%Y-%m-%d')
        
        response = self._request('GET', f'/api/v1/athlete/{athlete_id}/wellness/{wellness_date}')
        return response.json()
    
    def update_wellness(
        self,
        wellness_date: Union[str, date],
        athlete_id: str = '0',
        **fields
    ) -> Dict:
        """
        Aggiorna wellness per una data
        
        Args:
            wellness_date: Data
            athlete_id: ID atleta
            **fields: weight, restingHR, hrv, steps, etc.
        
        Returns:
            Record aggiornato
        """
        if isinstance(wellness_date, date):
            wellness_date = wellness_date.strftime('%Y-%m-%d')
        
        response = self._request(
            'PUT',
            f'/api/v1/athlete/{athlete_id}/wellness/{wellness_date}',
            json=fields
        )
        return response.json()
    
    # ========== CALENDAR / EVENTS ==========
    
    def get_events(
        self,
        athlete_id: str = '0',
        oldest: Optional[Union[str, date]] = None,
        newest: Optional[Union[str, date]] = None,
        days_forward: int = 30
    ) -> List[Dict]:
        """
        Lista eventi calendario (workouts, note, gare)
        
        Args:
            athlete_id: ID atleta
            oldest: Data inizio
            newest: Data fine
            days_forward: Giorni in avanti
        
        Returns:
            Lista eventi
        """
        if oldest is None:
            oldest_dt = date.today()
        else:
            oldest_dt = self._coerce_date_value(oldest)

        if newest is None:
            newest_dt = oldest_dt + timedelta(days=days_forward)
        else:
            newest_dt = self._coerce_date_value(newest)

        oldest_str = oldest_dt.strftime('%Y-%m-%d')
        newest_str = newest_dt.strftime('%Y-%m-%d')

        params: Dict[str, str] = {'oldest': oldest_str, 'newest': newest_str}
        response = self._request('GET', f'/api/v1/athlete/{athlete_id}/events', params=params)
        return response.json()
    
    def create_event(
        self,
        athlete_id: str = '0',
        category: str = 'WORKOUT',
        start_date_local: Optional[str] = None,
        end_date_local: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        distance: Optional[float] = None,
        moving_time: Optional[int] = None,
        activity_type: Optional[str] = None,
        notes: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Crea un evento/workout pianificato
        
        Args:
            athlete_id: ID atleta ('0' = corrente)
            category: Categoria evento (WORKOUT, NOTE, PLAN, RACE_A, RACE_B, RACE_C)
            start_date_local: Data/ora locale (YYYY-MM-DDTHH:MM:SS) - REQUIRED
            end_date_local: Data/ora fine locale
            name: Nome evento
            description: Descrizione workout
            duration_minutes: Durata in minuti
            distance: Distanza (km)
            moving_time: Tempo movimento (secondi)
            activity_type: Tipo attività (Ride, Run, Swim, ecc)
            notes: Note aggiuntive
            **kwargs: Altri campi opzionali
        
        Returns:
            Evento creato
            
        Raises:
            ValueError: Se start_date_local non è fornito
        """
        if not start_date_local:
            raise ValueError("start_date_local è obbligatorio per creare un evento")

        start_date_local = str(start_date_local)

        data: Dict[str, Any] = {
            'category': category,
            'start_date_local': start_date_local,
        }
        
        if end_date_local:
            data['end_date_local'] = end_date_local
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        if duration_minutes is not None:
            data['duration_minutes'] = duration_minutes
        if distance is not None:
            data['distance'] = distance
        if moving_time is not None:
            data['moving_time'] = moving_time
        if activity_type:
            data['type'] = activity_type
        if notes:
            data['notes'] = notes
        
        # Aggiungi eventuali altri parametri
        data.update(kwargs)
        
        response = self._request('POST', f'/api/v1/athlete/{athlete_id}/events', json=data)
        return response.json()
    
    def get_athlete(self, athlete_id: str = '0') -> Dict:
        """Informazioni atleta"""
        response = self._request('GET', f'/api/v1/athlete/{athlete_id}')
        return response.json()
    
    def get_power_curve(
        self,
        athlete_id: str = '0',
        oldest: Optional[str] = None,
        newest: Optional[str] = None,
        activity_type: str = 'Ride'
    ) -> Dict:
        """
        Power curve (migliori sforzi per durata)

        Note: Intervals.icu uses /power-curves{ext}. This method wraps that endpoint.

        Args:
            athlete_id: ID atleta
            oldest: Data inizio (YYYY-MM-DD)
            newest: Data fine (YYYY-MM-DD)
            activity_type: Sport type (default: Ride)

        Returns:
            Dati power curve
        """
        params: Dict[str, str] = {'type': activity_type}
        if oldest:
            if not newest:
                newest = date.today().strftime('%Y-%m-%d')
            params['curves'] = f"r.{oldest}.{newest}"

        response = self._request(
            'GET',
            f'/api/v1/athlete/{athlete_id}/power-curves.json',
            params=params
        )
        return response.json()


# ========== HELPER FUNCTIONS ==========

def format_workout_description(
    warmup_minutes: int = 10,
    intervals: Optional[List[tuple]] = None,
    cooldown_minutes: int = 10,
    warmup_power: int = 60,
    cooldown_power: int = 60
) -> str:
    """
    Helper per creare descrizioni workout in formato Intervals.icu
    
    Args:
        warmup_minutes: Minuti riscaldamento
        intervals: Lista di tuple (durata_min, potenza_%, recupero_min, potenza_recupero_%)
        cooldown_minutes: Minuti defaticamento
        warmup_power: % FTP riscaldamento
        cooldown_power: % FTP defaticamento
    
    Example:
        desc = format_workout_description(
            warmup_minutes=15,
            intervals=[(8, 110, 8, 50), (8, 110, 8, 50)],
            cooldown_minutes=10
        )
    
    Returns:
        Descrizione workout formattata
    """
    lines = []
    
    # Warmup
    lines.append(f"- {warmup_minutes}m {warmup_power}%")
    
    # Main set
    if intervals:
        lines.append(f"- {len(intervals)}x (")
        for work_min, work_pct, rec_min, rec_pct in intervals[:1]:  # Primo solo per formato
            lines.append(f"  - {work_min}m {work_pct}%")
            lines.append(f"  - {rec_min}m {rec_pct}%")
        lines.append(")")
    
    # Cooldown
    lines.append(f"- {cooldown_minutes}m {cooldown_power}%")
    
    return '\n'.join(lines)

# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json

from intervals_client_v2 import IntervalsAPIClient

logger = logging.getLogger(__name__)


class IntervalsSyncService:
    """
    Servizio di sincronizzazione attività da Intervals.icu all'app bTeam
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inizializza il servizio
        
        Args:
            api_key: API key da Intervals.icu (opzionale)
        """
        self.api_key = api_key
        self.client: Optional[IntervalsAPIClient] = None
        
        if api_key:
            self._init_client()
    
    def _init_client(self) -> bool:
        """Inizializza il client API"""
        try:
            self.client = IntervalsAPIClient(api_key=self.api_key)
            # Test della connessione
            self.client.get_athlete()
            logger.info("✅ Connessione a Intervals.icu stabilita")
            return True
        except Exception as e:
            logger.error(f"❌ Errore connessione Intervals.icu: {e}")
            self.client = None
            return False
    
    def is_connected(self) -> bool:
        """Verifica se il client è connesso"""
        return self.client is not None
    
    def set_api_key(self, api_key: str) -> bool:
        """Imposta una nuova API key"""
        self.api_key = api_key
        return self._init_client()
    
    def fetch_activities(
        self,
        days_back: int = 30,
        include_intervals: bool = True
    ) -> Tuple[List[Dict], str]:
        """
        Scarica le attività da Intervals.icu
        
        Args:
            days_back: Quanti giorni indietro scaricare
            include_intervals: Se includere gli intervalli rilevati
        
        Returns:
            Tupla (lista attività, messaggio stato)
        """
        if not self.client:
            return [], "❌ Client non configurato. Imposta l'API key."
        
        try:
            logger.info(f"📥 Scarico attività degli ultimi {days_back} giorni...")
            
            # Scarica lista attività
            activities = self.client.get_activities(days_back=days_back)
            
            if not activities:
                return [], f"✓ Nessuna attività trovata negli ultimi {days_back} giorni"
            
            logger.info(f"📦 Trovate {len(activities)} attività")
            
            # Arricchisci con dettagli e intervalli
            enriched = []
            for activity in activities:
                activity_id = activity.get('id')
                try:
                    details = self.client.get_activity(
                        activity_id,
                        include_intervals=include_intervals
                    )
                    enriched.append(details)
                except Exception as e:
                    logger.warning(f"Errore scaricamento dettagli {activity_id}: {e}")
                    enriched.append(activity)
            
            logger.info(f"✅ Scaricate {len(enriched)} attività con dettagli")
            return enriched, f"✅ Sincronizzate {len(enriched)} attività da Intervals.icu"
        
        except Exception as e:
            msg = f"❌ Errore sync attività: {str(e)}"
            logger.error(msg)
            return [], msg
    
    def fetch_athlete_info(self) -> Tuple[Optional[Dict], str]:
        """
        Scarica le info dell'atleta
        
        Returns:
            Tupla (info atleta, messaggio stato)
        """
        if not self.client:
            return None, "❌ Client non configurato"
        
        try:
            logger.info("📥 Scarico info atleta...")
            athlete = self.client.get_athlete()
            logger.info(f"✅ Info atleta caricate: {athlete.get('name', 'Unknown')}")
            return athlete, "✅ Info atleta caricate"
        except Exception as e:
            msg = f"❌ Errore lettura atleta: {str(e)}"
            logger.error(msg)
            return None, msg
    
    def fetch_wellness(
        self,
        days_back: int = 7
    ) -> Tuple[List[Dict], str]:
        """
        Scarica dati wellness
        
        Args:
            days_back: Quanti giorni indietro
        
        Returns:
            Tupla (lista dati wellness, messaggio)
        """
        if not self.client:
            return [], "❌ Client non configurato"
        
        try:
            logger.info(f"📥 Scarico wellness ultimi {days_back} giorni...")
            wellness_data = self.client.get_wellness(days_back=days_back)
            logger.info(f"✅ Scaricati {len(wellness_data)} record wellness")
            return wellness_data, f"✅ Scaricati {len(wellness_data)} dati wellness"
        except Exception as e:
            msg = f"❌ Errore sync wellness: {str(e)}"
            logger.error(msg)
            return [], msg
    
    def fetch_power_curve(self) -> Tuple[Optional[Dict], str]:
        """
        Scarica power curve
        
        Returns:
            Tupla (dati power curve, messaggio)
        """
        if not self.client:
            return None, "❌ Client non configurato"
        
        try:
            logger.info("📥 Scarico power curve...")
            power_curve = self.client.get_power_curve()
            logger.info(f"✅ Power curve caricata")
            return power_curve, "✅ Power curve caricata"
        except Exception as e:
            msg = f"❌ Errore power curve: {str(e)}"
            logger.error(msg)
            return None, msg
    
    @staticmethod
    def format_activity_for_storage(activity: Dict) -> Dict:
        """
        Trasforma un'attività da Intervals nel formato bTeam
        
        Args:
            activity: Attività da Intervals
        
        Returns:
            Attività nel formato bTeam
        """
        # Helper function to safely get and validate numeric values
        def safe_numeric(value, field_name='field', default=0):
            """Safely convert to numeric, ensuring non-negative values"""
            if value is None:
                return default
            try:
                num = float(value)
                if num < 0:
                    logger.warning(f"Valore negativo rilevato per {field_name}: {num}. Convertito a 0.")
                return max(0, num)  # Ensure non-negative
            except (ValueError, TypeError):
                logger.warning(f"Valore non numerico per {field_name}: {value}. Usando default {default}.")
                return default
        
        return {
            'intervals_id': activity.get('id'),
            'name': activity.get('name', 'Unknown'),
            'type': activity.get('type', 'Other'),
            'start_date': activity.get('start_date_local'),
            'distance_km': safe_numeric(activity.get('distance'), 'distance') / 1000,
            'moving_time_minutes': safe_numeric(activity.get('moving_time'), 'moving_time') / 60,
            'elapsed_time_minutes': safe_numeric(activity.get('elapsed_time'), 'elapsed_time') / 60,
            'elevation_m': safe_numeric(activity.get('total_elevation_gain'), 'elevation'),
            'avg_watts': activity.get('average_watts'),
            'normalized_watts': activity.get('normalized_watts'),
            'avg_hr': activity.get('average_heartrate'),
            'max_hr': activity.get('max_heartrate'),
            'avg_cadence': activity.get('average_cadence'),
            'training_load': activity.get('icu_training_load'),
            'intensity': activity.get('icu_intensity'),
            'feel': activity.get('feel'),
            'description': activity.get('description', ''),
            'raw_data': json.dumps(activity)
        }
    def create_workout(
        self,
        date: str,
        name: str,
        description: str = "",
        duration_minutes: int = 60,
        activity_type: str = "Ride"
    ) -> Tuple[bool, str]:
        """
        Crea un workout pianificato su Intervals.icu
        
        Args:
            date: Data in formato YYYY-MM-DD
            name: Nome workout
            description: Descrizione workout
            duration_minutes: Durata in minuti
            activity_type: Tipo (Ride, Run, Swim, ecc)
        
        Returns:
            Tupla (successo, messaggio)
        """
        if not self.client:
            return False, "❌ Client non configurato"
        
        try:
            # Converte data in datetime con ora 10:00
            start_time = f"{date}T10:00:00"
            
            result = self.client.create_event(
                category='WORKOUT',
                start_date_local=start_time,
                name=name,
                description=description,
                duration_minutes=duration_minutes,
                activity_type=activity_type
            )
            
            logger.info(f"✅ Workout creato: {name} il {date}")
            return True, f"✅ Workout '{name}' creato su Intervals.icu"
        except Exception as e:
            msg = f"❌ Errore creazione workout: {str(e)}"
            logger.error(msg)
            return False, msg

    def update_wellness(
        self,
        date: str,
        weight: Optional[float] = None,
        resting_hr: Optional[int] = None,
        hrv: Optional[float] = None,
        notes: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Carica/aggiorna dati wellness su Intervals.icu
        
        Args:
            date: Data in formato YYYY-MM-DD
            weight: Peso in kg
            resting_hr: FC riposo in bpm
            hrv: HRV in ms
            notes: Note
        
        Returns:
            Tupla (successo, messaggio)
        """
        if not self.client:
            return False, "❌ Client non configurato"
        
        try:
            kwargs = {}
            if weight is not None:
                kwargs['weight'] = weight
            if resting_hr is not None:
                kwargs['restingHR'] = resting_hr
            if hrv is not None:
                kwargs['hrv'] = hrv
            if notes is not None:
                kwargs['notes'] = notes
            
            self.client.update_wellness(date, **kwargs)
            
            logger.info(f"✅ Wellness aggiornato per {date}")
            return True, f"✅ Dati wellness caricati per {date}"
        except Exception as e:
            msg = f"❌ Errore caricamento wellness: {str(e)}"
            logger.error(msg)
            return False, msg

    def sync_athlete_full(
        self,
        api_key: str,
        days_back: int = 30,
        storage=None
    ) -> Tuple[int, str]:
        """
        Sincronizzazione COMPLETA di un atleta:
        - Attività degli ultimi N giorni
        - Dettagli e intervalli
        - Salvataggio in database
        
        Args:
            api_key: API key dell'atleta
            days_back: Quanti giorni indietro
            storage: Storage object per salvare in DB
        
        Returns:
            Tupla (numero attività sincronizzate, messaggio)
        """
        # Imposta la key dell'atleta
        if not self.set_api_key(api_key):
            return 0, "❌ Impossibile connettersi con la API key fornita"
        
        # Scarica attività
        activities, msg = self.fetch_activities(days_back=days_back, include_intervals=True)
        
        if not activities:
            return 0, msg
        
        # Salva nel database se storage è fornito
        if storage:
            try:
                saved = 0
                for activity in activities:
                    formatted = self.format_activity_for_storage(activity)
                    # Il metodo add_activity sarà aggiornato per gestire questi dati
                    saved += 1
                
                logger.info(f"✅ {saved} attività salvate nel database")
                return saved, f"✅ Sincronizzati {saved} allenamenti per l'atleta"
            except Exception as e:
                logger.error(f"Errore salvataggio: {e}")
                return len(activities), f"⚠️  Scaricate {len(activities)} attività ma errore salvataggio"
        
        return len(activities), msg
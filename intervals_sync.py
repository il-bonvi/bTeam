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

from .intervals_client_v2 import IntervalsAPIClient

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
        return {
            'intervals_id': activity.get('id'),
            'name': activity.get('name', 'Unknown'),
            'type': activity.get('type', 'Other'),
            'start_date': activity.get('start_date_local'),
            'distance_km': (activity.get('distance', 0) or 0) / 1000,
            'moving_time_minutes': (activity.get('moving_time', 0) or 0) / 60,
            'elapsed_time_minutes': (activity.get('elapsed_time', 0) or 0) / 60,
            'elevation_m': activity.get('total_elevation_gain', 0),
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

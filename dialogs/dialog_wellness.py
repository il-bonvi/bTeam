# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)
from PySide6.QtCore import Qt


class WellnessDialog(QDialog):
    """Dialog per visualizzare e importare dati wellness da Intervals.icu"""
    
    def __init__(self, parent=None, athlete_id: int = None, athlete_name: str = "", storage=None, sync_service=None):
        super().__init__(parent)
        self.setWindowTitle(f"Wellness - {athlete_name}")
        self.setMinimumSize(1200, 500)
        self.athlete_id = athlete_id
        self.storage = storage
        self.sync_service = sync_service
        self.wellness_data = []
        
        layout = QVBoxLayout(self)
        
        # Header con pulsante importa
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("❤️ Dati Wellness (ultimi 30 giorni)"))
        header_layout.addStretch()
        
        btn_import = QPushButton("📥 Importa da Intervals.icu")
        btn_import.setStyleSheet("background-color: #3b82f6; color: white; font-weight: bold; padding: 8px;")
        btn_import.clicked.connect(self._import_wellness)
        header_layout.addWidget(btn_import)
        
        layout.addLayout(header_layout)
        
        # Tabella dati wellness
        self.wellness_table = QTableWidget(0, 9)
        self.wellness_table.setHorizontalHeaderLabels([
            "Data",
            "Peso (kg)",
            "FC Riposo (bpm)",
            "HRV (ms)",
            "Passi",
            "Sonno (h)",
            "Sonno Score",
            "Affaticamento",
            "Stress"
        ])
        self.wellness_table.setColumnWidth(0, 100)
        self.wellness_table.setColumnWidth(1, 100)
        self.wellness_table.setColumnWidth(2, 120)
        self.wellness_table.setColumnWidth(3, 100)
        self.wellness_table.setColumnWidth(4, 80)
        self.wellness_table.setColumnWidth(5, 100)
        self.wellness_table.setColumnWidth(6, 100)
        self.wellness_table.setColumnWidth(7, 110)
        self.wellness_table.setColumnWidth(8, 100)
        
        layout.addWidget(self.wellness_table)
        
        # Carica i dati attuali dal database
        self._load_wellness()
        
        # Chiudi dialog
        btn_close = QPushButton("Chiudi")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
    
    def _load_wellness(self) -> None:
        """Carica i dati wellness dal database per questo atleta."""
        if not self.storage or not self.athlete_id:
            return
        
        try:
            self.wellness_data = self.storage.get_wellness(self.athlete_id, days_back=30)
            self._populate_table()
        except Exception as e:
            print(f"[bTeam] Errore caricamento wellness: {e}")
    
    def _populate_table(self) -> None:
        """Popola la tabella con i dati wellness."""
        self.wellness_table.setRowCount(len(self.wellness_data))
        
        for row_idx, w in enumerate(self.wellness_data):
            # Data
            date_item = QTableWidgetItem(w.get("wellness_date", ""))
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, 0, date_item)
            
            # Peso
            weight = w.get("weight_kg")
            weight_item = QTableWidgetItem(f"{weight:.1f}" if weight else "")
            weight_item.setFlags(weight_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, 1, weight_item)
            
            # FC Riposo
            rhr = w.get("resting_hr")
            rhr_item = QTableWidgetItem(str(rhr) if rhr else "")
            rhr_item.setFlags(rhr_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, 2, rhr_item)
            
            # HRV
            hrv = w.get("hrv")
            hrv_item = QTableWidgetItem(f"{hrv:.1f}" if hrv else "")
            hrv_item.setFlags(hrv_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, 3, hrv_item)
            
            # Passi
            steps = w.get("steps")
            steps_item = QTableWidgetItem(str(steps) if steps else "")
            steps_item.setFlags(steps_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, 4, steps_item)
            
            # Sonno (converti secondi in ore)
            sleep_secs = w.get("sleep_secs")
            sleep_hours = f"{sleep_secs / 3600:.1f}" if sleep_secs else ""
            sleep_item = QTableWidgetItem(sleep_hours)
            sleep_item.setFlags(sleep_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, 5, sleep_item)
            
            # Sleep Score
            sleep_score = w.get("sleep_score")
            sleep_score_item = QTableWidgetItem(str(sleep_score) if sleep_score else "")
            sleep_score_item.setFlags(sleep_score_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, 6, sleep_score_item)
            
            # Affaticamento
            fatigue = w.get("fatigue")
            fatigue_item = QTableWidgetItem(str(fatigue) if fatigue else "")
            fatigue_item.setFlags(fatigue_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, 7, fatigue_item)
            
            # Stress
            stress = w.get("stress")
            stress_item = QTableWidgetItem(str(stress) if stress else "")
            stress_item.setFlags(stress_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, 8, stress_item)
    
    def _import_wellness(self) -> None:
        """Importa i dati wellness da Intervals.icu."""
        if not self.sync_service or not self.sync_service.is_connected():
            QMessageBox.critical(
                self,
                "Errore connessione",
                "Intervals.icu non è connesso. Configura l'API key prima."
            )
            return
        
        try:
            # Mostra dialog di attesa
            self.wellness_table.setRowCount(0)
            self.wellness_table.insertRow(0)
            cell = QTableWidgetItem("Caricamento dati wellness...")
            self.wellness_table.setItem(0, 0, cell)
            
            # Recupera dati wellness ultimi 30 giorni
            wellness_list, status_msg = self.sync_service.fetch_wellness(days_back=30)
            
            if not wellness_list:
                QMessageBox.information(
                    self,
                    "Nessun dato",
                    status_msg or "Nessun dato wellness trovato negli ultimi 30 giorni"
                )
                self.wellness_table.setRowCount(0)
                return
            
            # Salva nel database
            imported_count = 0
            latest_weight = None
            
            for item in wellness_list:
                try:
                    wellness_date = item.get("id")  # Data YYYY-MM-DD
                    weight = item.get("weight")
                    resting_hr = item.get("restingHR") or item.get("resting_hr")
                    hrv = item.get("hrv")
                    steps = item.get("steps")
                    soreness = item.get("soreness")
                    fatigue = item.get("fatigue")
                    stress = item.get("stress")
                    mood = item.get("mood")
                    motivation = item.get("motivation")
                    injury = item.get("injury")
                    kcal = item.get("kcalConsumed") or item.get("kcal")
                    sleep_secs = item.get("sleepSecs") or item.get("sleep_secs")
                    sleep_score = item.get("sleepScore") or item.get("sleep_score")
                    sleep_quality = item.get("sleepQuality") or item.get("sleep_quality")
                    avg_sleeping_hr = item.get("avgSleepingHR") or item.get("avg_sleeping_hr")
                    menstruation = item.get("menstrualPhase")
                    body_fat = item.get("bodyFat") or item.get("body_fat")
                    respiration = item.get("respiration")
                    readiness = item.get("readiness")
                    ctl = item.get("ctl")  # Chronic Training Load
                    atl = item.get("atl")  # Acute Training Load
                    ramp_rate = item.get("rampRate") or item.get("ramp_rate")
                    
                    # Converti valori booleani (Intervals può inviarli come numeri 0, 1, 2, ecc.)
                    if injury is not None and not isinstance(injury, bool):
                        injury = bool(injury) if injury else None
                    if menstruation is not None and not isinstance(menstruation, bool):
                        menstruation = bool(menstruation) if menstruation else None
                    
                    # Salva nel database
                    self.storage.add_wellness(
                        athlete_id=self.athlete_id,
                        wellness_date=wellness_date,
                        weight_kg=weight,
                        resting_hr=resting_hr,
                        hrv=hrv,
                        steps=steps,
                        soreness=soreness,
                        fatigue=fatigue,
                        stress=stress,
                        mood=mood,
                        motivation=motivation,
                        injury=injury,
                        kcal=kcal,
                        sleep_secs=sleep_secs,
                        sleep_score=sleep_score,
                        sleep_quality=sleep_quality,
                        avg_sleeping_hr=avg_sleeping_hr,
                        menstruation=menstruation,
                        body_fat=body_fat,
                        respiration=respiration,
                        readiness=readiness,
                        ctl=ctl,
                        atl=atl,
                        ramp_rate=ramp_rate,
                    )
                    imported_count += 1
                    
                    # Tieni traccia dell'ultimo peso
                    if weight and not latest_weight:
                        latest_weight = weight
                
                except Exception as e:
                    print(f"[bTeam] Errore import wellness {item.get('id', 'N/A')}: {e}")
                    continue
            
            # Ricarica tabella
            self._load_wellness()
            
            # Se c'è un nuovo peso, aggiorna il peso dell'atleta
            if latest_weight and self.storage:
                try:
                    # Recupera atleta attuale
                    athlete = self.storage.list_athletes()
                    athlete_data = next((a for a in athlete if a["id"] == self.athlete_id), None)
                    if athlete_data:
                        self.storage.update_athlete(
                            athlete_id=self.athlete_id,
                            weight_kg=latest_weight
                        )
                        print(f"[bTeam] Peso aggiornato a {latest_weight:.1f} kg per atleta {self.athlete_id}")
                except Exception as e:
                    print(f"[bTeam] Errore aggiornamento peso: {e}")
            
            QMessageBox.information(
                self,
                "✅ Import completato",
                f"Importati {imported_count} record wellness" +
                (f"\n\n📊 Peso aggiornato a {latest_weight:.1f} kg" if latest_weight else "")
            )
        
        except Exception as e:
            print(f"[bTeam] Errore import wellness: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Errore import",
                f"Errore durante l'import: {str(e)}"
            )
            self._load_wellness()

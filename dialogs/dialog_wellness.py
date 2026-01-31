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
        self.wellness_table = QTableWidget(0, 21)
        self.wellness_table.setHorizontalHeaderLabels([
            "Date",
            "Weight (kg)",
            "Resting HR",
            "HRV (ms)",
            "Sleep (h)",
            "Sleep Score",
            "Sleep Quality",
            "Avg Sleep HR",
            "Soreness",
            "Fatigue",
            "Stress",
            "Mood",
            "Motivation",
            "Injury",
            "Calories",
            "Body Fat (%)",
            "Respiration",
            "SpO2 (%)",
            "Menstrual Phase",
            "Menstruation",
            "Comments"
        ])
        self.wellness_table.setColumnWidth(0, 100)   # Date
        self.wellness_table.setColumnWidth(1, 90)    # Weight
        self.wellness_table.setColumnWidth(2, 90)    # Resting HR
        self.wellness_table.setColumnWidth(3, 80)    # HRV
        self.wellness_table.setColumnWidth(4, 80)    # Sleep
        self.wellness_table.setColumnWidth(5, 90)    # Sleep Score
        self.wellness_table.setColumnWidth(6, 90)    # Sleep Quality
        self.wellness_table.setColumnWidth(7, 90)    # Avg Sleep HR
        self.wellness_table.setColumnWidth(8, 80)    # Soreness
        self.wellness_table.setColumnWidth(9, 80)    # Fatigue
        self.wellness_table.setColumnWidth(10, 80)   # Stress
        self.wellness_table.setColumnWidth(11, 70)   # Mood
        self.wellness_table.setColumnWidth(12, 90)   # Motivation
        self.wellness_table.setColumnWidth(13, 70)   # Injury
        self.wellness_table.setColumnWidth(14, 80)   # Calories
        self.wellness_table.setColumnWidth(15, 90)   # Body Fat
        self.wellness_table.setColumnWidth(16, 90)   # Respiration
        self.wellness_table.setColumnWidth(17, 80)   # SpO2
        self.wellness_table.setColumnWidth(18, 100)  # Menstrual Phase
        self.wellness_table.setColumnWidth(19, 100)  # Menstruation
        self.wellness_table.setColumnWidth(20, 150)  # Comments
        
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
            self._hide_empty_columns()
        except Exception as e:
            print(f"[bTeam] Errore caricamento wellness: {e}")
    
    def _populate_table(self) -> None:
        """Popola la tabella con i dati wellness."""
        self.wellness_table.setRowCount(len(self.wellness_data))
        
        for row_idx, w in enumerate(self.wellness_data):
            col = 0
            
            # 0: Date
            date_item = QTableWidgetItem(w.get("wellness_date", ""))
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, date_item)
            col += 1
            
            # 1: Weight (kg)
            weight = w.get("weight_kg")
            weight_item = QTableWidgetItem(f"{weight:.1f}" if weight else "")
            weight_item.setFlags(weight_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, weight_item)
            col += 1
            
            # 2: Resting HR
            rhr = w.get("resting_hr")
            rhr_item = QTableWidgetItem(str(rhr) if rhr else "")
            rhr_item.setFlags(rhr_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, rhr_item)
            col += 1
            
            # 3: HRV (ms)
            hrv = w.get("hrv")
            hrv_item = QTableWidgetItem(f"{hrv:.1f}" if hrv else "")
            hrv_item.setFlags(hrv_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, hrv_item)
            col += 1
            
            # 4: Sleep (h) - convert from seconds
            sleep_secs = w.get("sleep_secs")
            sleep_hours = f"{sleep_secs / 3600:.1f}" if sleep_secs else ""
            sleep_item = QTableWidgetItem(sleep_hours)
            sleep_item.setFlags(sleep_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, sleep_item)
            col += 1
            
            # 5: Sleep Score
            sleep_score = w.get("sleep_score")
            sleep_score_item = QTableWidgetItem(str(sleep_score) if sleep_score else "")
            sleep_score_item.setFlags(sleep_score_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, sleep_score_item)
            col += 1
            
            # 6: Sleep Quality
            sleep_quality = w.get("sleep_quality")
            sleep_quality_item = QTableWidgetItem(str(sleep_quality) if sleep_quality else "")
            sleep_quality_item.setFlags(sleep_quality_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, sleep_quality_item)
            col += 1
            
            # 7: Avg Sleep HR
            avg_sleep_hr = w.get("avg_sleeping_hr")
            avg_sleep_hr_item = QTableWidgetItem(f"{avg_sleep_hr:.1f}" if avg_sleep_hr else "")
            avg_sleep_hr_item.setFlags(avg_sleep_hr_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, avg_sleep_hr_item)
            col += 1
            
            # 8: Soreness
            soreness = w.get("soreness")
            soreness_item = QTableWidgetItem(str(soreness) if soreness else "")
            soreness_item.setFlags(soreness_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, soreness_item)
            col += 1
            
            # 9: Fatigue
            fatigue = w.get("fatigue")
            fatigue_item = QTableWidgetItem(str(fatigue) if fatigue else "")
            fatigue_item.setFlags(fatigue_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, fatigue_item)
            col += 1
            
            # 10: Stress
            stress = w.get("stress")
            stress_item = QTableWidgetItem(str(stress) if stress else "")
            stress_item.setFlags(stress_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, stress_item)
            col += 1
            
            # 11: Mood
            mood = w.get("mood")
            mood_item = QTableWidgetItem(str(mood) if mood else "")
            mood_item.setFlags(mood_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, mood_item)
            col += 1
            
            # 12: Motivation
            motivation = w.get("motivation")
            motivation_item = QTableWidgetItem(str(motivation) if motivation else "")
            motivation_item.setFlags(motivation_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, motivation_item)
            col += 1
            
            # 13: Injury
            injury = w.get("injury")
            injury_item = QTableWidgetItem(str(int(injury)) if injury else "")
            injury_item.setFlags(injury_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, injury_item)
            col += 1
            
            # 14: Calories
            kcal = w.get("kcal")
            kcal_item = QTableWidgetItem(str(kcal) if kcal else "")
            kcal_item.setFlags(kcal_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, kcal_item)
            col += 1
            
            # 15: Body Fat (%)
            body_fat = w.get("body_fat")
            body_fat_item = QTableWidgetItem(f"{body_fat:.1f}" if body_fat else "")
            body_fat_item.setFlags(body_fat_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, body_fat_item)
            col += 1
            
            # 16: Respiration
            respiration = w.get("respiration")
            respiration_item = QTableWidgetItem(f"{respiration:.1f}" if respiration else "")
            respiration_item.setFlags(respiration_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, respiration_item)
            col += 1
            
            # 17: SpO2 (%)
            spO2 = w.get("spO2")
            spO2_item = QTableWidgetItem(f"{spO2:.1f}" if spO2 else "")
            spO2_item.setFlags(spO2_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, spO2_item)
            col += 1
            
            # 18: Menstrual Phase
            menstrual_phase = w.get("menstrual_cycle_phase")
            phase_names = {1: "Menstrual", 2: "Follicular", 3: "Ovulatory", 4: "Luteal"}
            phase_item = QTableWidgetItem(phase_names.get(menstrual_phase, "") if menstrual_phase else "")
            phase_item.setFlags(phase_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, phase_item)
            col += 1
            
            # 19: Menstruation
            menstruation = w.get("menstruation")
            menstruation_item = QTableWidgetItem("Yes" if menstruation else ("No" if menstruation is False else ""))
            menstruation_item.setFlags(menstruation_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, menstruation_item)
            col += 1
            
            # 20: Comments
            comments = w.get("comments", "")
            comments_item = QTableWidgetItem(str(comments) if comments else "")
            comments_item.setFlags(comments_item.flags() & ~Qt.ItemIsEditable)
            self.wellness_table.setItem(row_idx, col, comments_item)
    
    def _hide_empty_columns(self) -> None:
        """Nascondi le colonne che non contengono dati in nessuna riga."""
        # Column indices and their keys
        column_keys = [
            (0, "wellness_date"), (1, "weight_kg"), (2, "resting_hr"), (3, "hrv"),
            (4, "sleep_secs"), (5, "sleep_score"), (6, "sleep_quality"), (7, "avg_sleeping_hr"),
            (8, "soreness"), (9, "fatigue"), (10, "stress"), (11, "mood"),
            (12, "motivation"), (13, "injury"), (14, "kcal"), (15, "body_fat"),
            (16, "respiration"), (17, "spO2"), (18, "menstrual_cycle_phase"), (19, "menstruation"), (20, "comments")
        ]
        
        for col_idx, key in column_keys:
            # Check if all values in this column are empty/None
            all_empty = True
            for row_data in self.wellness_data:
                value = row_data.get(key)
                if value is not None and value != "" and value is not False:
                    all_empty = False
                    break
            
            # Hide the column if all values are empty
            if all_empty:
                self.wellness_table.setColumnHidden(col_idx, True)
    
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
                    menstrual_phase = item.get("menstrualPhase")  # 1=menstrual, 2=follicular, 3=ovulatory, 4=luteal
                    menstruation = item.get("menstruation")  # Boolean for menstruation day
                    body_fat = item.get("bodyFat") or item.get("body_fat")
                    respiration = item.get("respiration")
                    spO2 = item.get("spO2")
                    comments = item.get("comments")
                    
                    # Converti menstrual_phase a int se numerico
                    if menstrual_phase is not None and not isinstance(menstrual_phase, int):
                        try:
                            menstrual_phase = int(menstrual_phase) if menstrual_phase else None
                        except (ValueError, TypeError):
                            menstrual_phase = None
                    
                    # Converti menstruation a boolean
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
                        menstrual_cycle_phase=menstrual_phase,
                        body_fat=body_fat,
                        respiration=respiration,
                        spO2=spO2,
                        comments=comments,
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

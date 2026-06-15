import webbrowser
import sys
import os
import requests  # 🚀 Used for real-time SerpApi credit metric tracking
import scraper_engine  # 🔗 Background scraper module
import export_engine   # 🔗 Document generation module

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QCheckBox, 
    QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QPainter, QPolygon, QColor, QCursor

def fetch_live_serp_credits():
    """Connects directly to SerpApi to extract remaining search credits in real-time."""
    api_key = scraper_engine.get_stored_api_key()
    if not api_key:
        return "Missing Key"
    endpoint = "https://serpapi.com/account.json"
    params = {"api_key": api_key}
    try:
        response = requests.get(endpoint, params=params, timeout=5)
        if response.status_code == 200:
            account_info = response.json()
            return str(account_info.get("plan_searches_left", 0))
    except:
        pass
    return "Offline (Check Connection)"


class LogoWidget(QWidget):
    """Custom widget rendering precise geometric emblem using vector points."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 50) 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        base_color = QColor("#6B1D66") 
        painter.setBrush(base_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, self.width(), self.height())
        fold_color = QColor("#E397E1") 
        painter.setBrush(fold_color)
        points = QPolygon([
            QPoint(0, 0), QPoint(self.width(), 0),
            QPoint(self.width() // 2, int(self.height() * 0.46))
        ])
        painter.drawPolygon(points)


class TimeVehicleUI(QWidget):
    def __init__(self):
        super().__init__()
        self.live_credits = fetch_live_serp_credits()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Time vehicle - 1.0")
        
        # 🔓 FLEXIBLE WINDOW RESIZING: Enables the Maximize button natively
        self.setMinimumSize(440, 600)  
        self.resize(480, 680)          
        self.setStyleSheet("background-color: #FFFFFF;")
        
        title_font = QFont("Arial", 14, QFont.Weight.Bold)
        section_font = QFont("Arial", 11, QFont.Weight.Bold)
        label_font = QFont("Arial", 10)
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        
        # Scroll Area Setup
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #FFFFFF; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #FFFFFF;")
        master_layout = QVBoxLayout(scroll_content)
        master_layout.setContentsMargins(0, 0, 0, 0)
        master_layout.setSpacing(0)
        
        # --- PREMIUM HEADER BANNER SECTION ---
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #002D4A; border: none;") 
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(25, 20, 25, 20)
        header_layout.setSpacing(15)
        
        self.logo_emblem = LogoWidget()
        header_layout.addWidget(self.logo_emblem)
        
        title = QLabel("TIME VEHICLE - 1.0")
        title.setFont(title_font)
        title.setStyleSheet("color: #FFFFFF; line-height: 1.2;") 
        header_layout.addWidget(title)
        header_layout.addStretch()
        master_layout.addWidget(header_widget)
        
        sheet_widget = QWidget()
        sheet_widget.setStyleSheet("background-color: #FFFFFF;")
        sheet_layout = QVBoxLayout(sheet_widget)
        sheet_layout.setSpacing(12)
        sheet_layout.setContentsMargins(25, 15, 25, 20)
        
        # LIVE METRIC BALANCE INDICATION ROW
        credit_frame = QFrame()
        credit_frame.setStyleSheet("background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 4px;")
        credit_layout = QHBoxLayout(credit_frame)
        credit_layout.setContentsMargins(12, 6, 12, 6)
        
        self.lbl_credits = QLabel(f"💳 Searches Remaining: {self.live_credits}", font=label_font)
        self.lbl_credits.setStyleSheet("color: #0F172A; font-weight: bold;")
        
        btn_recharge = QPushButton("🔌 Recharge")
        btn_recharge.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        btn_recharge.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_recharge.setStyleSheet("""
            QPushButton {
                background-color: #10B981; color: white; border: none; 
                border-radius: 4px; padding: 5px 12px;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        btn_recharge.clicked.connect(self.open_serpapi_billing)
        
        credit_layout.addWidget(self.lbl_credits)
        credit_layout.addStretch()
        credit_layout.addWidget(btn_recharge)
        sheet_layout.addWidget(credit_frame)
        
        # --- INPUT FIELDS SECTION ---
        lbl_prof = QLabel("Field of search/profession:", font=label_font)
        lbl_prof.setStyleSheet("color: #333333;")
        sheet_layout.addWidget(lbl_prof)
        self.input_profession = QLineEdit()
        self.input_profession.setPlaceholderText("e.g., Orthopedic doctor")
        sheet_layout.addWidget(self.input_profession)
        
        lbl_local = QLabel("Locality/area name :", font=label_font)
        lbl_local.setStyleSheet("color: #333333;")
        sheet_layout.addWidget(lbl_local)
        self.input_locality = QLineEdit()
        self.input_locality.setPlaceholderText("e.g., 401 SW 42nd Ave #200")
        sheet_layout.addWidget(self.input_locality)
        
        geo_layout = QHBoxLayout()
        geo_layout.setSpacing(15)
        
        vbox_city = QVBoxLayout()
        lbl_city = QLabel("City:", font=label_font)
        lbl_city.setStyleSheet("color: #333333;")
        vbox_city.addWidget(lbl_city)
        self.input_city = QLineEdit()
        self.input_city.setPlaceholderText("e.g., Miami")
        vbox_city.addWidget(self.input_city)
        
        vbox_state = QVBoxLayout()
        lbl_state = QLabel("State:", font=label_font)
        lbl_state.setStyleSheet("color: #333333;")
        vbox_state.addWidget(lbl_state)
        self.input_state = QLineEdit()
        self.input_state.setPlaceholderText("e.g., Florida")
        vbox_state.addWidget(self.input_state)
        
        vbox_country = QVBoxLayout()
        lbl_country = QLabel("Country:", font=label_font)
        lbl_country.setStyleSheet("color: #333333;")
        vbox_country.addWidget(lbl_country)
        self.input_country = QLineEdit()
        self.input_country.setPlaceholderText("e.g., USA")
        vbox_country.addWidget(self.input_country)
        
        geo_layout.addLayout(vbox_city, stretch=1)
        geo_layout.addLayout(vbox_state, stretch=1)
        geo_layout.addLayout(vbox_country, stretch=1)
        sheet_layout.addLayout(geo_layout)
        
        for edit in [self.input_profession, self.input_locality, self.input_city, self.input_state, self.input_country]:
            edit.setStyleSheet("padding: 8px; border: 1px solid #B0C4DE; border-radius: 4px; background: #FFFFFF; color: #000000;")
        
        self.add_separator(sheet_layout)
        
        # --- RATING RANGE FILTERS ---
        rating_label = QLabel("Google rating range")
        rating_label.setFont(section_font)
        rating_label.setStyleSheet("color: #002D4A;")
        sheet_layout.addWidget(rating_label)
        
        rating_layout = QHBoxLayout()
        ratings = ["5", "4", "3", "2", "1", "0", "ALL"]
        self.rating_checkboxes = {}
        checkbox_style = "QCheckBox { color: #333333; padding: 4px; } QCheckBox::indicator { width: 16px; height: 16px; }"
        
        for rate in ratings:
            cb = QCheckBox(rate)
            cb.setFont(label_font)
            cb.setStyleSheet(checkbox_style)
            if rate == "ALL":
                cb.setChecked(True)
                cb.toggled.connect(self.handle_all_ratings_toggle)
            else:
                cb.toggled.connect(self.handle_single_rating_toggle)
            rating_layout.addWidget(cb)
            self.rating_checkboxes[rate] = cb
            
        sheet_layout.addLayout(rating_layout)
        self.add_separator(sheet_layout)
        
        # --- DOWNLOAD SYSTEM SELECTION ---
        download_label = QLabel("Download to System:")
        download_label.setFont(section_font)
        download_label.setStyleSheet("color: #002D4A;")
        sheet_layout.addWidget(download_label)
        
        format_layout = QHBoxLayout()
        self.chk_excel = QCheckBox("Excel")
        self.chk_excel.setChecked(True)
        self.chk_excel.setFont(label_font)
        self.chk_excel.setStyleSheet(checkbox_style)
        
        format_layout.addWidget(self.chk_excel)
        sheet_layout.addLayout(format_layout)
        
        self.add_separator(sheet_layout)
        sheet_layout.addSpacing(5)
        
        # MAIN SUBMIT BUTTON
        self.btn_submit = QPushButton("SUBMIT")
        self.btn_submit.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.btn_submit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_submit.setStyleSheet("""
            QPushButton {
                background-color: #002D4A; color: white;
                padding: 12px; border: none; border-radius: 4px;
            }
            QPushButton:hover { background-color: #004473; }
            QPushButton:pressed { background-color: #001524; }
        """)
        self.btn_submit.clicked.connect(self.handle_submit_action)
        sheet_layout.addWidget(self.btn_submit)
        
        # --- SUPPORT BADGE FOOTER ROW ---
        sheet_layout.addSpacing(15)
        support_frame = QFrame()
        support_frame.setStyleSheet("background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 12px;")
        support_layout = QHBoxLayout(support_frame)
        
        lbl_support_text = QLabel("💬 Need help or customized solutions? WhatsApp us at:\n👉 +91 77803 79259")
        lbl_support_text.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        lbl_support_text.setStyleSheet("color: #475569; line-height: 1.4;")
        lbl_support_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        support_layout.addWidget(lbl_support_text)
        sheet_layout.addWidget(support_frame)
        
        master_layout.addWidget(sheet_widget)
        scroll_area.setWidget(scroll_content)
        outer_layout.addWidget(scroll_area)
        
    def add_separator(self, layout):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #E2E8F0; margin-top: 5px; margin-bottom: 5px; border: none; background-color: #E2E8F0; height: 1px;")
        layout.addWidget(line)

    def handle_all_ratings_toggle(self, checked):
        if checked:
            for rate, cb in self.rating_checkboxes.items():
                if rate != "ALL":
                    cb.blockSignals(True)
                    cb.setChecked(False)
                    cb.blockSignals(False)

    def handle_single_rating_toggle(self, checked):
        if checked:
            self.rating_checkboxes["ALL"].blockSignals(True)
            self.rating_checkboxes["ALL"].setChecked(False)
            self.rating_checkboxes["ALL"].blockSignals(False)
            
    def open_serpapi_billing(self, event=None):
        webbrowser.open("https://serpapi.com/plan")
        self.refresh_credit_display()
        
    def refresh_credit_display(self):
        self.live_credits = fetch_live_serp_credits()
        self.lbl_credits.setText(f"💳 Searches Remaining: {self.live_credits}")

    def handle_submit_action(self):
        profession = self.input_profession.text().strip()
        locality = self.input_locality.text().strip()
        city = self.input_city.text().strip()
        state = self.input_state.text().strip()
        country = self.input_country.text().strip()
        
        if not profession or not city:
            QMessageBox.warning(self, "Missing Information", "Profession and City fields are mandatory!")
            return
            
        selected_ratings = []
        if self.rating_checkboxes["ALL"].isChecked():
            selected_ratings = ["ALL"]
        else:
            for rate, cb in self.rating_checkboxes.items():
                if rate != "ALL" and cb.isChecked():
                    selected_ratings.append(rate)
                    
        if not selected_ratings:
            QMessageBox.warning(self, "Missing Rating", "Please select at least one rating box or select 'ALL'.")
            return

        # 🎯 KEEP SEARCH QUERY RESTRICTED TO KEYWORDS ONLY
        search_components = []
        if profession: search_components.append(profession)
        if locality:   search_components.append(locality)
        clean_search_query = " ".join(search_components)
        
        # Build a separate location context string out of geographic fields
        geo_components = []
        if city:    geo_components.append(city)
        if state:   geo_components.append(state)
        if country: geo_components.append(country)
        target_location_context = ", ".join(geo_components)
        
        self.btn_submit.setEnabled(False)
        self.btn_submit.setText("⏳ SCRAPING DATA... PLEASE WAIT")
        QApplication.processEvents()
        
        try:
            # 📡 1. Pull down the dictionary packet from the live-patched scraper engine
            extraction_packet = scraper_engine.extract_local_leads(
                search_query=clean_search_query, 
                allowed_ratings=selected_ratings,
                target_city=target_location_context
            )
            
            # 📦 2. Unpack the database rows and your explicit columns matrix sent from GitHub Gist
            extracted_data = extraction_packet.get("data", [])
            active_columns_layout = extraction_packet.get("columns_layout", None)
            
            if not extracted_data:
                QMessageBox.warning(self, "No Results", "No target entities found matching your parameters.")
                return
                
            saved_file_paths = []
            if self.chk_excel.isChecked():
                # 🚀 3. Pass BOTH records and columns over to export engine (Branded as timevehicle)
                xl_path = export_engine.save_to_excel(extracted_data, active_columns_layout)
                saved_file_paths.append(f"• Excel File Created: {xl_path}")
                
            self.refresh_credit_display()
            
            success_summary = (
                "SUCCESS: Leads Compiled Successfully!\n\n"
                f"Total Rows Gathered: {len(extracted_data)}\n\n"
                "Saved Local Destinations:\n" + "\n".join(saved_file_paths)
            )
            QMessageBox.information(self, "Extraction Complete", success_summary)
            
        except Exception as e:
            QMessageBox.critical(self, "Extraction Failure", f"An anomaly broke your live data loop: {str(e)}")
        finally:
            self.btn_submit.setEnabled(True)
            self.btn_submit.setText("SUBMIT")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 🍏 WINDOWS VS MULTI-OS STYLE OPTIMIZER
    if sys.platform == "win32":
        app.setStyle('Fusion')
        
    window = TimeVehicleUI()
    window.show()
    sys.exit(app.exec())
class ScanProgressDialog(QWidget):
    """Progress dialog shown during system scan."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SystemScope — Scanning...")
        self.setFixedSize(400, 150)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        self.status_label = QLabel("Initializing scan...")
        self.status_label.setStyleSheet("font-size: 12pt;")
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setMaximumHeight(20)
        layout.addWidget(self.progress_bar)
        
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("color: #8b949e; font-size: 10pt;")
        layout.addWidget(self.detail_label)
        
        # Style
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #161b22;
                color: #c9d1d9;
            }}
            QProgressBar {{
                border: 1px solid #30363d;
                border-radius: 4px;
                background-color: #0d1117;
            }}
            QProgressBar::chunk {{
                background-color: #ff3860;
                border-radius: 3px;
            }}
        """)
    
    def update_status(self, message):
        self.status_label.setText(message)
    
    def update_detail(self, message):
        self.detail_label.setText(message)
    
    def scan_complete(self):
        self.status_label.setText("Scan complete!")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        QTimer.singleShot(500, self.close)

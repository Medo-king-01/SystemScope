    def _setup_menu_bar(self):
        """Setup menu bar with Help > About."""
        menu_bar = self.menuBar()
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("ℹ️ About", self._show_about)
        help_menu.addAction("📋 System Requirements", self._show_requirements)
        help_menu.addSeparator()
        help_menu.addAction("🚪 Exit", self.close)

    def _show_about(self):
        """Show About dialog."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(
            self, "About SystemScope",
            "<h3>🔍 SystemScope v1.0</h3>"
            "<p><b>Local System Intelligence Dashboard</b></p>"
            "<p>Professional Windows system monitoring,<br>"
            "diagnostics, and reporting.</p>"
            "<hr>"
            "<p><b>Built by Medo</b><br>"
            "github.com/Medo-king-01</p>"
            "<hr>"
            "<p><small>MIT License</small></p>"
        )

    def _show_requirements(self):
        """Show System Requirements dialog."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self, "📋 System Requirements",
            "<h3>System Requirements</h3>"
            "<table cellpadding='6' cellspacing='0'>"
            "<tr><td><b>OS:</b></td><td>Windows 10 or later</td></tr>"
            "<tr><td><b>RAM:</b></td><td>4 GB minimum (8 GB recommended)</td></tr>"
            "<tr><td><b>GPU:</b></td><td>DirectX 10+ (NVIDIA/AMD/Intel)</td></tr>"
            "<tr><td><b>Storage:</b></td><td>50 MB free space</td></tr>"
            "<tr><td><b>Python:</b></td><td>3.10+ (if building from source)</td></tr>"
            "</table>"
            "<hr>"
            "<p><b>Features:</b></p>"
            "• CPU/RAM/GPU monitoring<br>"
            "• Network analysis (TCP ping, interfaces)<br>"
            "• Storage analysis (PowerShell .NET)<br>"
            "• Rule-based diagnostics<br>"
            "• Historical trend charts<br>"
            "• HTML/JSON/CSV export"
        )
# pip install PySide6 matplotlib pandas reportlab
import sys, os, pandas as pd
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFormLayout, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdfcanvas

DATA_FILE = "life_sync_data.csv"

TEXT = {
    "EN": {
        "title": "Life Sync",
        "info": "Enter your daily data:",
        "date": "Date (YYYY-MM-DD):",
        "sleep": "Sleep Hours:",
        "work": "Work Hours:",
        "mood": "Mood (1-10):",
        "add": "Add Data",
        "show": "Show Chart",
        "suggest": "Life Sync Suggestions",
        "data_added": "✅ Data added successfully!",
        "error": "❌ Invalid input! Check all fields.",
        "no_data": "No data available.",
        "export_pdf": "Export Weekly PDF"
    }
}

class LifeSyncSimple(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(TEXT["EN"]["title"])
        self.setGeometry(50, 50, 800, 600)
        self.setStyleSheet("background-color: #ffffff; color: #000000;")
        self.data = {"date": [], "sleep_hours": [], "work_hours": [], "mood": []}
        self.load_csv()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Info
        self.info_label = QLabel(TEXT["EN"]["info"])
        self.info_label.setFont(QFont("Tahoma", 12))
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        # Form
        form_layout = QFormLayout()
        self.date_input = QLineEdit()
        self.sleep_input = QLineEdit()
        self.work_input = QLineEdit()
        self.mood_input = QLineEdit()
        form_layout.addRow(TEXT["EN"]["date"], self.date_input)
        form_layout.addRow(TEXT["EN"]["sleep"], self.sleep_input)
        form_layout.addRow(TEXT["EN"]["work"], self.work_input)
        form_layout.addRow(TEXT["EN"]["mood"], self.mood_input)
        layout.addLayout(form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton(TEXT["EN"]["add"])
        self.add_btn.clicked.connect(self.add_data)
        self.show_btn = QPushButton(TEXT["EN"]["show"])
        self.show_btn.clicked.connect(self.show_chart)
        self.suggest_btn = QPushButton(TEXT["EN"]["suggest"])
        self.suggest_btn.clicked.connect(self.suggest)
        self.export_btn = QPushButton(TEXT["EN"]["export_pdf"])
        self.export_btn.clicked.connect(self.export_pdf)
        for btn in [self.add_btn, self.show_btn, self.suggest_btn, self.export_btn]:
            btn.setStyleSheet("background-color: #000000; color: white; padding: 6px; border-radius: 6px; font-size: 12px;")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.show_btn)
        btn_layout.addWidget(self.suggest_btn)
        btn_layout.addWidget(self.export_btn)
        layout.addLayout(btn_layout)

        # Chart
        self.figure = plt.figure(facecolor="#ffffff")
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        self.show_chart()

    def add_data(self):
        try:
            date = pd.to_datetime(self.date_input.text())
            sleep = float(self.sleep_input.text())
            work = float(self.work_input.text())
            mood = int(self.mood_input.text())
            if not (1 <= mood <= 10):
                raise ValueError("Mood out of range")
            self.data["date"].append(date)
            self.data["sleep_hours"].append(sleep)
            self.data["work_hours"].append(work)
            self.data["mood"].append(mood)
            self.info_label.setText(TEXT["EN"]["data_added"])
            self.date_input.clear()
            self.sleep_input.clear()
            self.work_input.clear()
            self.mood_input.clear()
            self.save_csv()
            self.show_chart()
        except Exception:
            self.info_label.setText(TEXT["EN"]["error"])

    def show_chart(self):
        self.figure.clear()
        if not self.data["date"]:
            self.info_label.setText(TEXT["EN"]["no_data"])
            return
        df = pd.DataFrame(self.data).sort_values("date")
        ax = self.figure.add_subplot(111)
        ax.plot(df['date'], df['sleep_hours'], marker='o', label="Sleep", color="#ff6f61")
        ax.plot(df['date'], df['work_hours'], marker='s', label="Work", color="#2196f3")
        ax.plot(df['date'], df['mood'], marker='^', label="Mood", color="#ffca28")
        ax.set_facecolor("#ffffff")
        ax.set_xlabel('Date', color="#000000")
        ax.set_ylabel('Value', color="#000000")
        ax.set_title("Life Sync Trend", fontsize=14, fontweight='bold', color="#000000")
        ax.tick_params(colors="#000000")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        self.canvas.draw()

    def suggest(self):
        if not self.data["date"]:
            self.info_label.setText(TEXT["EN"]["no_data"])
            return
        avg_sleep = sum(self.data["sleep_hours"]) / len(self.data["sleep_hours"])
        avg_work = sum(self.data["work_hours"]) / len(self.data["work_hours"])
        avg_mood = sum(self.data["mood"]) / len(self.data["mood"])
        suggestion = "💡 Suggestions:\n"
        suggestion += "- Sleep good\n" if avg_sleep >= 7 else "- Sleep low\n"
        suggestion += "- Work good\n" if avg_work >= 5 else "- Work low\n"
        suggestion += "- Mood good\n" if avg_mood >= 6 else "- Mood low\n"
        self.info_label.setText(suggestion)

    def save_csv(self):
        df = pd.DataFrame(self.data)
        df.to_csv(DATA_FILE, index=False)

    def load_csv(self):
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            self.data = df.to_dict(orient="list")

    def export_pdf(self):
        if not self.data["date"]:
            self.info_label.setText(TEXT["EN"]["no_data"])
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if not path:
            return
        df = pd.DataFrame(self.data)
        c = pdfcanvas.Canvas(path, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "Life Sync Weekly Report")
        y = 700
        for col in ["date", "sleep_hours", "work_hours", "mood"]:
            c.drawString(50, y, f"{col}: {df[col].tolist()}")
            y -= 20
        c.save()
        self.info_label.setText("✅ PDF exported successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LifeSyncSimple()
    window.show()
    sys.exit(app.exec())

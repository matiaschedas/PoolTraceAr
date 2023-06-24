import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QCheckBox, QSlider, QVBoxLayout, QHBoxLayout, QWidget, QPushButton


class PreprocesamientoWindow(QMainWindow):
    def __init__(self):
        super(PreprocesamientoWindow, self).__init__()

        self.setWindowTitle("Preprocesamiento de imagen")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        self.brightness_layout = QHBoxLayout()
        self.brightness_label = QLabel("Brillo", self)
        self.brightness_layout.addWidget(self.brightness_label)

        self.brightness_checkbox = QCheckBox(self)
        self.brightness_layout.addWidget(self.brightness_checkbox)

        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setDisabled(True)  # Desactivado por defecto
        self.brightness_layout.addWidget(self.brightness_slider)

        self.layout.addLayout(self.brightness_layout)

        self.contrast_layout = QHBoxLayout()
        self.contrast_label = QLabel("Contraste", self)
        self.contrast_layout.addWidget(self.contrast_label)

        self.contrast_checkbox = QCheckBox(self)
        self.contrast_layout.addWidget(self.contrast_checkbox)

        self.alpha_slider = QSlider(Qt.Horizontal)
        self.alpha_slider.setMinimum(0)
        self.alpha_slider.setMaximum(100)
        self.alpha_slider.setDisabled(True)  # Desactivado por defecto
        self.contrast_layout.addWidget(self.alpha_slider)

        self.beta_slider = QSlider(Qt.Horizontal)
        self.beta_slider.setMinimum(0)
        self.beta_slider.setMaximum(100)
        self.beta_slider.setDisabled(True)  # Desactivado por defecto
        self.contrast_layout.addWidget(self.beta_slider)

        self.layout.addLayout(self.contrast_layout)

        self.hist_layout = QHBoxLayout()
        self.hist_label = QLabel("Hist", self)
        self.hist_layout.addWidget(self.hist_label)

        self.hist_checkbox = QCheckBox(self)
        self.hist_layout.addWidget(self.hist_checkbox)

        self.hist_slider = QSlider(Qt.Horizontal)
        self.hist_slider.setMinimum(0)
        self.hist_slider.setMaximum(100)
        self.hist_slider.setDisabled(True)  # Desactivado por defecto
        self.hist_layout.addWidget(self.hist_slider)

        self.layout.addLayout(self.hist_layout)

        self.blur_layout = QHBoxLayout()
        self.blur_label = QLabel("Blur", self)
        self.blur_layout.addWidget(self.blur_label)

        self.blur_checkbox = QCheckBox(self)
        self.blur_layout.addWidget(self.blur_checkbox)

        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setMinimum(0)
        self.blur_slider.setMaximum(100)
        self.blur_slider.setDisabled(True)  # Desactivado por defecto
        self.blur_layout.addWidget(self.blur_slider)

        self.layout.addLayout(self.blur_layout)

        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        self.view_frame_button = QPushButton("Ver frame", self)
        self.button_layout.addWidget(self.view_frame_button)

        self.layout.addLayout(self.button_layout)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.brightness_checkbox.stateChanged.connect(self.on_brightness_checkbox_changed)
        self.contrast_checkbox.stateChanged.connect(self.on_contrast_checkbox_changed)
        self.hist_checkbox.stateChanged.connect(self.on_hist_checkbox_changed)
        self.blur_checkbox.stateChanged.connect(self.on_blur_checkbox_changed)
        self.brightness_slider.valueChanged.connect(self.on_brightness_slider_changed)
        self.alpha_slider.valueChanged.connect(self.on_contrast_alpha_slider_changed)
        self.beta_slider.valueChanged.connect(self.on_contrast_beta_slider_changed)
        self.hist_slider.valueChanged.connect(self.on_hist_slider_changed)
        self.blur_slider.valueChanged.connect(self.on_blur_slider_changed)
        self.view_frame_button.clicked.connect(self.on_view_frame_button_clicked)

    def on_brightness_checkbox_changed(self, state):
        if state == Qt.Checked:
            self.brightness_slider.setEnabled(True)
        else:
            self.brightness_slider.setEnabled(False)

    def on_contrast_checkbox_changed(self, state):
        if state == Qt.Checked:
            self.alpha_slider.setEnabled(True)
            self.beta_slider.setEnabled(True)
        else:
            self.alpha_slider.setEnabled(False)
            self.beta_slider.setEnabled(False)

    def on_hist_checkbox_changed(self, state):
        if state == Qt.Checked:
            self.hist_slider.setEnabled(True)
        else:
            self.hist_slider.setEnabled(False)

    def on_blur_checkbox_changed(self, state):
        if state == Qt.Checked:
            self.blur_slider.setEnabled(True)
        else:
            self.blur_slider.setEnabled(False)

    def on_brightness_slider_changed(self, value):
        brightness = value / 100.0
        print(f"Brightness: {brightness}")

    def on_contrast_alpha_slider_changed(self, value):
        alpha = value / 100.0
        print(f"Alpha: {alpha}")

    def on_contrast_beta_slider_changed(self, value):
        beta = value / 100.0
        print(f"Beta: {beta}")

    def on_hist_slider_changed(self, value):
        hist = value / 100.0
        print(f"Hist: {hist}")

    def on_blur_slider_changed(self, value):
        blur = value / 100.0
        print(f"Blur: {blur}")

    def on_view_frame_button_clicked(self):
        print("Ver frame")

    
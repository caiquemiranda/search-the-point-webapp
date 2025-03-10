import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                           QHBoxLayout, QWidget, QPushButton, QFileDialog, 
                           QScrollArea, QFrame, QSizePolicy)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint
import fitz  # PyMuPDF
import numpy as np
import pandas as pd

class ClickableImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.points = []
        self.zoom_factor = 1.0
        self.setMouseTracking(True)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.pixmap():
            painter = QPainter(self)
            pen = QPen(QColor(255, 0, 0))  # Cor vermelha
            pen.setWidth(5)
            painter.setPen(pen)
            
            for point in self.points:
                painter.drawEllipse(point, 5, 5)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.pixmap():
            pos = event.pos()
            self.points.append(pos)
            self.parent.capture_click(pos)
            self.update()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor *= 0.9
        
        self.zoom_factor = max(0.1, min(5.0, self.zoom_factor))
        self.parent.update_zoom()

class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.coordenadas = []
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Capturador de Coordenadas PDF')
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central com layout horizontal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Área esquerda (imagem)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Área de rolagem para a imagem
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Label da imagem personalizado
        self.image_label = ClickableImageLabel(self)
        self.image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.scroll_area.setWidget(self.image_label)
        
        # Botão para abrir PDF
        self.open_btn = QPushButton('Abrir PDF')
        self.open_btn.clicked.connect(self.open_pdf)
        left_layout.addWidget(self.open_btn)
        
        left_layout.addWidget(self.scroll_area)
        main_layout.addWidget(left_widget, stretch=4)  # 80% da largura
        
        # Área direita (coordenadas e controles)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_widget.setMaximumWidth(300)  # Largura fixa para a coluna lateral
        
        # Frame para lista de coordenadas
        coord_frame = QFrame()
        coord_frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        coord_layout = QVBoxLayout(coord_frame)
        
        # Label para título das coordenadas
        coord_title = QLabel("Coordenadas Capturadas")
        coord_title.setAlignment(Qt.AlignCenter)
        coord_layout.addWidget(coord_title)
        
        # Label para mostrar coordenadas
        self.coord_label = QLabel()
        self.coord_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        coord_layout.addWidget(self.coord_label)
        
        right_layout.addWidget(coord_frame)
        
        # Botões de controle
        self.save_btn = QPushButton('Salvar Coordenadas')
        self.save_btn.clicked.connect(self.save_coordinates)
        right_layout.addWidget(self.save_btn)
        
        self.clear_btn = QPushButton('Limpar Coordenadas')
        self.clear_btn.clicked.connect(self.clear_coordinates)
        right_layout.addWidget(self.clear_btn)
        
        main_layout.addWidget(right_widget, stretch=1)  # 20% da largura
        
    def open_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir PDF", "", "PDF files (*.pdf)")
        if file_name:
            # Abrir PDF com PyMuPDF
            doc = fitz.open(file_name)
            page = doc[0]  # Primeira página
            
            # Converter para imagem com alta resolução
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom para melhor qualidade
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            
            # Salvar dimensões originais
            self.original_width = pix.width
            self.original_height = pix.height
            
            # Mostrar imagem
            pixmap = QPixmap.fromImage(img)
            self.image_label.setPixmap(pixmap)
            self.update_zoom()
            
            doc.close()
            
            # Limpar coordenadas anteriores
            self.clear_coordinates()
    
    def update_zoom(self):
        if self.image_label.pixmap():
            scaled_pixmap = self.image_label.pixmap().scaled(
                self.image_label.pixmap().width() * self.image_label.zoom_factor,
                self.image_label.pixmap().height() * self.image_label.zoom_factor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
    
    def capture_click(self, pos):
        if self.image_label.pixmap():
            # Calcular coordenadas considerando o zoom e scroll
            scroll_x = self.scroll_area.horizontalScrollBar().value()
            scroll_y = self.scroll_area.verticalScrollBar().value()
            
            x = (pos.x() + scroll_x) / self.image_label.zoom_factor
            y = (pos.y() + scroll_y) / self.image_label.zoom_factor
            
            # Adicionar coordenadas à lista
            self.coordenadas.append({'x': int(x), 'y': int(y)})
            self.update_coordinates_display()
    
    def update_coordinates_display(self):
        text = "Pontos capturados:\n\n"
        for idx, coord in enumerate(self.coordenadas, 1):
            text += f"{idx}. X: {coord['x']}, Y: {coord['y']}\n"
        self.coord_label.setText(text)
    
    def save_coordinates(self):
        if self.coordenadas:
            file_name, _ = QFileDialog.getSaveFileName(self, "Salvar Coordenadas", "", "CSV files (*.csv)")
            if file_name:
                df = pd.DataFrame(self.coordenadas)
                df.to_csv(file_name, index=False)
    
    def clear_coordinates(self):
        self.coordenadas = []
        self.image_label.points = []
        self.update_coordinates_display()
        self.image_label.update()

def main():
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 
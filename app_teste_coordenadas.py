import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                           QHBoxLayout, QWidget, QPushButton, QFileDialog, 
                           QScrollArea, QFrame, QSizePolicy, QInputDialog,
                           QListWidget, QListWidgetItem)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint, QSize, QRectF
import fitz  # PyMuPDF
import numpy as np
import pandas as pd
import json

class Point:
    def __init__(self, x, y, name=""):
        self.x = x
        self.y = y
        self.name = name

    def to_dict(self):
        return {'x': self.x, 'y': self.y, 'name': self.name}

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
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Desenhar pontos
            for point in self.points:
                # Converter coordenadas do ponto para coordenadas da tela
                screen_x = point.x * self.zoom_factor
                screen_y = point.y * self.zoom_factor
                
                # Desenhar círculo vermelho
                painter.setPen(QPen(QColor(255, 0, 0), 2))
                painter.setBrush(QColor(255, 0, 0, 127))
                painter.drawEllipse(QPoint(int(screen_x), int(screen_y)), 5, 5)
                
                # Desenhar nome do ponto
                if point.name:
                    painter.setPen(QColor(0, 0, 0))
                    painter.drawText(QPoint(int(screen_x + 10), int(screen_y)), point.name)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.pixmap():
            pos = event.pos()
            # Converter coordenadas da tela para coordenadas da imagem
            x = int(pos.x() / self.zoom_factor)
            y = int(pos.y() / self.zoom_factor)
            self.parent.add_point(x, y)

    def wheelEvent(self, event):
        old_pos = event.pos()
        old_factor = self.zoom_factor
        
        # Ajustar zoom
        if event.angleDelta().y() > 0:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor *= 0.9
        
        self.zoom_factor = max(0.1, min(5.0, self.zoom_factor))
        
        # Atualizar zoom mantendo o ponto sob o cursor
        self.parent.update_zoom(old_pos, old_factor)

class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.points = []
        self.original_pixmap = None
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
        
        # Botão para abrir PDF
        self.open_btn = QPushButton('Abrir PDF')
        self.open_btn.clicked.connect(self.open_pdf)
        left_layout.addWidget(self.open_btn)
        
        # Área de rolagem para a imagem
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Label da imagem personalizado
        self.image_label = ClickableImageLabel(self)
        self.image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.scroll_area.setWidget(self.image_label)
        
        left_layout.addWidget(self.scroll_area)
        main_layout.addWidget(left_widget, stretch=4)
        
        # Área direita (lista de pontos e controles)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_widget.setMaximumWidth(300)
        
        # Lista de pontos
        self.points_list = QListWidget()
        self.points_list.itemDoubleClicked.connect(self.edit_point)
        right_layout.addWidget(QLabel("Pontos Capturados:"))
        right_layout.addWidget(self.points_list)
        
        # Botões
        btn_layout = QHBoxLayout()
        
        self.save_all_btn = QPushButton('Salvar Todos')
        self.save_all_btn.clicked.connect(self.save_all_points)
        btn_layout.addWidget(self.save_all_btn)
        
        self.clear_btn = QPushButton('Limpar Todos')
        self.clear_btn.clicked.connect(self.clear_points)
        btn_layout.addWidget(self.clear_btn)
        
        right_layout.addLayout(btn_layout)
        main_layout.addWidget(right_widget)
        
    def add_point(self, x, y):
        name, ok = QInputDialog.getText(self, 'Nome do Ponto', 'Digite um nome para o ponto:')
        if ok:
            point = Point(x, y, name)
            self.points.append(point)
            self.image_label.points.append(point)
            
            # Adicionar à lista
            item = QListWidgetItem(f"{point.name}: ({point.x}, {point.y})")
            item.setData(Qt.UserRole, len(self.points) - 1)  # Índice do ponto
            self.points_list.addItem(item)
            
            # Opções para o ponto
            point_widget = QWidget()
            point_layout = QHBoxLayout(point_widget)
            
            save_btn = QPushButton('Salvar')
            save_btn.clicked.connect(lambda: self.save_point(len(self.points) - 1))
            delete_btn = QPushButton('Excluir')
            delete_btn.clicked.connect(lambda: self.delete_point(len(self.points) - 1))
            
            point_layout.addWidget(save_btn)
            point_layout.addWidget(delete_btn)
            
            self.points_list.setItemWidget(item, point_widget)
            self.image_label.update()

    def edit_point(self, item):
        index = item.data(Qt.UserRole)
        point = self.points[index]
        name, ok = QInputDialog.getText(self, 'Editar Nome', 'Novo nome:', text=point.name)
        if ok:
            point.name = name
            item.setText(f"{point.name}: ({point.x}, {point.y})")
            self.image_label.update()

    def save_point(self, index):
        point = self.points[index]
        file_name, _ = QFileDialog.getSaveFileName(self, f"Salvar Ponto {point.name}", 
                                                 f"{point.name}.json", "JSON files (*.json)")
        if file_name:
            with open(file_name, 'w') as f:
                json.dump(point.to_dict(), f)

    def delete_point(self, index):
        self.points.pop(index)
        self.image_label.points = self.points
        self.points_list.takeItem(index)
        self.image_label.update()
        
    def save_all_points(self):
        if self.points:
            file_name, _ = QFileDialog.getSaveFileName(self, "Salvar Todos os Pontos", 
                                                     "pontos.csv", "CSV files (*.csv)")
            if file_name:
                df = pd.DataFrame([p.to_dict() for p in self.points])
                df.to_csv(file_name, index=False)

    def clear_points(self):
        self.points = []
        self.image_label.points = []
        self.points_list.clear()
        self.image_label.update()

    def open_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir PDF", "", "PDF files (*.pdf)")
        if file_name:
            try:
                doc = fitz.open(file_name)
                page = doc[0]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                
                self.original_width = pix.width
                self.original_height = pix.height
                self.original_pixmap = QPixmap.fromImage(img)
                
                self.image_label.setPixmap(self.original_pixmap)
                self.update_zoom()
                
                doc.close()
                self.clear_points()
            except Exception as e:
                print(f"Erro ao abrir PDF: {str(e)}")

    def update_zoom(self, old_pos=None, old_factor=None):
        if self.original_pixmap and self.image_label.pixmap():
            new_width = int(self.original_pixmap.width() * self.image_label.zoom_factor)
            new_height = int(self.original_pixmap.height() * self.image_label.zoom_factor)
            
            scaled_pixmap = self.original_pixmap.scaled(
                new_width,
                new_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            
            if old_pos and old_factor:
                # Ajustar scroll para manter o ponto sob o cursor
                scroll_x = self.scroll_area.horizontalScrollBar()
                scroll_y = self.scroll_area.verticalScrollBar()
                
                factor_change = self.image_label.zoom_factor / old_factor
                
                new_scroll_x = int(factor_change * scroll_x.value() + 
                                 (factor_change - 1) * old_pos.x())
                new_scroll_y = int(factor_change * scroll_y.value() + 
                                 (factor_change - 1) * old_pos.y())
                
                scroll_x.setValue(new_scroll_x)
                scroll_y.setValue(new_scroll_y)

def main():
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 
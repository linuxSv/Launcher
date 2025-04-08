#!/usr/bin/env python3
import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QFrame, QScrollArea, QGridLayout,
                            QLineEdit, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap

class StableLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.all_apps = []
        self.app_widgets = []  # Mantener referencia a los widgets
        self.initUI()
        
    def initUI(self):
        # Configuración básica de la ventana
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Pantalla completa
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        # Widget principal con fondo semitransparente
        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("""
            background-color: rgba(40, 40, 40, 0.75);
            border-radius: 15px;
        """)
        self.setCentralWidget(self.main_widget)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(60, 60, 60, 60)
        self.main_layout.setSpacing(20)
        
        # Añadir buscador
        self.add_search_bar()
        
        # Configurar área de aplicaciones
        self.setup_app_grid()
        
        # Botón de cerrar mejorado
        self.add_safe_close_button()
        
        # Cargar aplicaciones
        QTimer.singleShot(100, self.load_applications)

    def add_search_bar(self):
        """Barra de búsqueda centrada"""
        search_container = QWidget()
        search_container.setStyleSheet("background: transparent;")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar aplicaciones...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 15px;
                padding: 10px;
                color: white;
                font-size: 14px;
                min-width: 300px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
        """)
        self.search_input.textChanged.connect(self.filter_apps)
        
        search_layout.addStretch()
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        
        self.main_layout.addWidget(search_container)

    def setup_app_grid(self):
        """Configuración segura del área de apps"""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")
        
        self.icons_container = QWidget()
        self.icons_container.setStyleSheet("background: transparent;")
        
        self.grid_layout = QGridLayout(self.icons_container)
        self.grid_layout.setSpacing(30)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        
        self.scroll_area.setWidget(self.icons_container)
        self.main_layout.addWidget(self.scroll_area)

    def load_applications(self):
        """Carga segura de aplicaciones"""
        try:
            self.all_apps = []
            desktop_dirs = [
                '/usr/share/applications',
                os.path.expanduser('~/.local/share/applications')
            ]
            
            for desktop_dir in desktop_dirs:
                if os.path.exists(desktop_dir):
                    for entry in os.scandir(desktop_dir):
                        if entry.name.endswith('.desktop'):
                            try:
                                with open(entry.path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                if 'NoDisplay=true' in content:
                                    continue
                                    
                                name = self.get_desktop_field(content, 'Name')
                                icon = self.get_desktop_field(content, 'Icon')
                                exec_cmd = self.get_desktop_field(content, 'Exec')
                                
                                if name and exec_cmd:
                                    self.all_apps.append({
                                        'name': name,
                                        'icon': icon,
                                        'exec': exec_cmd.split('%')[0].strip()
                                    })
                            except:
                                continue
            
            self.all_apps.sort(key=lambda x: x['name'].lower())
            self.filter_apps("")
            self.search_input.setFocus()
        except Exception as e:
            print(f"Error loading apps: {e}")

    def get_desktop_field(self, content, field):
        """Extracción segura de campos"""
        try:
            start = content.find(f"{field}=")
            if start == -1:
                return ""
            start += len(field) + 1
            end = content.find("\n", start)
            return content[start:end].strip()
        except:
            return ""

    def filter_apps(self, text):
        """Filtrado seguro de aplicaciones"""
        try:
            # Limpiar widgets antiguos
            for widget in self.app_widgets:
                widget.deleteLater()
            self.app_widgets.clear()
            
            search_text = text.lower()
            filtered_apps = [app for app in self.all_apps if search_text in app['name'].lower()]
            
            for i, app in enumerate(filtered_apps):
                self.add_app_widget(app, i)
        except Exception as e:
            print(f"Error filtering apps: {e}")

    def add_app_widget(self, app, index):
        """Añadir widget de app con manejo seguro"""
        try:
            app_widget = QWidget()
            self.app_widgets.append(app_widget)  # Mantener referencia
            
            app_widget.setFixedSize(100, 120)
            app_widget.setStyleSheet("background: transparent;")
            
            app_layout = QVBoxLayout(app_widget)
            app_layout.setSpacing(5)
            app_layout.setContentsMargins(0, 0, 0, 0)
            
            # Icono
            icon_label = QLabel()
            icon = QIcon.fromTheme(app['icon'], QIcon.fromTheme("application-x-executable"))
            icon_label.setPixmap(icon.pixmap(64, 64))
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet("""
                QLabel {
                    background: transparent;
                    padding: 5px;
                    border-radius: 10px;
                }
                QLabel:hover {
                    background: rgba(255, 255, 255, 0.1);
                }
            """)
            
            # Nombre
            name_label = QLabel(app['name'])
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                    background: transparent;
                }
            """)
            name_label.setWordWrap(True)
            
            app_layout.addWidget(icon_label)
            app_layout.addWidget(name_label)
            
            # Evento clic seguro
            app_widget.mousePressEvent = lambda e, cmd=app['exec']: self.safe_launch(cmd)
            
            # Posición en grid
            row = index // 7
            col = index % 7
            self.grid_layout.addWidget(app_widget, row, col, Qt.AlignCenter)
        except Exception as e:
            print(f"Error adding app widget: {e}")

    def add_safe_close_button(self):
        """Botón de cierre seguro"""
        try:
            self.close_btn = QLabel("✕", self)
            self.close_btn.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 24px;
                    padding: 8px;
                    background: rgba(255, 255, 255, 0.15);
                    border-radius: 12px;
                    qproperty-alignment: AlignCenter;
                }
                QLabel:hover {
                    background: rgba(255, 255, 255, 0.25);
                }
            """)
            self.close_btn.setFixedSize(40, 40)
            self.close_btn.move(self.width() - 70, 30)
            self.close_btn.mousePressEvent = self.safe_close
            self.close_btn.show()
        except Exception as e:
            print(f"Error adding close button: {e}")

    def safe_launch(self, cmd):
        """Lanzamiento seguro de apps"""
        try:
            subprocess.Popen(cmd, shell=True)
        except Exception as e:
            print(f"Error launching app: {e}")
        finally:
            self.safe_close()

    def safe_close(self, event=None):
        """Cierre seguro con limpieza"""
        try:
            self.hide()
            QTimer.singleShot(100, self.cleanup_and_close)
        except Exception as e:
            print(f"Error during safe close: {e}")
            QApplication.quit()

    def cleanup_and_close(self):
        """Limpieza antes de cerrar"""
        try:
            # Limpiar widgets
            for widget in self.app_widgets:
                widget.deleteLater()
            self.app_widgets.clear()
            
            # Cerrar ventana
            self.close()
        except:
            QApplication.quit()

    def keyPressEvent(self, event):
        """Manejo seguro de teclado"""
        try:
            if event.key() == Qt.Key_Escape:
                self.safe_close()
            elif event.key() == Qt.Key_Return and self.search_input.hasFocus():
                if self.grid_layout.count() > 0:
                    first_item = self.grid_layout.itemAt(0)
                    if first_item:
                        first_widget = first_item.widget()
                        if first_widget:
                            first_widget.mousePressEvent(None)
            else:
                super().keyPressEvent(event)
        except Exception as e:
            print(f"Key press error: {e}")

    def mousePressEvent(self, event):
        """Cierre al hacer clic fuera"""
        if event.button() == Qt.LeftButton:
            try:
                child = self.childAt(event.pos())
                if not child or not hasattr(child, 'mousePressEvent'):
                    self.safe_close()
            except:
                self.safe_close()

if __name__ == '__main__':
    try:
        # Configuración segura
        os.environ['QT_QPA_PLATFORM'] = 'xcb'
        if 'DISPLAY' not in os.environ:
            os.environ['DISPLAY'] = ':0'
        
        app = QApplication(sys.argv)
        
        # Tema de iconos seguro
        try:
            if not QIcon.themeName():
                QIcon.setThemeName('Adwaita')
        except:
            pass
        
        # Crear y mostrar launcher
        launcher = StableLauncher()
        launcher.showFullScreen()
        
        # Conexión segura para cierre
        app.aboutToQuit.connect(launcher.cleanup_and_close)
        
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Initialization error: {e}")
        sys.exit(1)

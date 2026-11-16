import sys
import fitz  # PyMuPDF
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, 
                             QSplitter, QTextEdit, QTabWidget, QLineEdit, 
                             QFormLayout, QHeaderView, QFileDialog,
                             QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
                             QDialog, QTableWidgetItem, QMessageBox,
                             QDateEdit, QRadioButton, QButtonGroup, QPlainTextEdit,
                             QFrame, QStackedWidget, QComboBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QTimer, QDate, QMarginsF, QSize
from PyQt6.QtGui import QPdfWriter, QTextDocument, QPageSize, QPageLayout, QPixmap, QImage, QColor, QBrush
from PyQt6.QtSvgWidgets import QSvgWidget

import database as db
import validador_citacoes
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

from ui_theme import (
    DARK_GLASS_QSS,
    LIGHT_PAPER_QSS,
    THEME_TOKENS,
    load_svg_icon,
    load_svg_pixmap,
    resource_path,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for _env_dir in (db.get_data_dir(), BASE_DIR):
    _env_file = os.path.join(_env_dir, ".env")
    if os.path.exists(_env_file):
        load_dotenv(_env_file)


class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Projeto de Revisão")
        self.setMinimumWidth(480)
        
        self.student_name = ""
        self.thesis_title = ""
        self.advisor_name = ""
        self.advisor_email = ""
        self.pdf_path = ""
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header_row = QHBoxLayout()
        header_icon = QSvgWidget(resource_path("assets/logo.svg"))
        header_icon.setFixedSize(36, 36)
        header_title = QLabel("<b>Cadastrar Novo Trabalho de Conclusão</b>")
        header_row.addWidget(header_icon)
        header_row.addWidget(header_title)
        header_row.addStretch()
        layout.addLayout(header_row)

        form = QFormLayout()
        form.setSpacing(8)
        
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Nome completo do aluno")
        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText("Título completo do TCC")
        self.input_advisor_name = QLineEdit()
        self.input_advisor_name.setPlaceholderText("Opcional")
        self.input_advisor_email = QLineEdit()
        self.input_advisor_email.setPlaceholderText("Opcional (para envio do relatório)")
        
        form.addRow("Nome do Aluno:", self.input_name)
        form.addRow("Título do TCC:", self.input_title)
        form.addRow("Nome do Orientador:", self.input_advisor_name)
        form.addRow("E-mail do Orientador:", self.input_advisor_email)
        layout.addLayout(form)

        # Visual PDF Upload Card
        upload_card = QFrame()
        upload_card.setObjectName("upload_card")
        upload_layout = QHBoxLayout(upload_card)
        upload_layout.setContentsMargins(12, 10, 12, 10)
        upload_layout.setSpacing(12)

        upload_img = QLabel()
        upload_img.setPixmap(load_svg_pixmap("assets/illustrations/pdf_upload.svg", 52, 52))
        upload_img.setFixedSize(52, 52)
        upload_layout.addWidget(upload_img)

        upload_text_col = QVBoxLayout()
        upload_text_col.setSpacing(4)
        self.lbl_pdf_path = QLabel("Nenhum arquivo PDF selecionado")
        self.lbl_pdf_path.setObjectName("lbl_subtitle")
        self.lbl_pdf_path.setWordWrap(True)

        self.btn_select_pdf = QPushButton("Selecionar Arquivo PDF")
        self.btn_select_pdf.setObjectName("btn_blue")
        self.btn_select_pdf.setIcon(load_svg_icon("assets/icons/folder-open.svg", "#ffffff", 16))
        self.btn_select_pdf.clicked.connect(self.select_pdf)

        upload_text_col.addWidget(self.btn_select_pdf)
        upload_text_col.addWidget(self.lbl_pdf_path)
        upload_layout.addLayout(upload_text_col)
        layout.addWidget(upload_card)
        
        btn_layout = QHBoxLayout()
        btn_create = QPushButton("Criar Projeto")
        btn_create.setObjectName("btn_green")
        btn_create.setIcon(load_svg_icon("assets/icons/plus.svg", "#ffffff", 16))
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_red")
        
        btn_create.clicked.connect(self.accept_creation)
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_create)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def select_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir PDF do TCC", "", "Arquivos PDF (*.pdf)")
        if path:
            self.pdf_path = path
            self.lbl_pdf_path.setText(os.path.basename(path) + f"\n{path}")

    def accept_creation(self):
        self.student_name = self.input_name.text().strip()
        self.thesis_title = self.input_title.text().strip()
        self.advisor_name = self.input_advisor_name.text().strip()
        self.advisor_email = self.input_advisor_email.text().strip()
        
        if not self.student_name or not self.thesis_title or not self.pdf_path:
            QMessageBox.warning(self, "Aviso", "Por favor, preencha todos os campos obrigatórios (Aluno, TCC) e selecione um PDF.")
            return
            
        self.accept()


class EditProjectDialog(QDialog):
    def __init__(self, project_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Projeto de Revisão")
        self.setMinimumWidth(430)
        
        self.project_id = project_data['id']
        self.student_name = project_data['student_name']
        self.thesis_title = project_data['thesis_title']
        self.advisor_name = project_data.get('advisor_name', '')
        self.advisor_email = project_data.get('advisor_email', '')
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.input_name = QLineEdit(self.student_name)
        self.input_title = QLineEdit(self.thesis_title)
        self.input_advisor_name = QLineEdit(self.advisor_name)
        self.input_advisor_email = QLineEdit(self.advisor_email)
        
        form.addRow("Nome do Aluno:", self.input_name)
        form.addRow("Título do TCC:", self.input_title)
        form.addRow("Nome do Orientador:", self.input_advisor_name)
        form.addRow("E-mail do Orientador:", self.input_advisor_email)
        
        layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Salvar Alterações")
        btn_save.setObjectName("btn_green")
        btn_save.setIcon(load_svg_icon("assets/icons/save.svg", "#ffffff", 16))
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_red")
        
        btn_save.clicked.connect(self.accept_edit)
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def accept_edit(self):
        self.student_name = self.input_name.text().strip()
        self.thesis_title = self.input_title.text().strip()
        self.advisor_name = self.input_advisor_name.text().strip()
        self.advisor_email = self.input_advisor_email.text().strip()
        
        if not self.student_name or not self.thesis_title:
            QMessageBox.warning(self, "Aviso", "Por favor, preencha nome do aluno e título do TCC.")
            return
            
        self.accept()


class ExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Opções de Exportação")
        self.setMinimumWidth(420)
        
        self.evaluator_name = ""
        self.date_str = ""
        self.export_format = "pdf"
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.input_evaluator = QLineEdit()
        self.input_evaluator.setPlaceholderText("Ex: Prof. Dr. João Silva")
        
        self.input_date = QDateEdit()
        self.input_date.setCalendarPopup(True)
        self.input_date.setDate(QDate.currentDate())
        
        form.addRow("Avaliador(a):", self.input_evaluator)
        form.addRow("Data:", self.input_date)
        
        layout.addLayout(form)
        
        format_layout = QHBoxLayout()
        self.radio_pdf = QRadioButton("PDF (.pdf)")
        self.radio_pdf.setChecked(True)
        self.radio_pdf.setIcon(load_svg_icon("assets/icons/file-text.svg", "#ef4444", 16))
        self.radio_docx = QRadioButton("Word (.docx)")
        self.radio_docx.setIcon(load_svg_icon("assets/icons/file-text.svg", "#3b82f6", 16))
        
        self.format_group = QButtonGroup()
        self.format_group.addButton(self.radio_pdf)
        self.format_group.addButton(self.radio_docx)
        
        format_layout.addWidget(self.radio_pdf)
        format_layout.addWidget(self.radio_docx)
        
        form.addRow("Formato:", format_layout)
        
        btn_layout = QHBoxLayout()
        btn_export = QPushButton("Exportar")
        btn_export.setObjectName("btn_green")
        btn_export.setIcon(load_svg_icon("assets/icons/file-text.svg", "#ffffff", 16))
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_red")
        
        btn_export.clicked.connect(self.accept_export)
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_export)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def accept_export(self):
        self.evaluator_name = self.input_evaluator.text().strip()
        self.date_str = self.input_date.date().toString("dd/MM/yyyy")
        self.export_format = "pdf" if self.radio_pdf.isChecked() else "docx"
        self.accept()


class EmailSettingsDialog(QDialog):
    """Dialog to configure and test SMTP credentials (Gmail, Outlook or custom)."""

    PRESETS = {
        "Gmail (Google)": ("smtp.gmail.com", "587"),
        "Outlook / Microsoft 365": ("smtp.office365.com", "587"),
        "Outro (Personalizado)": ("", "587"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar E-mail (SMTP)")
        self.setMinimumWidth(520)

        current = db.get_smtp_settings()

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        self.combo_provider = QComboBox()
        self.combo_provider.addItems(list(self.PRESETS.keys()))
        if current["server"] == "smtp.office365.com":
            self.combo_provider.setCurrentText("Outlook / Microsoft 365")
        elif current["server"] and current["server"] != "smtp.gmail.com":
            self.combo_provider.setCurrentText("Outro (Personalizado)")
        else:
            self.combo_provider.setCurrentText("Gmail (Google)")
        self.combo_provider.currentTextChanged.connect(self._apply_preset)
        form.addRow("Provedor:", self.combo_provider)

        self.input_server = QLineEdit(current["server"] or "smtp.gmail.com")
        self.input_server.setPlaceholderText("ex: smtp.gmail.com")
        form.addRow("Servidor SMTP:", self.input_server)

        self.input_port = QLineEdit(current["port"] or "587")
        self.input_port.setPlaceholderText("587")
        form.addRow("Porta (TLS):", self.input_port)

        self.input_user = QLineEdit(current["user"])
        self.input_user.setPlaceholderText("seu-email@gmail.com")
        form.addRow("Seu E-mail:", self.input_user)

        self.input_password = QLineEdit(current["password"])
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setPlaceholderText("Senha de App de 16 letras (Google)")
        form.addRow("Senha / Senha de App:", self.input_password)

        self.chk_show_pwd = QCheckBox("Mostrar senha")
        self.chk_show_pwd.toggled.connect(
            lambda checked: self.input_password.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        form.addRow("", self.chk_show_pwd)

        layout.addLayout(form)

        help_box = QFrame()
        help_box.setObjectName("header_card")
        help_layout = QVBoxLayout(help_box)
        help_layout.setContentsMargins(12, 10, 12, 10)
        lbl_help = QLabel(
            "<b>Como usar com Gmail (Google):</b><br>"
            "1. Ative a <b>Verificação em duas etapas</b> na sua Conta Google.<br>"
            "2. Acesse <a href='https://myaccount.google.com/apppasswords'>myaccount.google.com/apppasswords</a> "
            "e crie uma <b>Senha de App</b> (ex.: Docentia).<br>"
            "3. Cole o código de <b>16 letras</b> acima (a senha comum do Gmail não funciona)."
        )
        lbl_help.setWordWrap(True)
        lbl_help.setOpenExternalLinks(True)
        lbl_help.setObjectName("lbl_subtitle")
        help_layout.addWidget(lbl_help)
        layout.addWidget(help_box)

        btn_layout = QHBoxLayout()
        btn_test = QPushButton(" Testar Conexão")
        btn_test.setObjectName("btn_blue")
        btn_test.setIcon(load_svg_icon("assets/icons/refresh.svg", "#ffffff", 15))
        btn_test.clicked.connect(self._test_connection)

        btn_save = QPushButton(" Salvar")
        btn_save.setObjectName("btn_green")
        btn_save.setIcon(load_svg_icon("assets/icons/save.svg", "#ffffff", 15))
        btn_save.clicked.connect(self._save_settings)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_red")
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_test)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _apply_preset(self, name: str):
        server, port = self.PRESETS.get(name, ("", "587"))
        if server:
            self.input_server.setText(server)
            self.input_port.setText(port)

    def _validated_values(self):
        server = self.input_server.text().strip()
        port_raw = self.input_port.text().strip()
        user = self.input_user.text().strip()
        password = self.input_password.text().strip()
        if not server or not port_raw or not user or not password:
            QMessageBox.warning(self, "Aviso", "Preencha servidor, porta, e-mail e senha.")
            return None
        try:
            port = int(port_raw)
        except ValueError:
            QMessageBox.warning(self, "Aviso", "A porta SMTP deve ser um número (ex.: 587).")
            return None
        return server, port, user, password

    def _test_connection(self):
        vals = self._validated_values()
        if not vals:
            return
        server, port, user, password = vals
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            with smtplib.SMTP(server, port, timeout=15) as smtp:
                smtp.starttls()
                smtp.login(user, password)
            QApplication.restoreOverrideCursor()
            QMessageBox.information(self, "Conexão OK", "Autenticação SMTP realizada com sucesso!")
        except smtplib.SMTPAuthenticationError as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(
                self,
                "Falha de Autenticação",
                "Não foi possível autenticar no servidor SMTP.\n\n"
                "Se estiver usando Gmail, lembre-se de utilizar uma Senha de App de 16 letras "
                "(a senha normal da conta Google é bloqueada).\n\n"
                f"Detalhe: {e}",
            )
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Erro de Conexão", f"Falha ao conectar no servidor SMTP:\n{e}")

    def _save_settings(self):
        vals = self._validated_values()
        if not vals:
            return
        server, port, user, password = vals
        db.set_smtp_settings(server, port, user, password)
        QMessageBox.information(self, "Sucesso", "Configurações de e-mail salvas localmente.")
        self.accept()


class PDFViewer(QGraphicsView):
    textSelected = pyqtSignal(str, int)  # Emits captured text and page number

    def __init__(self, theme="dark"):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        # Enable Rubber Band dragging for selecting area
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        
        self.pdf_document = None
        self.current_page_idx = 0
        self.pixmap_item = None
        self.zoom_factor = 1.25
        self.current_scale = 1.0
        self.set_theme(theme)

    def set_theme(self, theme: str):
        bg_hex = THEME_TOKENS.get(theme, THEME_TOKENS["dark"])["scene_bg"]
        self.scene.setBackgroundBrush(QBrush(QColor(bg_hex)))

    def load_pdf(self, file_path):
        try:
            self.pdf_document = fitz.open(file_path)
            self.current_page_idx = 0
            self.current_scale = 1.0
            self.render_page()
            return True
        except Exception as e:
            print(f"Erro ao carregar o PDF: {e}")
            return False

    def render_page(self):
        if not self.pdf_document:
            return
        
        page = self.pdf_document[self.current_page_idx]
        
        # Create a transform matrix to scale the rendering resolution
        mat = fitz.Matrix(self.current_scale, self.current_scale)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert PyMuPDF Pixmap to PyQt6 QImage then QPixmap
        fmt = QImage.Format.Format_RGB888 if pix.alpha == 0 else QImage.Format.Format_RGBA8888
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
        qpixmap = QPixmap.fromImage(img)
        
        self.scene.clear()
        self.pixmap_item = QGraphicsPixmapItem(qpixmap)
        self.scene.addItem(self.pixmap_item)
        self.setSceneRect(QRectF(self.pixmap_item.pixmap().rect()))
        
    def next_page(self):
        if self.pdf_document and self.current_page_idx < len(self.pdf_document) - 1:
            self.current_page_idx += 1
            self.render_page()

    def prev_page(self):
        if self.pdf_document and self.current_page_idx > 0:
            self.current_page_idx -= 1
            self.render_page()

    def zoom_in(self):
        self.current_scale *= self.zoom_factor
        self.render_page()

    def zoom_out(self):
        self.current_scale /= self.zoom_factor
        self.render_page()

    def mouseReleaseEvent(self, event):
        # Pegar o retângulo ANTES de chamar super() pois o evento pode limpar a seleção
        rubber_band_rect = self.rubberBandRect()
        
        super().mouseReleaseEvent(event)
        
        if not self.pdf_document:
            return
        
        if rubber_band_rect.isEmpty():
            return
            
        scene_rect = self.mapToScene(rubber_band_rect).boundingRect()
        
        pdf_rect = fitz.Rect(
            scene_rect.left() / self.current_scale,
            scene_rect.top() / self.current_scale,
            scene_rect.right() / self.current_scale,
            scene_rect.bottom() / self.current_scale
        )
        
        page = self.pdf_document[self.current_page_idx]
        
        text = page.get_textbox(pdf_rect).strip().replace('\n', ' ')
        
        if text:
            self.textSelected.emit(text, self.current_page_idx + 1)


class EditCitationDialog(QDialog):
    def __init__(self, row_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Verificação")
        self.setMinimumWidth(500)
        
        self.row_data = row_data
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.input_status = QLineEdit(str(row_data.get('Status', '')))
        self.input_citacao = QLineEdit(str(row_data.get('Citação Encontrada', '')))
        self.input_pagina = QLineEdit(str(row_data.get('Página', '')))
        
        self.input_contexto = QPlainTextEdit(str(row_data.get('Contexto', '')))
        self.input_contexto.setMaximumHeight(80)
        
        self.input_referencia = QPlainTextEdit(str(row_data.get('Referência Correspondente', '')))
        self.input_referencia.setMaximumHeight(80)
        
        form.addRow("Status:", self.input_status)
        form.addRow("Citação:", self.input_citacao)
        form.addRow("Página:", self.input_pagina)
        form.addRow("Contexto:", self.input_contexto)
        form.addRow("Referência:", self.input_referencia)
        
        layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Salvar")
        btn_save.setObjectName("btn_green")
        btn_save.setIcon(load_svg_icon("assets/icons/save.svg", "#ffffff", 16))
        btn_save.clicked.connect(self.accept)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_red")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
    def get_updated_data(self):
        return {
            'Status': self.input_status.text(),
            'Citação Encontrada': self.input_citacao.text(),
            'Página': self.input_pagina.text(),
            'Contexto': self.input_contexto.toPlainText(),
            'Referência Correspondente': self.input_referencia.toPlainText()
        }


class CitationReportDialog(QDialog):
    def __init__(self, results, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Relatório de Validação de Citações")
        self.setMinimumSize(940, 620)
        self.results = results
        
        layout = QVBoxLayout(self)
        
        summary_row = QHBoxLayout()
        total = len(results)
        ok_count = sum(1 for r in results if str(r.get('Status', '')).upper() == 'OK')
        warn_count = total - ok_count
        lbl_info = QLabel(
            f"<b>{total}</b> itens analisados  |  "
            f"<span style='color:#10b981;'><b>{ok_count}</b> OK</span>  |  "
            f"<span style='color:#f97316;'><b>{warn_count}</b> para revisar</span>"
        )
        summary_row.addWidget(lbl_info)
        summary_row.addStretch()
        layout.addLayout(summary_row)
        
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Status", "Citação Encontrada", "Página", "Contexto", "Referência Correspondente"])
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(34)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        layout.addWidget(self.table)
        
        self.populate_table()
        
        btn_layout = QHBoxLayout()
        
        btn_edit = QPushButton("Editar")
        btn_edit.setObjectName("btn_blue")
        btn_edit.setIcon(load_svg_icon("assets/icons/edit.svg", "#ffffff", 16))
        btn_edit.clicked.connect(self.edit_selected)
        
        btn_delete = QPushButton("Excluir")
        btn_delete.setObjectName("btn_red")
        btn_delete.setIcon(load_svg_icon("assets/icons/trash.svg", "#ffffff", 16))
        btn_delete.clicked.connect(self.delete_selected)
        
        btn_export = QPushButton("Exportar para Excel")
        btn_export.setObjectName("btn_green")
        btn_export.setIcon(load_svg_icon("assets/icons/table.svg", "#ffffff", 16))
        btn_export.clicked.connect(self.export_excel)
        
        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.accept)
        
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_export)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        
    def populate_table(self):
        self.table.setRowCount(0)
        for i, res in enumerate(self.results):
            self.table.insertRow(i)
            status_val = str(res.get('Status', ''))
            status_item = QTableWidgetItem(status_val)
            if status_val.upper() == 'OK':
                status_item.setIcon(load_svg_icon("assets/icons/check-circle.svg", "#10b981", 15))
            else:
                status_item.setIcon(load_svg_icon("assets/icons/alert-circle.svg", "#f97316", 15))
            self.table.setItem(i, 0, status_item)
            self.table.setItem(i, 1, QTableWidgetItem(str(res.get('Citação Encontrada', ''))))
            self.table.setItem(i, 2, QTableWidgetItem(str(res.get('Página', ''))))
            
            context = str(res.get('Contexto', ''))
            if len(context) > 60:
                context = context[:57] + "..."
            self.table.setItem(i, 3, QTableWidgetItem(context))
            
            ref = str(res.get('Referência Correspondente', ''))
            if len(ref) > 60:
                ref = ref[:57] + "..."
            self.table.setItem(i, 4, QTableWidgetItem(ref))

    def edit_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Aviso", "Selecione uma linha para editar.")
            return
            
        row = selected[0].row()
        row_data = self.results[row]
        
        dialog = EditCitationDialog(row_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_updated_data()
            self.results[row] = updated_data
            self.populate_table()

    def delete_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Aviso", "Selecione uma linha para excluir.")
            return
            
        row = selected[0].row()
        reply = QMessageBox.question(self, "Confirmar", "Tem certeza que deseja excluir esta verificação?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.results.pop(row)
            self.table.removeRow(row)

    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Relatório", "relatorio_citacoes.xlsx", "Excel Files (*.xlsx);;CSV Files (*.csv)")
        if path:
            try:
                import pandas as pd
                df = pd.DataFrame(self.results)
                if path.endswith('.csv'):
                    df.to_csv(path, index=False, sep=';', encoding='utf-8-sig')
                else:
                    df.to_excel(path, index=False)
                QMessageBox.information(self, "Sucesso", "Relatório exportado com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao exportar: {e}")


class TCCAssistantApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Docentia — Revisão Acadêmica de TCC v1.0")
        self.setGeometry(100, 100, 1260, 820)
        self.setWindowIcon(load_svg_icon("assets/logo.svg", color=None, size=64))
        
        db.init_db()
        self.current_theme = db.get_setting("theme", "dark")
        if self.current_theme not in ("dark", "light"):
            self.current_theme = "dark"
        
        self.current_project_id = None
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(14, 14, 14, 14)
        
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setInterval(2000)
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.timeout.connect(self.save_general_opinion)
        
        self.apply_theme(self.current_theme, persist=False)
        self.init_dashboard()

    def apply_theme(self, theme: str, persist: bool = True):
        self.current_theme = theme if theme in ("dark", "light") else "dark"
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(LIGHT_PAPER_QSS if self.current_theme == "light" else DARK_GLASS_QSS)
        if persist:
            db.set_setting("theme", self.current_theme)

        self._refresh_theme_controls()

    def toggle_theme(self):
        next_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(next_theme, persist=True)

    def _refresh_theme_controls(self):
        tokens = THEME_TOKENS[self.current_theme]
        neutral_color = tokens["neutral_icon"]

        if hasattr(self, "btn_theme_toggle") and self.btn_theme_toggle is not None:
            try:
                if self.current_theme == "dark":
                    self.btn_theme_toggle.setText(" Modo Claro")
                    self.btn_theme_toggle.setIcon(load_svg_icon("assets/icons/sun.svg", "#f59e0b", 16))
                    self.btn_theme_toggle.setToolTip("Alternar para o modo claro")
                else:
                    self.btn_theme_toggle.setText(" Modo Escuro")
                    self.btn_theme_toggle.setIcon(load_svg_icon("assets/icons/moon.svg", "#3b82f6", 16))
                    self.btn_theme_toggle.setToolTip("Alternar para o modo escuro")
            except RuntimeError:
                pass

        if hasattr(self, "btn_back_dashboard") and self.btn_back_dashboard is not None:
            try:
                self.btn_back_dashboard.setIcon(load_svg_icon("assets/icons/arrow-left.svg", neutral_color, 16))
            except RuntimeError:
                pass

        if hasattr(self, "btn_email_settings") and self.btn_email_settings is not None:
            try:
                self.btn_email_settings.setIcon(load_svg_icon("assets/icons/mail.svg", neutral_color, 16))
            except RuntimeError:
                pass

        if hasattr(self, "pdf_viewer") and self.pdf_viewer is not None:
            try:
                self.pdf_viewer.set_theme(self.current_theme)
            except RuntimeError:
                pass

        if hasattr(self, "category_tabs") and self.category_tabs is not None:
            try:
                self.update_tab_color(self.category_tabs.currentIndex())
            except RuntimeError:
                pass

        if hasattr(self, "search_icon_label") and self.search_icon_label is not None:
            try:
                self.search_icon_label.setPixmap(
                    load_svg_icon("assets/icons/search.svg", tokens["muted_icon"], 16).pixmap(16, 16)
                )
            except RuntimeError:
                pass

    def _create_theme_toggle_button(self) -> QPushButton:
        btn = QPushButton()
        btn.setObjectName("btn_theme_toggle")
        btn.setIconSize(QSize(16, 16))
        btn.clicked.connect(self.toggle_theme)
        self.btn_theme_toggle = btn
        self._refresh_theme_controls()
        return btn

    def _create_metric_card(self, title: str, icon_path: str, icon_color: str):
        card = QFrame()
        card.setObjectName("metric_card")
        row = QHBoxLayout(card)
        row.setContentsMargins(14, 10, 14, 10)
        row.setSpacing(12)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(load_svg_icon(icon_path, icon_color, 24).pixmap(24, 24))
        icon_lbl.setFixedSize(36, 36)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(icon_lbl)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        val_lbl = QLabel("0")
        val_lbl.setObjectName("lbl_metric_value")
        title_lbl = QLabel(title)
        title_lbl.setObjectName("lbl_metric_title")
        text_col.addWidget(val_lbl)
        text_col.addWidget(title_lbl)
        row.addLayout(text_col)
        row.addStretch()

        return card, val_lbl
        
    def init_dashboard(self):
        self.current_project_id = None
        self.pdf_viewer = None
        self.category_tabs = None
        self.btn_back_dashboard = None
        self.clear_layout(self.main_layout)
        
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header Card with Logo, Title & Theme Toggle
        header_card = QFrame()
        header_card.setObjectName("header_card")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(16, 12, 16, 12)
        header_layout.setSpacing(14)

        logo_widget = QSvgWidget(resource_path("assets/logo.svg"))
        logo_widget.setFixedSize(44, 44)
        header_layout.addWidget(logo_widget)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title = QLabel("<h2 style='margin:0;'>Docentia</h2>")
        subtitle = QLabel("Revisão acadêmica de TCC • Leitura interativa de PDFs, anotações e validação ABNT")
        subtitle.setObjectName("lbl_subtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header_layout.addLayout(title_col)
        header_layout.addStretch()

        self.btn_email_settings = QPushButton(" Configurar E-mail")
        self.btn_email_settings.setObjectName("btn_ghost")
        self.btn_email_settings.setIconSize(QSize(16, 16))
        self.btn_email_settings.setToolTip("Configurar conta Gmail / SMTP para envio de relatórios")
        self.btn_email_settings.clicked.connect(self.open_email_settings)
        header_layout.addWidget(self.btn_email_settings)

        header_layout.addWidget(self._create_theme_toggle_button())
        layout.addWidget(header_card)

        # Compact Summary Metric Cards
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(12)
        card_total, self.lbl_metric_total = self._create_metric_card(
            "Total de Revisões", "assets/icons/book-open.svg", "#3b82f6"
        )
        card_progress, self.lbl_metric_progress = self._create_metric_card(
            "Em Andamento", "assets/icons/clock.svg", "#f97316"
        )
        card_done, self.lbl_metric_done = self._create_metric_card(
            "Concluídas", "assets/icons/check-circle.svg", "#10b981"
        )
        metrics_row.addWidget(card_total)
        metrics_row.addWidget(card_progress)
        metrics_row.addWidget(card_done)
        layout.addLayout(metrics_row)
        
        # Action Bar + Search
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        btn_new = QPushButton(" Nova Revisão")
        btn_new.setObjectName("btn_green")
        btn_new.setIcon(load_svg_icon("assets/icons/plus.svg", "#ffffff", 16))
        btn_open = QPushButton(" Abrir Revisão")
        btn_open.setObjectName("btn_blue")
        btn_open.setIcon(load_svg_icon("assets/icons/folder-open.svg", "#ffffff", 16))
        btn_edit = QPushButton(" Editar")
        btn_edit.setObjectName("btn_blue")
        btn_edit.setIcon(load_svg_icon("assets/icons/edit.svg", "#ffffff", 16))
        btn_status = QPushButton(" Alterar Status")
        btn_status.setObjectName("btn_orange")
        btn_status.setIcon(load_svg_icon("assets/icons/refresh.svg", "#ffffff", 16))
        btn_delete = QPushButton(" Excluir")
        btn_delete.setObjectName("btn_red")
        btn_delete.setIcon(load_svg_icon("assets/icons/trash.svg", "#ffffff", 16))
        
        btn_new.clicked.connect(self.create_new_project)
        btn_open.clicked.connect(self.open_selected_project)
        btn_edit.clicked.connect(self.edit_selected_project)
        btn_status.clicked.connect(self.toggle_selected_project_status)
        btn_delete.clicked.connect(self.delete_selected_project)
        
        btn_layout.addWidget(btn_new)
        btn_layout.addWidget(btn_open)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_status)
        btn_layout.addWidget(btn_delete)
        btn_layout.addStretch()

        self.search_icon_label = QLabel()
        self.search_icon_label.setFixedSize(18, 18)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filtrar por aluno ou título...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.populate_dashboard)
        btn_layout.addWidget(self.search_icon_label)
        btn_layout.addWidget(self.search_input)
        layout.addLayout(btn_layout)

        # Stacked View: Table or Empty State Illustration
        self.dashboard_stack = QStackedWidget()

        self.project_list = QTableWidget(0, 5)
        self.project_list.setHorizontalHeaderLabels(["ID", "Nome do Aluno", "Título", "Status", "Última Atualização"])
        self.project_list.setAlternatingRowColors(True)
        self.project_list.verticalHeader().setDefaultSectionSize(36)
        self.project_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.project_list.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.project_list.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.project_list.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.project_list.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.project_list.hideColumn(0)
        self.project_list.itemDoubleClicked.connect(lambda _: self.open_selected_project())

        empty_card = QFrame()
        empty_card.setObjectName("empty_state_card")
        empty_layout = QVBoxLayout(empty_card)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.setSpacing(12)

        empty_img = QLabel()
        empty_img.setPixmap(load_svg_pixmap("assets/illustrations/empty_dashboard.svg", 240, 155))
        empty_img.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_empty_title = QLabel("<h3>Nenhuma revisão cadastrada ainda</h3>")
        self.lbl_empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty_desc = QLabel("Importe o PDF de um TCC para começar a registrar apontamentos e validar citações ABNT.")
        self.lbl_empty_desc.setObjectName("lbl_subtitle")
        self.lbl_empty_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_empty_new = QPushButton(" Criar Primeira Revisão")
        btn_empty_new.setObjectName("btn_green")
        btn_empty_new.setIcon(load_svg_icon("assets/icons/plus.svg", "#ffffff", 16))
        btn_empty_new.clicked.connect(self.create_new_project)

        empty_layout.addWidget(empty_img)
        empty_layout.addWidget(self.lbl_empty_title)
        empty_layout.addWidget(self.lbl_empty_desc)
        empty_layout.addWidget(btn_empty_new, alignment=Qt.AlignmentFlag.AlignCenter)

        self.dashboard_stack.addWidget(self.project_list)
        self.dashboard_stack.addWidget(empty_card)
        layout.addWidget(self.dashboard_stack)
        
        self.main_layout.addWidget(dashboard_widget)
        self._refresh_theme_controls()
        self.populate_dashboard()

    def populate_dashboard(self):
        self.project_list.setRowCount(0)
        all_projects = db.get_projects()

        total_count = len(all_projects)
        done_count = sum(1 for p in all_projects if p['status'] == "Concluído")
        progress_count = total_count - done_count

        if hasattr(self, "lbl_metric_total"):
            self.lbl_metric_total.setText(str(total_count))
            self.lbl_metric_progress.setText(str(progress_count))
            self.lbl_metric_done.setText(str(done_count))

        query = self.search_input.text().strip().lower() if hasattr(self, "search_input") else ""
        if query:
            projects = [
                p for p in all_projects
                if query in p['student_name'].lower() or query in p['thesis_title'].lower()
            ]
        else:
            projects = all_projects

        if total_count == 0:
            self.lbl_empty_title.setText("<h3>Nenhuma revisão cadastrada ainda</h3>")
            self.lbl_empty_desc.setText("Importe o PDF de um TCC para começar a registrar apontamentos e validar citações ABNT.")
            self.dashboard_stack.setCurrentIndex(1)
            return
        elif len(projects) == 0:
            self.lbl_empty_title.setText("<h3>Nenhum resultado encontrado</h3>")
            self.lbl_empty_desc.setText("Tente ajustar o termo de busca no filtro acima.")
            self.dashboard_stack.setCurrentIndex(1)
            return

        self.dashboard_stack.setCurrentIndex(0)

        for row_idx, p in enumerate(projects):
            self.project_list.insertRow(row_idx)
            self.project_list.setItem(row_idx, 0, QTableWidgetItem(str(p['id'])))
            self.project_list.setItem(row_idx, 1, QTableWidgetItem(p['student_name']))
            self.project_list.setItem(row_idx, 2, QTableWidgetItem(p['thesis_title']))
            
            # Translating default DB English status if present
            status = "Em Andamento" if p['status'] == "In Progress" else p['status']
            status_item = QTableWidgetItem(status)
            if status == "Concluído":
                status_item.setIcon(load_svg_icon("assets/icons/check-circle.svg", "#10b981", 15))
            else:
                status_item.setIcon(load_svg_icon("assets/icons/clock.svg", "#f97316", 15))
            self.project_list.setItem(row_idx, 3, status_item)
            
            updated_str = str(p['updated_at'])
            try:
                from datetime import datetime
                dt = datetime.strptime(updated_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
                updated_str = dt.strftime('%d/%m/%Y %H:%M:%S')
            except Exception:
                pass
            self.project_list.setItem(row_idx, 4, QTableWidgetItem(updated_str))

    def create_new_project(self):
        dialog = NewProjectDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            project_id = db.create_project(dialog.student_name, dialog.thesis_title, dialog.advisor_name, dialog.advisor_email, dialog.pdf_path)
            self.init_workspace(project_id)

    def edit_selected_project(self):
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione um projeto para editar.")
            return
        
        row = selected_items[0].row()
        project_id = int(self.project_list.item(row, 0).text())
        project_data = db.get_project(project_id)
        
        dialog = EditProjectDialog(project_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            db.update_project_details(project_id, dialog.student_name, dialog.thesis_title, dialog.advisor_name, dialog.advisor_email)
            self.populate_dashboard()

    def open_selected_project(self):
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione um projeto para abrir.")
            return
        
        row = selected_items[0].row()
        project_id = int(self.project_list.item(row, 0).text())
        self.init_workspace(project_id)

    def delete_selected_project(self):
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione um projeto para excluir.")
            return
            
        row = selected_items[0].row()
        project_id = int(self.project_list.item(row, 0).text())
        
        reply = QMessageBox.question(self, "Excluir Projeto", 
                                     "Tem certeza de que deseja excluir este projeto e todas as suas anotações?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db.delete_project(project_id)
            self.populate_dashboard()

    def toggle_selected_project_status(self):
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione um projeto para alterar o status.")
            return
            
        row = selected_items[0].row()
        project_id = int(self.project_list.item(row, 0).text())
        current_status = self.project_list.item(row, 3).text()
        
        new_status = "Concluído" if current_status == "Em Andamento" else "In Progress"
        
        db.update_project_status(project_id, new_status)
        self.populate_dashboard()

    def save_draft_and_exit(self):
        if self.current_project_id:
            self.save_general_opinion()
            db.touch_project(self.current_project_id)
        self.init_dashboard()

    def init_workspace(self, project_id):
        self.current_project_id = project_id
        self.editing_annotation_id = None
        self.search_icon_label = None
        project_data = db.get_project(project_id)
        
        if not project_data:
            QMessageBox.critical(self, "Erro", "Projeto não encontrado no banco de dados.")
            self.init_dashboard()
            return

        self.clear_layout(self.main_layout)
        
        workspace_widget = QWidget()
        layout = QVBoxLayout(workspace_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # Workspace Compact Header Bar
        top_card = QFrame()
        top_card.setObjectName("header_card")
        top_bar = QHBoxLayout(top_card)
        top_bar.setContentsMargins(12, 8, 12, 8)
        top_bar.setSpacing(10)

        self.btn_back_dashboard = QPushButton(" Painel")
        self.btn_back_dashboard.setObjectName("btn_ghost")
        self.btn_back_dashboard.clicked.connect(self.save_draft_and_exit)
        top_bar.addWidget(self.btn_back_dashboard)

        advisor_text = f"  |  <b>Orientador:</b> {project_data['advisor_name']}" if project_data.get('advisor_name') else ""
        info_label = QLabel(
            f"<b>Aluno:</b> {project_data['student_name']}  |  "
            f"<b>Título:</b> {project_data['thesis_title']}{advisor_text}"
        )
        info_label.setWordWrap(True)
        top_bar.addWidget(info_label, stretch=1)

        top_bar.addWidget(self._create_theme_toggle_button())
        layout.addWidget(top_card)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # ==========================================
        # LEFT COLUMN: PDF Viewer 
        # ==========================================
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 4, 0)
        
        pdf_toolbar = QHBoxLayout()
        btn_zoom_in = QPushButton()
        btn_zoom_in.setObjectName("btn_icon_blue")
        btn_zoom_in.setIcon(load_svg_icon("assets/icons/zoom-in.svg", "#ffffff", 18))
        btn_zoom_in.setToolTip("Ampliar")
        
        btn_zoom_out = QPushButton()
        btn_zoom_out.setObjectName("btn_icon_blue")
        btn_zoom_out.setIcon(load_svg_icon("assets/icons/zoom-out.svg", "#ffffff", 18))
        btn_zoom_out.setToolTip("Reduzir")
        
        btn_prev = QPushButton()
        btn_prev.setObjectName("btn_icon_orange")
        btn_prev.setIcon(load_svg_icon("assets/icons/chevron-left.svg", "#ffffff", 18))
        btn_prev.setToolTip("Página Anterior")
        
        btn_next = QPushButton()
        btn_next.setObjectName("btn_icon_orange")
        btn_next.setIcon(load_svg_icon("assets/icons/chevron-right.svg", "#ffffff", 18))
        btn_next.setToolTip("Próxima Página")
        
        self.page_nav_input = QLineEdit()
        self.page_nav_input.setFixedWidth(54)
        self.page_nav_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_total_pages = QLabel(" / X")
        
        btn_go_page = QPushButton()
        btn_go_page.setObjectName("btn_icon_blue")
        btn_go_page.setIcon(load_svg_icon("assets/icons/arrow-right.svg", "#ffffff", 16))
        btn_go_page.setToolTip("Ir para página")
        
        pdf_toolbar.addWidget(btn_zoom_in)
        pdf_toolbar.addWidget(btn_zoom_out)
        pdf_toolbar.addWidget(btn_prev)
        pdf_toolbar.addWidget(btn_next)
        pdf_toolbar.addWidget(QLabel("Página: "))
        pdf_toolbar.addWidget(self.page_nav_input)
        pdf_toolbar.addWidget(self.lbl_total_pages)
        pdf_toolbar.addWidget(btn_go_page)
        pdf_toolbar.addStretch()

        hint_lbl = QLabel("Arraste no PDF para capturar trecho")
        hint_lbl.setObjectName("lbl_subtitle")
        pdf_toolbar.addWidget(hint_lbl)
        
        left_layout.addLayout(pdf_toolbar)
        
        self.pdf_stack = QStackedWidget()
        self.pdf_viewer = PDFViewer(theme=self.current_theme)
        self.pdf_viewer.textSelected.connect(self.handle_text_captured)

        pdf_empty_card = QFrame()
        pdf_empty_card.setObjectName("empty_state_card")
        pdf_empty_layout = QVBoxLayout(pdf_empty_card)
        pdf_empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pdf_empty_layout.setSpacing(10)

        pdf_img = QLabel()
        pdf_img.setPixmap(load_svg_pixmap("assets/illustrations/pdf_placeholder.svg", 190, 140))
        pdf_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_pdf_placeholder = QLabel("Não foi possível carregar o arquivo PDF.")
        self.lbl_pdf_placeholder.setObjectName("lbl_subtitle")
        self.lbl_pdf_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_pdf_placeholder.setWordWrap(True)

        pdf_empty_layout.addWidget(pdf_img)
        pdf_empty_layout.addWidget(self.lbl_pdf_placeholder)

        self.pdf_stack.addWidget(self.pdf_viewer)
        self.pdf_stack.addWidget(pdf_empty_card)
        left_layout.addWidget(self.pdf_stack)
        
        btn_zoom_in.clicked.connect(self.pdf_viewer.zoom_in)
        btn_zoom_out.clicked.connect(self.pdf_viewer.zoom_out)
        btn_prev.clicked.connect(self.handle_prev_page)
        btn_next.clicked.connect(self.handle_next_page)
        self.page_nav_input.editingFinished.connect(self.go_to_page)
        btn_go_page.clicked.connect(self.go_to_page)
        
        # ==========================================
        # RIGHT COLUMN: Annotation Panel 
        # ==========================================
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(6, 0, 0, 0)
        
        form_layout = QFormLayout()
        
        self.category_tabs = QTabWidget()
        self.category_tabs.addTab(QWidget(), load_svg_icon("assets/icons/alert-circle.svg", "#ef4444", 15), "Apontamentos")
        self.category_tabs.addTab(QWidget(), load_svg_icon("assets/icons/help-circle.svg", "#eab308", 15), "Dúvida")
        self.category_tabs.addTab(QWidget(), load_svg_icon("assets/icons/lightbulb.svg", "#3b82f6", 15), "Sugestão")
        self.category_tabs.currentChanged.connect(self.update_tab_color)
        
        right_layout.addWidget(self.category_tabs)
        
        self.page_input = QLineEdit()
        self.page_input.setPlaceholderText("Preenchido automaticamente da seleção")
        form_layout.addRow("Página:", self.page_input)
        
        self.excerpt_input = QPlainTextEdit()
        self.excerpt_input.setPlaceholderText("Trecho de texto capturado automaticamente...")
        self.excerpt_input.setMaximumHeight(80)
        form_layout.addRow("Trecho:", self.excerpt_input)
        
        self.notes_input = QPlainTextEdit()
        self.notes_input.setPlaceholderText("Digite sua observação ou sugestão aqui...")
        self.notes_input.setMaximumHeight(100)
        form_layout.addRow("Observação:", self.notes_input)
        
        self.btn_save_ann = QPushButton(" Salvar Anotação")
        self.btn_save_ann.setObjectName("btn_orange")
        self.btn_save_ann.setIcon(load_svg_icon("assets/icons/save.svg", "#ffffff", 15))
        self.btn_save_ann.clicked.connect(self.save_annotation)
        
        self.btn_cancel_edit = QPushButton("Cancelar Edição")
        self.btn_cancel_edit.setObjectName("btn_red")
        self.btn_cancel_edit.clicked.connect(self.cancel_edit_annotation)
        self.btn_cancel_edit.setVisible(False)
        
        btn_ann_layout = QHBoxLayout()
        btn_ann_layout.addWidget(self.btn_save_ann)
        btn_ann_layout.addWidget(self.btn_cancel_edit)
        
        form_layout.addRow("", btn_ann_layout)
        
        right_layout.addLayout(form_layout)
        
        ann_label = QLabel("<b>Anotações Salvas para este Projeto</b>")
        right_layout.addWidget(ann_label)
        
        self.ann_list = QTableWidget(0, 4)
        self.ann_list.setHorizontalHeaderLabels(["ID", "Página", "Categoria", "Trecho"])
        self.ann_list.setAlternatingRowColors(True)
        self.ann_list.verticalHeader().setDefaultSectionSize(32)
        self.ann_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ann_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.ann_list.hideColumn(0)
        self.ann_list.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.ann_list.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        right_layout.addWidget(self.ann_list)
        
        ann_actions_layout = QHBoxLayout()
        btn_edit_ann = QPushButton(" Editar Selecionada")
        btn_edit_ann.setObjectName("btn_blue")
        btn_edit_ann.setIcon(load_svg_icon("assets/icons/edit.svg", "#ffffff", 15))
        btn_edit_ann.clicked.connect(self.load_annotation_for_editing)
        
        btn_delete_ann = QPushButton(" Excluir Selecionada")
        btn_delete_ann.setObjectName("btn_red")
        btn_delete_ann.setIcon(load_svg_icon("assets/icons/trash.svg", "#ffffff", 15))
        btn_delete_ann.clicked.connect(self.delete_selected_annotation)
        
        ann_actions_layout.addWidget(btn_edit_ann)
        ann_actions_layout.addWidget(btn_delete_ann)
        right_layout.addLayout(ann_actions_layout)
        
        lbl_general = QLabel("<b>Parecer Geral de Membro da Banca Avaliadora</b>")
        right_layout.addWidget(lbl_general)
        self.general_opinion = QPlainTextEdit()
        self.general_opinion.setMaximumHeight(100)
        self.general_opinion.setPlaceholderText("Escreva seu parecer geral sobre o TCC aqui...")
        
        if project_data['general_opinion']:
            self.general_opinion.setPlainText(project_data['general_opinion'])
        
        self.general_opinion.textChanged.connect(self.autosave_timer.start)
        right_layout.addWidget(self.general_opinion)
        
        footer_btn_layout = QHBoxLayout()
        btn_validate = QPushButton(" Validar Citações")
        btn_validate.setObjectName("btn_green")
        btn_validate.setIcon(load_svg_icon("assets/icons/check-circle.svg", "#ffffff", 15))
        btn_validate.clicked.connect(self.run_citation_validation)

        btn_export = QPushButton(" Exportar")
        btn_export.setObjectName("btn_blue")
        btn_export.setIcon(load_svg_icon("assets/icons/file-text.svg", "#ffffff", 15))
        btn_export.clicked.connect(self.open_export_dialog)
        
        btn_email = QPushButton(" E-mail")
        btn_email.setObjectName("btn_orange")
        btn_email.setIcon(load_svg_icon("assets/icons/mail.svg", "#ffffff", 15))
        btn_email.clicked.connect(self.send_reports_by_email)
        
        btn_save_exit = QPushButton(" Salvar e Sair")
        btn_save_exit.setObjectName("btn_orange")
        btn_save_exit.setIcon(load_svg_icon("assets/icons/save.svg", "#ffffff", 15))
        btn_save_exit.clicked.connect(self.save_draft_and_exit)
        
        footer_btn_layout.addWidget(btn_validate)
        footer_btn_layout.addWidget(btn_export)
        footer_btn_layout.addWidget(btn_email)
        footer_btn_layout.addWidget(btn_save_exit)
        right_layout.addLayout(footer_btn_layout)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # Define stretch factors and initial sizes to force 65% / 35% ratio
        splitter.setStretchFactor(0, 65)
        splitter.setStretchFactor(1, 35)
        splitter.setSizes([6500, 3500])
        
        layout.addWidget(splitter)
        self.main_layout.addWidget(workspace_widget)
        
        self._refresh_theme_controls()
        self.update_tab_color(0)
        
        if project_data['pdf_path']:
            success = self.pdf_viewer.load_pdf(project_data['pdf_path'])
            if success:
                self.pdf_stack.setCurrentIndex(0)
                self.update_page_label()
            else:
                self.lbl_pdf_placeholder.setText(f"Falha ao carregar PDF de:\n{project_data['pdf_path']}")
                self.pdf_stack.setCurrentIndex(1)
                QMessageBox.warning(self, "Erro", f"Falha ao carregar PDF de:\n{project_data['pdf_path']}")
        else:
            self.lbl_pdf_placeholder.setText("Nenhum arquivo PDF vinculado a este projeto.")
            self.pdf_stack.setCurrentIndex(1)
        
        self.populate_annotations()

    def handle_prev_page(self):
        self.pdf_viewer.prev_page()
        self.update_page_label()

    def handle_next_page(self):
        self.pdf_viewer.next_page()
        self.update_page_label()

    def update_page_label(self):
        if hasattr(self, 'pdf_viewer') and self.pdf_viewer and self.pdf_viewer.pdf_document:
            current = self.pdf_viewer.current_page_idx + 1
            total = len(self.pdf_viewer.pdf_document)
            if hasattr(self, 'page_nav_input'):
                self.page_nav_input.setText(str(current))
            if hasattr(self, 'lbl_total_pages'):
                self.lbl_total_pages.setText(f" / {total}")

    def go_to_page(self):
        if not hasattr(self, 'pdf_viewer') or not self.pdf_viewer or not self.pdf_viewer.pdf_document:
            return
        
        try:
            page_num = int(self.page_nav_input.text())
            total = len(self.pdf_viewer.pdf_document)
            if 1 <= page_num <= total:
                self.pdf_viewer.current_page_idx = page_num - 1
                self.pdf_viewer.render_page()
                self.update_page_label()
            else:
                self.update_page_label()
        except ValueError:
            self.update_page_label()

    def handle_text_captured(self, text, page_num):
        self.page_input.setText(str(page_num))
        self.excerpt_input.setPlainText(text)
        self.notes_input.setFocus()

    def save_annotation(self):
        if not self.current_project_id:
            return
        
        page_str = self.page_input.text()
        excerpt = self.excerpt_input.toPlainText().strip()
        notes = self.notes_input.toPlainText().strip()
        category = self.category_tabs.tabText(self.category_tabs.currentIndex())
        
        if not page_str.isdigit():
            QMessageBox.warning(self, "Validação", "A página deve ser um número inteiro.")
            return
            
        page = int(page_str)
        
        if self.editing_annotation_id:
            db.update_annotation(self.editing_annotation_id, page, excerpt, category, notes)
            self.editing_annotation_id = None
            self.btn_save_ann.setText(" Salvar Anotação")
            self.btn_cancel_edit.setVisible(False)
        else:
            db.add_annotation(self.current_project_id, page, excerpt, category, notes)
        
        self.page_input.clear()
        self.excerpt_input.clear()
        self.notes_input.clear()
        
        self.populate_annotations()
        
    def cancel_edit_annotation(self):
        self.editing_annotation_id = None
        self.btn_save_ann.setText(" Salvar Anotação")
        self.btn_cancel_edit.setVisible(False)
        self.page_input.clear()
        self.excerpt_input.clear()
        self.notes_input.clear()
        
    def load_annotation_for_editing(self):
        selected_items = self.ann_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione uma anotação para editar.")
            return
            
        row = selected_items[0].row()
        annotation_id = int(self.ann_list.item(row, 0).text())
        
        anns = db.get_annotations(self.current_project_id)
        ann = next((a for a in anns if a['id'] == annotation_id), None)
        
        if ann:
            self.editing_annotation_id = annotation_id
            self.page_input.setText(str(ann['page_number']))
            self.excerpt_input.setPlainText(ann['selected_text'])
            self.notes_input.setPlainText(ann['professor_notes'])
            
            # Find tab index
            for i in range(self.category_tabs.count()):
                if self.category_tabs.tabText(i) == ann['category']:
                    self.category_tabs.setCurrentIndex(i)
                    break
                    
            self.btn_save_ann.setText(" Atualizar Anotação")
            self.btn_cancel_edit.setVisible(True)

    def delete_selected_annotation(self):
        selected_items = self.ann_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione uma anotação para excluir.")
            return
            
        row = selected_items[0].row()
        annotation_id = int(self.ann_list.item(row, 0).text())
        
        reply = QMessageBox.question(self, "Excluir Anotação", 
                                     "Tem certeza de que deseja excluir esta anotação?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db.delete_annotation(annotation_id)
            if self.editing_annotation_id == annotation_id:
                self.cancel_edit_annotation()
            self.populate_annotations()

    def populate_annotations(self):
        if not self.current_project_id:
            return
        self.ann_list.setRowCount(0)
        anns = db.get_annotations(self.current_project_id)
        category_icons = {
            "Apontamentos": ("assets/icons/alert-circle.svg", "#ef4444"),
            "Dúvida": ("assets/icons/help-circle.svg", "#eab308"),
            "Sugestão": ("assets/icons/lightbulb.svg", "#3b82f6"),
        }
        for row_idx, ann in enumerate(anns):
            self.ann_list.insertRow(row_idx)
            self.ann_list.setItem(row_idx, 0, QTableWidgetItem(str(ann['id'])))
            self.ann_list.setItem(row_idx, 1, QTableWidgetItem(str(ann['page_number'])))

            cat_item = QTableWidgetItem(ann['category'])
            icon_cfg = category_icons.get(ann['category'])
            if icon_cfg:
                cat_item.setIcon(load_svg_icon(icon_cfg[0], icon_cfg[1], 14))
            self.ann_list.setItem(row_idx, 2, cat_item)
            
            excerpt = ann['selected_text']
            if len(excerpt) > 40:
                excerpt = excerpt[:37] + "..."
            self.ann_list.setItem(row_idx, 3, QTableWidgetItem(excerpt))

    def save_general_opinion(self):
        if self.current_project_id:
            text = self.general_opinion.toPlainText()
            db.update_general_opinion(self.current_project_id, text)

    def run_citation_validation(self):
        if not self.current_project_id:
            return
        project_data = db.get_project(self.current_project_id)
        pdf_path = project_data['pdf_path']
        
        if not pdf_path or not os.path.exists(pdf_path):
            QMessageBox.warning(self, "Erro", "PDF não encontrado.")
            return
            
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            results = validador_citacoes.run_validation(pdf_path)
            QApplication.restoreOverrideCursor()
            
            if not results:
                QMessageBox.information(self, "Aviso", "Nenhuma citação processada ou falha na extração.")
                return
                
            dialog = CitationReportDialog(results, self)
            dialog.exec()
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro durante a validação:\n{e}")

    def update_tab_color(self, index):
        if not self.category_tabs or index < 0:
            return
        tokens = THEME_TOKENS[self.current_theme]
        colors = tokens["tab_bgs"]
        borders = tokens["tab_borders"]
        tab_text = tokens["tab_text"]
        self.category_tabs.setStyleSheet(
            f"QTabBar::tab:selected {{ background: {colors[index]}; border-bottom: 2px solid {borders[index]}; font-weight: bold; color: {tab_text}; }}"
        )

    def open_export_dialog(self):
        if not self.current_project_id:
            return
        
        dialog = ExportDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            evaluator = dialog.evaluator_name
            date_str = dialog.date_str
            fmt = dialog.export_format
            
            project_data = db.get_project(self.current_project_id)
            default_name = f"Revisao_{project_data['student_name'].replace(' ', '_')}.{fmt}"
            
            filter_str = "Documentos PDF (*.pdf)" if fmt == "pdf" else "Documentos do Word (*.docx)"
            file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Relatório", default_name, filter_str)
            
            if not file_path:
                return
            
            self.save_general_opinion()
            
            if fmt == "pdf":
                self.generate_pdf(file_path, project_data, evaluator, date_str)
            else:
                self.generate_docx(file_path, project_data, evaluator, date_str)

    def generate_pdf(self, file_path, project_data, evaluator, date_str, show_msg=True):
        anns = db.get_annotations(self.current_project_id)
        
        html = f"""
        <html>
        <head>
            <style>
                body, div, p {{ font-family: Arial, sans-serif; font-size: 12pt; line-height: 1.6; color: #000; }}
                h1 {{ color: #000; text-align: center; border-bottom: 2px solid #000; padding-bottom: 10pt; font-size: 20pt; }}
                h2 {{ color: #000; margin-top: 30pt; font-size: 14pt; }}
                .info {{ font-size: 14pt; margin-bottom: 20pt; }}
                .notes {{ margin-bottom: 20pt; }}
                .signature-section {{ margin-top: 50pt; text-align: center; }}
                .cursive-signature {{ font-family: 'Lucida Handwriting', 'Brush Script MT', 'Apple Chancery', 'URW Chancery L', cursive; font-size: 12pt; color: #000; margin-bottom: 5pt; }}
                .signature-line {{ border-top: 1px solid #000; width: 300pt; margin: 0 auto; margin-top: 10pt; padding-top: 5pt; }}
            </style>
        </head>
        <body>
            <h1>Relatório de Revisão de TCC</h1>
            <div class='info'>
                <b>Aluno(a):</b> {project_data['student_name']}<br>
                <b>Título:</b> {project_data['thesis_title']}<br>
                <b>Avaliador(a):</b> {evaluator if evaluator else 'Professor(a) / Banca Examinadora'}
            </div>
        """
        
        for ann in anns:
            html += f"<h2>Página {ann['page_number']} - Categoria: {ann['category']}</h2>"
            html += f"<div><b>Trecho Citado:</b> \"{ann['selected_text']}\"</div>"
            html += f"<div class='notes'><b>Observações e Sugestões:</b><br>{ann['professor_notes'].replace(chr(10), '<br>')}</div>"
        
        html += "<h2>Parecer Geral</h2>"
        html += f"<div>{(project_data['general_opinion'] or 'Sem parecer geral.').replace(chr(10), '<br>')}</div>"
        
        html += f"""
            <div class='signature-section'>
                <div class='cursive-signature'>{evaluator if evaluator else ''}</div>
                <div class='signature-line'>{evaluator if evaluator else 'Assinatura'}</div>
                <div>{date_str}</div>
            </div>
        </body>
        </html>
        """
        
        document = QTextDocument()
        document.setHtml(html)
        
        writer = QPdfWriter(file_path)
        writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        writer.setPageMargins(QMarginsF(15, 15, 15, 15), QPageLayout.Unit.Millimeter)
        
        document.print(writer)
        if show_msg:
            QMessageBox.information(self, "Sucesso", f"Relatório PDF exportado com sucesso para:\n{file_path}")

    def generate_docx(self, file_path, project_data, evaluator, date_str, show_msg=True):
        try:
            import docx
            from docx.shared import Pt
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            
            doc = docx.Document()
            
            doc.add_heading('Relatório de Revisão de Trabalho de Conclusão de Curso (TCC)', 0)
            
            p_info = doc.add_paragraph()
            r_student = p_info.add_run(f"Aluno(a): {project_data['student_name']}\n")
            r_student.font.size = Pt(14)
            r_student.bold = True
            
            r_title = p_info.add_run(f"Título: {project_data['thesis_title']}\n")
            r_title.font.size = Pt(14)
            r_title.bold = True
            
            r_evaluator = p_info.add_run(f"Avaliador(a): {evaluator if evaluator else 'Professor(a) / Banca Examinadora'}")
            r_evaluator.font.size = Pt(14)
            r_evaluator.bold = True
            
            doc.add_paragraph() 
            
            anns = db.get_annotations(self.current_project_id)
            for ann in anns:
                doc.add_heading(f"Página {ann['page_number']} - Categoria: {ann['category']}", level=2)
                
                doc.add_paragraph(f"Trecho Citado: \"{ann['selected_text']}\"")
                doc.add_paragraph(f"Observações e Sugestões:\n{ann['professor_notes']}")
                doc.add_paragraph() 
            
            doc.add_heading('Parecer Geral de Membro da Banca Avaliadora', level=1)
            doc.add_paragraph(project_data['general_opinion'] or "Sem parecer geral.")
            
            doc.add_paragraph()
            doc.add_paragraph()
            doc.add_paragraph()
            
            p_sig = doc.add_paragraph()
            p_sig.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            if evaluator:
                r_sig = p_sig.add_run(evaluator)
                r_sig.font.name = 'Lucida Handwriting'
                r_sig.font.size = Pt(12)
            
            p_line = doc.add_paragraph()
            p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_line = p_line.add_run("_________________________________________________")
            
            p_name = doc.add_paragraph()
            p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_name.add_run(evaluator if evaluator else 'Assinatura')
            
            p_date = doc.add_paragraph()
            p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_date.add_run(date_str)
            
            doc.save(file_path)
            if show_msg:
                QMessageBox.information(self, "Sucesso", f"Relatório DOCX exportado com sucesso para:\n{file_path}")
            
        except ImportError:
            QMessageBox.critical(self, "Erro", "python-docx não está instalado. Por favor, rode: pip install python-docx")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao exportar relatório:\n{str(e)}")

    def open_email_settings(self):
        dialog = EmailSettingsDialog(self)
        return dialog.exec() == QDialog.DialogCode.Accepted

    def send_reports_by_email(self):
        if not self.current_project_id:
            return
        project_data = db.get_project(self.current_project_id)
        
        advisor_email = project_data.get('advisor_email', '').strip()
        if not advisor_email:
            QMessageBox.warning(self, "Aviso", "O e-mail do orientador não está configurado neste projeto. Edite o projeto para adicionar o e-mail.")
            return

        smtp_cfg = db.get_smtp_settings()
        if not smtp_cfg["server"] or not smtp_cfg["user"] or not smtp_cfg["password"]:
            reply = QMessageBox.question(
                self,
                "Configurar E-mail",
                "As credenciais de envio (SMTP/Gmail) ainda não estão configuradas.\n"
                "Deseja configurá-las agora?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes or not self.open_email_settings():
                return
            
        dialog = ExportDialog(self)
        dialog.setWindowTitle("Configurar Envio de E-mail")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            evaluator = dialog.evaluator_name
            date_str = dialog.date_str
            fmt = dialog.export_format
            
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            try:
                import tempfile
                temp_dir = tempfile.gettempdir()
                general_report_path = os.path.join(temp_dir, f"Parecer_{project_data['student_name'].replace(' ', '_')}.{fmt}")
                if fmt == "pdf":
                    self.generate_pdf(general_report_path, project_data, evaluator, date_str, show_msg=False)
                else:
                    self.generate_docx(general_report_path, project_data, evaluator, date_str, show_msg=False)
                    
                results = validador_citacoes.run_validation(project_data['pdf_path'])
                citation_report_path = os.path.join(temp_dir, f"Citacoes_{project_data['student_name'].replace(' ', '_')}.xlsx")
                import pandas as pd
                df = pd.DataFrame(results)
                df.to_excel(citation_report_path, index=False)
                
                self._send_email_smtp(advisor_email, general_report_path, citation_report_path, project_data)
                
                QApplication.restoreOverrideCursor()
                QMessageBox.information(self, "Sucesso", "E-mail enviado com sucesso ao orientador!")
                
            except Exception as e:
                QApplication.restoreOverrideCursor()
                QMessageBox.critical(self, "Erro", f"Falha ao enviar e-mail:\n{str(e)}")
                
    def _send_email_smtp(self, recipient_email, report1_path, report2_path, project_data):
        smtp_cfg = db.get_smtp_settings()
        smtp_server = smtp_cfg["server"]
        smtp_port = int(smtp_cfg["port"] or "587")
        smtp_user = smtp_cfg["user"]
        smtp_password = smtp_cfg["password"]
        
        if not smtp_server or not smtp_user or not smtp_password:
            raise Exception("Credenciais SMTP não configuradas. Use o botão 'Configurar E-mail' no Painel.")
            
        msg = EmailMessage()
        msg['Subject'] = f"Relatórios de Revisão de TCC - {project_data['student_name']}"
        msg['From'] = smtp_user
        msg['To'] = recipient_email
        msg.set_content(f"Prezado(a) Orientador(a),\n\nSegue em anexo o Parecer Geral e o Relatório de Validação de Citações referente ao TCC de {project_data['student_name']}.\n\nTítulo: {project_data['thesis_title']}\n\nAtenciosamente,\nDocentia — Assistente de Revisão de TCC.")
        
        import mimetypes
        for file_path in [report1_path, report2_path]:
            if not os.path.exists(file_path):
                continue
            ctype, encoding = mimetypes.guess_type(file_path)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            with open(file_path, 'rb') as fp:
                msg.add_attachment(fp.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(file_path))
                
        with smtplib.SMTP(smtp_server, smtp_port, timeout=20) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Docentia")
    app.setOrganizationName("Docentia")
    window = TCCAssistantApp()
    window.show()
    sys.exit(app.exec())

import os
import sys
import codecs
import pyperclip
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QComboBox, 
                            QLineEdit, QTextEdit, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

# 预设关键词
PRESET_KEYWORDS = [
    "error",
    "warning",
    "info"
]

class LogSearchTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.log_file_path = ""
        self.search_results = ""
        
    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('日志搜索工具 v1.0')
        self.setGeometry(300, 300, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 文件选择区域
        file_layout = QHBoxLayout()
        self.file_label = QLabel('日志文件:')
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        self.browse_button = QPushButton('浏览...')
        self.browse_button.clicked.connect(self.browse_file)
        
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(self.browse_button)
        
        # 关键词选择区域
        keyword_layout = QHBoxLayout()
        self.keyword_label = QLabel('关键词:')
        self.keyword_combo = QComboBox()
        self.keyword_combo.addItems(PRESET_KEYWORDS)
        self.keyword_combo.addItem("自定义...")
        self.keyword_combo.currentIndexChanged.connect(self.on_combo_changed)
        
        self.custom_keyword = QLineEdit()
        self.custom_keyword.setPlaceholderText('输入自定义关键词')
        self.custom_keyword.setVisible(False)
        
        self.search_button = QPushButton('搜索')
        self.search_button.clicked.connect(self.search_log)
        
        keyword_layout.addWidget(self.keyword_label)
        keyword_layout.addWidget(self.keyword_combo)
        keyword_layout.addWidget(self.custom_keyword)
        keyword_layout.addWidget(self.search_button)
        
        # 结果显示区域
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        
        # 复制按钮
        self.copy_button = QPushButton('复制到剪贴板')
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        
        # 添加所有布局到主布局
        main_layout.addLayout(file_layout)
        main_layout.addLayout(keyword_layout)
        main_layout.addWidget(QLabel('搜索结果:'))
        main_layout.addWidget(self.result_text)
        main_layout.addWidget(self.copy_button)
        
        # 设置拖放功能
        self.setAcceptDrops(True)
        
        self.show()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls and len(urls) > 0:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path):
                self.log_file_path = file_path
                self.file_path.setText(file_path)
            else:
                QMessageBox.warning(self, "警告", "请拖放一个有效的文件")
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择日志文件", "", "所有文件 (*)")
        if file_path:
            self.log_file_path = file_path
            self.file_path.setText(file_path)
    
    def on_combo_changed(self, index):
        # 如果选择了"自定义..."选项
        if index == len(PRESET_KEYWORDS):
            self.custom_keyword.setVisible(True)
        else:
            self.custom_keyword.setVisible(False)
    
    def get_selected_keyword(self):
        index = self.keyword_combo.currentIndex()
        if index < len(PRESET_KEYWORDS):
            return PRESET_KEYWORDS[index]
        else:
            return self.custom_keyword.text()
    
    def search_log(self):
        if not self.log_file_path:
            QMessageBox.warning(self, "警告", "请先选择日志文件")
            return
        
        keyword = self.get_selected_keyword()
        if not keyword:
            QMessageBox.warning(self, "警告", "请输入关键词")
            return
        
        self.result_text.clear()
        self.search_results = ""
        
        try:
            # 尝试使用不同的编码打开文件
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            for encoding in encodings:
                try:
                    with codecs.open(self.log_file_path, 'r', encoding=encoding) as file:
                        self.result_text.append(f"使用 {encoding} 编码成功打开文件\n")
                        self.search_results += f"使用 {encoding} 编码成功打开文件\n"
                        
                        found = False
                        for line_number, line in enumerate(file, start=1):
                            if keyword in line:
                                result_line = f"第 {line_number} 行: {line.strip()}\n"
                                self.result_text.append(result_line)
                                self.search_results += result_line
                                found = True
                        
                        if not found:
                            no_result = f"未找到包含关键词 '{keyword}' 的内容\n"
                            self.result_text.append(no_result)
                            self.search_results += no_result
                    return
                except UnicodeDecodeError:
                    continue
            
            error_msg = f"无法以支持的编码格式打开文件 {self.log_file_path}\n"
            self.result_text.append(error_msg)
            self.search_results += error_msg
            
        except Exception as e:
            error_msg = f"读取文件时出错: {e}\n"
            self.result_text.append(error_msg)
            self.search_results += error_msg
    
    def copy_to_clipboard(self):
        if self.search_results:
            pyperclip.copy(self.search_results)
            QMessageBox.information(self, "提示", "搜索结果已复制到剪贴板")
        else:
            QMessageBox.warning(self, "警告", "没有可复制的搜索结果")

def main():
    app = QApplication(sys.argv)
    ex = LogSearchTool()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
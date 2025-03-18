import os
import sys
import codecs
import pyperclip
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QComboBox, 
                            QLineEdit, QTextEdit, QFileDialog, QMessageBox,
                            QDialog, QListWidget, QCheckBox)  # 添加 QCheckBox
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

# 获取资源文件路径的辅助函数
def resource_path(relative_path):
    """ 获取资源的绝对路径 """
    try:
        # PyInstaller创建临时文件夹并将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# 从文件加载预设关键词
def load_keywords():
    keywords = ["error", "warning", "info"]  # 默认关键词
    
    try:
        keywords_path = resource_path("keywords.txt")
        if os.path.exists(keywords_path):
            with open(keywords_path, 'r', encoding='utf-8') as f:
                loaded_keywords = [line.strip() for line in f if line.strip()]
                if loaded_keywords:
                    keywords = loaded_keywords
    except Exception as e:
        print(f"加载关键词文件时出错: {e}")
    
    return keywords

# 保存关键词到文件
def save_keywords(keywords):
    try:
        # 尝试保存到资源路径
        keywords_path = resource_path("keywords.txt")
        
        # 如果在打包环境中，则保存到用户目录
        if hasattr(sys, '_MEIPASS'):
            home_dir = os.path.expanduser("~")
            app_dir = os.path.join(home_dir, ".log_search_tool")
            os.makedirs(app_dir, exist_ok=True)
            keywords_path = os.path.join(app_dir, "keywords.txt")
        
        with open(keywords_path, 'w', encoding='utf-8') as f:
            for keyword in keywords:
                f.write(f"{keyword}\n")
        return True, keywords_path
    except Exception as e:
        return False, str(e)

# 预设关键词
PRESET_KEYWORDS = load_keywords()

class KeywordDialog(QDialog):
    def __init__(self, parent=None, keywords=None):
        super().__init__(parent)
        self.keywords = keywords or []
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('编辑关键词')
        self.setGeometry(300, 300, 400, 300)
        
        layout = QVBoxLayout()
        
        # 关键词列表
        self.keyword_list = QListWidget()
        for keyword in self.keywords:
            self.keyword_list.addItem(keyword)
        
        # 编辑区域
        edit_layout = QHBoxLayout()
        self.keyword_edit = QLineEdit()
        self.keyword_edit.setPlaceholderText('输入关键词')
        
        self.add_button = QPushButton('添加')
        self.add_button.clicked.connect(self.add_keyword)
        
        self.remove_button = QPushButton('删除')
        self.remove_button.clicked.connect(self.remove_keyword)
        
        edit_layout.addWidget(self.keyword_edit)
        edit_layout.addWidget(self.add_button)
        edit_layout.addWidget(self.remove_button)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        self.save_button = QPushButton('保存')
        self.save_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton('取消')
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        # 添加所有布局
        layout.addWidget(QLabel('关键词列表:'))
        layout.addWidget(self.keyword_list)
        layout.addLayout(edit_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def add_keyword(self):
        keyword = self.keyword_edit.text().strip()
        if keyword and keyword not in self.keywords:
            self.keywords.append(keyword)
            self.keyword_list.addItem(keyword)
            self.keyword_edit.clear()
    
    def remove_keyword(self):
        selected_items = self.keyword_list.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            keyword = item.text()
            self.keywords.remove(keyword)
            self.keyword_list.takeItem(self.keyword_list.row(item))
    
    def get_keywords(self):
        return self.keywords

class LogSearchTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.log_file_path = ""
        self.search_results = ""
        
    # 在 LogSearchTool 类中添加 container_clicked 方法
    def container_clicked(self, event):
        """处理文件容器的点击事件"""
        self.browse_file()
        
    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('日志搜索工具 v1.0')
        self.setGeometry(300, 300, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 文件选择区域 - 修改为可点击的拖放区域
        file_layout = QVBoxLayout()
        file_layout.setSpacing(10)
        
        # 添加提示标签 - 将用于显示文件路径
        self.drop_label = QLabel('点击此区域选择文件或直接拖放文件到此处')
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setWordWrap(True)  # 允许文本换行
        
        # 将组件添加到文件布局 - 移除文件路径输入框
        file_layout.addWidget(self.drop_label)
        
        # 创建一个带边框的容器来包含文件选择区域
        self.file_container = QWidget()
        self.file_container.setLayout(file_layout)
        self.file_container.setStyleSheet("""
            QWidget {
                border: 2px dashed #aaa;
                border-radius: 8px;
                background-color: #f8f8f8;
                padding: 20px;
            }
            QWidget:hover {
                background-color: #e8e8e8;
                border-color: #888;
            }
            QLabel {
                font-size: 16px;
                color: #555;
            }
        """)
        # 使容器可点击
        self.file_container.mousePressEvent = self.container_clicked
        
        # 关键词选择区域
        keyword_layout = QVBoxLayout()
        
        # 添加预设关键词标签和编辑按钮在同一行
        preset_header_layout = QHBoxLayout()
        preset_label = QLabel('预设关键词(可多选):')
        self.edit_keywords_button = QPushButton('编辑关键词')
        self.edit_keywords_button.clicked.connect(self.edit_keywords)
        preset_header_layout.addWidget(preset_label)
        preset_header_layout.addStretch(1)  # 添加弹性空间
        preset_header_layout.addWidget(self.edit_keywords_button)
        keyword_layout.addLayout(preset_header_layout)
        
        # 使用垂直布局放置复选框
        self.keyword_checks_layout = QVBoxLayout()
        self.keyword_checks = []
        
        # 为每个预设关键词创建一个复选框
        for keyword in PRESET_KEYWORDS:
            check = QCheckBox(keyword)
            self.keyword_checks.append(check)
            self.keyword_checks_layout.addWidget(check)
        
        # 创建一个容器来包含所有复选框
        keyword_checks_container = QWidget()
        keyword_checks_container.setLayout(self.keyword_checks_layout)
        
        # 添加到主布局
        keyword_layout.addWidget(keyword_checks_container)
        
        # 自定义关键词输入框
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel('自定义关键词:'))
        self.custom_keyword = QLineEdit()
        self.custom_keyword.setPlaceholderText('输入自定义关键词(空格或|分隔多个关键词)')
        custom_layout.addWidget(self.custom_keyword)
        keyword_layout.addLayout(custom_layout)
        
        # 添加搜索选项区域
        options_layout = QHBoxLayout()
        
        # 添加搜索模式选项
        self.search_mode_label = QLabel('搜索模式:')
        self.search_mode_and = QCheckBox('与模式(必须包含所有关键词)')
        self.search_mode_and.setChecked(True)  # 默认选中"与"模式
        self.search_mode_or = QCheckBox('或模式(包含任一关键词即可)')
        
        # 确保只能选择一个模式
        def update_search_mode():
            if self.sender() == self.search_mode_and and self.search_mode_and.isChecked():
                self.search_mode_or.setChecked(False)
            elif self.sender() == self.search_mode_or and self.search_mode_or.isChecked():
                self.search_mode_and.setChecked(False)
            # 确保至少有一个选中
            if not self.search_mode_and.isChecked() and not self.search_mode_or.isChecked():
                self.search_mode_and.setChecked(True)
        
        self.search_mode_and.stateChanged.connect(update_search_mode)
        self.search_mode_or.stateChanged.connect(update_search_mode)
        
        # 添加大小写敏感选项
        self.case_sensitive = QCheckBox('区分大小写')
        
        # 将选项添加到布局
        options_layout.addWidget(self.search_mode_label)
        options_layout.addWidget(self.search_mode_and)
        options_layout.addWidget(self.search_mode_or)
        options_layout.addStretch(1)  # 添加弹性空间
        options_layout.addWidget(self.case_sensitive)
        
        keyword_layout.addLayout(options_layout)
        
        # 搜索按钮 - 整行显示
        self.search_button = QPushButton('搜索')
        self.search_button.clicked.connect(self.search_log)
        # 设置搜索按钮为绿色
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        keyword_layout.addWidget(self.search_button)
        
        # 移除原来的编辑关键词按钮布局
        # button_layout = QHBoxLayout()
        # self.edit_keywords_button = QPushButton('编辑关键词')
        # self.edit_keywords_button.clicked.connect(self.edit_keywords)
        # button_layout.addWidget(self.edit_keywords_button)
        # keyword_layout.addLayout(button_layout)
        
        # 结果显示区域
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        
        # 复制按钮
        self.copy_button = QPushButton('复制到剪贴板')
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        
        # 添加所有布局到主布局
        main_layout.addWidget(self.file_container)
        main_layout.addLayout(keyword_layout)  # 使用新的关键词布局
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
                # 修复这里：使用 drop_label 而不是不存在的 file_path
                self.drop_label.setText(f"已选择文件: {file_path}")
            else:
                QMessageBox.warning(self, "警告", "请拖放一个有效的文件")
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择日志文件", "", "所有文件 (*)")
        if file_path:
            self.log_file_path = file_path
            # 修复这里：使用 drop_label 而不是不存在的 file_path
            self.drop_label.setText(f"已选择文件: {file_path}")
    
    def on_combo_changed(self, index):
        # 如果选择了"自定义..."选项
        if index == len(PRESET_KEYWORDS):
            self.custom_keyword.setVisible(True)
        else:
            self.custom_keyword.setVisible(False)
    
    # 添加获取选中关键词的方法
    def get_selected_keywords(self):
        # 获取所有选中的预设关键词
        selected_keywords = []
        for check in self.keyword_checks:
            if check.isChecked():
                selected_keywords.append(check.text())
        
        # 获取自定义关键词
        custom_keyword = self.custom_keyword.text().strip()
        
        # 处理自定义关键词
        if custom_keyword:
            if '|' in custom_keyword:
                custom_keywords = [k.strip() for k in custom_keyword.split('|') if k.strip()]
            else:
                custom_keywords = [k.strip() for k in custom_keyword.split() if k.strip()]
            selected_keywords.extend(custom_keywords)
        
        return selected_keywords
    
    # 添加搜索日志的方法
    def search_log(self):
        if not self.log_file_path:
            QMessageBox.warning(self, "警告", "请先选择日志文件")
            return
        
        keywords = self.get_selected_keywords()
        if not keywords:
            QMessageBox.warning(self, "警告", "请选择或输入至少一个关键词")
            return
        
        self.result_text.clear()
        self.search_results = ""
        
        # 显示搜索中的提示
        self.result_text.append("正在搜索中，请稍候...\n")
        QApplication.processEvents()  # 处理待处理的事件，使界面保持响应
        
        try:
            # 尝试使用不同的编码打开文件
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'iso-8859-1']  # 添加更多编码支持
            file_size = os.path.getsize(self.log_file_path)
            
            # 移除大文件警告逻辑
            
            # 使用界面上的选项而不是弹窗
            is_and_mode = self.search_mode_and.isChecked()
            is_case_sensitive = self.case_sensitive.isChecked()
            
            # 添加调试信息
            self.result_text.clear()
            self.result_text.append("开始搜索...\n")
            self.result_text.append(f"文件路径: {self.log_file_path}\n")
            self.result_text.append(f"搜索关键词: {', '.join(keywords)}\n")
            self.result_text.append(f"搜索模式: {'与模式' if is_and_mode else '或模式'}\n")
            self.result_text.append(f"大小写敏感: {'是' if is_case_sensitive else '否'}\n")
            QApplication.processEvents()  # 更新界面
            
            # 预处理关键词
            processed_keywords = []
            for keyword in keywords:
                if not is_case_sensitive:
                    processed_keywords.append(keyword.lower())
                else:
                    processed_keywords.append(keyword)
            
            # 尝试打开文件并搜索
            file_opened = False
            
            for encoding in encodings:
                try:
                    self.result_text.append(f"\n尝试使用 {encoding} 编码打开文件...\n")
                    QApplication.processEvents()  # 更新界面
                    
                    with codecs.open(self.log_file_path, 'r', encoding=encoding) as file:
                        file_opened = True
                        self.result_text.clear()
                        self.search_results = f"使用 {encoding} 编码成功打开文件\n"
                        
                        # 添加搜索模式信息
                        mode_info = f"搜索模式: {'与模式(必须包含所有关键词)' if is_and_mode else '或模式(包含任一关键词即可)'}\n"
                        mode_info += f"大小写敏感: {'是' if is_case_sensitive else '否'}\n"
                        self.result_text.append(mode_info)
                        self.search_results += mode_info
                        
                        # 添加关键词信息 - 优化显示格式
                        keywords_str = "', '".join(keywords)
                        keywords_info = f"搜索条件: {len(keywords)}个关键词 ['{keywords_str}']\n"
                        if is_and_mode and len(keywords) > 1:
                            keywords_info += f"匹配规则: 必须同时包含所有关键词\n"
                        elif not is_and_mode and len(keywords) > 1:
                            keywords_info += f"匹配规则: 包含任一关键词即可\n"
                        self.result_text.append(keywords_info)
                        self.search_results += keywords_info
                        
                        # 添加文件信息
                        file_info = f"文件大小: {file_size / 1024 / 1024:.2f} MB\n"
                        self.result_text.append(file_info)
                        self.search_results += file_info
                        
                        found = False
                        line_count = 0
                        total_lines = 0
                        
                        # 计算总行数（仅对较小文件）
                        if file_size < 5 * 1024 * 1024:  # 降低到5MB
                            total_lines = sum(1 for _ in file)
                            file.seek(0)  # 重置文件指针
                            self.result_text.append(f"文件总行数: {total_lines}\n")
                            self.search_results += f"文件总行数: {total_lines}\n"
                        
                        # 每处理1000行更新一次界面
                        update_frequency = 1000 if file_size > 10 * 1024 * 1024 else 100
                        
                        # 添加结果计数器
                        result_count = 0
                        max_results = 5000  # 最大结果数限制
                        
                        # 添加一些调试信息
                        self.result_text.append("\n开始逐行搜索...\n")
                        QApplication.processEvents()  # 更新界面
                        
                        for line_number, line in enumerate(file, start=1):
                            line_count += 1
                            
                            # 处理行内容 - 确保是字符串类型
                            if not isinstance(line, str):
                                line = str(line)
                                
                            line_to_check = line if is_case_sensitive else line.lower()
                            
                            # 改进的关键词匹配逻辑
                            matched_keywords = []
                            for i, keyword in enumerate(processed_keywords):
                                if keyword in line_to_check:
                                    matched_keywords.append(keywords[i])
                            
                            # 根据搜索模式判断是否匹配
                            line_matched = False
                            if is_and_mode:
                                # 与模式：必须包含所有关键词
                                line_matched = len(matched_keywords) == len(keywords)
                            else:
                                # 或模式：包含任一关键词即可
                                line_matched = len(matched_keywords) > 0
                            
                            if line_matched:
                                # 不再限制行长度，显示完整内容
                                line_display = line.strip()
                                
                                # 直接显示匹配内容，不添加行号和关键词信息
                                result_line = line_display + "\n"
                                self.result_text.append(result_line)
                                self.search_results += result_line
                                found = True
                                result_count += 1
                                
                                # 不再弹窗询问是否继续，只在状态栏显示进度
                                if result_count % 500 == 0:
                                    progress_msg = f"已找到 {result_count} 个结果，继续搜索中...\n"
                                    self.result_text.append(progress_msg)
                                    self.search_results += progress_msg
                                    QApplication.processEvents()  # 更新界面
                                
                                # 如果结果超过最大限制，自动停止但不弹窗
                                if result_count >= max_results:
                                    limit_msg = f"\n已达到最大结果数限制({max_results})，搜索已停止。\n"
                                    self.result_text.append(limit_msg)
                                    self.search_results += limit_msg
                                    break
                            
                            # 定期更新界面
                            if line_count % update_frequency == 0:
                                progress = f"已处理 {line_number} 行"
                                if total_lines > 0:
                                    progress += f" ({line_number/total_lines*100:.1f}%)"
                                progress += f"，找到 {result_count} 个结果"
                                self.result_text.append(f"{progress}...\n")
                                QApplication.processEvents()  # 处理待处理的事件
                        
                        # 移除进度提示
                        self.result_text.clear()
                        self.result_text.append(f"使用 {encoding} 编码成功打开文件\n")
                        self.result_text.append(file_info)
                        if total_lines > 0:
                            self.result_text.append(f"文件总行数: {total_lines}\n")
                        
                        if found:
                            self.result_text.append(f"搜索完成，共找到结果在 {result_count} 行\n")
                            self.search_results += f"搜索完成，共找到结果在 {result_count} 行\n"
                            
                            # 修复搜索结果不显示问题
                            # 从搜索结果中提取实际的日志内容行
                            result_lines = []
                            for line in self.search_results.split('\n'):
                                # 排除所有非日志内容的行
                                if not (line.startswith("搜索") or 
                                       line.startswith("文件") or 
                                       line.startswith("使用") or 
                                       line.startswith("大小写") or 
                                       line.startswith("匹配规则") or 
                                       line.startswith("已找到") or 
                                       line.startswith("已达到") or 
                                       line.startswith("搜索条件") or 
                                       line.startswith("未找到") or 
                                       line == ""):
                                    result_lines.append(line)
                            
                            # 限制显示的结果数量
                            if len(result_lines) > 1000:
                                self.result_text.append("结果过多，仅显示前1000行：\n")
                                for line in result_lines[:1000]:
                                    self.result_text.append(line)
                                    # 添加空行实现隔行显示
                                    self.result_text.append("")
                                self.result_text.append(f"\n... 还有 {len(result_lines) - 1000} 行结果未显示 ...\n")
                            else:
                                for line in result_lines:
                                    self.result_text.append(line)
                                    # 添加空行实现隔行显示
                                    self.result_text.append("")
                        else:
                            keywords_str = "', '".join(keywords)
                            no_result = f"未找到包含关键词 '{keywords_str}' 的内容\n"
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
            # 提取所有匹配的行（现在直接是日志内容）
            matched_lines = []
            for line in self.search_results.split('\n'):
                # 排除进度信息和其他非日志内容
                if not (line.startswith("搜索") or 
                       line.startswith("文件") or 
                       line.startswith("使用") or 
                       line.startswith("大小写") or 
                       line.startswith("匹配规则") or 
                       line.startswith("已找到") or 
                       line.startswith("已达到") or 
                       line.startswith("搜索条件") or 
                       line.startswith("未找到") or 
                       line == ""):
                    matched_lines.append(line)
            
            # 将匹配的日志内容合并为一个字符串
            clipboard_content = "\n".join(matched_lines)
            
            if clipboard_content:
                pyperclip.copy(clipboard_content)
                QMessageBox.information(self, "提示", "匹配的日志内容已复制到剪贴板")
            else:
                QMessageBox.warning(self, "警告", "没有可复制的匹配内容")
        else:
            QMessageBox.warning(self, "警告", "没有可复制的搜索结果")
    
    # 添加编辑关键词的方法
    def edit_keywords(self):
        global PRESET_KEYWORDS
        dialog = KeywordDialog(self, PRESET_KEYWORDS.copy())
        if dialog.exec_() == QDialog.Accepted:
            # 保存当前选中的关键词
            selected_keywords = [check.text() for check in self.keyword_checks if check.isChecked()]
            
            # 更新预设关键词
            PRESET_KEYWORDS = dialog.get_keywords()
            
            # 清除现有复选框
            for check in self.keyword_checks:
                self.keyword_checks_layout.removeWidget(check)
                check.deleteLater()
            self.keyword_checks.clear()
            
            # 创建新的复选框
            for keyword in PRESET_KEYWORDS:
                check = QCheckBox(keyword)
                # 如果该关键词之前被选中，则保持选中状态
                if keyword in selected_keywords:
                    check.setChecked(True)
                self.keyword_checks.append(check)
                self.keyword_checks_layout.addWidget(check)
            
            # 保存关键词
            success, message = save_keywords(PRESET_KEYWORDS)
            if success:
                QMessageBox.information(self, "成功", f"关键词已保存到: {message}")
            else:
                QMessageBox.warning(self, "警告", f"保存关键词失败: {message}")

def main():
    app = QApplication(sys.argv)
    ex = LogSearchTool()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
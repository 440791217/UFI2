import json
import sys
import os
from tkinter import Widget
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QGroupBox, QComboBox, QMessageBox
import subprocess
import figure


class AnalyzerConfigDiaglog:
    def __init__(self, root, rootpath=None):
        super().__init__()
        self.root = root
        self.rootpath = rootpath
        self.outpath = os.path.join(self.rootpath, 'out')
        self.scriptspath = os.path.join(self.rootpath,'scripts')
        self.resultspath = os.path.join(self.rootpath,'results')
        self.analyze_script_path = None

    def show_directory_selection_panel(self):
        self.panel = QDialog()  # 将 QWidget 改为 QDialog
        layout = QVBoxLayout()

        # 模式选择部分
        mode_group = QGroupBox("模式选择")
        mode_layout = QHBoxLayout()
        mode_label = QLabel("选择模式:")
        self.mode_combobox = QComboBox()
        self.mode_combobox.addItems(["RF", "IOV", "IOA","MEM"])
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combobox)
        mode_group.setLayout(mode_layout)

        # 目录选择部分
        path_group = QGroupBox("目录选择设置")
        path_layout = QVBoxLayout()
        path_label_layout = QHBoxLayout()
        label = QLabel('选择的目录:')
        self.path_edit = QLineEdit()
        if not self.rootpath:
            initial_path = os.getcwd()
        else:
            initial_path = self.rootpath
        self.path_edit.setText(initial_path)
        select_button = QPushButton('选择目录')
        select_button.clicked.connect(self.select_directory)
        path_label_layout.addWidget(label)
        path_label_layout.addWidget(self.path_edit)
        path_label_layout.addWidget(select_button)
        path_layout.addLayout(path_label_layout)
        path_group.setLayout(path_layout)

        # 分析脚本选择部分
        script_group = QGroupBox("分析脚本选择")
        script_layout = QHBoxLayout()
        script_label = QLabel('选择分析脚本:')
        self.script_edit = QLineEdit()
        select_script_button = QPushButton('选择脚本')
        select_script_button.clicked.connect(self.select_script)
        script_layout.addWidget(script_label)
        script_layout.addWidget(self.script_edit)
        script_layout.addWidget(select_script_button)
        script_group.setLayout(script_layout)

        # 提示信息标签
        hint_label = QLabel("请选择合适的目录、模式和分析脚本用于后续操作。")
        layout.addWidget(hint_label)
        layout.addWidget(mode_group)
        layout.addWidget(path_group)
        layout.addWidget(script_group)

        # 确定和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton('确定')
        cancel_button = QPushButton('取消')
        ok_button.clicked.connect(self.ok_button_clicked)
        cancel_button.clicked.connect(self.panel.reject)  # 使用 reject 方法关闭对话框
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.analyze_script_path = None

        self.panel.setLayout(layout)
        self.panel.setWindowTitle('结果分析')
        self.panel.setModal(True)  # 设置为模态对话框
        self.panel.show()

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self.root, '选择目录', directory=self.outpath)
        if directory:
            self.path_edit.setText(directory)

    def select_script(self):
        file_dialog = QFileDialog(self.panel)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Python Files (*.py)")
        file_dialog.setDirectory(self.scriptspath)
        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                file_path = file_paths[0]
                self.script_edit.setText(file_path)
                self.analyze_script_path = file_path

    def ok_button_clicked(self):
        selected_path = self.path_edit.text()
        selected_mode = self.mode_combobox.currentText()
        if selected_mode in ["IOV", "IOA", "MEM"]:
            pass
            # QMessageBox.warning(self.root, "提示", "目前不支持INST和MEM分析！")
            # self.panel.reject()  # 使用 reject 方法关闭对话框
            # return

        if not self.analyze_script_path:
            QMessageBox.warning(self.root, "提示", "请选择分析脚本！")
            return

        if not os.path.isfile(self.analyze_script_path):
            QMessageBox.warning(self.root, "提示", f"选择的分析脚本 {self.analyze_script_path} 不存在！")
            return

        if not os.path.isdir(selected_path):
            QMessageBox.warning(self.root, "提示", f"选择的目录 {selected_path} 不存在！")
            return
        print('analyze_script_path',self.analyze_script_path)
        print('selected_path',selected_path)

        try:
            outlog=os.path.join(self.resultspath,'out.log')
            result = subprocess.run([sys.executable, self.analyze_script_path, selected_path,outlog ,self.mode_combobox.currentText()], capture_output=True, text=True)
            if result.returncode == 0:
                # QMessageBox.information(self.root, "提示", "数据处理完成。" + result.stdout)
                QMessageBox.information(self.root, "提示", "数据处理完成。")
                with open(outlog,'r') as rf:
                    result_data=json.load(rf)
                figure.plot_fig1(data=result_data,save_path=os.path.join(self.resultspath,'result.png'))
            else:
                QMessageBox.warning(self.root, "提示", f"数据处理失败。"+ result.stdout)
            self.panel.accept()  # 使用 accept 方法关闭对话框
        except FileNotFoundError:
            QMessageBox.warning(self.root, "提示", f"找不到要执行的Python解释器或脚本 {self.analyze_script_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    root = Widget()
    analyzer = AnalyzerConfigDiaglog(root)
    analyzer.show_directory_selection_panel()
    sys.exit(app.exec_())
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction, QDialog, QVBoxLayout, QLabel, QLineEdit, \
    QPushButton, QMessageBox, QSplitter, QFileSystemModel, QTreeView, QTextEdit, QWidget, QHBoxLayout, QGroupBox, \
    QTabWidget, QFileDialog, QInputDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QMimeData
import os
import shutil

# 全局变量，用于存储复制或剪切的文件路径
copied_paths = []
cut_paths = []


class Explore:
    def __init__(self, root) -> None:
        self.root = root

    def init_file_browser(self, rootpath):
        # 创建一个水平分割器
        self.splitter = QSplitter()

        # 创建文件系统模型
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(rootpath)  # 设置根路径为用户主目录

        # 创建树视图用于显示文件和文件夹
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setRootIndex(self.file_model.index(rootpath))
        self.tree_view.clicked.connect(self.show_file_content)
        # 自适应列宽
        self.tree_view.resizeColumnToContents(0)  # 自适应第一列（文件名列）的宽度
        # 隐藏修改时间和类型列
        self.tree_view.setColumnHidden(2, True)  # 隐藏类型列
        self.tree_view.setColumnHidden(3, True)  # 隐藏修改时间列
        # 允许拖放操作
        self.tree_view.setDragDropMode(QTreeView.DragDrop)
        self.tree_view.setDefaultDropAction(Qt.MoveAction)
        self.tree_view.setAcceptDrops(True)
        self.tree_view.viewport().setAcceptDrops(True)
        # 连接右键菜单信号
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)
        # 绑定拖放事件
        self.tree_view.dragEnterEvent = self.dragEnterEvent
        self.tree_view.dropEvent = self.dropEvent

        # 创建文本编辑框用于显示文件内容
        self.file_content_view = QTextEdit()
        self.file_content_view.setReadOnly(True)

        # 将树视图和文本编辑框添加到分割器中
        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(self.file_content_view)

        # 设置分割器的初始大小比例
        self.splitter.setSizes([200, 600])

        # 将分割器添加到主布局中
        self.root.main_layout.addWidget(self.splitter)

    def open_directory(self):
        directory = QFileDialog.getExistingDirectory(self.root, "选择目录")
        if directory:
            print(f"选择的目录是: {directory}")
            # 更新文件系统模型的根路径
            self.file_model.setRootPath(directory)
            # 更新树视图的根索引
            self.tree_view.setRootIndex(self.file_model.index(directory))

    def new_directory(self):
        directory = QFileDialog.getExistingDirectory(self.root, "新建目录")
        if directory:
            print(f"新建的目录是: {directory}")
            # 更新文件系统模型的根路径
            self.file_model.setRootPath(directory)
            # 更新树视图的根索引
            self.tree_view.setRootIndex(self.file_model.index(directory))

    def show_file_content(self, index):
        file_path = self.file_model.filePath(index)
        if os.path.isfile(file_path):
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension in ['.png', '.jpg', '.jpeg', '.bmp']:
                # 是图片文件，弹出对话框显示图片
                dialog = QDialog(self.root)
                dialog.setWindowTitle("图片查看器")
                layout = QVBoxLayout()
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    label = QLabel()
                    label.setPixmap(pixmap.scaledToWidth(800))  # 可以根据需要调整显示大小
                    layout.addWidget(label)
                    dialog.setLayout(layout)
                    dialog.exec_()
                else:
                    self.file_content_view.setPlainText("无法加载图片。")
            else:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        self.file_content_view.setPlainText(content)
                except Exception as e:
                    self.file_content_view.setPlainText(f"Error reading file: {e}")

    def show_context_menu(self, position):
        index = self.tree_view.indexAt(position)
        if index.isValid():
            menu = QMenu(self.tree_view)
            copy_action = QAction("复制", self.tree_view)
            copy_action.triggered.connect(lambda: self.copy_file(index))
            menu.addAction(copy_action)

            cut_action = QAction("剪切", self.tree_view)
            cut_action.triggered.connect(lambda: self.cut_file(index))
            menu.addAction(cut_action)

            paste_action = QAction("粘贴", self.tree_view)
            paste_action.triggered.connect(lambda: self.paste_file(index))
            menu.addAction(paste_action)

            rename_action = QAction("重命名", self.tree_view)
            rename_action.triggered.connect(lambda: self.rename_file(index))
            menu.addAction(rename_action)

            delete_action = QAction("删除", self.tree_view)
            delete_action.triggered.connect(lambda: self.delete_file(index))
            menu.addAction(delete_action)

            menu.exec_(self.tree_view.viewport().mapToGlobal(position))

    def delete_file(self, index):
        file_path = self.file_model.filePath(index)
        reply = QMessageBox.question(self.root, '确认删除', f'你确定要删除 {file_path} 吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                self.file_model.setRootPath(self.file_model.rootPath())
                QMessageBox.information(self.root, '成功', f'{file_path} 已删除。')
            except Exception as e:
                QMessageBox.warning(self.root, '错误', f'删除 {file_path} 时出错: {e}')

    def rename_file(self, index):
        file_path = self.file_model.filePath(index)
        new_name, ok = QInputDialog.getText(self.root, '重命名', '输入新的文件名:', text=os.path.basename(file_path))
        if ok and new_name:
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            try:
                os.rename(file_path, new_path)
                self.file_model.setRootPath(self.file_model.rootPath())
                QMessageBox.information(self.root, '成功', f'{file_path} 已重命名为 {new_path}。')
            except Exception as e:
                QMessageBox.warning(self.root, '错误', f'重命名 {file_path} 时出错: {e}')

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        print('dropEvent')
        target_index = self.tree_view.indexAt(event.pos())
        target_path = self.file_model.filePath(target_index)
        if os.path.isdir(target_path):
            mime_data = event.mimeData()
            if mime_data.hasUrls():
                for url in mime_data.urls():
                    source_path = url.toLocalFile()
                    try:
                        # 确保目标路径存在
                        if not os.path.exists(target_path):
                            os.makedirs(target_path)
                        # 移动文件
                        shutil.move(source_path, os.path.join(target_path, os.path.basename(source_path)))
                        self.file_model.setRootPath(self.file_model.rootPath())
                    except Exception as e:
                        QMessageBox.warning(self.root, '错误', f'移动 {source_path} 到 {target_path} 时出错: {e}')
        event.acceptProposedAction()

    def copy_file(self, index):
        global copied_paths
        file_path = self.file_model.filePath(index)
        copied_paths = [file_path]
        QMessageBox.information(self.root, '提示', f'{file_path} 已复制。')

    def cut_file(self, index):
        global cut_paths
        file_path = self.file_model.filePath(index)
        cut_paths = [file_path]
        QMessageBox.information(self.root, '提示', f'{file_path} 已剪切。')

    def paste_file(self, index):
        global copied_paths, cut_paths
        target_path = self.file_model.filePath(index)
        if os.path.isdir(target_path):
            for path in copied_paths:
                try:
                    if os.path.isfile(path):
                        shutil.copy2(path, os.path.join(target_path, os.path.basename(path)))
                    elif os.path.isdir(path):
                        shutil.copytree(path, os.path.join(target_path, os.path.basename(path)))
                    QMessageBox.information(self.root, '成功', f'{path} 已复制到 {target_path}。')
                except Exception as e:
                    QMessageBox.warning(self.root, '错误', f'复制 {path} 到 {target_path} 时出错: {e}')
            for path in cut_paths:
                try:
                    if os.path.isfile(path):
                        shutil.move(path, os.path.join(target_path, os.path.basename(path)))
                    elif os.path.isdir(path):
                        shutil.move(path, os.path.join(target_path, os.path.basename(path)))
                    QMessageBox.information(self.root, '成功', f'{path} 已移动到 {target_path}。')
                except Exception as e:
                    QMessageBox.warning(self.root, '错误', f'移动 {path} 到 {target_path} 时出错: {e}')
            copied_paths = []
            cut_paths = []
            self.file_model.setRootPath(self.file_model.rootPath())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)
        self.explore = Explore(self)
        root_path = os.path.expanduser("~")
        self.explore.init_file_browser(root_path)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
    
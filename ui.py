# ui.py

import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from file_operations import load_paths, add_path, remove_path, Watcher


# 경로 관리 윈도우 
class PathManagementWindow:
    def __init__(self, watchers):
        self.app = QApplication(sys.argv)
        self.watchers = watchers

        self.window = QWidget()
        self.window.setWindowTitle("경로 관리")
        self.window.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.table = QTableWidget(self.window)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["경로", "하위 감시 여부", "삭제"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.update_table()

        layout.addWidget(self.table)

        self.add_button = QPushButton("경로 추가", self.window)
        self.add_button.clicked.connect(self.add_path_ui)
        layout.addWidget(self.add_button)

        self.window.setLayout(layout)
        self.window.show()

        self.start_initial_watching()  # 기존 경로에 대한 감시 시작

        sys.exit(self.app.exec_())

    def update_table(self):
        # 경로 목록을 테이블에 업데이트
        paths = load_paths()
        self.table.setRowCount(len(paths))

        for row, path in enumerate(paths):
            path_item = QTableWidgetItem(path["path"])
            path_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, path_item)

            recursive_text = "O" if path["recursive"] else "X"
            recursive_item = QTableWidgetItem(recursive_text)
            recursive_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, recursive_item)

            delete_button = QPushButton("삭제")
            delete_button.clicked.connect(lambda _, path=path: self.remove_path_ui(path))
            self.table.setCellWidget(row, 2, delete_button)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, header.Stretch)
        header.setSectionResizeMode(1, header.Stretch)
        header.setSectionResizeMode(2, header.Stretch)

    # 기존 경로에 대한 감시 시작
    def start_initial_watching(self):
        paths = load_paths()
        for path in paths:
            if path["path"] not in self.watchers:
                watcher = Watcher(path["path"], path["recursive"])
                watcher.run()
                self.watchers[path["path"]] = watcher

    # 경로 추가
    def add_path_ui(self):
        new_path = QFileDialog.getExistingDirectory(None, "경로 선택", os.path.expanduser("~"))
        
        if new_path:
            recursive = self.ask_recursive_ui()
            try:
                add_path(new_path, recursive)
                self.update_table()
                if new_path not in self.watchers:
                    watcher = Watcher(new_path, recursive)
                    watcher.run()
                    self.watchers[new_path] = watcher
            except ValueError:
                QMessageBox.warning(self.window, "경고", "이미 추가된 경로입니다.")

    # 경로 제거
    def remove_path_ui(self, path):
        remove_path(path["path"])
        self.update_table()
        if path["path"] in self.watchers:
            self.watchers[path["path"]].stop()
            del self.watchers[path["path"]]

    # 하위 경로 감시 여부
    def ask_recursive_ui(self):
        reply = QMessageBox.question(self.window, '하위 감시 여부', '하위 폴더까지 감시하시겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes

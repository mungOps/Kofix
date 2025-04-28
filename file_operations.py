# file_operations.py

import os
import json
import unicodedata
import rumps
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

BASE_DIR = os.path.join(os.path.expanduser("~"), ".kofix")
PATH_FILE = os.path.join(BASE_DIR, "kofix.json")

def load_paths():
    if not os.path.exists(PATH_FILE):
        return []
    with open(PATH_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_paths(paths):
    with open(PATH_FILE, "w", encoding="utf-8") as f:
        json.dump(paths, f, indent=2, ensure_ascii=False)

def add_path(new_path, recursive=True):
    paths = load_paths()
    if any(p["path"] == new_path for p in paths):
        raise ValueError("이미 추가된 경로입니다.")
    paths.append({"path": new_path, "recursive": recursive})
    save_paths(paths)

def remove_path(target_path):
    paths = load_paths()
    paths = [p for p in paths if p["path"] != target_path]
    save_paths(paths)

# NFC 유니코드 형식 변환
def normalize_path(path: str):
    directory, name = os.path.split(path)
    normalized_name = unicodedata.normalize('NFC', name)
    if len(name) == len(normalized_name):
        return

    normalized_path = os.path.join(directory, normalized_name)
    os.rename(path, normalized_path)

# NFC 유니토브 형식 변환 / 디렉토리
def normalize_filenames_in_directory(directory):
    for dir_path, child_dir_names, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dir_path, filename)
            normalize_path(str(file_path))
        for dir_name in child_dir_names:
            child_dir_path = os.path.join(dir_path, dir_name)
            normalize_path(str(child_dir_path))
        break

# 변경 파일 감시
class Watcher:
    observer: Observer | None = None
    timer: rumps.Timer | None = None

    def __init__(self, directory_to_watch, recursive=True):
        self.directory_to_watch = directory_to_watch
        self.recursive = recursive  # Add recursive attribute to handle the flag

    def run(self):
        event_handler = Handler()

        if self.observer:
            self.observer.stop()
        self.observer = Observer()
        self.observer.schedule(event_handler, self.directory_to_watch, recursive=self.recursive)  # Use recursive flag here
        self.observer.start()

        def _maintainer(timer: rumps.Timer):
            if self.observer.is_alive():
                self.observer.join(1)

        self.timer = rumps.Timer(_maintainer, 1)
        self.timer.start()

    def stop(self):
        try:
            self.observer.stop()
            self.observer.join()
        except Exception as e:
            print(f"감시 종료 중 오류 발생: {e}")
        finally:
            if self.timer:
                self.timer.stop()


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.event_type in ['created', 'modified', 'moved']:
            normalize_filenames_in_directory(event.src_path if event.event_type != 'moved' else event.dest_path)

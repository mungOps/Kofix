# main.py

import rumps
from ui import PathManagementWindow
from file_operations import Watcher

class KofixApp(rumps.App):
    def __init__(self):
        super().__init__("Kofix", icon="resources/icon.png")
        self.menu = [
            rumps.MenuItem("경로관리", callback=self.open_path_management),
        ]
        self.watchers = {}

    def open_path_management(self, _):
        PathManagementWindow(self.watchers)

    def quit_app(self, _):
        self.quit()

if __name__ == "__main__":
    app = KofixApp()
    app.run()

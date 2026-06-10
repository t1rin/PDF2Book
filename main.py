import dearpygui.dearpygui as dpg

from core import PDFImposer
from ui import *


class PDF2BookApp:
    def __init__(self):
        self.pdf_path = None
        self.pdf_imposer = PDFImposer()

        self.theme = conf.selected_theme
        self.current_page = 1
        
    def log_message(self, msg=None):
        if msg: dpg.set_value("log_output", msg)
        else: dpg.set_value("log_output", "")

    def run(self):
        dpg.create_context()
        
        dpg.create_viewport(**conf.viewport_options)

        create_main_window(self)
        register_callbacks(self)
        register_keyboards(self)
        register_themes(self)
        
        dpg.set_primary_window("primary_window", True)
        
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


if __name__ == "__main__":
    app = PDF2BookApp()
    app.run()
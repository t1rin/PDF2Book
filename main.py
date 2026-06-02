import dearpygui.dearpygui as dpg

from ui.main_window import create_main_window
from ui.callbacks import register_callbacks
from ui.themes import apply_theme
import ui.config as conf 


class PDF2BookApp:
    def __init__(self):
        self.pdf_path = None
        
    def run(self):
        dpg.create_context()
        
        dpg.create_viewport(**conf.viewport_options)

        create_main_window(self)
        #register_callbacks(self)
        apply_theme()
        
        dpg.set_primary_window("primary_window", True)

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


if __name__ == "__main__":
    app = PDF2BookApp()
    app.run()
import dearpygui.dearpygui as dpg

from core import PDFImposer
from ui.visualization import Scene
from ui.config import MODE
import ui


class PDF2BookApp:
    def __init__(self):
        self.pdf_path = None
        self.pdf_imposer = PDFImposer()

        self.mode = MODE.PAGE
        self.theme = ui.conf.selected_theme
        self.font = ui.conf.selected_font
        self.pw_left = ui.conf.parametrs_window_on_the_left
        self.scale = ui.conf.scale

        self.scene = Scene()

        self.is_indexation = False
        self.is_split_file = False
        self.current_page = 1

        self._old_size_drawlist = None
        
    def log_message(self, msg=None):
        if msg: dpg.set_value("log_output", msg)
        else: dpg.set_value("log_output", "")

    def run(self):
        dpg.create_context()

        dpg.create_viewport(**ui.conf.viewport_options)

        dpg.set_viewport_resize_callback(self.on_viewport_resize)
        dpg.set_exit_callback(self.on_exit)

        ui.create_main_window(self)
        ui.register_callbacks(self)
        ui.register_mouse_handlers(self)
        ui.register_keyboards(self)
        ui.register_themes(self)
        ui.create_drag_and_drop(self)
        
        self.scene.update()

        dpg.setup_dearpygui()
        dpg.show_viewport()
        
        while dpg.is_dearpygui_running():
            self.on_frame()
            dpg.render_dearpygui_frame()

        dpg.destroy_context()

    def on_frame(self):
        if dpg.get_frame_count() < 25:
            ui.resize_update(self)
        else:
            showed = self.pdf_imposer.is_processing()
            if dpg.does_item_exist("loading_window"):
                dpg.configure_item("loading_window", show=showed)

            size_drawlist = dpg.get_item_rect_size("drawlist_window")
            if self._old_size_drawlist is None:
                self._old_size_drawlist = size_drawlist
                return
            if self._old_size_drawlist != size_drawlist:
                padding = 2 * ui.conf.padding_drawlist
                dpg.configure_item("drawlist_3d", 
                                   width=size_drawlist[0]-padding,
                                   height=size_drawlist[1]-padding)
    
    def on_viewport_resize(self):
        ui.resize_update(self)

    def on_exit(self):
        ui.conf.selected_font = self.font
        ui.conf.selected_theme = self.theme
        ui.conf.parametrs_window_on_the_left = self.pw_left
        ui.conf.scale = self.scale
        ui.conf.save()
        print("Завершение...")
        
        if self.pdf_imposer:
            del self.pdf_imposer
        dpg.stop_dearpygui()

def main():
    app = PDF2BookApp()
    app.run()


if __name__ == "__main__":
    main()
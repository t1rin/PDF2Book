import dearpygui.dearpygui as dpg

from core import PDFImposer
from ui.visualization import Scene
from ui.textures import TextureManager
from ui.themes import ThemeManager
from ui.config import MODE
import ui


class PDF2BookApp:
    def __init__(self):
        self.pdf_path = None
        self.mode = MODE.PREVIEW

        self.theme = ui.conf.selected_theme
        self.font = ui.conf.selected_font
        self.title_font = ui.conf.title_font
        self.pw_left = ui.conf.parametrs_window_on_the_left
        self.scale = ui.conf.scale

        self.pdf_imposer = PDFImposer()
        self.texture_manager = None
        self.theme_manager = None
        self.scene = None

        self.is_indexation = False
        self.is_split_file = False
        self.current_page = 1

        self._old_size_drawlist = None
        self._processing = None

    def initialize(self):
        self.theme_manager = ThemeManager(self)
        self.texture_manager = TextureManager(self)
        self.scene = Scene(self)

    def message(self, content=None, mood=None, sep="\n\n"):
        color = None
        if mood == True:
            color = (50, 150, 100)
        if mood == False:
            color = (200, 50, 50)
        dpg.configure_item("log_output", color=color)

        if isinstance(content, str):
            message = content
        else:
            message = ""

        if isinstance(content, list) and all([isinstance(msg, str) 
                                              for msg in content]):
            for i in range(len(content)):
                message += content[i] + sep

        dpg.set_value("log_output", message)

    def run(self):
        dpg.create_context()

        dpg.create_viewport(**ui.conf.viewport_options)

        dpg.set_viewport_resize_callback(self.on_viewport_resize)
        dpg.set_exit_callback(self.on_exit)

        self.create_ui()

        dpg.setup_dearpygui()
        dpg.show_viewport()
        
        while dpg.is_dearpygui_running():
            self.on_frame()
            dpg.render_dearpygui_frame()

        dpg.destroy_context()

    def create_ui(self):
        self.initialize()

        to_delete = ["primary_window", "loading_window", "context_menu",
                     "split_file_checkbox", "drawlist_window", "plot_window"]
        for item in to_delete:
            if dpg.does_item_exist(item):
                dpg.delete_item(item)

        ui.create_main_window(self)
        ui.register_callbacks(self)
        ui.register_mouse_handlers(self)
        ui.register_keyboards(self)
        ui.create_drag_and_drop(self)

        self.theme_manager.update()
        self.scene.update()

    def on_frame(self):
        if dpg.get_frame_count() < 25:
            ui.resize_update(self)
        else:
            show = self._processing or self.pdf_imposer.is_processing()
            if dpg.does_item_exist("loading_window"):
                dpg.configure_item("loading_window", show=show)

            if dpg.does_item_exist("drawlist_window"):
                size_drawlist = dpg.get_item_rect_size("drawlist_window")
                if self._old_size_drawlist is None:
                    self._old_size_drawlist = size_drawlist
                    return
                if self._old_size_drawlist != size_drawlist:
                    padding = 2 * ui.conf.padding_drawlist
                    width = size_drawlist[0] - padding
                    height = size_drawlist[1] - padding
                    dpg.configure_item("drawlist_3d", width=width, height=height)
                    self.scene.set_clip_space(width, height)
                    self.scene.update()
    
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
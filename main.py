import dearpygui.dearpygui as dpg

from core import PDFImposer
from ui.visualization import Scene
from ui.textures import TextureManager
from ui.themes import ThemeManager
from ui.config import MODE
from utils import get_startup_path
import ui


class PDF2BookApp:
    def __init__(self, startup_path=None):
        self.pdf_path = None
        self.mode = MODE.PREVIEW
        self.conf = ui.conf

        self.theme = self.conf.selected_theme
        self.font = self.conf.selected_font
        self.title_font = self.conf.title_font
        self.pw_left = self.conf.parametrs_window_on_the_left

        self._startup_path = startup_path
        self.imposer_options = self.conf.imposer_options
        self.pdf_imposer = PDFImposer(**self.imposer_options)
        self.texture_manager = None
        self.theme_manager = None
        self.scene = None

        self.is_indexation = False
        self.is_split_file = False
        self.current_page = 1

        self.need_reload = None
        self._old_size_drawlist = None
        self._processing = None

    def initialize(self):
        self.theme_manager = ThemeManager(self)
        self.texture_manager = TextureManager(self)
        self.scene = Scene(self)

    def message(self, content=None, mood=None, sep="\n\n"):
        color = None
        if mood == True:
            color = self.conf.themes[self.theme]["positive_color"]
        if mood == False:
            color = self.conf.themes[self.theme]["negative_color"]
        dpg.configure_item("log_output", color=color)

        if isinstance(content, str):
            message = content
        else:
            message = ""

        if isinstance(content, list) and all([isinstance(msg, str) 
                                              for msg in content]):
            for i in range(len(content)):
                message += content[i] + sep

        if dpg.does_item_exist("log_output"):
            dpg.set_value("log_output", message)

    def run(self):
        dpg.create_context()

        dpg.create_viewport(**self.conf.viewport_options)

        dpg.set_viewport_resize_callback(self.on_viewport_resize)
        dpg.set_exit_callback(self.on_exit)

        self.initialize()
        self.create_ui()
        self.load_startup_path()

        dpg.setup_dearpygui()
        dpg.show_viewport()
        
        while dpg.is_dearpygui_running():
            self.on_frame()
            dpg.render_dearpygui_frame()

        dpg.destroy_context()

    def restart(self) -> None:
        self.need_reload = True
        dpg.stop_dearpygui()

    def create_ui(self):
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

    def load_startup_path(self):
        if self._startup_path:
            path = self._startup_path
            ui.callbacks.load_file(self, path)

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
                    padding = 2 * self.conf.padding_drawlist
                    width = size_drawlist[0] - padding
                    height = size_drawlist[1] - padding
                    dpg.configure_item("drawlist_child_window", width=width, height=height)
                    dpg.configure_item("drawlist_3d", width=width, height=height)
                    self.scene.set_clip_space(width, height)
                    self.scene.update()
    
    def on_viewport_resize(self):
        ui.resize_update(self)

    def on_exit(self):
        self.conf.selected_font = self.font
        self.conf.selected_theme = self.theme
        self.conf.parametrs_window_on_the_left = self.pw_left
        self.conf.save()

        if not self.need_reload:
            print("Завершение...")
        
        if self.pdf_imposer:
            del self.pdf_imposer
        if self.texture_manager:
            self.texture_manager.delete_textures()
        dpg.stop_dearpygui()


def main():
    startup_path = get_startup_path()
    app = PDF2BookApp(startup_path=startup_path)
    app.run()

    if app.need_reload:
        import sys, subprocess

        subprocess.Popen([sys.executable, *sys.argv])
        sys.exit(0)


if __name__ == "__main__":
    main()
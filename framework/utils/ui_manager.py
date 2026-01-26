import imgui
import glfw
from imgui.integrations.glfw import GlfwRenderer

class UIManager:
    def __init__(self, window):
        """
        Initializes ImGui context, GlfwRenderer, and input callbacks.
        :param window: The GLFW window object.
        """
        self.window = window
        
        # 1. Create Context
        imgui.create_context()
        self.impl = GlfwRenderer(window, attach_callbacks=False)
        
        # 2. Setup Input Callbacks (Wrappers)
        self._setup_callbacks()

    def _setup_callbacks(self):
        """Overrides GLFW callbacks to capture input for ImGui."""
        
    def setup_input_chaining(self, glwindow_wrapper):
        """
        Sets up GLFW callbacks to route input to ImGui first, then to the glwindow_wrapper.
        """
        def key_callback_wrapper(window, key, scancode, action, mods):
            self.impl.keyboard_callback(window, key, scancode, action, mods)
            if not imgui.get_io().want_capture_keyboard:
                glwindow_wrapper.key_callback(window, key, scancode, action, mods)

        def mouse_button_callback_wrapper(window, button, action, mods):
            self.impl.mouse_callback(window, button, action, mods)
            if not imgui.get_io().want_capture_mouse:
                glwindow_wrapper.mouse_button_callback(window, button, action, mods)

        def scroll_callback_wrapper(window, x_offset, y_offset):
            self.impl.scroll_callback(window, x_offset, y_offset)
            if not imgui.get_io().want_capture_mouse:
                glwindow_wrapper.scroll_callback(window, x_offset, y_offset)

        def char_callback_wrapper(window, char):
            self.impl.char_callback(window, char)
            
        glfw.set_key_callback(self.window, key_callback_wrapper)
        glfw.set_mouse_button_callback(self.window, mouse_button_callback_wrapper)
        glfw.set_scroll_callback(self.window, scroll_callback_wrapper)
        glfw.set_char_callback(self.window, char_callback_wrapper)

    def render(self, draw_callback, *args, **kwargs):
        """
        Standard render loop: Process Inputs -> New Frame -> Callback -> Render -> Draw Data.
        """
        self.impl.process_inputs()
        imgui.new_frame()
        
        if draw_callback:
            draw_callback(*args, **kwargs)
            
        imgui.render()
        self.impl.render(imgui.get_draw_data())
        
    def shutdown(self):
        self.impl.shutdown()

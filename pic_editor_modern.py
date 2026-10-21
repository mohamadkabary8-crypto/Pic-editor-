import os
import time
from functools import partial

from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

from PIL import (
    Image, ImageOps, ImageEnhance, ImageFilter,
    ImageDraw, ImageFont
)

try:
    from plyer import filechooser
    PLYER_AVAILABLE = True
except ImportError:
    filechooser = None
    PLYER_AVAILABLE = False


APP_NAME = "Pic Editor"

BG = (0.045, 0.05, 0.09, 1)
PANEL = (0.09, 0.105, 0.17, 1)
PANEL_LIGHT = (0.13, 0.15, 0.23, 1)
BUTTON = (0.15, 0.17, 0.27, 1)
ACCENT = (0.48, 0.31, 0.98, 1)
ACCENT_BLUE = (0.20, 0.42, 0.92, 1)
MINT = (0.15, 0.72, 0.60, 1)
TEXT_COLOR = (0.96, 0.97, 1, 1)
MUTED = (0.66, 0.69, 0.80, 1)

Window.clearcolor = BG


class ModernButton(Button):
    def __init__(self, **kwargs):
        self.normal_color = kwargs.pop("normal_color", BUTTON)
        self.pressed_color = kwargs.pop("pressed_color", ACCENT_BLUE)
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("color", TEXT_COLOR)
        kwargs.setdefault("font_size", "13sp")
        kwargs.setdefault("bold", True)
        super().__init__(**kwargs)

        with self.canvas.before:
            self.bg_color = Color(*self.normal_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(14)]
            )

        self.bind(pos=self.update_bg, size=self.update_bg)
        self.bind(state=self.animate_state)

    def update_bg(self, *_):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def animate_state(self, *_):
        Animation.cancel_all(self.bg_color)
        target = self.pressed_color if self.state == "down" else self.normal_color
        Animation(rgba=target, duration=0.13, t="out_quad").start(self.bg_color)


def make_button(text, callback=None, height=46, color=BUTTON):
    button = ModernButton(
        text=text,
        size_hint_y=None,
        height=dp(height),
        normal_color=color,
        pressed_color=ACCENT_BLUE
    )
    if callback:
        button.bind(on_release=callback)
    return button


def make_label(text, height=30, size=14, color=TEXT_COLOR):
    return Label(
        text=text,
        size_hint_y=None,
        height=dp(height),
        font_size=f"{size}sp",
        color=color,
        halign="center",
        valign="middle"
    )


def add_rounded_background(widget, color=PANEL, radius=20):
    with widget.canvas.before:
        Color(*color)
        rect = RoundedRectangle(
            pos=widget.pos, size=widget.size, radius=[dp(radius)]
        )

    def update(*_):
        rect.pos = widget.pos
        rect.size = widget.size

    widget.bind(pos=update, size=update)
    return rect


class Spacer(Widget):
    def __init__(self, height=None, **kwargs):
        if height is not None:
            kwargs["size_hint_y"] = None
            kwargs["height"] = dp(height)
        else:
            kwargs["size_hint_y"] = 1
        super().__init__(**kwargs)


class PicEditorApp(App):
    def build(self):
        self.title = APP_NAME
        self.data_dir = self.user_data_dir
        os.makedirs(self.data_dir, exist_ok=True)

        self.manager = ScreenManager(
            transition=SlideTransition(duration=0.18)
        )
        self.manager.add_widget(HomeScreen(name="home"))
        self.manager.add_widget(GalleryScreen(name="gallery"))
        self.manager.add_widget(EditorScreen(name="editor"))
        return self.manager


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(24), dp(20), dp(16)],
            spacing=dp(12)
        )
        add_rounded_background(root, BG, 0)

        root.add_widget(Label(
            text="[b]PIC [color=B49AFF]EDITOR[/color][/b]",
            markup=True, font_size="30sp",
            size_hint_y=None, height=dp(66),
            color=TEXT_COLOR
        ))
        root.add_widget(make_label(
            "YOUR CREATIVE PHOTO STUDIO", 30, 12, MUTED
        ))
        root.add_widget(Spacer(height=12))

        card = BoxLayout(
            orientation="vertical", padding=dp(18),
            spacing=dp(10), size_hint_y=None, height=dp(205)
        )
        add_rounded_background(card, PANEL, 22)
        card.add_widget(Label(
            text="[b]Make every photo special[/b]",
            markup=True, font_size="19sp", color=TEXT_COLOR
        ))
        card.add_widget(make_label(
            "Edit, enhance and create.", 28, 13, MUTED
        ))
        card.add_widget(make_button(
            "＋   CHOOSE A PHOTO",
            self.open_gallery, 54, ACCENT
        ))
        root.add_widget(card)

        root.add_widget(Spacer(height=8))
        root.add_widget(Label(
            text="[b]YOUR WORKSPACE[/b]",
            markup=True, size_hint_y=None,
            height=dp(32), font_size="15sp",
            color=TEXT_COLOR, halign="left"
        ))
        root.add_widget(make_button(
            "▣   OPEN PHOTO GALLERY",
            self.open_gallery, 50, ACCENT_BLUE
        ))
        root.add_widget(make_button(
            "ⓘ   ABOUT PIC EDITOR",
            self.about, 46, PANEL_LIGHT
        ))
        root.add_widget(Spacer())
        root.add_widget(make_label(
            "POWERED BY KIVY + PILLOW", 24, 10, MUTED
        ))
        self.add_widget(root)

    def open_gallery(self, *_):
        self.manager.current = "gallery"
        self.manager.get_screen("gallery").refresh_files()

    def about(self, *_):
        show_message(
            "Pic Editor",
            "A mobile photo editor built with Python, Kivy and Pillow."
        )


class GalleryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=dp(10), spacing=dp(9)
        )
        add_rounded_background(root, BG, 0)

        root.add_widget(Label(
            text="[b]PHOTO GALLERY[/b]",
            markup=True, size_hint_y=None,
            height=dp(42), font_size="21sp",
            color=TEXT_COLOR
        ))

        header = BoxLayout(
            size_hint_y=None, height=dp(46), spacing=dp(7)
        )
        header.add_widget(make_button("BACK", self.go_home, 44, PANEL_LIGHT))
        header.add_widget(make_button("REFRESH", self.refresh_files, 44, ACCENT_BLUE))
        header.add_widget(make_button("BROWSE", self.browse_files, 44, ACCENT))
        root.add_widget(header)

        self.status = make_label("Choose a photo to edit.", 34, 12, MUTED)
        root.add_widget(self.status)

        scroll = ScrollView()
        self.grid = GridLayout(
            cols=1, spacing=dp(7), padding=dp(3),
            size_hint_y=None
        )
        self.grid.bind(minimum_height=self.grid.setter("height"))
        scroll.add_widget(self.grid)
        root.add_widget(scroll)
        self.add_widget(root)

    def go_home(self, *_):
        self.manager.current = "home"

    def search_dirs(self):
        candidates = [
            "/storage/emulated/0/DCIM/Camera",
            "/storage/emulated/0/Pictures",
            "/storage/emulated/0/Download",
            "/storage/emulated/0/DCIM",
            "/storage/emulated/0"
        ]
        return [p for p in candidates if os.path.isdir(p)]

    def refresh_files(self, *_):
        self.grid.clear_widgets()
        found = []
        extensions = (".jpg", ".jpeg", ".png", ".webp", ".bmp")

        for folder in self.search_dirs():
            try:
                for name in os.listdir(folder):
                    path = os.path.join(folder, name)
                    if (
                        os.path.isfile(path)
                        and name.lower().endswith(extensions)
                        and path not in found
                    ):
                        found.append(path)
            except (PermissionError, OSError) as error:
                print("Cannot read folder:", folder, error)

        try:
            found.sort(key=os.path.getmtime, reverse=True)
        except OSError:
            pass

        for path in found:
            self.grid.add_widget(make_button(
                "▧   " + os.path.basename(path),
                partial(self.open_image, path),
                height=52, color=PANEL_LIGHT
            ))

        self.status.text = (
            f"{len(found)} image(s) found" if found else
            "No images found. Check permissions or tap BROWSE."
        )

    def browse_files(self, *_):
        if not PLYER_AVAILABLE:
            show_message(
                "File browser",
                "Plyer is not available. Check Android file permissions "
                "or install Plyer if supported by your Pydroid setup."
            )
            return
        try:
            filechooser.open_file(
                on_selection=self.on_file_selected,
                filters=["*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp"]
            )
        except Exception as error:
            show_message("Browse error", str(error))

    def on_file_selected(self, selection):
        if selection:
            path = selection[0]
            if os.path.isfile(path):
                Clock.schedule_once(lambda _dt: self.open_image(path), 0)

    def open_image(self, path, *_):
        try:
            editor = self.manager.get_screen("editor")
            editor.load_image(path)
            if editor.current_img is not None:
                self.manager.current = "editor"
        except Exception as error:
            show_message("Open image error", str(error))


class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.original_img = None
        self.base_img = None
        self.current_img = None
        self.image_path = None
        self.history = []
        self.max_history = 8
        self.pending_update = None

        self.preview_path = os.path.join(
            App.get_running_app().user_data_dir
            if App.get_running_app() else ".",
            "pic_editor_preview.jpg"
        )

        root = BoxLayout(
            orientation="vertical",
            padding=dp(8), spacing=dp(7)
        )
        add_rounded_background(root, BG, 0)

        root.add_widget(Label(
            text="[b]PHOTO WORKSHOP[/b]",
            markup=True, size_hint_y=None,
            height=dp(35), font_size="18sp",
            color=TEXT_COLOR
        ))

        header = BoxLayout(
            size_hint_y=None, height=dp(43), spacing=dp(5)
        )
        header.add_widget(make_button("GALLERY", self.go_gallery, 42, PANEL_LIGHT))
        header.add_widget(make_button("UNDO", self.undo, 42, BUTTON))
        header.add_widget(make_button("RESET", self.reset_image, 42, BUTTON))
        header.add_widget(make_button("SAVE", self.save_image, 42, ACCENT))
        root.add_widget(header)

        preview_panel = BoxLayout(
            padding=dp(5), size_hint_y=1
        )
        add_rounded_background(preview_panel, PANEL, 18)
        self.preview = KivyImage(
            allow_stretch=True, keep_ratio=True
        )
        preview_panel.add_widget(self.preview)
        root.add_widget(preview_panel)

        sliders = BoxLayout(
            orientation="vertical",
            size_hint_y=None, height=dp(132),
            padding=[dp(8), dp(3), dp(8), dp(3)],
            spacing=dp(1)
        )
        add_rounded_background(sliders, PANEL, 16)

        sliders.add_widget(make_label("BRIGHTNESS", 22, 11, MUTED))
        self.brightness = Slider(min=0.2, max=2.0, value=1.0, step=0.05)
        self.brightness.bind(value=self.schedule_adjustment)
        sliders.add_widget(self.brightness)

        sliders.add_widget(make_label("CONTRAST", 22, 11, MUTED))
        self.contrast = Slider(min=0.2, max=2.0, value=1.0, step=0.05)
        self.contrast.bind(value=self.schedule_adjustment)
        sliders.add_widget(self.contrast)

        sliders.add_widget(make_label("SATURATION", 22, 11, MUTED))
        self.saturation = Slider(min=0.0, max=2.0, value=1.0, step=0.05)
        self.saturation.bind(value=self.schedule_adjustment)
        sliders.add_widget(self.saturation)
        root.add_widget(sliders)

        tool_scroll = ScrollView(
            size_hint_y=None, height=dp(112)
        )
        tool_grid = GridLayout(
            cols=3, spacing=dp(6), padding=dp(2),
            size_hint_y=None
        )
        tool_grid.bind(minimum_height=tool_grid.setter("height"))

        actions = [
            ("↻ ROTATE", self.rotate_image),
            ("✂ CROP", self.crop_image),
            ("⇋ FLIP", self.flip_image),
            ("FILTERS", self.show_filters),
            ("ADD TEXT", self.add_text_popup),
            ("SHARPEN", self.sharpen),
            ("BLUR", self.blur),
            ("GRAYSCALE", self.grayscale),
            ("SAVE COPY", self.save_image)
        ]
        for title, callback in actions:
            tool_grid.add_widget(make_button(
                title, callback, 40, PANEL_LIGHT
            ))

        tool_scroll.add_widget(tool_grid)
        root.add_widget(tool_scroll)
        self.add_widget(root)

    def load_image(self, path):
        try:
            with Image.open(path) as source:
                img = ImageOps.exif_transpose(source).convert("RGB")
            img.thumbnail((3000, 3000), Image.Resampling.LANCZOS)

            self.image_path = path
            self.original_img = img.copy()
            self.base_img = img.copy()
            self.current_img = img.copy()
            self.history = []
            self.set_slider_values(1.0, 1.0, 1.0)
            self.update_display()
        except Exception as error:
            self.current_img = None
            show_message("Image error", str(error))

    def set_slider_values(self, brightness, contrast, saturation):
        self.brightness.value = brightness
        self.contrast.value = contrast
        self.saturation.value = saturation

    def get_adjusted_image(self):
        if self.base_img is None:
            return None
        img = self.base_img.copy()
        if self.brightness.value != 1.0:
            img = ImageEnhance.Brightness(img).enhance(self.brightness.value)
        if self.contrast.value != 1.0:
            img = ImageEnhance.Contrast(img).enhance(self.contrast.value)
        if self.saturation.value != 1.0:
            img = ImageEnhance.Color(img).enhance(self.saturation.value)
        return img

    def schedule_adjustment(self, *_):
        if self.base_img is None:
            return
        if self.pending_update is not None:
            self.pending_update.cancel()
        self.pending_update = Clock.schedule_once(self.apply_adjustments, 0.12)

    def apply_adjustments(self, *_):
        self.pending_update = None
        if self.base_img is None:
            return
        try:
            self.current_img = self.get_adjusted_image()
            self.update_display()
        except Exception as error:
            print("Adjustment error:", error)

    def update_display(self):
        if self.current_img is None:
            return
        try:
            self.current_img.save(self.preview_path, "JPEG", quality=86)
            self.preview.source = self.preview_path
            self.preview.reload()
        except Exception as error:
            print("Preview error:", error)

    def push_history(self):
        if self.base_img is None:
            return
        self.history.append(self.base_img.copy())
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def commit_image(self, img):
        if self.base_img is None or img is None:
            return
        self.push_history()
        self.base_img = img.convert("RGB").copy()
        self.current_img = self.base_img.copy()
        self.set_slider_values(1.0, 1.0, 1.0)
        self.update_display()

    def undo(self, *_):
        if not self.history:
            show_message("Undo", "There are no more steps to undo.")
            return
        self.base_img = self.history.pop()
        self.current_img = self.base_img.copy()
        self.set_slider_values(1.0, 1.0, 1.0)
        self.update_display()

    def reset_image(self, *_):
        if self.original_img is None:
            return
        self.base_img = self.original_img.copy()
        self.current_img = self.original_img.copy()
        self.history = []
        self.set_slider_values(1.0, 1.0, 1.0)
        self.update_display()

    def rotate_image(self, *_):
        if self.base_img is not None:
            self.commit_image(self.get_adjusted_image().rotate(270, expand=True))

    def flip_image(self, *_):
        if self.base_img is not None:
            self.commit_image(ImageOps.mirror(self.get_adjusted_image()))

    def crop_image(self, *_):
        if self.base_img is None:
            return
        img = self.get_adjusted_image()
        width, height = img.size
        left, top = int(width * 0.08), int(height * 0.08)
        right, bottom = int(width * 0.92), int(height * 0.92)
        if right > left and bottom > top:
            self.commit_image(img.crop((left, top, right, bottom)))

    def grayscale(self, *_):
        if self.base_img is not None:
            self.commit_image(ImageOps.grayscale(
                self.get_adjusted_image()
            ).convert("RGB"))

    def sharpen(self, *_):
        if self.base_img is not None:
            img = self.get_adjusted_image().filter(
                ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)
            )
            self.commit_image(img)

    def blur(self, *_):
        if self.base_img is not None:
            self.commit_image(
                self.get_adjusted_image().filter(
                    ImageFilter.GaussianBlur(radius=2)
                )
            )

    def show_filters(self, *_):
        filters = [
            ("Original", "original"), ("Sepia", "sepia"),
            ("Vivid", "vivid"), ("Warm", "warm"),
            ("Cool", "cool"), ("Invert", "invert"),
            ("Posterize", "posterize"), ("Contour", "contour"),
            ("Emboss", "emboss"), ("Find Edges", "edges"),
            ("Soft Glow", "glow"), ("Solarize", "solarize"),
            ("Vintage", "vintage"), ("Smooth", "smooth"),
            ("Detail", "detail")
        ]

        content = BoxLayout(
            orientation="vertical", padding=dp(10), spacing=dp(8)
        )
        scroll = ScrollView()
        grid = GridLayout(
            cols=2, spacing=dp(7), size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter("height"))

        popup = Popup(
            title="PHOTO FILTERS", content=content,
            size_hint=(0.92, 0.8), background_color=PANEL
        )
        for title, mode in filters:
            grid.add_widget(make_button(
                title, partial(self.apply_filter, mode, popup),
                45, PANEL_LIGHT
            ))
        scroll.add_widget(grid)
        content.add_widget(scroll)
        content.add_widget(make_button(
            "CLOSE", lambda *_: popup.dismiss(), 44, ACCENT
        ))
        popup.open()

    def apply_filter(self, mode, popup, *_):
        popup.dismiss()
        if self.base_img is None:
            return
        try:
            img = self.get_adjusted_image()

            if mode == "original":
                img = self.original_img.copy()
            elif mode == "sepia":
                img = ImageOps.colorize(
                    ImageOps.grayscale(img), "#38251b", "#f4dfb5"
                )
            elif mode == "vivid":
                img = ImageEnhance.Color(img).enhance(1.65)
                img = ImageEnhance.Contrast(img).enhance(1.08)
            elif mode == "warm":
                r, g, b = img.split()
                r = r.point(lambda p: min(255, int(p * 1.10)))
                b = b.point(lambda p: int(p * 0.90))
                img = Image.merge("RGB", (r, g, b))
            elif mode == "cool":
                r, g, b = img.split()
                r = r.point(lambda p: int(p * 0.90))
                b = b.point(lambda p: min(255, int(p * 1.10)))
                img = Image.merge("RGB", (r, g, b))
            elif mode == "invert":
                img = ImageOps.invert(img)
            elif mode == "posterize":
                img = ImageOps.posterize(img, 4)
            elif mode == "contour":
                img = img.filter(ImageFilter.CONTOUR)
            elif mode == "emboss":
                img = img.filter(ImageFilter.EMBOSS)
            elif mode == "edges":
                img = img.filter(ImageFilter.FIND_EDGES)
            elif mode == "glow":
                img = Image.blend(
                    img, img.filter(ImageFilter.GaussianBlur(4)), 0.35
                )
            elif mode == "solarize":
                img = ImageOps.solarize(img, threshold=128)
            elif mode == "vintage":
                gray = ImageOps.grayscale(img)
                sepia = ImageOps.colorize(gray, "#352319", "#e8c998")
                img = ImageEnhance.Contrast(sepia).enhance(0.9)
            elif mode == "smooth":
                img = img.filter(ImageFilter.SMOOTH_MORE)
            elif mode == "detail":
                img = img.filter(ImageFilter.DETAIL)

            self.commit_image(img)
        except Exception as error:
            show_message("Filter error", str(error))

    def add_text_popup(self, *_):
        if self.base_img is None:
            return

        content = BoxLayout(
            orientation="vertical", padding=dp(10), spacing=dp(8)
        )
        text_input = TextInput(
            hint_text="Enter text or watermark",
            multiline=False, size_hint_y=None, height=dp(48)
        )
        content.add_widget(text_input)

        buttons = BoxLayout(
            size_hint_y=None, height=dp(45), spacing=dp(7)
        )
        popup = Popup(
            title="ADD TEXT", content=content, size_hint=(0.92, 0.36)
        )
        buttons.add_widget(make_button(
            "CANCEL", lambda *_: popup.dismiss(), 44, PANEL_LIGHT
        ))
        buttons.add_widget(make_button(
            "ADD", lambda *_: self.add_text(text_input.text, popup),
            44, ACCENT
        ))
        content.add_widget(buttons)
        popup.open()

    def add_text(self, text, popup):
        popup.dismiss()
        if self.base_img is None or not text.strip():
            return

        img = self.get_adjusted_image()
        draw = ImageDraw.Draw(img)
        font_size = max(18, int(img.width * 0.045))
        font = None

        for path in [
            "/system/fonts/Roboto-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "DejaVuSans.ttf"
        ]:
            try:
                font = ImageFont.truetype(path, font_size)
                break
            except (OSError, IOError):
                pass

        if font is None:
            font = ImageFont.load_default()

        draw.text(
            (int(img.width * 0.05), int(img.height * 0.84)),
            text, fill=(255, 225, 50), font=font,
            stroke_width=2, stroke_fill=(0, 0, 0)
        )
        self.commit_image(img)

    def save_image(self, *_):
        if self.base_img is None:
            show_message("Save", "Open a photo first.")
            return
        try:
            img = self.get_adjusted_image()
            public_dir = "/storage/emulated/0/Pictures/PicEditor"

            if os.path.isdir("/storage/emulated/0/Pictures"):
                output_dir = public_dir
            else:
                output_dir = os.path.join(
                    App.get_running_app().user_data_dir, "PicEditor"
                )
            os.makedirs(output_dir, exist_ok=True)

            filename = "PicEditor_" + time.strftime("%Y%m%d_%H%M%S") + ".jpg"
            path = os.path.join(output_dir, filename)
            img.save(path, "JPEG", quality=95, optimize=True)

            show_message(
                "Saved successfully",
                "Image saved to:\n" + path
            )
        except Exception as error:
            show_message("Save error", str(error))

    def go_gallery(self, *_):
        self.manager.current = "gallery"


def show_message(title, message):
    content = BoxLayout(
        orientation="vertical", padding=dp(12), spacing=dp(10)
    )
    label = Label(
        text=message, color=TEXT_COLOR,
        halign="center", valign="middle"
    )
    label.bind(size=lambda instance, size: setattr(
        instance, "text_size", size
    ))
    content.add_widget(label)

    popup = Popup(
        title=title, content=content,
        size_hint=(0.9, 0.42)
    )
    content.add_widget(make_button(
        "OK", lambda *_: popup.dismiss(), 44, ACCENT
    ))
    popup.open()


if __name__ == "__main__":
    PicEditorApp().run()

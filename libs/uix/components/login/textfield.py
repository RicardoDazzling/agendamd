from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivymd.uix.button import MDButton
from kivymd.uix.textfield import MDTextField

from libs.applibs.utils import ignore_args


class LoginTextField(MDTextField):

    next = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(LoginTextField, self).__init__(
            *args,
            **kwargs
        )
        self.mode = "outlined"
        self.bind(_helper_text_label=self.on_helper_text_label)
        if self._helper_text_label:
            self.on_helper_text_label()

    @ignore_args
    def on_helper_text_label(self):
        self._helper_text_label.bind(text=self._update_helper_text)

    @ignore_args
    def _update_helper_text(self):
        Clock.schedule_once(self._update_helper_text_label)

    @ignore_args
    def _update_helper_text_label(self):
        texture = self._helper_text_label
        canvas_group = self.canvas.before.get_group("helper-text-color")[0]
        color = (
            self.theme_cls.onSurfaceVariantColor
            if not self._helper_text_label.text_color_focus
            else self._helper_text_label.text_color_focus
        ) if not self.error else self._get_error_color()

        @ignore_args
        def update_helper_text():
            helper_text_rectangle = self.canvas.before.children[8]
            helper_text_rectangle.texture = None
            texture.texture_update()
            helper_text_rectangle.size = texture.texture_size
            helper_text_rectangle.texture = texture.texture

        if texture:
            Animation(rgba=color, d=0).start(canvas_group)
            a = Animation(color=color, d=0)
            a.bind(on_complete=update_helper_text)
            a.start(texture)

    def on_focus(self, instance, focus: bool) -> None:
        super(LoginTextField, self).on_focus(instance, focus)
        __icon_name = self._leading_icon.icon.replace("-outline", "")
        self._leading_icon.icon = __icon_name + ("" if self.focus else "-outline")

    def on_text_validate(self) -> None:
        super().on_text_validate()
        if isinstance(self.next, (MDTextField, MDButton)):
            self.next.focus = True

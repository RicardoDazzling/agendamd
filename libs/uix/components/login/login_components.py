from kivy.animation import Animation
from kivy.metrics import dp
from kivy.properties import StringProperty, Clock, ObjectProperty
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldLeadingIcon, MDTextFieldHintText, MDTextFieldHelperText

from libs.uix.components import MDTextFieldTrailingIconButton


class LoginTextField(MDTextField):

    next = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(LoginTextField, self).__init__(
            *args,
            **kwargs
        )
        self.mode = "outlined"
        self.bind(_helper_text_label=self.on_helper_text_label)

    def on_helper_text_label(self, *args):
        self._helper_text_label.bind(text=self._update_helper_text)

    def _update_helper_text(self, *args):
        Clock.schedule_once(self._update_helper_text_label)

    def _update_helper_text_label(self, *args):
        texture = self._helper_text_label
        canvas_group = self.canvas.before.get_group("helper-text-color")[0]
        color = (
            self.theme_cls.onSurfaceVariantColor
            if not self._helper_text_label.text_color_focus
            else self._helper_text_label.text_color_focus
        ) if not self.error else self._get_error_color()

        def update_helper_text(*args):
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

    def on_enter(self) -> None:
        super().on_enter()
        if isinstance(self.next, (MDTextField, MDButton)):
            self.next.focus = True


class LoginPasswordTextField(LoginTextField):

    def __init__(self, **kwargs):
        super(LoginPasswordTextField, self).__init__(
            MDTextFieldTrailingIconButton(icon="eye-off", text_field=self),
            **kwargs
        )
        self.password = True
        self._trailing_icon.bind(on_press=self.show_password)

    def show_password(self, *args):
        if self._trailing_icon.icon == "eye-off":
            self.password = False
            self._trailing_icon.icon = "eye"
        elif self._trailing_icon.icon == "eye":
            self.password = True
            self._trailing_icon.icon = "eye-off"


class LoginFormButton(MDButton):
    def __init__(self, **kwargs):
        super(LoginFormButton, self).__init__(**kwargs)
        self.style = "filled"
        self.theme_width = "Custom"
        self.height = dp(46)
        self.size_hint_x = .5
        self.pos_hint = {"center_x": .5}

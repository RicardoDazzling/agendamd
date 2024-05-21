from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.app import App


class KLCheckbox(MDBoxLayout):
    def __init__(self, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        self.adaptive_height = True
        self.app = App.get_running_app()
        self.checkbox = MDCheckbox(active=self.app.DB.keep)
        self.checkbox.bind(active=self.on_checkbox_active)
        self.label = MDLabel(
            text="Permanecer logado",
            adaptive_height=self.adaptive_height,
            padding_x=dp(12),
            pos_hint={"center_y": .5}
        )
        self.add_widget(self.checkbox)
        self.add_widget(self.label)

    def on_checkbox_active(self, *args):
        self.app.DB.keep = args[1]

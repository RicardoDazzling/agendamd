from kivy.metrics import dp
from kivy.properties import BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from globals import translator as _


class KLCheckbox(MDBoxLayout):

    active = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        self.adaptive_height = True

        self.checkbox = MDCheckbox()
        self.checkbox.bind(active=self.setter("active"))
        self.bind(active=self.checkbox.setter("active"))

        self.label = _.bind_translation(MDLabel(
            adaptive_height=self.adaptive_height,
            padding_x=dp(12),
            pos_hint={"center_y": .5}
        ), 'text', "Keep logged in.")
        self.add_widget(self.checkbox)
        self.add_widget(self.label)

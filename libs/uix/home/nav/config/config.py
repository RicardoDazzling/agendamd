from functools import partial
from typing import Optional

from kivy.app import App
from kivy.properties import ObjectProperty
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen

from globals import USERS, CONFIG, translator as _
from libs.applibs.entities import User
from libs.applibs.utils import ignore_instance
from libs.uix.components.config import MouseCaller, ConfigSwitch, ConfigItem
from libs.uix.components.config.password_dialog import PasswordDialog


class ConfigScreen(MDScreen):
    _translations: list[str] = _.translations
    _default_string = f" ({_('Default')})"
    _lbl_name: Optional[MDLabel] = ObjectProperty(None)
    _lbl_email: Optional[MDLabel] = ObjectProperty(None)
    _swt_dark_mode: Optional[ConfigSwitch] = ObjectProperty(None)
    _itm_language: Optional[ConfigItem] = ObjectProperty(None)
    _itm_title: Optional[ConfigItem] = ObjectProperty(None)
    _itm_description: Optional[ConfigItem] = ObjectProperty(None)
    _itm_tag: Optional[ConfigItem] = ObjectProperty(None)

    def __init__(self, **kwargs):
        _.bind(self._update_translations)
        super().__init__(**kwargs)
        self._app = App.get_running_app()
        self._password_dialog = PasswordDialog()
        self._language_dropdown = MDDropdownMenu(
            caller=MouseCaller(), items=[
                {
                    "text": translation,
                    "on_release": partial(self.change_language, translation),
                } for translation in self._translations
            ]
        )

    @staticmethod
    def on_ids(self, value: dict):
        if value:
            self._lbl_name = value.get('lbl_name', None)
            self._lbl_email = value.get('lbl_email', None)
            self._swt_dark_mode = value.get('swt_dark_mode', None)
            self._itm_language = value.get('itm_language', None)
            self._itm_title = value.get('itm_title', None)
            self._itm_description = value.get('itm_description', None)
            self._itm_tag = value.get('itm_tag', None)

    @staticmethod
    def on__lbl_name(self, value: MDLabel):
        if USERS.logged():
            value.text = USERS.name
        USERS.bind(on_name=partial(self.set_label, value))

    @staticmethod
    def on__lbl_email(self, value: MDLabel):
        if USERS.logged():
            value.text = USERS.email
        USERS.bind(on_email=partial(self.set_label, value))

    @staticmethod
    def set_label(instance: MDLabel, value: str):
        instance.text = value

    @ignore_instance
    def on__swt_dark_mode(self, value: ConfigSwitch):
        value.active = CONFIG.dark_mode
        value.bind(active=lambda i, v: self.set_dark_mode(active=v))

    @ignore_instance
    def on__itm_language(self, value: ConfigItem):
        name = "LANGUAGE"
        __current = getattr(_, name.lower())
        if __current == CONFIG.default_config[name.upper()]:
            __current += self._default_string
        value.current = __current
        value.id = 'itm_language'

    @ignore_instance
    def on__itm_title(self, value: ConfigItem):
        value.current = self.get_config('task_max_title_size')
        value.bind(on_edit=self.set_config)
        value.id = 'itm_title'

    @ignore_instance
    def on__itm_description(self, value: ConfigItem):
        value.current = self.get_config('task_max_description_size')
        value.bind(on_edit=self.set_config)
        value.id = 'itm_description'

    @ignore_instance
    def on__itm_tag(self, value: ConfigItem):
        value.current = self.get_config('task_max_tag_size')
        value.bind(on_edit=self.set_config)
        value.id = 'itm_tag'

    _user = User(keep_logged=CONFIG.keep_logged)

    def set_config(self, instance: ConfigItem, value: str):
        __id = instance.id
        if __id not in ['itm_title', 'itm_description', 'itm_tag']:
            raise IndexError(f'Unknown Item id: {__id}')
        __property = ('task_max_title_size' if __id == 'itm_title' else
                      'task_max_description_size' if __id == 'itm_description' else
                      'task_max_tag_size')  # if __id == 'itm_tag'

        setattr(USERS, __property, int(value))

        if int(value) == getattr(self._user, __property):
            instance.current += self._default_string

    def get_config(self, name: str) -> str:
        name = name.lower()
        __current = getattr(USERS.user, name)
        __default = getattr(self._user, name)
        __current = str(__current) + (self._default_string if __current == __default else '')
        return __current

    def change_password(self):
        self._password_dialog.open()

    @staticmethod
    def change_language(language: str):
        _.language = language
        CONFIG.language = language

    def logout(self):
        self._app.manager.switch_to("login")
        USERS.logout()

    def set_dark_mode(self, active: bool):
        self._app.theme_cls.theme_style = "Dark" if active else "Light"
        CONFIG.dark_mode = active

    def on_item_release(self, instance: ConfigItem):
        __id = instance.id
        if __id == 'itm_language':
            self._language_dropdown.open()
            return
        if __id in ['itm_title', 'itm_description', 'itm_tag']:
            instance.edit()
            return
        raise IndexError('Unknown item')

    def _update_translations(self):
        self._default_string = f" ({_('Default')})"
        self.on__itm_language(self, self._itm_language)
        self.on__itm_title(self, self._itm_title)
        self.on__itm_description(self, self._itm_description)
        self.on__itm_tag(self, self._itm_tag)

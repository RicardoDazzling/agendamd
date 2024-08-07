__pycache__ = __import__('settings').start()
__version__ = __import__('version').__version__

import os

# Environments Variables
from settings import settings

from globals import *
from libs.devlibs import translator, Translator

# Kaki Dependencies:
# import os

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.lang import Builder

# My Dependencies.
from kivy.uix.screenmanager import NoTransition
from kivy.properties import ObjectProperty
from kivy.lang import global_idmap
from kivymd.theming import ThemeManager
from logging import getLogger, WARNING
from typing import Optional

from libs.applibs.utils import log

# Disable debug requests log:
getLogger("requests").setLevel(WARNING)
getLogger("urllib3").setLevel(WARNING)
getLogger("PIL").setLevel(WARNING)


class AgendaMDApp(MDApp):

    # DEBUG = 1  # set this to 0 make live app not working

    CURRENT_DIR = os.getcwd()

    NAME = settings.NAME

    CACHE_DIR = settings.CACHE_DIR

    KV_FILES = [
        "components\\login\\__init__.kv",
        "components\\dashboard\\calendar_item\\calendar_item.kv",
        "components\\dashboard\\minimized_calendar_item\\minimized_calendar_item.kv",
        "login\\login\\login.kv",
        "login\\register\\register.kv",
        "home\\home.kv",
        "home\\nav\\dashboard\\dashboard.kv",
        "home\\nav\\config\\config.kv",
    ]

    CLASSES = {
        "KLCheckbox": "components",
        "MDTextFieldTrailingIconButton": "components.textfields",
        "ComboTextField": "components.textfields",
        "DateTimeTextField": "components.textfields",
        "LoginTextField": "components.login",
        "LoginPasswordTextField": "components.login",
        "LoginFormButton": "components.login",
        "MDStaticCard": "components.home",
        "BaseCalendarItem": "components.home",
        "CalendarItem": "components.home",
        "CalendarItemNav": "components.home",
        "MinimizedCalendarItem": "components.home",
        "ConfigButtonText": "components.config",
        "ConfigCardHeader": "components.config",
        "ConfigItem": "components.config",
        "ConfigSwitch": "components.config",
        "LoginScreen": "login",
        "RegisterScreen": "login",
        "HomeScreen": "home",
        "DashboardScreen": "home.nav",
        "ConfigScreen": "home.nav",
    }

    translator: Optional[Translator] = ObjectProperty(None)
    manager = ObjectProperty(None)

    progress_bar = None

    def __init__(self, **kwargs):
        self.SCREENS = {}
        self.IMAGE_CACHE_DIR = os.path.join(self.CACHE_DIR, 'img')
        if not os.path.exists(self.IMAGE_CACHE_DIR):
            os.mkdir(self.IMAGE_CACHE_DIR)
            CONFIG.dark_mode = self.theme_cls.theme_style == 'Dark'
        super().__init__(**kwargs)
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style = "Dark" if CONFIG.dark_mode else "Light"

    def build(self):
        super(AgendaMDApp, self).build()
        Builder.load_file(os.path.join(os.getcwd(), "libs/uix/screenmanager/screenmanager.kv"))
        Factory.register("MainScreenManager",  module="libs.uix.screenmanager")
        self.manager = Factory.MainScreenManager()
        # self.icon = os.path.join(os.getcwd(), "assets", "fav", "fav.png")
        self.title = os.getenv("NAME")
        return self.manager

    def on_start(self):
        super(AgendaMDApp, self).on_start()
        Window.show()
        self.global_init()

        log(self, 'Building', 'info')
        __cmd = os.getcwd()
        for widget in self.KV_FILES:
            Builder.load_file(os.path.join(__cmd, 'libs', 'uix', widget))
        for key, widgets in self.CLASSES.items():
            Factory.register(key, module='.'.join(('libs', 'uix', widgets)))
        Window.clearcolor = self.theme_cls.backgroundColor
        self.theme_cls.bind(backgroundColor=lambda i, v, w=Window: setattr(w, 'clearcolor', v))

        __switch_to_home = False
        if USERS.logged():
            if USERS.keep_logged:
                USERS.decrypt_database()
                __switch_to_home = True
        self.SCREENS['login'] = Factory.LoginScreen(name="login")
        self.SCREENS['register'] = Factory.RegisterScreen(name="register")
        self.SCREENS['home'] = Factory.HomeScreen(name="home")
        self.manager.add_widget(self.SCREENS['login'])
        self.manager.add_widget(self.SCREENS['register'])
        self.manager.add_widget(self.SCREENS['home'])

        if __switch_to_home:
            self.manager.switch_to("home", transition=NoTransition())

    def on_stop(self):
        if USERS.logged():
            USERS.encrypt_database()

    def global_init(self):
        self.translator = translator
        global_idmap['_'] = translator
        global_idmap['settings'] = settings
        global_idmap['USERS'] = USERS
        global_idmap['CONFIG'] = CONFIG
        global_idmap['TASKS'] = TASKS
        global_idmap['TAGS'] = TAGS


if __name__ == "__main__":
    log('Master', 'Initializing App.', 'info')
    app = AgendaMDApp()
    log('Master', 'Running App.', 'info')
    app.run()

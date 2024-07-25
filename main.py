import os

# Environments Variables
import sys

from settings import settings

os.environ["NAME"] = settings.NAME
os.environ["CACHE_DIR"] = settings.CACHE_DIR
os.environ['KIVY_HOME'] = os.path.join(settings.CACHE_DIR, '.kivy')
__pycache__ = os.path.join(settings.CACHE_DIR, 'pycache')
os.environ["PYTHONPYCACHEPREFIX"] = __pycache__
sys.pycache_prefix = __pycache__

from globals import USERS
from libs.devlibs import translator

# Kaki Dependencies:
# import os

from kivymd.app import MDApp
from kivy.core.window import Window
Window.borderless = True
from kivy.factory import Factory
from kivy.lang import Builder

# My Dependencies.
import trio

from kivy.uix.screenmanager import NoTransition
from kivy.properties import ObjectProperty
from kivy.lang import global_idmap
from kivymd.theming import ThemeManager
from logging import getLogger, WARNING
from typing import Optional

from libs.devlibs import Translator
from libs.applibs.utils import log

# Disable debug requests log:
getLogger("requests").setLevel(WARNING)
getLogger("urllib3").setLevel(WARNING)
getLogger("PIL").setLevel(WARNING)


class AgendaMDApp(MDApp):

    # DEBUG = 1  # set this to 0 make live app not working

    nursery = None

    CURRENT_DIR = os.getcwd()

    NAME = settings.NAME

    CACHE_DIR = settings.CACHE_DIR

    KV_FILES = [
        os.path.join(os.getcwd(), "libs\\uix\\components\\login\\login_components.kv"),
        os.path.join(os.getcwd(), "libs\\uix\\components\\home\\calendar_item\\calendar_item.kv"),
        os.path.join(os.getcwd(), "libs\\uix\\components\\home\\minimized_calendar_item\\minimized_calendar_item.kv"),
        os.path.join(os.getcwd(), "libs\\uix\\login\\login\\login.kv"),
        os.path.join(os.getcwd(), "libs\\uix\\login\\register\\register.kv"),
        os.path.join(os.getcwd(), "libs\\uix\\home\\home.kv"),
        os.path.join(os.getcwd(), "libs\\uix\\home\\nav\\dashboard\\dashboard.kv"),
    ]

    CLASSES = {
        "KLCheckbox": "libs.uix.components",
        "MDTextFieldTrailingIconButton": "libs.uix.components.textfields",
        "ComboTextField": "libs.uix.components.textfields",
        "DateTimeTextField": "libs.uix.components.textfields",
        "LoginTextField": "libs.uix.components.login",
        "LoginPasswordTextField": "libs.uix.components.login",
        "LoginFormButton": "libs.uix.components.login",
        "MDStaticCard": "libs.uix.components.home",
        "BaseCalendarItem": "libs.uix.components.home",
        "CalendarItem": "libs.uix.components.home",
        "CalendarItemNav": "libs.uix.components.home",
        "MinimizedCalendarItem": "libs.uix.components.home",
        "LoginScreen": "libs.uix.login",
        "RegisterScreen": "libs.uix.login",
        "HomeScreen": "libs.uix.home",
        "DashboardScreen": "libs.uix.home.nav",
    }

    translator: Optional[Translator] = ObjectProperty(None)
    manager = ObjectProperty(None)

    progress_bar = None

    def __init__(self, **kwargs):
        self.SCREENS = {}
        self.IMAGE_CACHE_DIR = os.path.join(self.CACHE_DIR, 'img')
        if not os.path.exists(self.IMAGE_CACHE_DIR):
            os.mkdir(self.IMAGE_CACHE_DIR)
        super().__init__(**kwargs)

    async def app_func(self):

        async with trio.open_nursery() as nursery:
            self.nursery = nursery

            async def run_wrapper(*args):
                # trio needs to be set so that it'll be used for the event loop
                await self.async_run(async_lib='trio')
                nursery.cancel_scope.cancel()

            nursery.start_soon(run_wrapper)

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
        self.translation_init()
        self.nursery.start_soon(self._build)

    async def _build(self, *args):
        log(self, 'Building', 'info')
        for widget in self.KV_FILES:
            Builder.load_file(widget)
        for key, widgets in self.CLASSES.items():
            Factory.register(key, module=widgets)
        Window.clearcolor = (1, 1, 1, 1) if ThemeManager().theme_style == 'Light' else (0, 0, 0, 1)
        Window.borderless = False
        Window.resizable = True
        await self.start()

    async def start(self):
        __switch_to_home = False
        if USERS.logged():
            if USERS.user.keep_logged:
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

    def translation_init(self):
        self.translator = translator
        global_idmap['_'] = translator


if __name__ == "__main__":
    try:
        log('Master', 'Initializing App.', 'info')
        app = AgendaMDApp()
        log('Master', 'Running App.', 'info')
        trio.run(app.app_func)
    finally:
        os.environ['CLOSED'] = 'True'

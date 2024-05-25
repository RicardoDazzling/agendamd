import os

# Environments Variables

from appdirs import user_cache_dir
import sys

from libs.applibs.db import DB

os.environ["NAME"] = "AgendaMD"
os.environ["CACHE_DIR"] = user_cache_dir(os.getenv("NAME").lower())
os.environ['KIVY_HOME'] = os.path.join(os.getenv("CACHE_DIR"), '.kivy')
__pycache__ = os.path.join(os.getenv("CACHE_DIR"), 'pycache')
os.environ["PYTHONPYCACHEPREFIX"] = __pycache__
sys.pycache_prefix = __pycache__

# Kaki Dependencies:
# import os

from kivymd.app import MDApp
from kivy.core.window import Window
Window.borderless = True
from kivy.factory import Factory
from kivy.lang import Builder

# My Dependencies.
import trio

from kivy.properties import DictProperty, ObjectProperty
from logging import getLogger, WARNING
from kivymd.theming import ThemeManager
from kivy.uix.screenmanager import NoTransition

from libs.applibs.utils import log

# Disable debug requests log:
getLogger("requests").setLevel(WARNING)
getLogger("urllib3").setLevel(WARNING)
getLogger("PIL").setLevel(WARNING)


class SPyBApp(MDApp):

    # DEBUG = 1  # set this to 0 make live app not working

    nursery = None

    CURRENT_DIR = os.getcwd()

    NAME = os.getenv("NAME")

    CACHE_DIR = os.getenv("CACHE_DIR")

    KV_FILES = [
        os.path.join(os.getcwd(), "libs\\uix\\components\\login\\login_components.kv"),
        os.path.join(os.getcwd(), "libs\\uix\\components\\home\\calendar_icon\\calendar_item.kv"),
        os.path.join(os.getcwd(), "libs\\uix\\login\\login\\login.kv"),
        os.path.join(os.getcwd(), "libs\\uix\\login\\register\\register.kv"),
        os.path.join(os.getcwd(), "libs\\uix\\home\\home.kv"),
        os.path.join(os.getcwd(), "libs\\uix\\home\\nav\\dashboard\\dashboard.kv"),
    ]

    CLASSES = {
        "KLCheckbox": "libs.uix.components",
        "MDTextFieldTrailingIconButton": "libs.uix.components",
        "LoginTextField": "libs.uix.components.login",
        "LoginPasswordTextField": "libs.uix.components.login",
        "LoginFormButton": "libs.uix.components.login",
        "CheckIcon": "libs.uix.components.home",
        "CalendarItem": "libs.uix.components.home",
        "LoginScreen": "libs.uix.login",
        "RegisterScreen": "libs.uix.login",
        "Home": "libs.uix.home",
        "Dashboard": "libs.uix.home.nav",
    }

    current_user = DictProperty(None)

    manager = ObjectProperty(None)

    progress_bar = None

    DB = DB()

    def __init__(self, **kwargs):
        self.SCREENS = {}
        self.IMAGE_CACHE_DIR = os.path.join(self.CACHE_DIR, 'img')
        if not os.path.exists(self.IMAGE_CACHE_DIR):
            os.mkdir(self.IMAGE_CACHE_DIR)
        super().__init__(**kwargs)

    async def app_func(self):
        '''trio needs to run a function, so this is it. '''

        async with trio.open_nursery() as nursery:
            '''In trio you create a nursery, in which you schedule async
            functions to be run by the nursery simultaneously as tasks.

            This will run all two methods starting in random order
            asynchronously and then block until they are finished or canceled
            at the `with` level. '''
            self.nursery = nursery

            async def run_wrapper(*args):
                # trio needs to be set so that it'll be used for the event loop
                await self.async_run(async_lib='trio')
                nursery.cancel_scope.cancel()

            nursery.start_soon(run_wrapper)

    def build(self):
        super(SPyBApp, self).build()
        Builder.load_file(os.path.join(os.getcwd(), "libs/uix/screenmanager/screenmanager.kv"))
        Factory.register("MainScreenManager",  module="libs.uix.screenmanager")
        self.manager = Factory.MainScreenManager()
        # self.icon = os.path.join(os.getcwd(), "assets", "fav", "fav.png")
        self.title = os.getenv("NAME")
        return self.manager

    def on_start(self):
        super(SPyBApp, self).on_start()
        Window.show()
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
        self.SCREENS['home'] = Factory.Home(name="home")
        self.SCREENS['register'] = Factory.RegisterScreen(name="register")
        self.SCREENS['login'] = Factory.LoginScreen(name="login")
        self.manager.add_widget(self.SCREENS['home'])
        self.manager.add_widget(self.SCREENS['register'])
        self.manager.add_widget(self.SCREENS['login'])

        if (self.DB.logged() and not self.DB.keep) or not self.DB.logged():
            self.manager.switch_to("login", transition=NoTransition())
            return


if __name__ == "__main__":
    try:
        log('Master', 'Initializing App.', 'info')
        app = SPyBApp()
        log('Master', 'Running App.', 'info')
        trio.run(app.app_func)
    finally:
        os.environ['CLOSED'] = 'True'

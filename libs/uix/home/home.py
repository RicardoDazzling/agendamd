from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.navigationrail import MDNavigationRail, MDNavigationRailItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager

from typing import Optional, Literal

from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

from globals import translator as _
from libs.uix.home.nav import DashboardScreen


class HomeScreen(MDScreen):
    active_item: Optional[Literal['dashboard', 'list', 'inbox']] = None
    _screen_manager: Optional[MDScreenManager] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dashboard_screen = DashboardScreen(name='dashboard')
        self._not_implemented_snackbar = MDSnackbar(
            MDSnackbarText(
                text=_("This feature isn't implemented yet."),
            ),
            y=dp(24),
            pos_hint={"right": .98},
            size_hint=(None, None),
            width=dp(300),
        )

    def on_ids(self, instance, value: dict):
        if isinstance(value, dict):
            __nav_rail: Optional[MDNavigationRail] = value.get('nav_rail', None)
            __dashboard_item: Optional[MDNavigationRailItem] = value.get('dashboard_item', None)
            __list_item: Optional[MDNavigationRailItem] = value.get('list_item', None)
            __inbox_item: Optional[MDNavigationRailItem] = value.get('inbox_item', None)
            self._screen_manager = value.get('screen_manager', None)
            if self._screen_manager is not None:
                self._screen_manager.bind(current=self.on_current)
                self._add_screens()

    def on_pre_enter(self, *args):
        self._add_screens(True)

    def on_current(self, instance, screen_name: str):
        if not screen_name:
            return
        __nav_rail: MDNavigationRail = self.ids.nav_rail
        __item_name: list[Literal['dashboard', 'list', 'inbox']] = ['dashboard', 'list', 'inbox']
        __active_item = __item = None
        for item_name in __item_name:
            if item_name in screen_name:
                if self.active_item != item_name:
                    __item: Optional[MDNavigationRailItem] = self.ids.get(item_name + "_item")
                    __active_item = item_name
                    break
                else:
                    return
        if __active_item is None or __item is None:
            raise ValueError(f"Active Item or Item is None")
        __icon = getattr(__item, '_icon_item')
        if __icon.icon == 'blank':
            Clock.schedule_once(lambda x: self.on_current(instance, screen_name))
            return
        __nav_rail.set_active_item(__item)
        __icon.icon = __icon.icon.replace('-outline', '')
        if self.active_item is not None:
            __old_item = self.ids.get(self.active_item + '_item')
            __old_icon = getattr(__item, '_icon_item')
            __old_icon.icon = __old_icon.icon.replace('-outline', '') + '-outline'
        self.active_item = __active_item

    def _add_screens(self, on_pre_enter: bool = False):
        if not on_pre_enter or self._screen_manager is None:
            return
        if self._screen_manager.screen_names:
            return
        self._screen_manager.add_widget(self._dashboard_screen)

    def _goto(self, screen_name: Literal['dashboard', 'list', 'inbox'],
              instance: Optional[MDNavigationRailItem] = None, value: bool = True):
        if not value:
            return
        if screen_name == self._screen_manager.current:
            return
        if screen_name not in self._screen_manager.screen_names:
            if self._not_implemented_snackbar.parent is None:
                self._not_implemented_snackbar.open()
            instance.active = False
            return
        __screen_names = ['dashboard', 'list', 'inbox']
        if __screen_names.index(screen_name) < __screen_names.index(self._screen_manager.current):
            self._screen_manager.switch_to(screen_name, transition=SlideTransition(), direction='up')
        else:
            self._screen_manager.switch_to(screen_name, transition=SlideTransition(), direction='down')

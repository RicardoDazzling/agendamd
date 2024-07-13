from kivy.clock import Clock
from kivymd.uix.navigationrail import MDNavigationRail, MDNavigationRailItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager

from typing import Optional, Literal


class Home(MDScreen):
    active_item: Optional[Literal['dashboard', 'list', 'inbox']] = None

    def on_ids(self, instance, value: dict):
        if isinstance(value, dict):
            __nav_rail: Optional[MDNavigationRail] = value.get('nav_rail', None)
            __dashboard_item: Optional[MDNavigationRailItem] = value.get('dashboard_item', None)
            __list_item: Optional[MDNavigationRailItem] = value.get('list_item', None)
            __inbox_item: Optional[MDNavigationRailItem] = value.get('inbox_item', None)
            __screen_manager: Optional[MDScreenManager] = value.get('screen_manager', None)
            if __screen_manager is not None:
                __screen_manager.bind(current=self.on_current)

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

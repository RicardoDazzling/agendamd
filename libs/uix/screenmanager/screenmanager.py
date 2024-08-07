from kivy.compat import iteritems
from kivy.uix.screenmanager import ScreenManagerException, Screen, TransitionBase
from kivymd.uix.screenmanager import MDScreenManager


class MainScreenManager(MDScreenManager):

    def switch_to(self, screen, **options):
        """Add a new or existing screen to the ScreenManager and switch to it.
        The previous screen will be "switched away" from. `options` are the
        :attr:`transition` options that will be changed before the animation
        happens.

        If no previous screens are available, the screen will be used as the
        main one::

            sm = ScreenManager()
            sm.switch_to(screen1)
            # later
            sm.switch_to(screen2, direction='left')
            # later
            sm.switch_to(screen3, direction='right', duration=1.)

        If any animation is in progress, it will be stopped and replaced by
        this one: you should avoid this because the animation will just look
        weird. Use either :meth:`switch_to` or :attr:`current` but not both.

        The `screen` name will be changed if there is any conflict with the
        current screen.

        .. versionadded: 1.8.0
        """
        assert screen is not None

        if isinstance(screen, str):
            screen = self.get_screen(screen)

        if not isinstance(screen, Screen):
            raise ScreenManagerException(
                'ScreenManager accepts only Screen widget.')

        # stop any transition that might be happening already
        self.transition.stop()

        # ensure the screen name will be unique
        if screen not in self.screens:
            if self.has_screen(screen.name):
                screen.name = self._generate_screen_name()

        # change the transition if given explicitly
        old_transition = self.transition
        specified_transition = options.pop("transition", None)
        if specified_transition:
            self.transition = specified_transition

        # change the transition options
        old_attributes = {}
        for key, value in iteritems(options):
            if key != "REMOVE_OLD_FLAG":
                old_attributes[key] = getattr(self.transition, key)
                setattr(self.transition, key, value)

        if not isinstance(self.transition, TransitionBase):
            return

        # add and leave if we are set as the current screen
        if screen.manager is not self:
            self.add_widget(screen)
        if self.current_screen is screen:
            return

        old_current = self.current_screen

        if "REMOVE_OLD_FLAG" in options:
            def remove_old_screen(transition):
                if old_current in self.children:
                    self.remove_widget(old_current)
                    self.transition = old_transition
                    for ikey, ivalue in iteritems(old_attributes):
                        setattr(self.transition, ikey, ivalue)
                transition.unbind(on_complete=remove_old_screen)
            self.transition.bind(on_complete=remove_old_screen)
        else:
            def change_transition(transition):
                self.transition = old_transition
                for ikey, ivalue in iteritems(old_attributes):
                    setattr(self.transition, ikey, ivalue)
                transition.unbind(on_complete=change_transition)
            self.transition.bind(on_complete=change_transition)

        self.current = screen.name

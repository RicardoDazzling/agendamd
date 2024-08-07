from kivymd.uix.card import MDCard


class MDStaticCard(MDCard):
    def __init__(self, *args, **kwargs):
        super(MDStaticCard, self).__init__(*args, **kwargs)
        self.theme_bg_color = 'Custom'
        self.md_bg_color = self.theme_cls.surfaceContainerLowestColor
        self.theme_cls.bind(surfaceContainerLowestColor=self.setter('md_bg_color'))

    def on_enter(self) -> None:
        pass

    def on_leave(self) -> None:
        pass

    def on_press(self) -> None:
        pass

    def on_release(self, *args) -> None:
        pass

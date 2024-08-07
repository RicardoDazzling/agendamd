from typing import Callable

from kivy.metrics import dp
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText, MDSnackbarSupportingText, MDSnackbarButtonContainer, \
    MDSnackbarActionButton, MDSnackbarActionButtonText, MDSnackbarCloseButton


class LoginSnackbar(MDSnackbar):
    def __init__(self,
                 *args,
                 supporting_text: str = "Aviso",
                 action_text: str = "",
                 action: Callable = lambda e: None,
                 **kwargs):
        __args = list(args)
        __args.append(MDSnackbarText(text="Aviso!"))
        __args.append(MDSnackbarSupportingText(text=supporting_text))
        __args.append(MDSnackbarButtonContainer(
                MDSnackbarActionButton(
                    MDSnackbarActionButtonText(
                        text=action_text
                    ),
                    on_release=action
                ),
                MDSnackbarCloseButton(
                    icon="close",
                    on_release=self.dismiss,
                ),
                pos_hint={"center_y": 0.5}
            ))
        if "orientation" not in kwargs:
            kwargs["orientation"] = "horizontal"
        if "y" not in kwargs:
            kwargs["y"] = dp(24)
        if "width" not in kwargs and "size_hint" not in kwargs:
            kwargs["size_hint"] = (None, None)
            kwargs["width"] = dp(500)
        if "pos_hint" not in kwargs:
            kwargs["pos_hint"] = {"center_x": 0.5}
        super(LoginSnackbar, self).__init__(*__args, **kwargs)

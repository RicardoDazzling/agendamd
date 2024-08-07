__all__ = ["Translator", "translator"]

import gettext
import glob
import os

from babel.messages import mofile, pofile
from kivy.event import EventDispatcher
from kivy.logger import Logger
from kivy.properties import OptionProperty

from libs.applibs.db.config import CONFIG


local_edit = os.path.join('assets', 'translations')
domain = 'messages'
translations: list[str] = os.listdir(os.path.join(os.getcwd(), local_edit))


class Translator(EventDispatcher):

    language = OptionProperty(translations[0], options=translations)

    def __init__(self, **kwargs):
        self.local_edit = local_edit
        self.domain = domain
        self.translations = translations
        super().__init__(**kwargs)
        self.observers = []
        self.gettext = lambda message: message

    def _(self, message):
        return self.gettext(message)

    translate = _
    __call__ = translate

    def bind(self, func, *args, **kwargs):
        self.observers.append((func, args, kwargs))

    def unbind(self, func, *args, **kwargs):
        args = (func, args, kwargs)
        if args in self.observers:
            self.observers.remove(args)

    def on_language(self, _, language):
        self.gettext = gettext.translation(
            self.domain,
            self.local_edit,
            languages=[language],
            fallback=True if language == 'en_US' else False,
        ).gettext

        for func, args, kwargs in self.observers:
            try:
                func(*args)
            except ReferenceError:
                continue

    def compile_languages(self, remove_po_files=False):
        for filename in glob.glob(f'{self.local_edit}/*/LC_MESSAGES/{self.domain}.po'):
            language = filename[
                len(f'{self.local_edit}/'):-len(f'/LC_MESSAGES/{self.domain}.po')
            ]

            Logger.info('Translator: Compiling language %s...', language)

            with open(filename, 'rb') as po_file:
                catalog = pofile.read_po(po_file, locale=language)

            mo_filename = filename.replace('.po', '.mo')

            with open(mo_filename, 'wb') as mo_file:
                mofile.write_mo(mo_file, catalog)

            if remove_po_files:
                os.remove(filename)

    def bind_and_return_text(self, widget, text: str, property_name='text') -> str:
        self.bind(lambda t, w, s, n="text": w.__setattr__(n, t(s)), self, widget, text, property_name)
        return self(text)

    def bind_translation(self, widget, property_name: str, text: str):
        self.bind(lambda t, w, n, s: w.__setattr__(n, t(s)), self, widget, property_name, text)
        setattr(widget, property_name, self(text))
        return widget


if "translator" not in globals():
    translator = Translator()
    translator.compile_languages()
    translator.language = CONFIG.language

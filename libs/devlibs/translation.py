import gettext
import glob
import os

from babel.messages import mofile, pofile
from kivy.event import EventDispatcher
from kivy.logger import Logger
from kivy.properties import OptionProperty

from libs.applibs.db.config import CONFIG


__all__ = ["Translator", "translator"]


class Translator(EventDispatcher):

    language = OptionProperty("en_US", options=['en_US', 'pt_BR'])
    domain = 'messages'
    local_edit = 'assets\\translations'

    def __init__(self, **kwargs):
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
                func(*args, None, None)
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


if "_" not in globals():
    translator = Translator()
    translator.compile_languages()
    translator.language = CONFIG.language

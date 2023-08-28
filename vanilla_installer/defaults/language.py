# keyboard.py
#
# Copyright 2022 mirkobrombin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundationat version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
from gi.repository import Adw, Gtk
from gi.repository import GnomeDesktop
from vanilla_installer.core.languages import all_languages, current_language

@Gtk.Template(resource_path="/org/vanillaos/Installer/gtk/widget-language.ui")
class LanguageRow(Adw.ActionRow):
    __gtype_name__ = "LanguageRow"

    select_button = Gtk.Template.Child()
    suffix_bin = Gtk.Template.Child()

    def __init__(self, title, subtitle, selected_language, **kwargs):
        super().__init__(**kwargs)
        self.__title = title
        self.__subtitle = subtitle
        self.__selected_language = selected_language

        self.set_title(title)
        self.suffix_bin.set_label(subtitle)

        self.select_button.connect("toggled", self.__on_check_button_toggled)

    def __on_check_button_toggled(self, widget):
        self.__selected_language["language_title"] = self.__title
        self.__selected_language["language_subtitle"] = self.__subtitle


@Gtk.Template(resource_path="/org/vanillaos/Installer/gtk/default-language.ui")
class VanillaDefaultLanguage(Adw.Bin):
    __gtype_name__ = "VanillaDefaultLanguage"

    btn_next = Gtk.Template.Child()
    entry_search_language = Gtk.Template.Child()
    search_controller = Gtk.EventControllerKey.new()
    all_languages_group = Gtk.Template.Child()

    selected_language = {'language_title': None, 'language_subtitle': None}

    def __init__(self, window, distro_info, key, step, **kwargs):
        super().__init__(**kwargs)
        self.__window = window
        self.__distro_info = distro_info
        self.__key = key
        self.__step = step

        self.__language_rows = self.__generate_language_list_widgets(self.selected_language)
        for i, widget in enumerate(self.__language_rows):
            self.all_languages_group.append(widget)

        # signals
        self.btn_next.connect("clicked", self.__window.next)
        self.search_controller.connect("key-released", self.__on_search_key_pressed)
        self.entry_search_language.add_controller(self.search_controller)

    def __generate_language_list_widgets(self, selected_language):
        language_widgets = []
        curr_language = GnomeDesktop.get_language_from_locale(current_language, None)

        for language_subtitle, language_title in all_languages.items():
            language_row = LanguageRow(language_title, language_subtitle, selected_language)
            
            if len(language_widgets)>0:
                language_row.select_button.set_group(language_widgets[0].select_button)
            language_widgets.append(language_row)

            if curr_language == language_title:
                language_row.select_button.set_active(True)

        return language_widgets

    def get_finals(self):
        return {
            "language": self.selected_language["language_subtitle"]
        }

    def __on_search_key_pressed(self, *args):
        keywords = re.sub(r"[^a-zA-Z0-9 ]", "", self.entry_search_language.get_text().lower())

        for row in self.all_languages_group:
            row_title = re.sub(r'[^a-zA-Z0-9 ]', '', row.get_title().lower())
            row_subtitle = re.sub(r'[^a-zA-Z0-9 ]', '', row.suffix_bin.get_label().lower())
            search_text = row_title + ' ' + row_subtitle
            row.set_visible(re.search(keywords, search_text, re.IGNORECASE) is not None)

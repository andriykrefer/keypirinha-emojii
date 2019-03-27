# Keypirinha launcher (keypirinha.com)

import keypirinha_util as kpu
import keypirinha as kp
import time
import os
import json
import codecs
from .pyperclip import copy as pcopy

HAS_SUBMENU = True

class Emojii(kp.Plugin):
    def __init__(self):
        super().__init__()
        self.EMOJII_CATEGORY = kp.ItemCategory.USER_BASE + 1
        self.db = []
        self.catalog = [];

    def _make_catalog_from_json(self):
        self.db = []
        self.db = json.loads(self.load_text_resource('db.json'))

        self.catalog = [];
        for ix, e in enumerate(self.db):
            label = e['name'] + ' ' + e['shortcode']
            icon = 'res://%s/%s'%(self.package_full_name(),e['file'])
            short_desc = 'Press Enter to copy or Tab for more options'
            item = self.create_item(
                category=self.EMOJII_CATEGORY,
                label=label,
                short_desc=short_desc,
                target=str(ix),
                args_hint=kp.ItemArgsHint.ACCEPTED,
                hit_hint=kp.ItemHitHint.IGNORE,
                icon_handle=self.load_icon(icon),
                data_bag=json.dumps(e),
                loop_on_suggest=True
            )
            self.catalog.append(item)
        
        if HAS_SUBMENU:
            self.set_catalog([])
            icon = 'res://%s/%s'%(self.package_full_name(),'img/logo.png')
            self.set_catalog([
                self.create_item(
                    category=self.EMOJII_CATEGORY,
                    label='Emojii: Search',
                    short_desc='Enter to search emoji',
                    target='emojii',
                    args_hint=kp.ItemArgsHint.REQUIRED,
                    hit_hint=kp.ItemHitHint.IGNORE,
                    icon_handle=self.load_icon(icon),
                    loop_on_suggest=True
                )
            ])
        else:
            self.set_catalog(self.catalog)

    def on_start(self):
        pass

    def on_catalog(self):
        self.set_catalog([])
        start_time = time.time()
        self._make_catalog_from_json()
        elapsed = time.time() - start_time
        stat_msg = "Cataloged {} items in {:0.1f} seconds"
        self.info(stat_msg.format(len(self.db), elapsed))

    def on_suggest(self, user_input, items_chain):
        if not items_chain:
            return

        emoji_level = 1 if HAS_SUBMENU else 0
        level = len(items_chain)
        if level==emoji_level:
            self._set_catalog_as_suggestions()
        elif level==(emoji_level+1):
            self._set_emoji_options_as_suggestions(items_chain[emoji_level])

    def _set_catalog_as_suggestions(self):
        self.set_suggestions(self.catalog, sort_method=kp.Sort.NONE)

    # selected_item is an item from items_chain in self.on_suggest
    def _set_emoji_options_as_suggestions(self, selected_item):
        target = selected_item.target()
        item = self.db[int(selected_item.target())]
        suggestions = []
        suggestions.append(
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label='Emoji',
                short_desc="Press Enter to copy to the clipboard",
                target='copyemoji_'+target,
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE,
                icon_handle=self.load_icon('res://%s/%s'%(self.package_full_name(),item['file'])),
                loop_on_suggest=False
            )
        )
        if item['shortcode'] != '':
            suggestions.append(
                self.create_item(
                    category=kp.ItemCategory.KEYWORD,
                    label=item['shortcode'],
                    short_desc="(shortcode) Press Enter to copy to the clipboard",
                    target='copyshortcode_'+target,
                    args_hint=kp.ItemArgsHint.FORBIDDEN,
                    hit_hint=kp.ItemHitHint.IGNORE,
                    icon_handle=self.load_icon('res://'+self.package_full_name()+'/img/text.png'),
                    loop_on_suggest=False
                )
            )
        suggestions.append(
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label='U+'+hex(item['codepoint']),
                short_desc="(codepoint) Press Enter to copy to the clipboard",
                target='copycodepoint_'+target,
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE,
                icon_handle=self.load_icon('res://'+self.package_full_name()+'/img/text.png'),
                loop_on_suggest=False
            )
        )
        suggestions.append(
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label='String.fromCodePoint('+hex(item['codepoint'])+')',
                short_desc="(javascript) Press Enter to copy to the clipboard",
                target='copyjs_'+target,
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE,
                icon_handle=self.load_icon('res://'+self.package_full_name()+'/img/js.png'),
                loop_on_suggest=False
            )
        )
        suggestions.append(
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label='unichr('+hex(item['codepoint'])+')',
                short_desc="(python2) Press Enter to copy to the clipboard",
                target='copypy2_'+target,
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE,
                icon_handle=self.load_icon('res://'+self.package_full_name()+'/img/python.png'),
                loop_on_suggest=False
            )
        )
        suggestions.append(
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label='chr('+hex(item['codepoint'])+')',
                short_desc="(python3) Press Enter to copy to the clipboard",
                target='copypy3_'+target,
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE,
                icon_handle=self.load_icon('res://'+self.package_full_name()+'/img/python.png'),
                loop_on_suggest=False
            )
        )
        suggestions.append(
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label='&#x'+hex(item['codepoint']),
                short_desc="(html) Press Enter to copy to the clipboard",
                target='copyhtml_'+target,
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE,
                icon_handle=self.load_icon('res://'+self.package_full_name()+'/img/html.png'),
                loop_on_suggest=False
            )
        )
        self.set_suggestions(suggestions, sort_method=kp.Sort.NONE)

    def on_execute(self, item, action):
        # Sometimes item.data_bag() returns an empty string,
        # may be a keypirinha bug. Therefore I am not using this field to pass
        # data. (Using self.db[int(item.target())])
        ix = None
        action = None
        if item.target().find('_') >= 0:
            sp = item.target().split('_')
            ix = int(sp[1])
            action = sp[0]
        else:
            ix = int(item.target())
            action = 'default'
        e = self.db[ix]

        if action=='default':
            pcopy(chr(e['codepoint']))

        elif action=='copyemoji':
            pcopy(chr(e['codepoint']))

        else:
            pcopy(item.label())

    def on_events(self, flags):
        pass

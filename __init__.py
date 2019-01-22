# -*- coding: utf-8 -*-
#  Ivan Schurawel
# October 21, 2018

"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from aqt import mw
# import all of the Qt GUI library
from aqt.qt import *

from anki.cards import Card
from aqt.utils import askUser, tooltip
from anki.hooks import addHook

import time
import datetime


def onDeckBrowserDelayCards(did):
    deck_name = mw.col.decks.name(did)
    cids = mw.col.decks.cids(did, children=True)
    if not cids:
        tooltip("Deck contains no cards.")
        return
    r = askUser("This will delay <b>ALL</b> cards in the deck"
                " '{}' by the number of days the deck is overdue."
                "<br><br>Are you sure you want to proceed?".format(deck_name),
                defaultno=True, title="Delay Overdue Cards")
    if not r:
        return
    delay_cards(did)


def delay_cards(did):
    deckManager = mw.col.decks
    today_date = datetime.date.today()
    collection_creation = mw.col.crt
    collection_creation_date = datetime.date.fromtimestamp(collection_creation)
    difference = (today_date - collection_creation_date).days
    cards = [Card(mw.col, cid) for cid in deckManager.cids(did)]
    max_days_due = 0
    DUE = 2
    SUSPENDED = -1
    for card in cards:
        if card.type == DUE and card.queue != SUSPENDED and card.due <= difference:
            days_due = difference - card.due
            if days_due > max_days_due:
                max_days_due = days_due
    for card in cards:
        if card.type == DUE and card.queue != SUSPENDED:
            adjusted_due_date = card.due + max_days_due
            card.due = adjusted_due_date
            card.flush()
    deck = deckManager.get(did)
    mw.col.decks.save(deck)
    mw.col.decks.flush()
    mw.deckBrowser.refresh()
    tooltip("Delayed deck by: %d days" % max_days_due)


def onDeckBrowserShowOptions(menu, did):
    a = menu.addAction("Delay Overdue")
    a.triggered.connect(lambda _, did=did: onDeckBrowserDelayCards(did))


addHook('showDeckOptions', onDeckBrowserShowOptions)

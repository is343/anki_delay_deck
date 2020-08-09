# -*- coding: utf-8 -*-
#  Ivan Schurawel
# October 21, 2018
# January 22, 2019
# August 9, 2020

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
from aqt.utils import askUser, getOnlyText, showWarning, tooltip
from anki.hooks import addHook

import time
import datetime

DUE = 2
SUSPENDED = -1

def onDeckBrowserDelayCards(did):
    deck_name = mw.col.decks.name(did)
    cids = mw.col.decks.cids(did, children=True)
    if not cids:
        tooltip("Deck contains no cards.")
        return

    deckManager = mw.col.decks
    cards = [Card(mw.col, cid) for cid in deckManager.cids(did)]

    days_to_delay = calculate_delay(did, cards)

    confirm_response = askUser("The oldest card is {0} days overdue."
                " Delay all cards by {0} days?"
                "<br><br>If you press 'No' you will be able to manually enter"
                " how many days to delay by.".format(days_to_delay),
                defaultno=True, title="Confirm Delay")
                
    if not confirm_response:
        days_to_delay = getOnlyText("How many days would you like to delay? (Negative numbers will bring days forward)")

        if not days_to_delay:
            return
        try:
            days_to_delay = int(days_to_delay)
            if type(days_to_delay) != int:
                raise ValueError('Not a valid int')
                return
        except:
                showWarning("Please only enter whole numbers")
                return

    delay_cards(did, deckManager, cards, days_to_delay)

def calculate_delay(did, cards):
    today_date = datetime.date.today()
    collection_creation = mw.col.crt
    collection_creation_date = datetime.date.fromtimestamp(collection_creation)
    difference = (today_date - collection_creation_date).days
    max_days_due = 0
    for card in cards:
        if card.type == DUE and card.queue != SUSPENDED and card.due <= difference:
            days_due = difference - card.due
            if days_due > max_days_due:
                max_days_due = days_due

    return max_days_due

def delay_cards(did, deckManager, cards, days_to_delay):
    for card in cards:
        if card.type == DUE:
            adjusted_due_date = card.due + days_to_delay
            card.due = adjusted_due_date
            card.flush()
    deck = deckManager.get(did)
    mw.col.decks.save(deck)
    mw.col.decks.flush()
    mw.deckBrowser.refresh()

    main_text = "Delayed deck by:"
    days_text = "days"

    if days_to_delay == 1 | days_to_delay == -1:
        days_text = "day"
    if days_to_delay < 0:
        main_text = "Deck brought forward by:"
        days_to_delay *= -1
    
    tooltip("{0} {1} {2}".format(main_text, days_to_delay, days_text))


def onDeckBrowserShowOptions(menu, did):
    a = menu.addAction("Delay Overdue")
    a.triggered.connect(lambda _, did=did: onDeckBrowserDelayCards(did))


addHook('showDeckOptions', onDeckBrowserShowOptions)

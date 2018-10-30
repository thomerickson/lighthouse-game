# draggable.py

from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.app import App
from kivy.uix.scatter import Scatter
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.animation import Animation, AnimationTransition

import card_db
import random
import time

def scr_ratio(a, axis):
    ''' Takes an initial value 'x' on the 'axis' axis and returns the complement axis value '''
    if axis == 'x':
        return a * (16/9)
    else:
        return a * (9/16)

# CONFIGURATION
###############################################

Window.borderless = False
Window.resizable = True
Window.size = (int(scr_ratio(725, 'y')), 725)
Window.bottom = 0

WINDOW_WIDTH = dp(Window.size[0])
CARD_WIDTH = dp(85)
CARD_HEIGHT = dp(CARD_WIDTH * 1.5)

HAND_MARGIN = dp((WINDOW_WIDTH - CARD_WIDTH*4)/5)
HAND_BOT_MARGIN = dp(80)

FIELD_BOT_MARGIN = dp(Window.size[1]-CARD_HEIGHT-80)
FIELD_CARD_MARGIN = dp(60)

COL_0 = HAND_MARGIN
COL_1 = HAND_MARGIN*2 + CARD_WIDTH
COL_2 = HAND_MARGIN*3 + CARD_WIDTH*2
COL_3 = HAND_MARGIN*4 + CARD_WIDTH*3

CARD_LOCS = {'deck': (COL_3, HAND_BOT_MARGIN),
             'discard': (0,0),
             'hand0': (COL_0, HAND_BOT_MARGIN),
             'hand1': (COL_1, HAND_BOT_MARGIN),
             'hand2': (COL_2, HAND_BOT_MARGIN)}

COST_COLOR = (0, 0, 0, 1)
POWER_COLOR = (1, 1, 1, 1)

# build the field locations

for i in range(4):
    for depth in range(7):
        exec("CARD_LOCS['field"+str(i)+str(depth)+"'] = (COL_"+str(i)+", FIELD_BOT_MARGIN-(FIELD_CARD_MARGIN*depth))")

# DEBUG: check field locations

# for k in CARD_LOCS:
#     print(k + str(CARD_LOCS[k]))

# CLASSES
###############################################

class Sprite(Image):
    def __init__(self, size, **kwargs):
        super(Sprite, self).__init__(mipmap=True, **kwargs)
        # self.texture.min_filter = 'nearest'
        # self.texture.mag_filter = 'nearest'
        self.allow_stretch = True
        self.size = size
        self.size_hint = (None, None)
        # self.pos_hint = (None, None)

class Field(Sprite):
    def __init__(self, location, **kwargs):
        super(Field, self).__init__(**kwargs)
        self.location = location
        self.stack = []
        self.points = 0
        self.point_label = Label(text=str(self.points), opacity=1, pos_hint=(None, None), pos=(self.x-dp(5)+(CARD_WIDTH/2), self.y+(CARD_HEIGHT)), size=(dp(10), dp(5)), font_size=15, color=POWER_COLOR)
        self.add_widget(self.point_label)

    def update(self):
        self.points = 0
        for card in self.stack:
            if hasattr(card, 'bonus_reqs') and self.check_bonus(card.bonus_reqs):
                self.points += card.bonus
            if hasattr(card, 'power'):
                self.points += card.power
            if hasattr(card, 'cost'):
                self.points -= card.cost
        self.point_label.text = str(self.points)

    def add_card(self, card):
        self.stack.append(card)
        self.parent.rem_hand(card)
        stack_loc = 'field' + str(self.location) + str(len(self.stack)-1)
        card.change_loc(stack_loc)
        self.update()

    def rem_card(self, card):
        self.points -= card.power
        self.stack.remove(card)
        self.parent.discard.append(card)

    def check_requirements(self, req):
        reqs_total = len(req)
        for r in req:
            if len(self.stack) == 0:
                if r == 'field':
                    reqs_total -= 1
            elif r in self.stack[0].cardtype:
                reqs_total -= 1
        return reqs_total == 0

    def check_bonus(self, bonus_reqs):
        bonus_reqs_total = len(bonus_reqs)
        for r in bonus_reqs:
            if len(self.stack) == 0:
                if r == 'field':
                    bonus_reqs_total -= 1
            else:
                for card in self.stack:
                    if r in card.cardtype:
                        bonus_reqs_total -= 1
                        break
        return bonus_reqs_total == 0

class OldCard(Scatter):
    def __init__(self, name, img_src, cardtype, flavor, cost, power, bonus, reqs, bonus_reqs, location, **kwargs):
        super(Card, self).__init__()
        self.do_scale = False
        self.do_rotation = False
        self.do_translation = False
        self.location = location
        self.name = name
        self.cardtype = cardtype
        self.flavor = flavor
        self.img_src = img_src
        self.img_sprite = Sprite(size=(CARD_WIDTH, CARD_HEIGHT), source=self.img_src)
        self.add_widget(self.img_sprite)
        self.size = self.img_sprite.size
        self.size_hint = (None, None)
        self.cost = cost
        self.power = power
        self.bonus = bonus
        self.reqs = reqs
        self.bonus_reqs = bonus_reqs
        if self.cost <= 0:
            self.power_label = Label(text='+'+str(self.power), opacity=1, pos_hint=(None, None), pos=(self.width-dp(18), self.height-dp(22)), size=(dp(10), dp(5)), font_size=15, color=POWER_COLOR)
            self.add_widget(self.power_label)
        else:
            self.cost_label = Label(text='-'+str(self.cost), opacity=1, pos_hint=(None, None), pos=(self.width-dp(18), self.height-dp(22)), size=(dp(10), dp(5)), font_size=15, color=COST_COLOR)
            self.add_widget(self.cost_label)
        # self.pos_hint = (None, None)
        self.opacity = 0

    def update(self):
        self.pos = CARD_LOCS[self.location]
        # self.size = self.img.size
        # self.size_hint = (None, None)
        # self.pos_hint = (None, None)

    def hide(self):
        self.opacity = 0

    def show(self):
        self.opacity = 1

    def lock(self):
        self.do_translation = False

    def unlock(self):
        self.do_translation = True

    def change_loc(self, location, animate=False):
        self.location = location
        if animate:
            anim = Animation(pos=CARD_LOCS[self.location], t='out_quad', d=.25)
            anim.start(self)
        else:
            self.update()

    def on_touch_down(self, touch):
        ''' Allows tapping a card locked to a field location to show it's information '''

        if self.collide_point(*touch.pos) and self.do_translation == (False, False):
            print('tapped locked card: {}'.format(self.name))
            self.show_info()
            return True
        else:
            return super(Card, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        ''' Checks for several conditions on a touch_up event:
            1) None or small drag distance registers as a 'tap' to show info card
            2) Collision detection with field, then checking to see if placing
                card here is valid
        '''
        if not touch.grab_current == self:
            # ignore if current card not the target
            return False
        if self.collide_point(*touch.pos) and self.do_translation != (False, False):
            # first check to see if displaying info and dismiss

            # then check to see if tapped or dragged:
            if (abs(CARD_LOCS[self.location][0] - self.pos[0]) < dp(5)) and (abs(CARD_LOCS[self.location][1] - self.pos[1]) < dp(5)):
                self.pos = CARD_LOCS[self.location]
                print('CARD TAPPED AT LOC: ' + str(self.location))
                self.show_info()
            else:
                collide = []
                for field in self.parent.fields:
                    if self.collide_widget(field):
                        collide.append(field.location)

                if len(collide) == 0 or len(collide) > 1:
                    # either collided with nothing or more than one, so animate back to
                    self.change_loc(self.location, animate=True)
                else:
                    # check to see if current card meets requirements in the field,
                    # and add card to stack and lock, or animate back to place
                    if self.parent.fields[collide[0]].check_requirements(self.reqs):
                        self.parent.fields[collide[0]].add_card(self)
                        self.lock()
                    self.change_loc(self.location, animate=True)
        return super(Card, self).on_touch_up(touch)

    def show_info(self):
        self.popup = Info_card(self)
        self.parent.add_widget(self.popup)
        for child in self.parent.children:
            child.disabled = True

    def hide_info(self):
        self.parent.remove_widget(self.popup)
        for child in self.parent.children:
            child.disabled = False

class Card(Scatter):
    def __init__(self, name, flavor, img, reqs, location='deck', **kwargs):
        super(Card, self).__init__()
        self.do_scale = False
        self.do_rotation = False
        self.do_translation = False
        self.location = location
        self.name = name
        self.flavor = flavor
        self.reqs = reqs
        self.img_src = img
        self.img_sprite = Sprite(size=(CARD_WIDTH, CARD_HEIGHT), source=self.img_src)
        self.add_widget(self.img_sprite)
        self.size = self.img_sprite.size
        self.size_hint = (None, None)

    def update(self):
        self.pos = CARD_LOCS[self.location]

    def hide(self):
        self.opacity = 0

    def show(self):
        self.opacity = 1

    def lock(self):
        self.do_translation = False

    def unlock(self):
        self.do_translation = True

    def change_loc(self, location, animate=False):
        self.location = location
        if animate:
            anim = Animation(pos=CARD_LOCS[self.location], t='out_quad', d=.25)
            anim.start(self)
        else:
            self.update()

    def on_touch_down(self, touch):
        ''' Allows tapping a card locked to a field location to show it's information '''

        if self.collide_point(*touch.pos) and self.do_translation == (False, False):
            print('tapped locked card: {}'.format(self.name))
            self.show_info()
            return True
        else:
            return super(Card, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        ''' Checks for several conditions on a touch_up event:
            1) None or small drag distance registers as a 'tap' to show info card
            2) Collision detection with field, then checking to see if placing
                card here is valid
        '''
        if not touch.grab_current == self:
            # ignore if current card not the target
            return False
        if self.collide_point(*touch.pos) and self.do_translation != (False, False):
            # first check to see if displaying info and dismiss

            # then check to see if tapped or dragged:
            if (abs(CARD_LOCS[self.location][0] - self.pos[0]) < dp(5)) and (abs(CARD_LOCS[self.location][1] - self.pos[1]) < dp(5)):
                self.pos = CARD_LOCS[self.location]
                print('CARD TAPPED AT LOC: ' + str(self.location))
                self.show_info()
            else:
                collide = []
                for field in self.parent.fields:
                    if self.collide_widget(field):
                        collide.append(field.location)

                if len(collide) == 0 or len(collide) > 1:
                    # either collided with nothing or more than one, so animate back to
                    self.change_loc(self.location, animate=True)
                else:
                    # check to see if current card meets requirements in the field,
                    # and add card to stack and lock, or animate back to place
                    if self.parent.fields[collide[0]].check_requirements(self.reqs):
                        self.parent.fields[collide[0]].add_card(self)
                        self.lock()
                    self.change_loc(self.location, animate=True)
        return super(Card, self).on_touch_up(touch)

    def show_info(self):
        self.popup = Info_card(self)
        self.parent.add_widget(self.popup)
        for child in self.parent.children:
            child.disabled = True

    def hide_info(self):
        self.parent.remove_widget(self.popup)
        for child in self.parent.children:
            child.disabled = False

class PlanetCard(Card):
    def __init__(self, power, **kwargs):
        super(PlanetCard, self).__init__(**kwargs)
        self.power = power
        self.power_label = Label(text='+'+str(self.power), opacity=1, pos_hint=(None, None), pos=(self.width-dp(18), self.height-dp(22)), size=(dp(10), dp(5)), font_size=15, color=POWER_COLOR)
        self.add_widget(self.power_label)

class TechCard(Card):
    def __init__(self, cost, power, bonus, bonus_reqs, **kwargs):
        super(TechCard, self).__init__(**kwargs)
        self.cost = cost
        self.power = power
        self.bonus = bonus
        self.bonus_reqs = bonus_reqs
        if self.cost > 0:
            self.cost_label = Label(text='-'+str(self.cost), opacity=1, pos_hint=(None, None), pos=(self.width-dp(18), self.height-dp(22)), size=(dp(10), dp(5)), font_size=15, color=COST_COLOR)
            self.add_widget(self.cost_label)
        elif self.power > 0:
            self.power_label = Label(text='+'+str(self.power), opacity=1, pos_hint=(None, None), pos=(self.width-dp(18), self.height-dp(22)), size=(dp(10), dp(5)), font_size=15, color=POWER_COLOR)
            self.add_widget(self.power_label)

class EventCard(Card):
    def __init__(self, cost, power, bonus, bonus_reqs, action, **kwargs):
        super(EventCard, self).__init__(**kwargs)
        self.cost = cost
        self.power = power
        self.bonus = bonus
        self.bonus_reqs = bonus_reqs
        self.action = action




class Info_card(Scatter):
    def __init__(self, card, **kwargs):
        super(Info_card, self).__init__(**kwargs)
        self.do_rotation, self.do_scale, self.do_translation = False, False, False
        self.card = card
        self.img = Sprite((CARD_WIDTH*3.5,CARD_HEIGHT*3.5), source=self.card.img_src)
        self.size = self.img.size
        self.size_hint = (None, None)
        self.pos = ((Window.width-CARD_WIDTH*3.5)/2, (Window.height-CARD_HEIGHT*3.5)/2)
        self.flavor = Label(text=self.card.flavor, size=(self.width-dp(50), CARD_HEIGHT*3.5/3), pos=(self.x-dp(25), self.y-dp(80)), text_size=(self.width-dp(50), CARD_HEIGHT*3.5/3))
        self.add_widget(self.img)
        self.add_widget(self.flavor)

        if hasattr(self.card, 'cost'):
            # print(self.card.cost)
            self.cost_label = Label(text='-'+str(self.card.cost), opacity=1, pos=(CARD_WIDTH*3.5-dp(55), CARD_HEIGHT*3.5-dp(70)), size=(dp(15), dp(10)), font_size=30, color=(0, 0, 0, 1))
            self.add_widget(self.cost_label)
        elif hasattr(self.card, 'power'):
            # print(self.card.power)
            self.power_label = Label(text='+'+str(self.card.power), opacity=1, pos=(CARD_WIDTH*3.5-dp(55), CARD_HEIGHT*3.5-dp(70)), size=(dp(15), dp(10)), font_size=30, color=(1, 1, 1, 1))
            self.add_widget(self.power_label)


    def on_touch_down(self, touch):
        self.card.hide_info()


# GAME LOGIC
###############################################

class Game(FloatLayout):

    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)

        self.hand = [None, None, None]
        self.fields = [None, None, None, None]
        self.deck = []
        self.discard = []

        img = Sprite(size=(Window.width, Window.height), source='images/Galaxy-bg.png', pos=(0,0))
        self.add_widget(img)

        self.build_board()
        self.build_deck(card_db.cards)
        self.update()

    def update(self):
        # fill empty hands if possible
        while self.hand.count(None) != 0 and len(self.deck) > 0:
            self.add_hand(self.deck.pop())


    def build_board(self):
        for place in ['deck', 'hand0', 'hand1', 'hand2']:
            img = Sprite(size=(CARD_WIDTH, CARD_HEIGHT), source='images/Blank-Space.png', pos=CARD_LOCS[place])
            self.add_widget(img)
        for i in range(4):
            field = Field(location=i, size=(CARD_WIDTH, CARD_HEIGHT), source='images/Blank-Space.png', pos=CARD_LOCS['field'+str(i)+'0'], )
            self.fields[i] = field
            self.add_widget(field)


    def build_deck(self, db):
        ''' Build the deck using a shuffled database of cards, db '''
        card_object = None
        for card in db:
            if 'planet' in card['cardtype']:
                card_object = PlanetCard(**card)
            elif card['cardtype'] == 'tech':
                card_object = TechCard(**card)
            elif card['cardtype'] == 'event':
                card_object = EventCard(**card)
            if card_object:
                self.deck.append(card_object)
                card_object.update()
        for card in self.deck:
            self.add_widget(card)


    def add_hand(self, card):
        ''' Add selected card (card) to the hand pile, which automatically
        fills empty spaces, or returns False if hand is full '''

        if self.hand.count(None) == 0:
            print('ERR: HAND IS FULL')
            return False
        for i in range(3):
            if self.hand[i] == None:
                self.hand[i] = card
                card.show()
                card.do_translation = True
                card.change_loc('hand' + str(i), animate=True)
                print('ADDED CARD {} TO {}'.format(card.name, card.location))
                return True


    def rem_hand(self, card):
        ''' remove card from hand pile, returns False if card doesn't exist '''

        if card in self.hand:
            i = self.hand.index(card)
            self.hand[i] = None
            return True
        else:
            print('ERR: CARD NOT IN HAND')
            return False

class TestApp(App):
    def build(self):

        game = Game()
        return game

TestApp().run()
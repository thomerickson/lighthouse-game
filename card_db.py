# card-db.py

# All cards require: name, img, cardtype, flavor, reqs
# Planets require: power
# Tech requires: cost, power, bonus, bonus_reqs
# Events require: cost, power, bonus, bonus_reqs, action

planets = [
    {'name': 'earth',
    'img': 'images/Earth-Card.png',
    'cardtype': ['planet', 'habitable'],
    'flavor': 'The third rock from the sun. Birthplace of humankind. Ideal for life and rich with resources.',
    'power': 5,
    'reqs': ['field'],},
    {'name': 'mars',
    'img': 'images/Mars-Card.png',
    'cardtype': ['planet', 'rocky'],
    'flavor': 'Earth\'s second closest neighbor. Uninhabitable without considerable effort, but a decent supply of resources including water.',
    'power': 2,
    'reqs': ['field'],}
]

tech = [
    {'name': 'capitol city',
    'img': 'images/Earth-Card.png',
    'cardtype': 'tech',
    'flavor': 'A bustling capitol city. Adds +2. If built on a habitable planet, adds +4.',
    'cost': 2,
    'power': 2,
    'bonus': 2,
    'reqs': ['planet'],
    'bonus_reqs': ['habitable']}
]

events = [
    {'name': 'Asteroid',
    'img': 'images/Earth-Card.png',
    'cardtype': 'event',
    'flavor': 'A humongous asteroid. -1 to any planet.',
    'cost': 0,
    'power': 0,
    'bonus': -1,
    'reqs': ['planet'],
    'bonus_reqs': [],
    'action' : ['destroy_or_damage']}
]

cards = planets + tech
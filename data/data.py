#! /usr/bin/python3
"""
Information for cosmogon to work.

This file includes lists, dictionaries, and arrays.
"""
import numpy

names = ["Ogarthe", "Ulfheim", "Elomkuk", "Unnwn", "Emirovati", "Ircadie", "Usgard", "Usphedil", "Etlontus", "Uvelon", "Oxus Minde", "Iyothe", "Amorthe", "Gungei", "Oztlán", "Biltea", "Boarmelond", "Burengan", "Bruhmepira", "Brottia", "Cemolet", "Cackeigne", "Fforeon", "Deya", "Darudo", "Aden", "Hisparedis", "Garius", "Foneus", "Merios", "Filies", "Howaeko", "Hievan", "Hol", "Hill", "Hyparberia", "Orkelli", "Jubelqi", "Jobilse", "Jembodvīpe", "Jetinheum", "Roynas", "Sugeiney", "Kotazh", "Kilub", "Kenlin", "Kvonlund", "Kyöpalenvaero", "Loistrygen", "Puramo", "Limeria", "Lantoketa", "Lyanissu", "Mug Mall", "Morapes", "Muctlon", "Alympes", "Panglei", "Ma", "Mospilheum", "Nireko", "Jurasolim", "Nebire", "Noflhaem", "Naflhol", "Nurvoni", "Norimbaga", "Nyse", "Poitati", "Puncheio", "Pongeuo", "Pindæmanaim", "Plarima", "Puhjala ", "Pirgotary", "Quavire", "Cíbile", "Rom Sata ", "Semivosirine", "Schilamanci", "Shumbhelo", "Shengro-Le", "Sadem", "Gamirreh", "Seddani", "Svorgi", "Svertálfohaemr", "Tokime-go-hire", "Tirturas", "Thamoscyre", "Thala", "Thiviroiyem Potha", "Túr ne nÉg", "Volhello", "Vunehaemr", "Wostarnissa", "Xebolbi", "Yami", "Ys", "Zorehimle", "Zurzaro", "Zoin"]

char_dict = {
    1: "~",
    2: "╬",
    3: "░",
    4: "¶",
    5: "^",
    6: "#",
    7: "ª",
    8: "a",
    9: "A",
        }

type_dict = {
    1: "Water",
    2: "River",
    3: "Plains",
    4: "Woods",
    5: "Mountains",
    6: "Farms",
    7: "Village",
    8: "Town",
    9: "City",
        }

testmat = numpy.array([
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,3,3,3,3,3,3,3,3,1,1,1,1,1,1,3,3,3,3,3,3,1,1,1,1,1,1,1,1],
    [1,1,1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,3,3,3,3,3,3,3,3,3,3,1,1,1,3,3,3,3,3,3,3,3,3,3,3,1,1,1,1],
    [1,1,1,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4,3,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1,1],
    [1,1,3,3,3,3,3,3,3,3,4,4,4,4,4,4,3,3,3,3,2,3,3,3,3,3,4,4,4,4,4,4,4,4,4,4,4,3,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,3,3,3,3,3,4,4,4,4,4,4,4,4,4,3,3,3,2,3,3,3,3,3,4,4,4,4,4,4,4,4,4,4,4,3,3,3,3,3,3,3,3,1,1,1,1,1],
    [1,3,3,3,3,3,3,3,3,4,4,4,4,4,4,4,3,3,3,3,2,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,3,3,3,3,3,3,3,3,1,1,1,1,1,1],
    [1,1,1,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4,4,2,4,4,4,4,4,4,3,3,3,3,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4,2,2,4,4,4,4,3,3,1,1,1,1,1,1,1,1,3,3,3,3,3,3,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4,4,2,4,4,4,4,3,1,1,1,1,1,1,1,1,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1],
    [1,1,2,2,3,3,3,3,3,4,4,4,4,4,4,4,4,4,4,4,4,2,2,4,2,2,2,1,1,1,1,1,1,1,1,1,3,3,3,3,2,2,1,1,1,1,1,1,1,1],
    [1,1,3,2,2,2,2,3,4,4,4,4,4,4,4,4,4,4,4,4,4,4,2,2,2,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,3,3,3,3,1,1,1,1,1],
    [1,3,3,3,3,3,2,2,2,2,3,3,3,3,3,3,3,4,4,4,4,4,2,4,4,4,4,4,4,4,4,4,4,4,3,2,2,2,3,3,3,3,3,1,1,1,1,1,1,1],
    [1,3,3,3,3,3,3,3,3,2,2,2,2,4,4,4,4,4,4,4,4,4,4,2,4,4,4,4,4,4,4,4,2,2,2,2,4,4,4,4,3,3,3,3,3,1,1,1,1,1],
    [1,3,3,3,3,3,3,3,3,3,3,4,4,2,4,4,4,4,4,4,4,4,5,2,4,4,4,4,4,4,4,4,2,4,4,4,4,3,3,3,3,3,3,3,1,1,1,1,1,1],
    [1,1,1,3,3,3,3,3,3,4,4,4,4,2,2,2,4,4,4,2,2,2,5,5,4,4,4,4,4,4,2,2,2,4,4,4,4,4,4,4,4,3,3,3,3,3,3,1,1,1],
    [1,1,1,1,3,3,3,3,3,3,3,3,4,4,4,2,2,2,2,2,4,4,4,5,5,4,4,2,2,2,2,4,4,4,4,4,4,4,4,4,4,4,3,3,3,3,3,1,1,1],
    [1,1,3,3,3,3,3,3,4,4,4,4,4,4,2,2,4,4,4,4,4,4,4,5,5,2,2,2,4,4,4,4,4,4,4,4,4,3,3,3,3,3,3,1,1,1,1,1,1,1],
    [1,1,3,3,3,3,3,3,4,4,4,4,4,2,2,4,4,4,4,4,4,4,5,5,4,4,4,4,4,4,4,4,4,4,4,3,3,3,3,3,3,3,3,3,3,3,3,1,1,1],
    [1,3,3,3,3,3,3,3,3,4,4,4,4,2,4,4,4,4,4,4,4,4,2,5,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,3,3,3,3,3,3,1,1,1,1],
    [1,3,3,3,2,2,2,2,2,4,4,2,2,2,4,4,4,4,4,4,4,2,2,5,5,4,4,4,4,4,4,4,4,4,4,4,3,3,3,3,3,3,3,3,3,3,1,1,1,1],
    [1,1,1,2,2,3,3,3,2,2,2,2,4,4,4,4,4,4,4,4,4,2,4,5,4,4,3,3,3,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4,4,4,2,2,4,4,4,4,4,4,4,4,3,3,3,3,3,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4,4,4,4,2,4,4,4,4,4,4,4,4,4,4,4,4,4,4,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1],
    [1,1,3,3,3,3,3,3,3,3,3,3,3,3,4,4,4,4,4,2,2,3,3,3,3,3,3,3,3,4,3,3,3,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,3,3,1,1,1,3,3,3,3,3,3,3,4,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1],
    [1,1,1,1,1,3,3,1,1,1,1,1,3,3,3,3,3,2,2,2,3,3,3,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,3,1,1,1,1,1,1,1,3,3,3,3,2,3,3,3,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ])

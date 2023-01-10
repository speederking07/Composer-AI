import math
from typing import List, Dict, Set

import mido

import pygame as pg

BITS_PER_SECOND = 60


class Note:
    def __init__(self, note, start, length, tempo=0.5, metro=(4, 4), velocity=64):
        self.note = note
        self.start = start
        self.length = length
        self.end = start + length
        self.tempo = tempo
        self.metro = metro
        self.velocity = velocity

    def __repr__(self):
        return f"{self.note} - s:{self.start} - l:{self.length}"

    def __str__(self):
        return self.__repr__()


def load_midi(path: str) -> mido.MidiFile:
    return mido.MidiFile(path)


def midi_to_notes(midi: mido.MidiFile) -> List[Note]:
    timing = 0.0
    tempo = 0.5
    metro = 4, 4
    pressed = {}
    res = []
    for msg in midi:
        timing += msg.time
        if msg.type == "time_signature":
            metro = msg.numerator, msg.denominator
        if msg.type == "set_tempo":
            tempo = msg.tempo / 1000000
        if msg.type == 'note_on' and msg.velocity > 0:
            pressed[msg.note] = timing, msg.velocity, tempo, metro
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            if msg.note in pressed.keys():
                start, velocity, tempo, metro = pressed.pop(msg.note)
                res.append(Note(msg.note, start, timing - start, tempo, metro, velocity))
    return res


def play_notes(notes: List[Note], sounds: Dict[int, pg.mixer.Sound], active: Set[int], frame: int) -> Set[int]:
    current = set()
    notes_played = []
    for note in notes:
        key = note.note
        start_pos = math.floor(-note.start * BITS_PER_SECOND + frame)
        length = math.floor(note.length * BITS_PER_SECOND)
        if start_pos < 0:
            break
        elif start_pos - length > 0:
            notes_played.append(note)
        else:
            current.add(key)
    for key in current.difference(active):
        sounds[key].play()
    for key in active.difference(current):
        sounds[key].fadeout(800)
    for note in notes_played:
        if note.note in current:
            sounds[note.note].play()
        notes.remove(note)
    return current

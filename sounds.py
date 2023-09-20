import pyxel
# sounds go here?

# pyxel.init(192, 128, title="Words vs Werewolves", fps = 30, quit_key=pyxel.KEY_ESCAPE, display_scale=4)

class CanonD:
    def __init__(self):
    # bottom line, repeated 25 times
        pyxel.sound(0).set_notes("D1A1D2F#2 A0E1A1C#2 B0F#1B1D2 F#0C#1F#1A1 G0D1G1B1 D0A0D1F#1 G0D1G1B1 A0E1A1C#2")
        pyxel.sound(0).speed = 36
        pyxel.sound(1).set_notes("F#3 E3 D3 C#3 B2 A2 B2 C#3")
        pyxel.sound(1).speed = 144
        pyxel.sound(2).set_notes("D3D3F#3F#3 A3A3G3G3 F#3F#3D3D3 F#3F#3F#3E3 D3D3B2B2 D3D3F#3F#3 G3G3B3B3 A3A3A3G3")
        pyxel.sound(2).speed = 36
        pyxel.sound(3).set_notes("D3C#3D3A2 A2A2C#3C#3 D3D3F#3F#3 A3A3A3B3 G3F#3E3G3 F#3E3D3C#3 B2A2D3D3 D3D3D3C#3")
        pyxel.sound(3).set_effects("NNNF NNNN NNNN NNNN NNNN NNNN NNNF NNNN")
        pyxel.sound(3).speed = 36
        pyxel.sound(4).set_notes("D3C#3D3A2 C#3A2E3F#3 D3D3C#3B2 C#3F#3A3B3 G3F#3E3G3 F#3E3D3C#3 B2A2G2F#2 E2G2F#2E2")
        pyxel.sound(4).set_effects("NNNN NNNN FNNN NNNN NNNN NNNN NNNF NNNN")
        pyxel.sound(4).speed = 36
        pyxel.sound(5).set_notes("D3D3E3E3F#3F#3G3G3 A3A3E3E3A3A3G3G3 F#3F#3B3B3A3A3G3G3 A3A3G3G3F#3F#3E3E3 "
                                 "D3D3B2B2B2B2C#3C#3 D3D3F#3E3D3D3F#3F#3 G3G3D3C#3B3B3C#3C#3 D3D3D3D3D3D3C#3C#3")
        pyxel.sound(5).set_effects("NNNNNNNN NNNNNNNN NNNNNNNN NNNNNNNN NNNFNNNN NNNNNNNN NNNNNNNN NNNNNNNN")
        pyxel.sound(5).speed = 18
        pyxel.sound(6).set_notes("A3A3F#3G3A3A3F#3G3 A3A2B2C#3D3E3F#3G3 F#3F#3D3E3F#3F#3F#2G2 A2B2A2G2A2F#2G2A2 "
                                 "G2G2B2A2G2G2F#2E2 F#2E2D2E2F#2G2A2B2 G2G2B2A2B2B2C#3D3 A2B2C#3D3E3F#3G3A3")
        pyxel.sound(6).speed = 18
        pyxel.sound(7).set_notes("A3A3F#3G3A3A3F#3G3 A3A2B2C#3D3E3F#3G3 F#3F#3D3E3F#3F#3F#2G2 A2B2A2G2A2F#2G2A2 "
                                 "G2G2B2A2G2G2F#2E2 F#2E2D2E2F#2G2A2B2 G2G2B2A2B2B2C#3D3 A2B2C#3D3E3F#3G3A3")
        pyxel.sound(7).speed = 18
        pyxel.sound(8).set_notes("A3A3F#3G3A3A3F#3G3 A3A2B2C#3D3E3F#3G3 F#3F#3D3E3F#3F#3F#2G2 A2B2A2G2A2F#2G2A2 "
                                 "G2G2B2A2G2G2F#2E2 F#2E2D2E2F#2G2A2B2 G2G2B2A2B2B2C#3D3 A2B2C#3D3E3F#3G3A3")
        pyxel.sound(8).speed = 36

        self.measure_number = 0
        self.is_playing = False
        self.measure_increased = False

    def play(self):
        pyxel.music(0).set([], [], [], [0])
        pyxel.playm(0)
        self.measure_number = 0
        self.is_playing = True
        self.measure_increased = False

    def update(self):
        if self.is_playing:
            try:
                sound_no, note_no = pyxel.play_pos(3)
                if note_no % 8 == 0 and not self.measure_increased:
                    self.measure_number += 1
                    self.measure_increased = True

                if note_no % 8 == 4:
                    self.measure_increased = False

            except:
                if self.measure_number % 4 == 0:
                    if self.measure_number == 4:
                        pyxel.music(0).set([1], [], [], [0])
                    if self.measure_number == 12:
                        pyxel.music(0).set([2], [], [], [0])
                    if self.measure_number == 20:
                        pyxel.music(0).set([3], [], [], [0])
                    if self.measure_number == 28:
                        pyxel.music(0).set([4], [], [], [0])
                    if self.measure_number == 32:
                        pyxel.music(0).set([5], [], [], [0])
                    if self.measure_number == 36:
                        pyxel.music(0).set([6], [], [], [0])
                    pyxel.playm(0)

from .gui import *
from . import quests
import random


def make_loading_menu(app, text=""):
    f = Frame(app)
    f.pxsize = 32
    f.ypos += 10
    if text:
        for i in text.split('\n'):
            f.add_button(i, action=app.continue_game_accent)

        loading_text = random.choice([
            'Wait a sec',
            'Please wait...',
            'Loooooading..',
            'Hold on a sec',
            'Charging shields...',
            'Loading fuel..',
            'Wait a minute...',
            'TODO: place a spinner here',
            'Loading...',
        ])
        f.loading_button = f.add_button(loading_text, action=app.continue_game_accent)
    else:
        f.add_button("Loading...")
    app.loading_menu = f


def update_game_menu(app, f):
    played_races = {}
    available_races = {}
    all_tracks_opened = '1' == app.config['AllOpen']
    # Update records
    for name, fn, b, req in f.named_buttons:
        t = app.get_race_record(fn)
        c = app.is_race_completed(fn)
        if t or c:
            played_races[fn] = 1
            b.text = name + " " + (t or "(completed)")
            # b.text = name + " " + "(completed)"

    # Fill availability
    for name, fn, b, req in f.named_buttons:
        for i in req.split():
            if i not in played_races:
                break
        else:
            available_races[fn] = 1
    for i in available_races:
        if not app.is_race_available(i):
            app.set_race_available(i)

    # Update availability
    for name, fn, b, req in f.named_buttons:
        if not app.is_race_available(fn):
            if all_tracks_opened:
                b.color = pygame.Color('black')
            else:
                b.disabled = True
        else:
            b.color = pygame.Color('white')
            b.disabled = False

def prepare_menu(app):
    app.new_menu = None
    app.custom_races_menu = None
    app.save_menu = None
    app.load_menu = None
    app.main_menu = None
    app.options_menu = None
    app.sound_menu = Frame(app)
    app.controls_menu = Frame(app)
    app.difficulty_menu = Frame(app)
    app.credits_menu = None
    app.loading_menu = None

    def ss(d):
        def sg():
            app.main_menu.continue_button.disabled = False
            app.start_game(d)

        return sg

    def sc(d, rt, laps=0):
        def sg():
            app.main_menu.continue_button.disabled = False
            app.start_custom_race(d, rt, laps)

        return sg

    f = Frame(app)
    f.ypos += 100
    f.continue_button = f.add_button("Continue", action=app.continue_game)
    f.continue_button.disabled = True
    f.add_button("Start Race", action=lambda: app.select_menu(app.new_menu))
    # f.add_button("Custom Races",
    #             action=lambda: app.select_menu(app.custom_races_menu))
    f.add_button("Options", action=lambda: app.select_menu(app.options_menu))
    f.add_button("Exit", action=app.exit)
    app.main_menu = f

    f = Frame(app)
    f.ypos += 20
    f.pxsize = 32

    races = [
        ['Butterfly lake', 'lake.png', ''],  # main 1
        ['Sunny islands', 'sunny.png', 'lake.png'],  # main 2
        ['Currents', 'currents.png', 'sunny.png'],  # main 3
        ['Long river', 'long.png', 'currents.png'],

        # group of four
        ['Riverland conters', 'rivers.png', 'long.png'],
        ['Swampland contest', 'swamps.png', 'long.png'],
        ['Irrigation', 'irrigation.png', 'long.png'],
        ['Cooland contest', 'ice.png', 'long.png'],

        ['Rescue', 'rescue.png', 'swamps.png rivers.png irrigation.png ice.png'],
        ['Curl', 'curl.png', 'rescue.png'],
        ['Exotic', 'exotic.png', 'curl.png'],  #

        # optional
        ['The End', 'lake2.png', 'exotic.png'],  #
        ['Longer river', 'longer.png', 'long.png'],  #
        ['Second Sandland contest', 'irrigation2.png', 'irrigation.png longer.png'],  #
        ['Second Riverland contest', 'rivers2.png', 'rivers.png longer.png'],  #
        # ['Testing lake', 'test.png', ''],
    ]
    app.set_race_available('test.png')
    app.set_race_available('lake.png')
    f.named_buttons = []
    for name, fn, req in races:
        b = f.add_button(name, action=ss(fn))
        f.named_buttons.append([name, fn, b, req])

    update_game_menu(app, f)
    f.add_button("Back", action=lambda: app.select_menu(app.main_menu))
    app.new_menu = f
    f.update = update_game_menu

    app.loading_menu = None

    f = Frame(app)
    f.ypos += 80
    f.add_button("Loading..")
    app.loading_menu = f

    f = Frame(app)
    f.ypos += 100
    f.add_button("Sound", action=lambda: app.select_menu(app.sound_menu))
    f.add_button("Controls", action=lambda: app.select_menu(app.controls_menu))
    f.add_button("Difficulty", action=lambda: app.select_menu(app.difficulty_menu))
    f.add_button("")
    f.add_button("Back", action=lambda: app.select_menu(app.main_menu))
    app.options_menu = f

    app.sound_menu.ypos += 40
    app.sound_menu.pxsize = 32
    music_enabled = app.sound_menu.add_checkbox("Music")
    music_enabled.state = app.config['Music'] == '1'
    minc = app.sound_menu.add_button("Music volume +")
    app.sound_menu.music_volume = app.sound_menu.add_volumebox()
    mdec = app.sound_menu.add_button("Music volume -")
    minc.onclick = app.sound_menu.music_volume.inc
    mdec.onclick = app.sound_menu.music_volume.dec
    app.sound_menu.music_volume.value = int(
        float(app.config['MusicVolume']) * app.sound_menu.music_volume.maxvalue)

    def music_volume_changed():
        app.config['Music'] = '1' if music_enabled.state else '0'
        app.config['MusicVolume'] = "{0:.2f}".format(
            float(app.sound_menu.music_volume.value) / float(
                app.sound_menu.music_volume.maxvalue))
        app.mus.onMusicVolumeChanged()

    def music_settings_changed():
        app.config['Music'] = '1' if music_enabled.state else '0'
        app.config['MusicVolume'] = "{0:.2f}".format(
            float(app.sound_menu.music_volume.value) / float(
                app.sound_menu.music_volume.maxvalue))
        app.save_config()
        app.load_config()
        app.mus.onMusicToggle()

    app.sound_menu.music_volume.onchange = music_volume_changed
    music_enabled.ontoggle = music_settings_changed

    app.sound_menu.add_button("")
    sound_enabled = app.sound_menu.add_checkbox("Sound")
    sound_enabled.state = app.config['Sound'] == '1'

    sinc = app.sound_menu.add_button("Sound volume +")
    app.sound_menu.sound_volume = app.sound_menu.add_volumebox()
    sdec = app.sound_menu.add_button("Sound volume -")
    sinc.onclick = app.sound_menu.sound_volume.inc
    sdec.onclick = app.sound_menu.sound_volume.dec
    app.sound_menu.sound_volume.value = int(
        float(app.config['SoundVolume']) * app.sound_menu.sound_volume.maxvalue)

    def sound_volume_changed():
        app.config['Sound'] = '1' if sound_enabled.state else '0'
        app.config['SoundVolume'] = "{0:.2f}".format(
            float(app.sound_menu.sound_volume.value) / float(
                app.sound_menu.sound_volume.maxvalue))
        app.mus.effect('win')

    def sound_settings_changed():
        app.config['Sound'] = '1' if sound_enabled.state else '0'
        app.config['SoundVolume'] = "{0:.2f}".format(
            float(app.sound_menu.sound_volume.value) / float(
                app.sound_menu.sound_volume.maxvalue))
        app.save_config()
        app.load_config()
        app.mus.effect('win')

    app.sound_menu.sound_volume.onchange = sound_volume_changed
    sound_enabled.ontoggle = sound_settings_changed

    app.sound_menu.add_button("")
    app.sound_menu.add_button("Back",
                              action=lambda: app.select_menu(app.options_menu))

    app.controls_menu.ypos += 40
    app.controls_menu.pxsize = 32
    app.controls_menu.add_button("Controls are predefined")

    app.controls_menu.add_button("Move forward: W, Up")
    app.controls_menu.add_button("Move back: S, Down")
    app.controls_menu.add_button("Turn left: A, Left")
    app.controls_menu.add_button("Turn left: D, Right")
    app.controls_menu.add_button("")
    app.controls_menu.add_button("Hold mouse button to look around")
    app.controls_menu.add_button("")
    app.controls_menu.add_button("Menu: Esc")
    app.controls_menu.add_button("Quit: F10")
    app.controls_menu.add_button("")
    app.controls_menu.add_button("Back",
                                 action=lambda: app.select_menu(app.options_menu))

    app.difficulty_menu.ypos += 40
    cen = app.difficulty_menu.add_checkbox("Currents")
    cen.state = app.config['NoCurrents'] == '0'
    app.difficulty_menu.add_button("")

    sen = app.difficulty_menu.add_checkbox("Shield Regeneration")
    sen.state = app.config['ShieldRegeneration'] == '1'
    ten = app.difficulty_menu.add_checkbox("More time")
    ten.state = app.config['MoreTime'] == '1'

    app.difficulty_menu.add_button("")
    aen = app.difficulty_menu.add_checkbox("All races opened")
    aen.state = app.config['AllOpen'] == '1'

    def difficulty_changed():
        app.config['NoCurrents'] = '0' if cen.state else '1'
        app.config['ShieldRegeneration'] = '1' if sen.state else '0'
        app.config['MoreTime'] = '1' if ten.state else '0'
        app.config['AllOpen'] = '1' if ten.state else '0'
        app.save_config()
        app.load_config()

    cen.ontoggle = difficulty_changed
    sen.ontoggle = difficulty_changed
    ten.ontoggle = difficulty_changed
    aen.ontoggle = difficulty_changed
    app.difficulty_menu.add_button("")
    app.difficulty_menu.add_button("Back", action=lambda: app.select_menu(
        app.options_menu))

    f = Frame(app)
    f.ypos += 100
    f.add_button("Lake circuit", action=sc('lake.png', 'circuit', laps=3))
    f.add_button("Currents circuit", action=sc('currents.png', 'circuit', laps=3))
    f.add_button("Long circuit", action=sc('longer.png', 'circuit', laps=2))
    f.add_button("Back", action=lambda: app.select_menu(app.main_menu))
    app.custom_races_menu = f

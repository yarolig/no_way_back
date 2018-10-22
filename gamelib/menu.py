
from .gui import *


def prepare_menu(app):
    app.new_menu = None
    app.save_menu = None
    app.load_menu = None
    app.main_menu = None
    app.options_menu = None
    app.sound_menu = None
    app.credits_menu = None

    def ss(d):
        return lambda: app.start_game(d)

    f = Frame()
    f.ypos += 100
    f.addButton("New Game", action=lambda: app.select_menu(app.new_menu))
    f.addButton("Load Game", action=lambda: app.select_menu(app.save_menu))
    f.addButton("Save Game", action=lambda: app.select_menu(app.load_menu))
    f.addButton("Options", action=lambda: app.select_menu(app.options_menu))
    f.addButton("Credits", action=lambda: app.select_menu(app.credits_menu))
    f.addButton("Exit", action=app.exit)
    app.main_menu = f

    f = Frame()
    f.ypos += 100
    f.addButton("Easy", action=ss('easy'))
    f.addButton("Normal", action=ss('normal'))
    f.addButton("Hard", action=ss('hard'))
    f.addButton("")
    f.addButton("Impossible", action=ss('impossible'))
    f.addButton("")
    f.addButton("Back", action=lambda: app.select_menu(app.main_menu))
    app.new_menu = f

    f = Frame()
    f.ypos += 100
    # f.addButton("Graphics",action=lambda:app.select_menu(app.sound_menu))
    f.addButton("Sound", action=lambda: app.select_menu(app.sound_menu))
    # f.addButton("Controls",action=lambda:app.select_menu(app.sound_menu))
    f.addButton("")
    f.addButton("Back", action=lambda: app.select_menu(app.main_menu))
    app.options_menu = f

    f = Frame()
    f.ypos += 100

    f.addButton("Play music")
    f.addButton("Music volume")
    f.addButton("")
    f.addButton("Sound volume")
    f.addButton("")
    f.addButton("Back", action=lambda: app.select_menu(app.options_menu))
    app.sound_menu = f

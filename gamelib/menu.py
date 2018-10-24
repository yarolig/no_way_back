
from .gui import *


def prepare_menu(app):
    app.new_menu = None
    app.save_menu = None
    app.load_menu = None
    app.main_menu = None
    app.options_menu = None
    app.sound_menu = None
    app.credits_menu = None

    app.loading_menu = None

    def ss(d):
        return lambda: app.start_game(d)

    f = Frame(app)
    f.ypos += 100
    f.add_button("Start Race", action=lambda: app.select_menu(app.new_menu))
    #f.addButton("Load Game", action=lambda: app.select_menu(app.save_menu))
    #f.addButton("Save Game", action=lambda: app.select_menu(app.load_menu))
    f.add_button("Options", action=lambda: app.select_menu(app.options_menu))
    f.add_button("Credits", action=lambda: app.select_menu(app.credits_menu))
    f.add_button("Exit", action=app.exit)
    app.main_menu = f

    f = Frame(app)
    f.ypos += 80
    f.pxsize = 32
    #f.addButton("Easy", action=ss('easy'))
    #f.addButton("Normal", action=ss('normal'))
    #f.addButton("Hard", action=ss('hard'))
    #f.addButton("")
    #f.addButton("Impossible", action=ss('impossible'))
    #f.addButton("")
    f.add_button("Butterfly lake", action=ss('lake.png'))
    f.add_button("Sunny islands", action=ss('sunny.png'))
    f.add_button("Wind", action=ss('wind.png'))
    f.add_button("Currents", action=ss('currents.png'))
    f.add_button("Trading", action=ss('trading.png'))
    f.add_button("Rivers", action=ss('rivers.png'))
    f.add_button("Railroad", action=ss('rail.png'))
    f.add_button("Swamps", action=ss('swamps.png'))
    f.add_button("Irrigation", action=ss('irrigation.png'))
    f.add_button("Ice", action=ss('ice.png'))
    f.add_button("Exotic", action=ss('exotic.png'))
    f.add_button("Rescue", action=ss('rescue.png'))
    f.add_button("Curl", action=ss('curl.png'))

    f.add_button("Back", action=lambda: app.select_menu(app.main_menu))
    app.new_menu = f

    app.loading_menu = None

    f = Frame(app)
    f.ypos += 80
    f.add_button("Loading..")
    app.loading_menu = f

    f = Frame(app)
    f.ypos += 100
    # f.addButton("Graphics",action=lambda:app.select_menu(app.sound_menu))
    f.add_button("Sound", action=lambda: app.select_menu(app.sound_menu))
    # f.addButton("Controls",action=lambda:app.select_menu(app.sound_menu))
    f.add_button("")
    f.add_button("Back", action=lambda: app.select_menu(app.main_menu))
    app.options_menu = f

    f = Frame(app)
    f.ypos += 100

    f.add_button("Play music")
    f.add_button("Music volume")
    f.add_button("")
    f.add_button("Sound volume")
    f.add_button("")
    f.add_button("Back", action=lambda: app.select_menu(app.options_menu))
    app.sound_menu = f

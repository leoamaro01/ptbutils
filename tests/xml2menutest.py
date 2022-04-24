import sys, os

current_dir = sys.path[0]
parent = os.path.dirname(current_dir)
sys.path.append(parent)

import xml2bot.xml2menu as xml2menu

menu = xml2menu.xml2menu(os.path.join(current_dir, "receive_slap_menu.xml"))

print(str(menu))

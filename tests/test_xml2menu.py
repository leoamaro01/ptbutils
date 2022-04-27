import sys, os

current_dir = sys.path[0]
parent = os.path.dirname(current_dir)
sys.path.append(parent)

import xml2bot.xml2menu as xml2menu


def test_complex_case():
    import responses

    menu = xml2menu.xml2menu(os.path.join(current_dir, "menus/responsibility_menu.xml"))
    assert menu == xml2menu.XMLMenu(
        name="responsibility_menu",
        formats=["name", "responsible", "responsibilizer"],
        text="This is\n<b>{responsible}'s</b>\nresponsibility, {name}!",
        buttons=[
            xml2menu.XMLMenuButton(
                text="Ok, {responsibilizer}, whatever...",
                row=0,
                menu_link="receive_slap_menu",
            ),
            xml2menu.XMLMenuButton(
                text="<i>Accepts graciously</i>",
                row=0,
                callback_function=responses.run,
            ),
            xml2menu.XMLMenuButton(
                text="Custom answer\nWhatever...",
                row=-1,
                prompt_link="say_anything_prompt",
            ),
        ],
    )

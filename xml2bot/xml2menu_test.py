from xml2menu import XMLMenu, XMLMenuButton, xml2menu


def test_callback():
    print("TEST!")


def test_xml2menu():
    menu = xml2menu("menutest.xml")
    expected = XMLMenu(
        name="menutest",
        text="Main Menu",
        buttons=[
            XMLMenuButton(
                text="1stButton",
                callback_function="tests.xml2menu_test.test_callback",
                row=-1,
            ),
            XMLMenuButton(
                text="2nd Button",
                menu_link="menu2",
                row=0,
            ),
        ],
    )

    assert str(menu) == str(expected)

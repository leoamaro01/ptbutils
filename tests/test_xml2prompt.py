import sys, os

current_dir = sys.path[0]
parent = os.path.dirname(current_dir)
sys.path.append(parent)

from xml2bot.xml2prompt import xml2prompt, XMLPrompt


def test_xml2prompt():
    import prompt_functions, prompt_validators

    prompt = xml2prompt(
        """<?xml version="1.0" encoding="UTF-8"?>
<prompt name="say_anything" formats="sayer">
    <text>What would you like to say, {sayer}?</text>
    <validator function="prompt_validators.always_true" />
    <callback function="prompt_functions.echo_that_shit" />
    <cancel>
        <text>
            Cancel!!!
        </text>
        <callback function="prompt_functions.get_slapped_again" />
    </cancel>
</prompt>"""
    )
    assert prompt == XMLPrompt(
        name="say_anything",
        formats=["sayer"],
        text="What would you like to say, {sayer}?",
        callback=prompt_functions.echo_that_shit,
        validator=prompt_validators.always_true,
        cancel_text="Cancel!!!",
        cancel_callback=prompt_functions.get_slapped_again,
    )

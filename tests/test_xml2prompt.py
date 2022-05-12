import sys, os

current_dir = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current_dir)

sys.path.append(parent)

import xml2bot.xml2prompt as xml2prompt


def test_xml2prompt():
    import prompt_functions, prompt_validators

    prompt = xml2prompt.parse_prompt(
        os.path.join(current_dir, "prompts/say_anything_prompt.xml")
    )

    comparable = xml2prompt.XMLPrompt(
        name="say_anything",
        formats=["sayer"],
        text="What would you like to say, {sayer}?",
        callback=prompt_functions.echo_that_shit,
        validator=prompt_validators.always_true,
        cancel_text="Cancel!!!",
        cancel_callback=prompt_functions.get_slapped_again,
    )

    print(prompt.__dict__)
    print(comparable.__dict__)

    assert prompt == comparable

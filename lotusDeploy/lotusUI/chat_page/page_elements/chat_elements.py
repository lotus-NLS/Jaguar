from element_types import InputElem, DivElem
from styling import Style, Percentage, Pixels, Cursor, Color, Position, Display

userInput = InputElem(
    the_id = 'text_bar',
    placeholder='Type a message...',
    style=Style(
        width=Percentage(80),
        margin_right=Pixels(num_pixels=10)
    )
)
btn = DivElem(
    div_id='Send',
    children='Click Me',
    style=Style(
        padding=Pixels(num_pixels=10),
        cursor=Cursor.POINTER(),
        color=Color.WHITE(),
        background_color=Color.BLUE()
    )
)
bottom_container = DivElem(
    div_id='bottom-container',
    children=[userInput.component, btn.component],
    style=Style(
        position=Position.FIXED(),
        bottom=Pixels(num_pixels=0),
        width=Percentage(100),
        display=Display.FLEX(),
        justify_content="space-between",
        padding=Pixels(num_pixels=10),
        background_color=Color.LIGHT_GRAY()
    )
)
chat_window = DivElem(
    div_id='chat-window',
    children=[],
    style=Style(
        overflow_y="auto",
        height=f'85vh',
        padding=Pixels(num_pixels=10),
        margin_bottom=Pixels(num_pixels=10),
        border="1px solid {}".format(Color.LIGHT_GRAY())
    )
)

def get_settings():
    return dict(

        size=(1000, 500),  # standard size of window (Tuple[int, int] or (1000, 500) by default if None)
        max_size=None,  # maximum size of window (Tuple[int, int] or None)
        min_size=(800, 400),  # minimum size of window (Tuple[int, int] or None)
        window_icon='visualElements/icon.png',
        close_icon='classes/framelessWindow/buttons/close.png',
        maximize_icon='classes/framelessWindow/buttons/maximize.png',
        restore_icon='classes/framelessWindow/buttons/restore.png',
        minimize_icon='classes/framelessWindow/buttons/minimize.png',

    )
import kayaku


def init_kayaku():
    kayaku.initialize({"{**}": "./config/{**}"})

    from library.model.config import MelchiorConfig

    kayaku.create(MelchiorConfig)


def validate_config():
    pass

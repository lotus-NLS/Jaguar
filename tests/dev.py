# from engine import LotusEngine
#
# # ----------------------------------------------
#
# the_engine = LotusEngine(use_local=True)
# the_engine.launch(on_console=True)

from hollarek.logging import get_logger, LogSettings



logger = get_logger(settings=LogSettings(include_call_location=True))

try:
    raise RecursionError
except:
    logger.log(f'Example message',with_traceback=True)


try:
    from .panelizer_action import PanelizerAction
    PanelizerAction().register()
except Exception as e:
    import sys
    import logging
    logging.exception("Failed to register Panelizer plugin")

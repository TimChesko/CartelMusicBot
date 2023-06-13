

class DialogsCollector:
    def __init__(self):
        self.dialogs: list = []

    def include_dialog(self, dialog_collector):
        if isinstance(dialog_collector, DialogsCollector):
            self.dialogs.extend(dialog_collector.dialogs)
        else:
            self.dialogs.append(dialog_collector)

    def include_dialogs(self, *dialogs_collector) -> None:
        if not dialogs_collector:
            raise ValueError("At least one dialog must be provided")
        for router in dialogs_collector:
            self.include_dialog(router)

    def __repr__(self):
        return repr(self.dialogs)

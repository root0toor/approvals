class LogContext:
    taskid: str = "1324"
    usergroupid: int = None
    userid: int = None
    collaborator_id: int = None
    route: str = None
    host: str = None
    ip: str = None
    duration: int = None
    method: str = None

    @staticmethod
    def _as_dict():
        context = {}
        for attr in dir(LogContext):
            if attr.startswith("_"):
                continue
            context[attr] = getattr(LogContext, attr)
        return context

    @classmethod
    def _reset(cls):
        cls.duration = None

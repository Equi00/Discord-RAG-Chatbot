import logging
import datetime
from typing import override
import json

class AppJSONFormatter(logging.Formatter):
    def __init__(self, *, fmt_keys: dict[str, str] | None = None):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)
    
    def _prepare_log_dict(self, record: logging.LogRecord):
        always_fields = {
            "message": record.getMessage(),
            "timestamp": datetime.datetime.fromtimestamp(
                record.created, tz=datetime.timezone.utc
            ).isoformat()
        }

        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatException(record.stack_info)

        message = {}

        for key, val in self.fmt_keys.items():
            if val in always_fields:
                message[key] = always_fields.pop(val)
            elif hasattr(record, val):
                value = getattr(record, val)
                if value:
                    message[key] = value

        message.update(always_fields)

        return message
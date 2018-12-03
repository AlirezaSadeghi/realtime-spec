from realtime.helpers import UtilityHelper


class ValidatorBase(object):

    def __init__(self, data):
        self._data = data
        self._errors = []

    def add_errors(self, err):
        self._errors.append(err)

    @property
    def errors(self):
        return self._errors


class PostValidator(ValidatorBase):
    _TIMESTAMP = 'timestamp'
    _ACTION = 'action'
    _USER = 'user'

    FIELDS = [_TIMESTAMP, _ACTION, _USER]

    SUPPORTED_ACTIONS = ['click', 'impression']

    def is_valid(self):
        for key in PostValidator.FIELDS:
            if key not in self._data or not self._data.get(key).strip():
                self.add_errors('%s - Is required' % key)
                return False

        timestamp = self._data[PostValidator._TIMESTAMP]
        if not UtilityHelper.ts_is_valid(timestamp):
            self.add_errors('Invalid timestamp: %s' % timestamp)
            return False

        action = self._data[PostValidator._ACTION]
        if action not in PostValidator.SUPPORTED_ACTIONS:
            self.add_errors('Action not supported: %s' % action)
            return False

        return True


class GetValidator(ValidatorBase):
    _TIMESTAMP = 'timestamp'

    FIELDS = [_TIMESTAMP]

    def is_valid(self):
        if GetValidator._TIMESTAMP not in self._data:
            self.add_errors('%s - Is required' % GetValidator._TIMESTAMP)
            return False

        timestamp = self._data[GetValidator._TIMESTAMP]
        if not UtilityHelper.ts_is_valid(timestamp):
            self.add_errors('Invalid timestamp: %s' % timestamp)
            return False

        return True

import datetime
import sys
import json


class Base(object):
    """Base object so we can set attributes without setting the access time"""

    def _remove(self):
        return



class LazyLoader(Base):
    def __init__(self, _id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super(Base, self).__setattr__('id', _id)
        super(Base, self).__setattr__('_loaded', False)

    def __sizeof__(self):
        return super().__sizeof__() + sys.getsizeof(self.id) + sys.getsizeof(self._loaded)

    def _remove(self):
        del self.id
        del self._loaded
        return super()._remove()

    def __getattribute__(self, item):
        if item is 'id':
            return super(Base, self).__getattribute__('id')
        if not super(Base, self).__getattribute__('_loaded'):
            super(Base, self).__getattribute__('_load')()
        return super(Base, self).__getattribute__(item)

    def __setattr__(self, key, value):
        super(object, self).__getattribute__('_store')(key, value)
        return super(Base, self).__setattr__(key, value)

    def __setitem__(self, key, value):
        super(Base, self).__getattribute__('_store')(key, value)
        return super().__setitem__(key, value)

    def __getitem__(self, item):
        if not super(Base, self).__getattribute__('_loaded'):
            super(Base, self).__getattribute__('_load')()
        return super().__getitem__(item)

    def _load(self):
        if super(Base, self).__getattribute__('id') is None:
            raise IndexError('The ID is not set')
        pass  # TODO implement this. Load source and destination
        super(Base, self).__setattr__('_loaded', True)

    def _store(self, key, value):
        pass

    def _unload(self):
        pass

    def __hash__(self):
        return super(Base, self).__getattribute__('id')  # Dont update last accessed when hashing


class LastAccessed(Base):
    def _get_current_time(self):
        return datetime.datetime.now()

    def _set_last_accessed(self):
        return super(Base, self).__setattr__('_last_accessed', super(Base, self).__getattribute__('_get_current_time')())

    def __sizeof__(self):
        return super().__sizeof__() + sys.getsizeof(self._last_accessed)

    def _remove(self):
        del self._last_accessed
        return super()._remove()

    def __getattribute__(self, item):
        if item not in ('_last_accessed', '_loaded'):
            super(Base, self).__getattribute__('_set_last_accessed')()
        return super(Base, self).__getattribute__(item)

    def __setitem__(self, key, value):
        super(Base, self).__getattribute__('_set_last_accessed')()
        return super(Base, self).__setitem__(key, value)

    def __getitem__(self, item):
        super(Base, self).__getattribute__('_set_last_accessed')()
        return super(Base, self).__getitem__(item)

    def _e_dec(func):
        def inner(self, rhs):
            self._set_last_accessed()
            try:
                rhs._set_last_accessed()
            except AttributeError:
                pass
            return func(self, rhs)
        return inner

    @_e_dec
    def __eq__(self, other):
        return other is self

    def _e(op):
        def func(self, rhs):
            super(Base, self).__getattribute__('_set_last_accessed')()
            if isinstance(rhs, LastAccessed):
                super(Base, rhs).__getattribute__('_set_last_accessed')()
            return getattr(super(), '{}'.format(op))(rhs)
        return func

    __lt__ = _e('__lt__')
    __le__ = _e('__le__')
    __gt__ = _e('__gt__')
    __ge__ = _e('__ge__')
    __ne__ = _e('__ne__')

    __add__ = _e('__add__')
    __sub__ = _e('__sub__')
    __mul__ = _e('__mul__')
    __truediv__ = _e('__truediv__')
    __floordiv__ = _e('__floordiv__')
    __mod__ = _e('__mod__')
    __divmod__ = _e('__divmod__')
    __pow__ = _e('__pow__')
    __lshift__ = _e('__lshift__')
    __rshift__ = _e('__rshift__')
    __and__ = _e('__and__')
    __xor__ = _e('__xor__')
    __or__ = _e('__or__')


class LazyLoadNode(LazyLoader, LastAccessed, dict):
    def __init__(self, _id=None, *args, **kwargs):
        super().__init__(_id, *args, **kwargs)
        super(Base, self).__setattr__('sources', set())
        super(Base, self).__setattr__('destinations', set())

    def __sizeof__(self):
        return super().__sizeof__() + (sys.getsizeof(self.sources) + sys.getsizeof(self.destinations))

    def _remove(self):
        del self.sources
        del self.destinations
        super()._remove()
        del self

    def __hash__(self):
        return super().__hash__()

    def __setattr__(self, key, value):
        return self.__setitem__(key, value)

    def __getattr__(self, item):
        return self.__getitem__(item)


class LazyLoadRelation(LazyLoader, LastAccessed, dict):

    def __init__(self, _id=None, source=None, label=None, destination=None, *args, **kwargs):
        super().__init__(_id, *args, **kwargs)
        super(Base, self).__setattr__('source', source)
        super(Base, self).__setattr__('destination', destination)
        super(Base, self).__setattr__('label', label)

    def __sizeof__(self):
        return super().__sizeof__() + (sys.getsizeof(self.source) + sys.getsizeof(self.destination) +
                                        sys.getsizeof(self.label))

    def _remove(self):
        del self.source
        del self.destination
        del self.label
        super()._remove()
        del self

    def __hash__(self):
        return super().__hash__()

    def __setattr__(self, key, value):
        return self.__setitem__(key, value)

    def __getattr__(self, item):
        return self.__getitem__(item)

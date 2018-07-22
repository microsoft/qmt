class TaskMetaclass(type):

    class_registry = {}

    def __new__(mcs, name, bases, class_dict):
        cls = type.__new__(mcs, name, bases, class_dict)

        TaskMetaclass.register_class(cls)

        return cls

    @staticmethod
    def register_class(class_to_register):
        TaskMetaclass.class_registry[class_to_register.__name__] = class_to_register

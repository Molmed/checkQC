
import importlib
import pkgutil

import checkQC.handlers
from checkQC.handlers.qc_handler import QCHandler


class QCHandlerNotFoundException(Exception):
    pass


class QCHandlerFactory(object):

    @staticmethod
    def create_subclass_instance(class_name, class_config):
        """
        This method will look for a class with the given `class_name` in the `checkQC.handlers` module.
        If it can find a class with a matching name it will return a instance of that class.
        :param class_name: the name of the class to instantiate
        :param class_config: dictionary with configuration for the class
        :return: A instance of the class represented by class_name
        """
        package = checkQC.handlers
        prefix = package.__name__ + "."

        modules = list(pkgutil.iter_modules(package.__path__, prefix))
        for importer, modname, ispkg in modules:
            importlib.import_module(modname)
        qc_handler_subclasses = list(QCHandler.__subclasses__())
        try:
            i = list(map(lambda clazz: clazz.__name__, qc_handler_subclasses)).index(class_name)
            return qc_handler_subclasses[i](qc_config=class_config)
        except ValueError:
            raise QCHandlerNotFoundException("Could not identify a QCHandler with name: {}".format(class_name))


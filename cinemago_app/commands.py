import unittest
from flask.ext.script import Command, Option


class TestCommand(Command):

    option_list = (
        Option('--directory', '-d', dest='directory'),
    )

    def run(self, directory):
        target = 'tests'
        if directory is not None:
            target += '/{dir}'.format(dir=directory)
        tests = unittest.TestLoader().discover(target)
        unittest.TextTestRunner(verbosity=2).run(tests)

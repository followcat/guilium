# This code is part of the guilium project.
# Copyright (C) 2013-2016 The guilium project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os
import sys
import time
import shlex
import inspect
import importlib

import nose
import nose.core
import nose.util
import nose.config
import nose.failure
import nose.plugins

import core.runtime
import core.test
import nose_plugin
import nose_plugin.suite


class Guilium(nose.plugins.Plugin):
    """"""
    config=nose.config.Config()
    sut = []

    def options(self, parser, env):
        """"""
        nose.plugins.Plugin.options(self, parser, env)
        parser.add_option('--stub', action='store',
                          dest='stub',
                          metavar="DEVICEstub",
                          help="Specify the stub.")
        parser.add_option('--sut', action='store',
                          dest='sut',
                          metavar="DEVICE1,DEVICE2",
                          help="Specify the system under test.")
        parser.add_option('--runlog', action='store_true',
                          dest='runlog',
                          default=False,
                          help="if run from the log file")
        return parser

    def configure(self, options, config):
        """Read system under test from options"""
        nose.plugins.Plugin.configure(self, options, config)
        options.sut = options.sut.split(',')

    def prepareTestLoader(self, loader):
        """Set the system under test in loader config"""
        loader.suiteClass=nose_plugin.ContextSuiteFactory(config=self.config,
                                        suiteClass=nose_plugin.ContextSuite)
        self.suiteClass = loader.suiteClass
        self.loader = loader

    def wantClass(self, cls):
        """Select only subclass is core.test.Test"""
        return not(self.runlog) and issubclass(cls, core.test.Test)
        
    def wantFunction(self, function):
        """Do not select TestLogProcedureGenerator"""
        return "Test" in function.__name__ 

    def makeTest(self, obj, parent=None):
        """"""
        if nose.util.isclass(obj):
            if issubclass(obj, core.test.Test):
                return self.loadTestsFromTestCase(obj)
        elif inspect.isfunction(obj):
            if parent and obj.__module__ != parent.__name__:
                obj = nose.util.transplant_func(obj, parent.__name__)
            if nose.util.isgenerator(obj):
                return self.loadTestsFromGenerator(obj, parent)

    def loadTestsFromTestCase(self, cls):
        """"""
        return self.suiteClass(tests=[cls(application_class=self.application_class),])

    def loadTestsFromGenerator(self, generator, module):
        """"""
        def generate(g=generator, m=module):
            generated = False
            try:
                for test in g():
                    test_func, arg = self.loader.parseGeneratedTest(test)
                    generated = True
                    yield nose_plugin.suite.FunctionTestCase(test_func, config=self.config, arg=arg, descriptor=g)
                if not generated:
                    yield self.no_generate
            except KeyboardInterrupt:
                raise
            except:
                exc = sys.exc_info()
                yield nose.failure.Failure(exc[0], exc[1], exc[2],
                              address=nose.util.test_address(generator))
        return self.suiteClass(generate, context=generator, can_split=False)
    
    def no_generate(self, args):
        """this function is defined to skip test if a generator create nothing to test"""
        pass


class TestRunner(nose.core.TextTestRunner):

    def run(self, test):
        """Overrides to provide plugin hooks and defer all output to
        the test result class.
        """
        #from father class code
        wrapper = self.config.plugins.prepareTest(test)
        if wrapper is not None:
            test = wrapper

        wrapped = self.config.plugins.setOutputStream(self.stream)
        if wrapped is not None:
            self.stream = wrapped

        result = self._makeResult()
        start = time.time()

        runtime = core.runtime.Runtime(self.config.options)
        runtime.setup_environment()
        runtime.start_test()
        setattr(test.config, 'runtime', runtime)
        test(result)

        #from father class code
        stop = time.time()
        result.printErrors()
        result.printSummary(start, stop)
        self.config.plugins.finalize(result)
        return result

class TestProgram(nose.core.TestProgram):
    def runTests(self):
        self.testRunner = TestRunner(stream=self.config.stream,
                                              verbosity=self.config.verbosity,
                                              config=self.config)
        super(TestProgram, self).runTests()


if __name__ == '__main__':
    sys.argv = sys.argv + shlex.split('--nologcapture')
    TestProgram(addplugins=[Guilium()])


#!/usr/bin/env python
################################################################################
#                                                                              #
# Copyright (C) 2006-2007  Gary S Thompson                                     #
#                         (see https://gna.org/users/varioustoxins             #
#                                      for contact details)                    #
#                                                                              #
#                                                                              #
# This file is part of the program relax.                                      #
#                                                                              #
# relax is free software; you can redistribute it and/or modify                #
# it under the terms of the GNU General Public License as published by         #
# the Free Software Foundation; either version 2 of the License, or            #
# (at your option) any later version.                                          #
#                                                                              #
# relax is distributed in the hope that it will be useful,                     #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
# GNU General Public License for more details.                                 #
#                                                                              #
# You should have received a copy of the GNU General Public License            #
# along with relax; if not, write to the Free Software                         #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    #
#                                                                              #
################################################################################



''' unit_test_runner provides utilities for the running of unit tests from the
    command line or within the relax testing frame work.

    Unit tests in the relax frame work are stored in a directory structure
    rooted at <relax-root-directory>/test_suite/unit_tests. The directory
    unit tests contains a directory structure that mirrors the relax directory
    structure and which ideally contains one unit test file/module for each
    file/module in the relax framework. The default convention is that the unit
    test module for a relax module called <relax-module> is called
    test_<relax-module> (stored in test_<relax-module>.py). The unit test module
    test_<relax-module> should then contain a class called Test_<relax-module>
    which is a child of TestCase and contains methods whose names start with
    'test' and take no arguments other than self.

    A concrete example:

    for class <relax-root-directory>/maths-fns/chi2.py FIXME:***complete***




    The framework can discover sets of unit tests from the file system and add
    them to TestSuites either from the command line or programmatically from
    inside another program. It also has the ability to search for a  root unit
    test and system directory from a position anywhere inside the unit test
    hierarchy.

    TODO: examine PEP 338 and runpy.run_module(modulename): Executing Modules as Scripts
          for a later version of relax that is dependant on python 2.5
    TODO: split out runner part from search part
'''

import os,re,unittest,string,sys
from optparse import OptionParser
from textwrap import dedent
from copy import copy



# constants
###########
PY_FILE_EXTENSION='.py'
PY_UNIT_TEST_PATTERN='test_.*\.py$'

# utility functions
###################


def get_startup_path():
    '''Get the path of the directory the program started from.

       The startup path is the first path in sys.path (the internal PYTHONPATH)
       by convention. If the first element of sys.path is an empty trying the
       current working directory is used instead.

       @rtype:  string
       @return: a file system path for the current operating system
    '''

    startup_path = sys.path[0]
    if startup_path == '':
        startup_path = os.getcwd()
    return startup_path


def import_module(module_path):
    ''' import the python module named by module_path

        @type module_path: a string containing a dot separated module path
        @param module_path: a module path in python dot separated format
                            note: this currently doesn't support relative module
                            paths as defined by pep328 and python 2.5
        @rtype:     list of class module instances or None
        @return:    the module path as a list of module instances or None
                    if the module path cannot be found in the python path

        '''

    module = None
    result = None

    #try:
    module = __import__(module_path)
    #except:
    #    print 'failed'
    #    sys.exit()

    if module != None:
        result = [module]
        components = module_path.split('.')
        for component in components[1:]:
            module = getattr(module, component)
            result.append(module)
    return result


def get_module_relative_path(package_path, module_name, root_paths=None):
    '''Find the relative path of a module to one of a set of root paths using
       a  list of package paths and a module name.

       As the module may match more than one path the first path that
       can contain it is chosen.

       @type  package_path: string
       @param package_path: path of a python packages leading to module_name


       @type module_name: string
       @param module_name: the name of the module to load

       @type  root_paths: sequence of strings
       @param root_paths: a set of paths to search for the module in.if None is
              passed the list is initialized from the internal PYTHONPATH
              sys.path. Elements which are empty strings are replace with
              the current working directory sys.getcwd()


       @returns: a relative module path to one of the rootPaths which is
                 separated by '.'s if the modulePath is a subpath of one of
                 the root paths, otherwise None

    '''

    relative_path = None
    if root_paths == None:
        root_paths = sys.path
    for root_path in root_paths:
        root_path = segment_path(os.path.abspath(root_path))
        package_path = segment_path(os.path.abspath(package_path))

        common_prefix = get_common_prefix(root_path, package_path)
        if common_prefix == root_path:
            relative_path = package_path[len(common_prefix):]
            break

    if relative_path != None:
        relative_path = '.'.join(relative_path)

        if relative_path != '':
            relative_path = '.'.join((relative_path, module_name))
        else:
            relative_path = module_name



    return relative_path


def get_common_prefix(path1, path2):
    '''Get the common prefix between two paths.

       @type path1: a list of path segments
       @param path1: the first path to be compared

       @type path2: a list of path segments
       @param path2: the second path to be compared

       @return: the common path shared between the two paths starting from the
                root directory as a list of segments. If there is no common
                path an empty list is returned.
    '''

    result_path = []
    for elem1,elem2 in map(None, path1, path2):
        if elem1 == None or elem2 == None:
            break

        if elem1 == elem2:
          result_path.append(elem1)
    return result_path


def segment_path(path, normalise=True):
    '''Segment a path into a list of components (drives, files, directories etc).

       @type path: a path
       @param path: the path to segment

       @type normalise: Boolean
       @param normalise: whether to normalise the path before starting.

       @result: a list of path segments
    '''

    if normalise:
        path = os.path.normpath(path)

    result  = []
    (head, tail) = os.path.split(path)
    if head =='' or tail == '':
        result.append(head+tail)
    else:
        while head != '' and tail != '':
            result.append(tail)
            head,tail = os.path.split(head)
        result.append(head+tail)
        result.reverse()
    return result


def join_path_segments(segments):
    '''Join a list of path segments (drives, files, directories etc) into a path.

       @type path: a list of path segments
       @param path: the path segments to join into a path

        @rtype: string
       @result: the path containing the joined path segments
    '''

    if len(segments) == 0:
        result = ''
    else:
        segments_copy = segments[:]

        segments_copy.reverse()

        result = segments_copy.pop()
        while len(segments_copy) > 0:
            result = os.path.join(result, segments_copy.pop())

    return result

class ExtendedException(Exception):
    def __init__(self,e,module):
        self.e=e
        self.module=module


    def __str__(self):
        result = self.e.__str__()
        result = result + '\n\n***WARNING: no tests from module %s will be run!!!' % self.module
        return result

class ImportErrorTestCase(unittest.TestCase):
    def __init__(self,module_name,syntax_error):
        super(ImportErrorTestCase,self).__init__('testImportError')
        self.syntax_error=syntax_error


    def testImportError(self):
        raise self.syntax_error
        #self.fail(self.syntax_error.__str__())


def load_test_case(package_path,  module_name, class_name):
    ''' load a testCase from the file system using a package path, file name
        and class name

        @type package_path: string with . separated fields
        @param package_path: path to the module as a list of package names
                             separated by dots

        @type module_name: string
        @param module_name: name of the module to load the class from

        @type class_name: string
        @param class_name: name of the class to load

        @rtype:
        @return:
        '''

    result = None
    packages = None
    package_path=get_module_relative_path(package_path, module_name)

    #catch syntax errors
    try:
        packages = import_module(package_path)
#    except ImportError,e:
#        result = unittest.TestSuite()
#        bad_syntax = ImportErrorTestCase('testImportError',e)
#        result.addTest(bad_syntax)
    except Exception,e:
        result = unittest.TestSuite()
        ee = ExtendedException(e,module_name)
        bad_syntax = ImportErrorTestCase('testImportError',ee)
        result.addTest(bad_syntax)


    if packages != None:
        # some input packages may not contain the required class
        if hasattr(packages[-1], class_name):
            clazz =  getattr(packages[-1], class_name)
            result = unittest.TestLoader().loadTestsFromTestCase(clazz)
    return result


#def load_test_case(package_path,  module_name, class_name):
#    ''' load a testCase from the file system using a package path, file name
#        and class name
#
#        @type package_path: string with . separated fields
#        @param package_path: path to the module as a list of package names
#                             separated by dots
#
#        @type module_name: string
#        @param module_name: name of the module to load the class from
#
#        @type class_name: string
#        @param class_name: name of the class to load
#
#        FIXME:
#        @rtype:
#        @return:
#        '''
#    result = None
#    package_path=get_module_relative_path(package_path, module_name)
#    packages = import_module(package_path)
#
#
#    if packages != None:
#        # some input packages may not contain the required class
#        if hasattr(packages[-1], class_name):
#            clazz =  getattr(packages[-1], class_name)
#            result = unittest.TestLoader().loadTestsFromTestCase(clazz)
#    return result



class Test_finder:
    '''Find and load unit test classes as a hierarchy of TestSuites and TestCases.

       The class provides functions for running or returning the resulting
       TestSuite and requires a root directory to start searching from.

       TestCases are identified by the class name matching a pattern
       (pattern_string)
    '''

    suite = unittest.TestSuite()
    '''the root test suite to which testSuites and cases are added'''

    def __init__(self, root_path=None, pattern_list=[PY_UNIT_TEST_PATTERN]):
        ''' Initialise the unit test finder.

            @type root_path: string
            @param root_path: the path to starts searching for unit tests from,
                              all sub directories and files  are searched

            @type pattern_list: list of string
            @param pattern_list: a lsit of regular expression patterns which identifie
                                   a file as one containing a unit test TestCase
        '''

        self.root_path = root_path
        if self.root_path == None:
            self.root_path = get_startup_path()
        self.patterns=[]
        for pattern in pattern_list:
            self.patterns.append(re.compile(pattern))
        self.paths_scanned = False


    def scan_paths(self):
        '''Scan directories and paths for unit test classes and load them into TestSuites

            @rtype: a hierachy of pyunit testSuites and testCases
        '''

        print self.root_path
        self.suite = unittest.TestSuite()
        suite_dictionary = {'':self.suite}
        for (dir_path, dir_names, file_names) in os.walk(self.root_path):
            # to remove warnings of unused names
            if __debug__:
                dir_names=dir_names

            for file_name in file_names:
                module_found = None
                for pattern in self.patterns:
                    if pattern.match(file_name):
                        module_found = file_name
                        break

                if module_found != None:
                    # build class name
                    module_found = os.path.splitext(module_found)[0]
                    class_name = string.upper(module_found[0]) + module_found[1:]


                    module_path = get_module_relative_path(dir_path, module_found)
                    #FIXME add verbose search option
                    #if self.verbose:
                    #    print 'loading module: ' + module_path


                    path  = ['']
                    for elem in module_path.split('.'):
                        old_path_key  =  '.'.join(path)
                        path.append(elem)
                        path_key = '.'.join(path)
                        if path_key not in suite_dictionary:
                            test_suite = unittest.TestSuite()
                            suite_dictionary[path_key]=test_suite
                            suite_dictionary[old_path_key].addTest(test_suite)

#                     modules = import_module(module_path)
#                     print 'modules: ', modules
#                     clazz =  getattr(modules[-1], class_name)
#                     suite_dictionary[path_key].addTest(unittest.TestLoader().loadTestsFromTestCase(clazz))
                    found_test_case = load_test_case(dir_path, module_found, class_name)
                    if found_test_case != None:
                        suite_dictionary[path_key].addTest(found_test_case)

        return self.suite

class Unit_test_runner(object):
    '''Class to run a particular unit test or a directory of unit tests.'''

    #constants
    ##########

    TEST_SUITE_ROOT='test-suite-root_constant'
    ''' @type TEST_SUITE_ROOT: string
        @ivar TEST_SUITE_ROOT: constant indicating the use of the current unit test suite found from the root_path'''

    system_path_pattern = ['test_suite' + os.sep + 'unit_tests', os.pardir + os.sep + os.pardir]
    ''' @type system_path_pattern: list of strings
        @ivar system_path_pattern: a search template for the directory in which relax is installed.
                                 The directory which relax is installed in is viewed as the the 'PYTHONPATH'
                                 of the classes to be tested. It must be unique and defined
                                 relative to the test suite. For the current setup
                                 in relax this is (\'test_suite\', /'..\'). The first string is a
                                 directory structure to match the second string is a relative path from that
                                 directory to the system directory. The search is started from the
                                 value of root_path in the file system.
    '''

    unit_test_path_pattern = ['test_suite' + os.sep + 'unit_tests', os.curdir]
    '''  @type unit_test_path_pattern: a list of strings
         @ivar unit_test_path_pattern: a search template for the directory from which all unit
                                       module directories descend. For the current setup in relax
                                       this is (\'unit_tests\', \'.\'). The search is started from the
                                       value of root_path in the file system.
    '''

    test_case_patterns = ['test_.*\.py$']
    '''  @type  test_case_patterns: a list of strings containing regex patterns
         @ivar  test_case_patterns: a list of regex patterns against which files will be
                tested to see if they are expected to contain unit tests. If
                the file has the correct pattern the module contained inside the
                file will be searched for testCases e.g in the case of test_float.py
                the module to be searched for would be test_float.Test_float.
    '''

    def __init__(self, root_path=os.curdir, test_module=None, search_for_root_path=True,
                  search_for_unit_test_path=True, verbose = False):
        '''Initialise the unit test runner.

          @type  root_path: a string containing a directory name
          @param root_path: root path to start searching for modules to unit test
                 from. Two special cases arise: if the string contains '.'
                 the search starts from the current working directory, if the value is
                 the special value TEST_SUITE_ROOT defined in this class the root of the
                 test suite is sought from the current working directory using
                 find_unit_test_directory_path() and used instead. Default current
                 working directory.

          @type  test_module: string
          @param test_module: the name of a module to unit test. If the variable
                 is None a search for all unit tests using <test-pattern> will start
                 from <root_path>, if the variable is '.' a search for all unit tests will
                 commence from the current working directory, otherwise it will be used as
                 a module path from the
                 current root_path or CHECKME: ****module_directory_path****. The module name can be in the directory path format
                 used by the current operating system or a unix style path with /'s including
                 a final .py extension or a dotted moudle name

          @type  search_for_root_path: boolean
          @param search_for_root_path: whether to carry out a search from the root_directory
                                       using self.system_path_pattern to find the directory self.system_directory
                                       if no search is carried out self.system_directory is set to None and it is
                                       the responsibility of code creating the class to set it before self.run
                                       is called

          @type  search_for_unit_test_path: boolean
          @param search_for_unit_test_path: whether to carry out a search from the root_directory
                                           using self.unit_test_path_patter to find the directory self.unit_test_directory
                                           if no search is carried out self.unit_test_directory is set to None and it is
                                           the responsibility of code creating the class to set it before self.run
                                           is called



         @type  verbose: Boolean
         @param verbose: produce verbose output during testing e.g. directories
                 searched root directories etc
        '''

        # setup root path
        # deal with finding root of unit test hierachy
        if root_path is self.TEST_SUITE_ROOT:
            root_path = self.find_unit_test_directory_path(root_path)

        # deal with using pwd
        elif root_path == os.curdir:
            root_path =  os.getcwd()

        self.root_path =  root_path

        if (search_for_root_path) == True or (search_for_unit_test_path == True):
            if verbose:
                print 'searching for paths'
                print '-------------------'
                print ''

         # find system directories or leave it for someone else as needed
        if search_for_root_path:

            self.system_directory = self.get_first_instance_path(root_path,
                                                                 self.system_path_pattern[0],
                                                                 self.system_path_pattern[1])


            if self.system_directory == None:
                raise Exception("can't find system directory start from %s" % root_path)
            else:
                if verbose:
                    print 'search for system directory found:    %s' % self.system_directory
        else:
            self.system_directory = None

        if search_for_unit_test_path:
            self.unit_test_directory = self.get_first_instance_path(root_path,
                                                                    self.unit_test_path_pattern[0],
                                                                    self.unit_test_path_pattern[1])
            if self.unit_test_directory == None:
                raise Exception("can't find unit test directory start from %s" % root_path)
            else:
                if verbose:
                    print 'search for unit test directory found: %s' % self.unit_test_directory
        else:

            self.unit_test_directory = None

        if (search_for_root_path) == True or (search_for_unit_test_path == True):
            if verbose:
                print ''

        #deal with test_module
        if test_module == None:
            test_module=self.root_path
        elif test_module == os.curdir:
            test_module =  os.getcwd()
        elif test_module == self.TEST_SUITE_ROOT:
            test_module = self.unit_test_directory


        self.test_module = test_module

        # other instance variables
        self.verbose = verbose


    def get_first_instance_path(self, path, target_path, offset_path=os.curdir):
        '''Get the minimal path searching up the file system to target_directory.

            the algorithm is that we repeatedly chop the end off path and see if
            the tail of the path matches target_path If it doesn't match we search
            in the resulting directory by asspending target_path and seeing if it exists
            in the file system. Finally once the required directory structure has been
            found  the offset_path is appended to the found path and the resulting path
            normalised


            Note the algorithm understands .. and .

            @type path:  a directory path in a string
            @param path: a directory path to search up

            @type  target_path: a directory  name in a string
            @param target_path: a directory to find in the path or
                                     below one of the elements in the path

             @type offset_path: string containing a relative path
             @param offset_path: an relative path offset to add to the path that has been
                                 found to give the result directory

            @rtype: string containing a path
            @return: the path that has been found or None if the path cannot be found
                     by walking up and analysing the current directory structure
        '''

        seg_path = segment_path(os.path.normpath(path))
        seg_target_directory = segment_path(target_path)
        seg_target_directory_len = len(seg_target_directory)

        found_seg_path = None
        while len(seg_path) > 0 and found_seg_path == None:


           if seg_path[-seg_target_directory_len:] == seg_target_directory[-seg_target_directory_len:]:
               found_seg_path=seg_path
               break
           else:
               extended_seg_path =  copy(seg_path)
               extended_seg_path.extend(seg_target_directory)
               if os.path.exists(os.path.join(*extended_seg_path)):
                   found_seg_path=extended_seg_path
                   break

           seg_path.pop()


        result = None
        if found_seg_path != None and len(found_seg_path) != 0:
            seg_offset_path = segment_path(offset_path)
            found_seg_path.extend(seg_offset_path)
            result = os.path.normpath(join_path_segments(found_seg_path))

        return result


    def paths_from_test_module(self, test_module):
        '''Determine the possible paths of the test_module.

           it is assumed that the test_module can be either a path or
           a python module or package name including dots

           The following heuristics are used

                1. if the test_module=None add the value '.'
                2. if the test_module ends with a PY_FILE_EXTENSION append
                   test_module with the PY_FILE_EXTENSION removed
                3. add the module_name with .'s converted to /'s and
                   any elements of the form PY_FILE_EXTENSION removed
                3. repeat 2 and 3 with the last element of the path
                   repeated with the first letter capitalised


           note: we can't deal with module methods...

           @rtype: a set of strings
           @return: a set of possible module names in python . separated format
        '''

        result  = set()

        # check for current working directory
        if test_module == None:
            result.add(os.curdir)
        else:
            # add a direct file
            mpath = []
            test_module_segments=segment_path(test_module)
            for elem in test_module_segments:
                if elem.endswith(PY_FILE_EXTENSION):
                    mpath.append(os.path.splitext(elem)[0])
                else:
                    mpath.append(elem)

            result.add(tuple(mpath))

            mpath=copy(mpath)
            mpath.append(mpath[-1].capitalize())
            result.add(tuple(mpath))


            module_path_elems = test_module.split('.')


            module_norm_path = []
            for elem in module_path_elems:
                if elem != PY_FILE_EXTENSION[1:]:
                    module_norm_path.append(elem)


            # see if we can find a dot separated module
            # a package name first
            elems_ok = True
            for elem in module_norm_path:
                if len(segment_path(elem)) > 1:
                    elems_ok = False
                    break

            if elems_ok:
                result.add(tuple(module_norm_path))

                mpath=copy(module_norm_path)
                mpath.append(module_norm_path[-1].capitalize())
                result.add(tuple(mpath))


        return result


    def run(self, runner=None):
        '''Run a unit test or set of unit tests.

            @type runner: a unit test runner such as TextTestRunner or
                          a sub class of BaseGUITestRunner
            @param runner: a unit test runner such as TextTestRunner
                           None indicates use of the default unit test runner
                           for an example of how to write a test runner
                           @see the python documentation for TextTestRunner
                           in the python source


            @rtype: String
            @return: a string indicating success or failure of the unit tests
                     run
        '''

        msg = ''' Either set self.%s to a %s directory or set search_for_%s_path in
                  self.__init__ to True'''
        msg=dedent(msg)
        if self.unit_test_directory ==  None:
            raise Exception(msg % ('unit_test_directory', 'unit test', 'unit_test'))
        if self.system_directory == None:
            raise Exception(msg % ('system_directory', 'system', 'root'))


        print 'testing units...'
        print '----------------'
        print


        module_paths = self.paths_from_test_module(self.test_module)
        if self.verbose:
            print 'root path:          ', self.root_path
            print 'system directory:   ', self.system_directory
            print 'unit test directory:', self.unit_test_directory
            print ''
            for i,elem in enumerate(module_paths):
                print 'module path %d:  %s'  % (i,elem)
            print ''


        # add SystemDirectory to python path
        sys.path.pop(0)
        sys.path.insert(0,self.system_directory)



        tests = None

        # use search path first
        for module_path in module_paths:
            module_string = os.path.join(*module_path)

            if os.path.isdir(module_string):
                #iterate and load unit tests from module path
                finder = Test_finder(module_string, self.test_case_patterns)
                finder.scan_paths()
                tests=finder.suite
                break


        if tests == None:
            for module_path in module_paths:
                print module_path
                path_len = len(module_path)
                if path_len <= 1:
                    continue
                elif path_len == 2:

                    print 'trying to load 2: ',  module_path[0], module_path[1]
                    tests=load_test_case('', module_path[0], module_path[1])
                else:
                    print 'trying to load 3: ', os.path.join(*module_path[:-2]), module_path[-2], module_path[-1]
                    tests=load_test_case(os.path.join(*module_path[:-2]), module_path[-2], module_path[-1])
                if tests != None:
                    break

        if runner == None:
            runner = unittest.TextTestRunner()


        if self.verbose:
            print 'results'
            print '-------'
            print ''

        # Run the unit tests and catch the TestResult object.
        if tests != None and tests.countTestCases() != 0:
            results = runner.run(tests)
            result_string = results.wasSuccessful()
        elif tests == None:
            results=None
            result_string = 'Error: no test directories found for input module: %s' % self.test_module
            print result_string
        else:
            results=None
            result_string = 'note: no tests found for input module: %s' % self.test_module
            print result_string

        #Return the result of all the tests.
        return result_string

if __name__ == '__main__':

# should be unit tests ;-)
#    print '1',get_module_relative_path('/A/B/C', ('/A/B',))
#    print '2',get_module_relative_path('/A/B/C', ('/A/B/C',))
#    print '3',get_module_relative_path('/A/B/C', ('/A/B/D/W',))
#    print get_common_prefix(('A','B','C'), ('A','B','C'))
#    print get_common_prefix(('A','B','C'), ('A','B','C','D'))
#    print get_common_prefix(('D','E'), ('A','B','C','D'))
#    print get_common_prefix(('A','B','C','F'), ('A','B','C','D'))
#    print get_common_prefix((),('A','B','C','D'))
#    print ('A','B','C') == ('A','B','C')
    parser = OptionParser()

    parser.add_option("-v", "--verbose", dest="verbose",
                      help="verbose test ouput", default=False, action='store_true')

    parser.add_option("-u", "--system", dest="system_directory",
                      help="path to relax top directory which contains test_suite", default=None)

    parser.add_option("-s", "--utest", dest="unit_test_directory",help="default unit test directory",
                      default=None)

#    parser.add_option("-g", "--gui", dest="gui",help="run with a gui",default=False, action='store_true')

    usage="""
    %%prog [options] [<file-or-dir>...]

      a program to find and run subsets of the relax unit test suite using pyunit.
      (details of how to write pyunit tests can be found in your python distributions
      library reference)


    arguments:
      <file-or-dir> = <file-path> | <dir-path> is a list which can contain
                      inter-mixed directories and files

      <file-path>  =  a file containing a test case class files of the same
                      name with the first letter capitalised

                      e.g. maths_fns/test_chi2.py will be assumed to contain
                      a test case class called Test_chi2

      <dir-path>   =  a path which will be recursivley searched for <file-path>s
                      which end in %s
      """ % PY_FILE_EXTENSION

    parser.set_usage(dedent(usage))

    (options, args) = parser.parse_args()

    search_system=True
    search_unit=True

    if options.system_directory != None:
        if not os.path.exists(options.system_directory):
            print "The path to the system directory doeesn't exist"
            print "provided path: %s" % options.system_directory
            print "exiting..."
            sys.exit(0)
        search_system=False

    if options.unit_test_directory != None:
        if not os.path.exists(options.unit_test_directory):
            print "The path to the system directory doeesn't exist"
            print "provided path: %s" % options.unit_test_directory
            print "exiting..."
            sys.exit(0)
        search_unit=False

    if len(args) < 1:
        args = [None]

    for arg in args:
        runner = Unit_test_runner(test_module=arg, verbose=options.verbose,
                                  search_for_unit_test_path = search_unit,
                                  search_for_root_path=search_system)

        if not search_system:
            runner.system_directory = options.system_directory

        if not search_unit:
            runner.unit_test_directory = options.unit_test_directory

        runner.run()

#    root = tk.Tk()
#    root.title("relax unit tests")
#    gui = unitgui.TkTestRunner(root)
#    runner.run()




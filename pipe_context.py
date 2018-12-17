#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Jared Webber
    jmw150530

:synopsis:
    Creates the Pipeline Context.

:description:
    This module creates the pipeline context using the formula manager to import
    formulas from a formulas.xml file. The asset_manager context is set by passing these
    formulas to the PathContext class which validates the path on disk and returns
    a completed path. The PipeContext class then has it's variables created with kwargs
    based upon the project formulas and the disk path.

:applications:
    Any applications that are required to run this runner, i.e. Maya.

:see_also:
    Any other code that you have written that this module is similar to.

"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Built-in
import os
import re as re
import path_lib as fm
from pipe_utils import IO
preferences = None
bpy = None
sep = os.path.sep
#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#


#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

from contextlib import contextmanager, AbstractContextManager
from pipe_enums import PIPELINE


class PipeContext(AbstractContextManager):
    """
    this stores pipeline values
    """

    def __init__(self, **kwargs):

        self._context:str = None
        self._old_context:list = []
        global preferences
        self.asset = kwargs.setdefault('asset', None)
        self.asset_type = kwargs.setdefault('asset_type', None)
        self.context_area = kwargs.setdefault('context_area', "pipeline")
        self.disk_type = kwargs.setdefault('disk_type', None)
        drive = PIPELINE.OS
        self.drive = kwargs.setdefault('drive', drive)
        self.project = kwargs.setdefault('project', None)
        self.preferences = None        
        self.user = False
        

    def __enter__(self):
        """
        Upon entering a fresh PipeContext Manager assign the current context to the platform specific base drive
        :return:
        """
        try:
            if not self.context and self.drive is not None:
                self.context = self.drive
        except AttributeError:
            IO.error("'drive' keyword not set")
        finally:
            pass


    def __exit__(self, exc_type, exc_value, traceback):
        """
        Set current context to the cached context
        :param exc_type:
        :param exc_value:
        :param traceback:
        :return:
        """
        
        if self.context and self.context == self.old_context[-1:]:
            self.old_context.pop()
        return self.context


    def __str__(self):
        pass


    def __repr__(self):
        pass


    # def __eq__(self):
        # pass


    # def __hash__(self):
    #     return hash((self.context))


    def context_init(self):
        if not self.context and self.drive is not None:
                self.context = self.drive


    @classmethod
    def get_path(cls, formula="pipe_base_dir", *args, **kwargs) -> str or list:
        """
        Evaluate a formula and return a path
        :param formula:
        :param args: positional arguments, e.g. parent_formula
        :param kwargs: keyword_arguments to pass to PipeContext
        :return: path
        """
        
        argv = None
        if args:
            argv = args

        IO.debug(f"Formula               : {formula}")
        IO.debug(f"Additional Forumlas   : {argv}")
        IO.debug(f"Keyword Arguments     : {kwargs}")

        pc = cls(**kwargs)
        with pc:
            if isinstance(formula, list):
                # Evaluate Multiple Paths
                for f in formula:
                    _eval = pc.eval_path
                    path = _eval(f, *args, **kwargs)
            else:
                # Evaluate Single Path
                _eval = pc.eval_path
                path = _eval(formula, *args, **kwargs)
            return pc.context


    def eval_path(self, formula, *args, **kwargs):
        """
        Evaluate a formula and return a path object
        :param formula: A string representing the formula to evaluate
        :param kwargs: Variables to pass to PipeContext
        :return: path
        """
        # Initialize PipeContext Instance in PathContext
        pcontext = PathContext(self)
        path = pcontext.get_path(formula, *args, **kwargs)
        self.context = path
        return path


    @classmethod
    def relpath(cls, new_path, start=None, path_type="bpy"):
        """Generate a relative path"""
        ctx = cls.context
        new_ctx = os.path.normpath(new_path)
        if start == ctx:
            start = ctx
        if path_type == 'bpy':
            return cls._bpy_relpath(new_path, start)
        else:
            return os.path.relpath(new_ctx, start=start)


    @staticmethod
    def _bpy_relpath(path, start=None):
        import bpy.path.relpath as relpath
        return relpath(path, start)


    @property
    def context(self) -> str:
        return self._context

    @context.setter
    def context(self, context_path:str):
        """
        Sets the current context
        Evaluates current context agains
        """
        # Get the current set context
        current_context = self._context
        if current_context and current_context != self._old_context[-1:]:
            # Check against the new context before appending the current one.
            if context_path != current_context:
                # Append the current context to the old context before switching
                self._old_context.append(current_context)
        self._context = context_path

    @context.deleter
    def context(self):
        base = preferences.pipe_base_dir
        if base:
            self._context = base
        else:
            self._context = None


    @property
    def old_context(self) -> list:
        return self._old_context

    @old_context.setter
    def old_context(self, context_path:str or list):
        if isinstance(context_path, str):
            self._old_context.append(context_path)
        elif isinstance(context_path, list):
            self._old_context = context_path


    def examine_path(self, path, pipe_base_dir=None, var=None) -> str or dict:
        """
        NOTE: NOT YET IMPLEMENTED
        Examine a path on disk and derive the current context
        :param path: Current Path to evaluate
        :param pipe_base_dir: Pipeline Base Directory
        :param var: Specific formula/path
        :return: path_item or path_dict
        """
        pcontext = PathContext(self)
        # Return a Single Path
        if var is None:
            path_item = pcontext.examine_path(path, pipe_base_dir=pipe_base_dir, var=var)
            return path_item
        # Return the entire Path Context
        else:
            path_dict = pcontext.examine_path(path, pipe_base_dir=pipe_base_dir, var=var)
            return path_dict
            

class PathContext(object):
    """
    this class resolves a real path on disk
    """

    def __init__(self, pipe_context):
        self.pipe_context = pipe_context
        self.path = None
        self.path_dict = None


    @staticmethod
    def create_path(path):
        os.makedirs(path, exist_ok=True)


    def get_path(self, formula, *args, **kwargs):
        """
        Return or Yield a formula path
        :param formula: formula to evaluate
        :param args[0]: parent_formula
        :param kwargs: keyword_arguments
        :return:
        """

        # Load Formula manager
        formula_manager = fm.FormulaManager(self.pipe_context.user)
        if args:
            for arg in args:
                parent_formula = arg
                formula_manager.get_formula(parent_formula)
        formula_pieces = formula_manager.get_formula(formula)
        return self._get_form_path(formula_pieces, **kwargs)


    def _get_form_path(self, formula_pieces, **kwargs):
        """Return a single formula using the passed in formula pieces"""
        return self._return_path(formula_pieces, **kwargs)


    def _return_path(self, pieces, **kwargs) -> str :
        """
        Return a normalized path by pulling values of formula pieces out of a dict
        :param path: list or set
        :param pieces: formula pieces
        :param y: yield
        :param kwargs: keyword arguments
        :return:
        """
        # Iterate over each piece
        path = []
        for piece in pieces:
            # No Bracketed Values to clean, put in path
            if not '{' in piece:
                path.append(piece)
                continue
            # Regex to find all bracketed values and clean them
            cleaned = re.findall(r'{(.*?)\}', piece, 0)
            # Check if the cleaned value is in kwargs
            if cleaned[0] in kwargs:
                value = kwargs[cleaned[0]]
                path.append(value)
            # Check if the cleaned value is in PipeContext
            elif cleaned[0] in self.pipe_context.__dict__.keys():
                value = self.pipe_context.__dict__[cleaned[0]]
                path.append(value)
        # IO.debug("Returning Path")
        return os.path.normpath((os.path.sep).join(path))


    def examine_path(self, path, pipe_base_dir=None, var=None):
        """

        :param path: Current context path we want to examine
        :param pipe_base_dir: Pipeline Base Directory Path
        :param var: Variable we want to examine in this path
        :return:
        """

        return ""
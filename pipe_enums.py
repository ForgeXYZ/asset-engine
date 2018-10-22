#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Jared Webber

:synopsis:
    This module contains enums for the OS/Platform, Rigs, and Disciplines

:description:
    

"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#
import os
import platform
import sys
#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#

def enum(**enums):
    return type('Enum', (), enums)

OSDrives = enum(WINDOWS='C:/', LINUX='/home/', MAC='/home/')

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#
class PIPE_OS(object):
    def __init__(self):
        self.os    = None
        self.drive = None
        self.eval_os()
        self.eval_drive()


    def eval_os(self):
        self.os = platform.system()


    def eval_drive(self):
        if self.os == 'Windows':
            self.drive = OSDrives.WINDOWS
        elif self.os == 'Linux':
            self.drive = OSDrives.LINUX
        elif self.os == 'Darwin':
            self.drive = OSDrives.MAC


class PIPE_DISK(object):
    """Pipeline Disk enum"""

    CODE   = 'code'
    CONFIG = 'config'
    DATA   = 'data'
    RENDER = 'render'
    STORE  = 'store'
    WORK   = 'work'
    ALL    = [CODE, CONFIG, DATA, STORE, WORK]

    @classmethod
    def get_all(cls):
        return cls.ALL

class DisciplineType(object):
    """Discipline Types base class with long and short names"""
    def __init__(self, long, short):
        self.long  = long
        self.short = short

    def get_long(self):
        return self.long

    def get_short(self):
        return self.short


class PIPE_DISC:
    """Pipeline Discipline enum"""
    MODEL           = DisciplineType('modeling', 'mdl')
    SURFACE         = DisciplineType('shading', 'surf')
    RIG             = DisciplineType('rigging', 'rig')
    LAYOUT          = DisciplineType('layout', 'lay')
    ANIMATION       = DisciplineType('animation', 'ani')
    LIGHT           = DisciplineType('lighting', 'lit')
    COMP            = DisciplineType('compositing', 'comp')


RigTypes = enum(ANI='ani_rig',
                CACHE='cache_rig',
                LAY='lay_rig',
                MODEL='model_rig',
                PREVIS='previs_rig',
                LIT='lit_rig')


class PIPELINE:
    _pipe_base = PIPE_OS()
    OS = _pipe_base.os
    DRIVE = _pipe_base.drive
    DISC = PIPE_DISC
    DISK = PIPE_DISK


class FileSize:
    """
    Implements classmethod size() to return current bytes of a file or
    a human-readable string of the file size info.
    Using the traditional system, where a factor of 1024 is used::

    si system           -> size(2000000, system=si)             = 2M
    alternative system  -> size(2000000, system=alternative)    = 2MB
    """
    traditional = [
        (1024 ** 5, 'P'),
        (1024 ** 4, 'T'),
        (1024 ** 3, 'G'),
        (1024 ** 2, 'M'),
        (1024 ** 1, 'K'),
        (1024 ** 0, 'B'),
    ]

    alternative = [
        (1024 ** 5, ' PB'),
        (1024 ** 4, ' TB'),
        (1024 ** 3, ' GB'),
        (1024 ** 2, ' MB'),
        (1024 ** 1, ' KB'),
        (1024 ** 0, (' byte', ' bytes')),
    ]

    verbose = [
        (1024 ** 5, (' petabyte', ' petabytes')),
        (1024 ** 4, (' terabyte', ' terabytes')),
        (1024 ** 3, (' gigabyte', ' gigabytes')),
        (1024 ** 2, (' megabyte', ' megabytes')),
        (1024 ** 1, (' kilobyte', ' kilobytes')),
        (1024 ** 0, (' byte', ' bytes')),
    ]

    iec = [
        (1024 ** 5, 'Pi'),
        (1024 ** 4, 'Ti'),
        (1024 ** 3, 'Gi'),
        (1024 ** 2, 'Mi'),
        (1024 ** 1, 'Ki'),
        (1024 ** 0, ''),
    ]

    si = [
        (1000 ** 5, 'P'),
        (1000 ** 4, 'T'),
        (1000 ** 3, 'G'),
        (1000 ** 2, 'M'),
        (1000 ** 1, 'K'),
        (1000 ** 0, 'B'),
    ]

    @classmethod
    def size(cls, bytes:bytes, system=alternative) -> str or bytes:
        """
        Return human-readable file size or bytes integer.

        :param bytes: bytes from file
        :param system: file-size formatting
        :return: file-size
        """
        for factor, suffix in system:
            if bytes >= factor:
                break
        amount = int(bytes / factor)
        if isinstance(suffix, tuple):
            singular, multiple = suffix
            if amount == 1:
                suffix = singular
            else:
                suffix = multiple
        return str(amount) + suffix

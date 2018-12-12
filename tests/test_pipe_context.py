# ----------------------------------------------------------------------------#
# ------------------------------------------------------------------ HEADER --#
"""
:author:
    Jared Webber
    
:synopsis:
    Test: Pipe Context Path Resolution

:description:
    This test suite evaluates the pipeline logic required for parsing
    formulas and turning them into paths on disk.
    
    Three Tests:

        1) Single Path 
        Find a 'pr_base_dir' path given a set of keyword arguments to establish context.

            - Evaluates 1 Path
            - Establishes Context with kwargs

        2) Child Paths
        Find an 'as_base_dir' path given a positional argument parent_formula ('p'), 
        and a set of keyword arguments to establish context.

            - Evaluates Parent Path to establish context
            - Evaluates Child Path within updated context

        3) Multiple Paths
        Find 'pipe_sbs_dir' and 'pr_as_dir' (a list of formulas), given a set of keyword -
        arguments to establish context.

            - Evaluates each path, while subsequently updating a shared context pointer.


    NOTE: CHANGE $PIPE_BASE_DIR = '/home/user/pipeline/' to a path that exists on 
    your system 

"""

# ----------------------------------------------------------------------------#
# --------------------------------------------------------------- IMPORTS ----#
import unittest, os
from pipe_utils import IO, bcolors
from pipe_context import PipeContext as PC
pipe_base_dir = os.path.join('home', 'user', 'pipeline')
# ----------------------------------------------------------------------------#
# --------------------------------------------------------------- FUNCTIONS --#
class PipeContextTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_single_path(self):
        IO.info("TEST ---| Single Path")
        path = PC.get_path(
            'pr_base_dir',
            drive=pipe_base_dir, project='avengers',
            asset_type='alien', asset="nova_prime_soldier.blend"
        ) # Get a path from PipeContext
        message = f"\n{bcolors.FAIL}  ERROR: {'Test 1: Single-Path Pipeline Context test failed'}\n"
        self.assertEqual(
            path, 
            (f"{os.path.join(pipe_base_dir, 'projects', 'avengers')}"),
            message
        )
        IO.block("Found Path: %s" % path)


    def test_child_path(self):
        IO.info("TEST ---| Child Path")

        path = PC.get_path(
            'as_base_dir', 'pr_as_type_dir',
            drive=pipe_base_dir, project='project_2',
            asset_type='architecture', asset="empire_state_building"
        )
        message = f"\n{bcolors.FAIL}  ERROR: {'Test 2: Child-Path Pipeline Context test failed'}\n"
        self.assertEqual(
            path, 
            (f"{os.path.join(pipe_base_dir, 'projects', 'project_2', 'assets', 'architecture', 'empire_state_building')}"),
            message
        )
        IO.block("Found Path: %s" % path)
    

    def test_multi_path(self):
        IO.info("TEST ---| Multi Path")

        path_list = ['pipe_base_dir', 'pipe_mtlx_dir', 'as_tex_dir']
        path = PC.get_path(
            path_list, 'pr_as_type_dir', 'as_geo_dir',
            drive=pipe_base_dir, project='Interstellar',
            asset_type='Vehicles', asset="Endurance"
        )
        message = f"\n{bcolors.FAIL}  ERROR: {'Test 3: Multi-Path Pipeline Context test failed'}\n"
        self.assertEqual(
            path, 
            (f"{os.path.join(pipe_base_dir, 'projects', 'Interstellar', 'assets', 'Vehicles', 'Endurance', 'surfacing', 'textures')}"),
            message
        )
        IO.block("Found Path: %s" % path)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(PipeContextTest('test_single_path'))
    suite.addTest(PipeContextTest('test_child_path'))
    suite.addTest(PipeContextTest('test_multi_path'))
    return suite


if __name__ == '__main__':
    IO.info("-----| Executing Pipeline Test Suite   |-----")
    IO.block(f"Pipeline Base Directory ---| {pipe_base_dir}" )
    runner = unittest.TextTestRunner()
    runner.run(suite())
    IO.info("-----| Closing Pipeline Test Suite     |----- ")
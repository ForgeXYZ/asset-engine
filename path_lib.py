#!/usr/bin/env python

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Jared Webber

:synopsis:
    Interprets formulas defined via configuration files to generate real paths on disk

:description:
    FormulaManager 

"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Built-in
import re
import os
import sys
from pipe_utils import IO
preferences = None

#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#


#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

class FormulaManager(object):
    """
    Logical manager class for all formulas defined in the pipeline
    
    """
    def __init__(self, user=False):
        self.all_formulas = []
        self.formulas_dict = {}
        self.formula_disk = None
        self.formulas = []
        self.file_location = os.path.normpath(os.path.realpath(__file__)
                                              + '/../data/formulas/pipeline_formulas.cfg')
        self.project_file = os.path.normpath(os.path.realpath(__file__)
                                             + '/../data/formulas/project_formulas.cfg')
        self.asset_file = os.path.normpath(os.path.realpath(__file__)
                                           + '/../data/formulas/asset_formulas.cfg')
                                           
    def get_formula(self, formula=None):
        """Get a particular formula path by reading the associated formulas from disk"""
        if formula is not None:
            # Multiple Formulas
            if isinstance(formula, list):
                form_vals = []
                for form in formula:
                    self.read_formulas(formula=form)
                    form_val = self.parse_formulas(formula=form)
                    form_vals.append(form_val)
                # Return Multiple Forumlas
                return form_vals
            # Single Formula
            elif isinstance(formula, str):
                self.read_formulas(formula=formula)
                # Return One Forumla
                return self.parse_formulas(formula=formula)
        # All Formulas
        elif formula is None:
            # Return All Forumlas
            self.read_formulas()
            return self.parse_formulas()
        # Return None if Formula isn't in the dictionary:
        return None

    def read_formulas(self, formula=None):
        """Conditionally reads formula configuration files based on a passed in formula value"""

        class Formula:
            
            pass


        def _read(file_location=self.file_location):
            keep = []
            with open(file_location, 'r') as fh:
                for line in fh:
                    line = line.strip()
                    if ',' in line:
                        keep.append(line)
                        if '#' in line:
                            keep.remove(line)
            self.all_formulas = keep

        def _read_projects(file_location=self.project_file):
            with open(file_location, 'r') as fh:
                for line in fh:
                    line = line.strip()
                    if 'pr_' in line:
                        self.all_formulas.append(line)
                        if '#' in line:
                            self.all_formulas.remove(line)
            return self.all_formulas


        def _read_assets(file_location=self.asset_file):
            with open(file_location, 'r') as fh:
                for line in fh:
                    line = line.strip()
                    if 'as_' in line:
                        self.all_formulas.append(line)
                        if '#' in line:
                            self.all_formulas.remove(line)
            return self.all_formulas
        
        _read(file_location=self.file_location)

        # Conditionally read other formulas
        if 'pr_' in formula:
            _read_projects()
        if 'as_' in formula:
            _read_assets()
        if not formula:
            _read_projects()
            _read_assets()

            
    def parse_formulas(self, formula=None):
        """Split, clean and expand formulas after they have been read"""

        self.split_formulas()
        self.clean_formulas()
        self.expand_formulas()
        
        # Return Formula Values
        if formula:
            if formula in self.formulas_dict:
                formula_vals = self.formulas_dict[formula]
                return formula_vals.split()
        elif not formula:
            formula_vals = self.formulas_dict
            return formula_vals


    def split_formulas(self):
        """Split on equals signs and append the correct pieces"""

        all_formulas = self.all_formulas
        for formula_line in all_formulas:
            formula_pieces = formula_line.split(' = ')
            self.formulas_dict[formula_pieces[0]] = formula_pieces[1]
            self.formulas.append(formula_pieces[0])

        return self.formulas


    def clean_formulas(self):
        """Clean up the formulas from any unused characters"""

        for formula in self.formulas:
            clean_formula = self.formulas_dict[formula]
            clean_formula = clean_formula.replace(',', '')
            clean_formula = clean_formula.replace('\'', '')
            clean_formula = clean_formula.replace('(', '')
            clean_formula = clean_formula.replace(')', '')
            clean_formula = clean_formula.strip()
            self.formulas_dict[formula] = clean_formula
        
        return self.formulas_dict


    def expand_formulas(self):
        """Expand all the formulas using regex"""
        import re
        
        for formula in self.formulas:
            if not 'pipe_' in self.formulas_dict[formula]:
                if not 'pr_' in self.formulas_dict[formula]:
                    if not 'as_' in self.formulas_dict[formula]:
                        continue

            # Get the formula that we want to inherit values from.
            bracketed_values = re.findall(r'\{(.*?)\}', self.formulas_dict[formula])
            formula_to_switch = bracketed_values[0]
            if not formula_to_switch:
                continue
            
            # Get the formula with that value.
            legit_values = self.formulas_dict[formula_to_switch]
            replacement_str = "{%s}" % formula_to_switch
            
            if formula_to_switch in self.formulas_dict.keys():
                # Replace the 'pr_' value with the legit_values.
                current_value = self.formulas_dict[formula]
                current_value = current_value.replace(replacement_str, legit_values)
                self.formulas_dict[formula] = current_value


    def get_formula_disk(self, formula):
        """Checks the 'disk_type' key in the formula dict and then returns the value"""

        if formula in self.formulas_dict:
            formula_disk = self.formulas_dict['disk_type']
            self.formula_disk = formula_disk
            return self.formula_disk
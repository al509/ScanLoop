# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 16:23:44 2023

@author: Илья
after 
https://stackoverflow.com/questions/2121874/python-pickling-after-changing-a-modules-directory

"""

import io
import pickle


class RenameUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        renamed_module = module
        if module == "Scripts.SNAP_experiment":
            renamed_module = "SNAP_experiment"

        return super(RenameUnpickler, self).find_class(renamed_module, name)


def renamed_load(file_obj):
    return RenameUnpickler(file_obj).load()


def renamed_loads(pickled_bytes):
    file_obj = io.BytesIO(pickled_bytes)
    return renamed_load(file_obj)
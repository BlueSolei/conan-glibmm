#!/usr/bin/env python
# -*- coding: utf-8 -*-

class PkgEnv(object):
    def __init__(self, conanfile):
        self.conanfile = conanfile
        self.env = {}

    def add_pkg(self, dep_name, **args):
            deps = self.conanfile.deps_cpp_info[dep_name]
            CFLAGS = " -I".join([""] + deps.include_paths)
            LIBS   = " -L".join([""] + deps.lib_paths)
            LIBS  += " -l".join([""] + args.get('libs', deps.libs))

            prefix = args.get('prefix', dep_name.upper())

            cflags_key = prefix + '_CFLAGS'
            libs_key   = prefix + '_LIBS'

            self.env[cflags_key] = (self.env.get(cflags_key, '') + ' ' + CFLAGS).strip()
            self.env[libs_key]   = (self.env.get(libs_key  , '') + ' ' + LIBS).strip()

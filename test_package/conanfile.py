#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake
import os
from os import path

username = os.getenv("CONAN_USERNAME", "noface")
channel  = os.getenv("CONAN_CHANNEL", "testing")
version  = "2.48.1"
name     = "glibmm"

class TestPackage(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = (
        "%s/%s@%s/%s" % (name, version, username, channel),
    )
    build_requires = (
        "waf/0.1.1@noface/stable",
        "WafGenerator/0.0.5@noface/stable"
    )

    generators = "Waf"
    exports = "wscript"

    def imports(self):
        # Copy waf executable to project folder
        self.copy("waf", dst=".")

        self.copy("*.dll", dst="bin", src="bin")    # From bin to bin
        self.copy("*.dylib*", dst="bin", src="lib") # From lib to bin

    def build(self):
        self.build_path = path.abspath("build")

        self.run(
            "waf configure build -o %s" % (self.build_path),
            cwd=self.conanfile_directory)

    def test(self):
        exec_path = path.join(self.build_path, 'example')
        self.output.info("running test: " + exec_path)
        self.run(exec_path)

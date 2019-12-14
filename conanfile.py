import os
from os import path

from conans import ConanFile, tools
from conans.tools import download, untargz, check_sha256, pythonpath

from pkg_config import PkgEnv


class Recipe(ConanFile):
    name = "glibmm"
    version = "2.63.1"
    description = "glibmm, a C++ API for parts of glib that are useful for C++"
    license = "LGPL"
    url = "https://gitlab.com/no-face/glibmm-conan"  # recipe repo url
    lib_urls = {
        "project": "https://www.gtkmm.org",  # official page is same of gtkmm
        "repo": "https://git.gnome.org/browse/glibmm",
        "mirror_github": "https://github.com/GNOME/glibmm",
        "docs": "https://developer.gnome.org/glibmm/stable/"
    }

    settings = "os", "compiler", "arch"
    options = {
        "shared": [True, False],
    }
    default_options = (
        "shared=True",
    )

    requires = (
        "sigc++/2.10.0@bincrafters/stable",
        "glib/2.58.3@bincrafters/stable"
    )

    #    build_requires    = (
    #        "AutotoolsHelper/0.0.1@noface/experimental"
    #    )

    exports = "pkg_config.py"

    BASE_URL_DOWNLOAD = "https://download.gnome.org/sources/" + name
    VER_MAGOR = "{}.{}".format(*version.split('.')[:2])
    GLIBMM_FILE_BASE_NAME = "{}-{}".format(name, version)  # e.g. glibmm-2.63.1
    FILE_URL = "{}/{}/{}.tar.xz".format(BASE_URL_DOWNLOAD, VER_MAGOR, GLIBMM_FILE_BASE_NAME)
    FILE_SHA256 = '4f99e29bd0a67afd94c0d6fdad2b86bc5cd944cd5d4ff097520dc58b6c997ada'

    def source(self):
        zip_name = self.name + ".tar.xz"
        download(self.FILE_URL, zip_name)
        check_sha256(zip_name, self.FILE_SHA256)
        untargz(zip_name)  # will extract sources to a folder named GLIBMM_FILE_BASE_NAME

    def build(self):
        with tools.environment_append(self.build_env()):
            self.prepare_build()
            self.configure_and_make()

    def package(self):
        self.output.info("Files already installed in build step")

    def package_info(self):
        glibmmdir = "glibmm-2.4"
        giommdir = "giomm-2.4"

        includes = [
            path.join("include", glibmmdir),
            path.join("lib", glibmmdir, "include"),  # adds config.h
            path.join("include", giommdir),
            path.join("lib", giommdir, "include")  # adds config.h
        ]

        self.cpp_info.includedirs = includes
        self.cpp_info.resdirs = ['share']
        self.cpp_info.libs = ["glibmm-2.4", "giomm-2.4"]

    ##################################################################################################

    def build_env(self):
        pkgEnv = PkgEnv(self)

        pkgEnv.add_pkg("libsigcplusplus", prefix="GLIBMM")
        pkgEnv.add_pkg("libsigcplusplus", prefix="GIOMM")
        pkgEnv.add_pkg("glib", prefix="GLIBMM", libs=["gobject-2.0", "gmodule-2.0", "glib-2.0"])
        pkgEnv.add_pkg("glib", prefix="GIOMM", libs=["gio-2.0", "glib-2.0"])

        env = pkgEnv.env

        self.output.info("env: " + str(env))

        return env

    def prepare_build(self):
        self.output.info("preparing build")

        if getattr(self, "package_dir", None) is None:
            # Make install dir
            self.package_dir = path.abspath(path.join(".", "install"))
            self._try_make_dir(self.package_dir)

    def configure_and_make(self):
        with tools.chdir(self.GLIBMM_FILE_BASE_NAME), pythonpath(self):
            from autotools_helper import Autotools

            autot = Autotools(self,
                              shared=self.options.shared)

            autot.configure()
            autot.build()
            autot.install()

    def _try_make_dir(self, dir):
        try:
            os.mkdir(dir)
        except OSError:
            # dir already exist
            pass

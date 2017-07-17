import os
from os import path

from conans import ConanFile, tools
from conans.tools import download, unzip, untargz, check_sha256, pythonpath

from pkg_config import PkgEnv

class Recipe(ConanFile):
    name        = "glibmm"
    version     = "2.48.1"
    description = "libsigc++ implements a typesafe callback system for standard C++"
    license     = "LGPL"
    url         = "https://gitlab.com/no-face/libsigcplusplus-conan"  #recipe repo url
    lib_urls   = {
        "project"        : "https://www.gtkmm.org", # official page is same of gtkmm
        "repo"           : "https://git.gnome.org/browse/glibmm",
        "mirror_github"  : "https://github.com/GNOME/glibmm",
        "docs"           : "https://developer.gnome.org/glibmm/stable/"
    }

    settings    = "os", "compiler", "arch"
    options = {
        "shared" : [True, False],
    }
    default_options = (
        "shared=True",
    )

    requires = (
        "libsigcplusplus/2.10.0@noface/testing",
        "glib/2.48.2@noface/testing"
    )

    build_requires    = (
        "untarxz/0.0.1@noface/testing",
        "AutotoolsHelper/0.0.1@noface/experimental"
    )

    exports = "pkg_config.py"

    BASE_URL_DOWNLOAD       = "https://download.gnome.org/sources/" + name
    FILE_URL                = "{}/{}/{}-{}.tar.xz".format(BASE_URL_DOWNLOAD, "2.48", name, version)
    EXTRACTED_FOLDER_NAME   = "{}-{}".format(name, version)
    FILE_SHA256             = 'dc225f7d2f466479766332483ea78f82dc349d59399d30c00de50e5073157cdf'

    def source(self):
        zip_name = self.name + ".tar.xz"
        download(self.FILE_URL, zip_name)
        check_sha256(zip_name, self.FILE_SHA256)

        with pythonpath(self):
            from untarxz import untarxz
            untarxz(self, zip_name)

    def build(self):
        with tools.environment_append(self.build_env()):
            self.prepare_build()
            self.configure_and_make()

    def package(self):
        self.output.info("Files already installed in build step")

    def package_info(self):
        glibmmdir = "glibmm-2.4"
        giommdir  = "giomm-2.4"

        includes = [
            path.join("include", glibmmdir)
            , path.join("lib", glibmmdir, "include") # adds config.h

            , path.join("include", giommdir)
            , path.join("lib", giommdir, "include") # adds config.h
        ]

        self.cpp_info.includedirs   = includes
        self.cpp_info.resdirs       = ['share']
        self.cpp_info.libs          = ["glibmm-2.4", "giomm-2.4"]
    
    ##################################################################################################

    def build_env(self):
        pkgEnv = PkgEnv(self)

        pkgEnv.add_pkg("libsigcplusplus", prefix="GLIBMM")
        pkgEnv.add_pkg("libsigcplusplus", prefix="GIOMM")
        pkgEnv.add_pkg("glib", prefix="GLIBMM", libs=["gobject-2.0", "gmodule-2.0", "glib-2.0"])
        pkgEnv.add_pkg("glib", prefix="GIOMM",  libs=["gio-2.0", "glib-2.0"])

        env = pkgEnv.env

        self.output.info("env: " + str(env))

        return env

    def prepare_build(self):
        self.output.info("preparing build")

        if getattr(self, "package_dir", None) is None:
            #Make install dir
            self.package_dir = path.abspath(path.join(".", "install"))
            self._try_make_dir(self.package_dir)
    
    def configure_and_make(self):
        with tools.chdir(self.EXTRACTED_FOLDER_NAME), pythonpath(self):
            from autotools_helper import Autotools

            autot = Autotools(self,
                shared      = self.options.shared)

            autot.configure()
            autot.build()
            autot.install()

    def _try_make_dir(self, dir):
        try:
            os.mkdir(dir)
        except OSError:
            #dir already exist
            pass

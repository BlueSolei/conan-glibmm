import os
from os import path

from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.tools import untargz, pythonpath, download, check_sha256


class Recipe(ConanFile):
    name = "glibmm"
    version = "2.58.1"  # "2.63.1"
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
        "shared=False",
    )

    requires = (
        "sigc++/2.10.0@bincrafters/stable",
        "glib/2.58.3@bincrafters/stable"
    )

    generators = "pkg_config"

    BASE_URL_DOWNLOAD = "https://download.gnome.org/sources/" + name
    VER_MAGOR = "{}.{}".format(*version.split('.')[:2])
    GLIBMM_FILE_BASE_NAME = "{}-{}".format(name, version)  # e.g. glibmm-2.63.1
    FILE_URL = "{}/{}/{}.tar.xz".format(BASE_URL_DOWNLOAD, VER_MAGOR, GLIBMM_FILE_BASE_NAME)
    FILE_SHA256 = '6e5fe03bdf1e220eeffd543e017fd2fb15bcec9235f0ffd50674aff9362a85f0'

    def source(self):
        zip_name = self.name + ".tar.xz"
        download(self.FILE_URL, zip_name)
        check_sha256(zip_name, self.FILE_SHA256)
        untargz(zip_name)  # will extract sources to a folder named GLIBMM_FILE_BASE_NAME
        os.remove(zip_name)

    def build(self):
        sig_cpp_pc_old = os.path.join(self.build_folder, "sigc++.pc")
        sig_cpp_pc_new = os.path.join(self.build_folder, "sigc++-2.0.pc")
        if os.path.exists(sig_cpp_pc_old):
            print(f"rename({sig_cpp_pc_old} -->, {sig_cpp_pc_new})")
            os.rename(sig_cpp_pc_old, sig_cpp_pc_new)

        src = os.path.join(self.build_folder, self.GLIBMM_FILE_BASE_NAME)
        with tools.chdir(src), tools.environment_append({"PKG_CONFIG_PATH": self.build_folder}):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.libs.append('resolv')
            is_shared = "yes" if self.options["shared"] else "no"
            is_static = "yes" if not self.options["shared"] else "no"
            args = [f"--enable-static={is_static}", f"--enable-shared={is_shared}"]
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package(self):
        pass

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

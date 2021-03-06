# Copyright 2020 Danct12 <danct12@disroot.org>
# SPDX-License-Identifier: GPL-3.0-or-later
import logging

import pmb.chroot
import pmb.chroot.apk
import pmb.build
import pmb.helpers.run
import pmb.helpers.pmaports


def check(args, pkgname):
    pmb.chroot.apk.install(args, ["atools"])

    # Run apkbuild-lint on copy of pmaport in chroot
    pmb.build.init(args)
    pmb.build.copy_to_buildpath(args, pkgname)
    logging.info("(native) linting " + pkgname + " with apkbuild-lint")
    pmb.chroot.user(args, ["apkbuild-lint", "APKBUILD"],
                    check=False, output="stdout",
                    working_dir="/home/pmos/build",
                    # Workaround, until we have CUSTOM_VALID_OPTIONS (#553)
                    env={"SKIP_INVALID_OPTION": "1"})

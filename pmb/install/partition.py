# Copyright 2020 Oliver Smith
# SPDX-License-Identifier: GPL-3.0-or-later
import logging
import os
import time
import pmb.chroot
import pmb.config
import pmb.install.losetup


def partitions_mount(args):
    """
    Mount blockdevices of partitions inside native chroot
    """
    prefix = args.sdcard
    if not args.sdcard:
        img_path = "/home/pmos/rootfs/" + args.device + ".img"
        prefix = pmb.install.losetup.device_by_back_file(args, img_path)

    partition_prefix = None
    tries = 20
    for i in range(tries):
        for symbol in ["p", ""]:
            if os.path.exists(prefix + symbol + "1"):
                partition_prefix = symbol
        if partition_prefix is not None:
            break
        logging.debug("NOTE: (" + str(i + 1) + "/" + str(tries) + ") failed to find"
                      " the install partition. Retrying...")
        time.sleep(0.1)

    if partition_prefix is None:
        raise RuntimeError("Unable to find the partition prefix,"
                           " expected the first partition of " +
                           prefix + " to be located at " + prefix +
                           "1 or " + prefix + "p1!")

    for i in [1, 2]:
        source = prefix + partition_prefix + str(i)
        target = args.work + "/chroot_native/dev/installp" + str(i)
        pmb.helpers.mount.bind_file(args, source, target)


def partition(args, size_boot):
    """
    Partition /dev/install and create /dev/install{p1,p2}

    size_boot: size of the boot partition in bytes.
    """
    # Convert to MB and print info
    mb_boot = str(round(size_boot / 1024 / 1024)) + "M"
    logging.info("(native) partition /dev/install (boot: " + mb_boot +
                 ", root: the rest)")

    filesystem = args.deviceinfo["boot_filesystem"] or "ext2"

    # Actual partitioning with 'parted'. Using check=False, because parted
    # sometimes "fails to inform the kernel". In case it really failed with
    # partitioning, the follow-up mounting/formatting will not work, so it
    # will stop there (see #463).
    boot_part_start = args.deviceinfo["boot_part_start"] or "2048"

    commands = [
        ["mktable", "msdos"],
        ["mkpart", "primary", filesystem, boot_part_start + 's', mb_boot],
        ["mkpart", "primary", mb_boot, "100%"],
        ["set", "1", "boot", "on"]
    ]
    for command in commands:
        pmb.chroot.root(args, ["parted", "-s", "/dev/install"] +
                        command, check=False)

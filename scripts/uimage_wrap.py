#!/usr/bin/env python3
import ctypes
from ctypes import c_uint8, c_uint16, c_uint32, c_uint64, sizeof
import struct
from enum import IntEnum, auto
import zlib
import os
from functools import partial
import argparse
import logging

log = logging.getLogger(__file__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.WARNING)


#
# Operating System Codes
#
# The following are exposed to uImage header.
# New IDs *MUST* be appended at the end of the list and *NEVER*
# inserted for backward compatibility.
#
class IHOS(IntEnum):
    IH_OS_INVALID = 0       # Invalid OS
    IH_OS_OPENBSD = auto()            # OpenBSD
    IH_OS_NETBSD = auto()            # NetBSD
    IH_OS_FREEBSD = auto()            # FreeBSD
    IH_OS_4_4BSD = auto()            # 4.4BSD
    IH_OS_LINUX = auto()            # Linux
    IH_OS_SVR4 = auto()            # SVR4
    IH_OS_ESIX = auto()            # Esix
    IH_OS_SOLARIS = auto()            # Solaris
    IH_OS_IRIX = auto()            # Irix
    IH_OS_SCO = auto()            # SCO
    IH_OS_DELL = auto()            # Dell
    IH_OS_NCR = auto()            # NCR
    IH_OS_LYNXOS = auto()            # LynxOS
    IH_OS_VXWORKS = auto()            # VxWorks
    IH_OS_PSOS = auto()            # pSOS
    IH_OS_QNX = auto()            # QNX
    IH_OS_U_BOOT = auto()            # Firmware
    IH_OS_RTEMS = auto()            # RTEMS
    IH_OS_ARTOS = auto()            # ARTOS
    IH_OS_UNITY = auto()            # Unity OS
    IH_OS_INTEGRITY = auto()        # INTEGRITY
    IH_OS_OSE = auto()            # OSE
    IH_OS_PLAN9 = auto()            # Plan 9
    IH_OS_OPENRTOS = auto()        # OpenRTOS
    IH_OS_ARM_TRUSTED_FIRMWARE = auto()     # ARM Trusted Firmware
    IH_OS_TEE = auto()            # Trusted Execution Environment
    IH_OS_OPENSBI = auto()            # RISC-V OpenSBI
    IH_OS_EFI = auto()            # EFI Firmware (e.g. GRUB2)
    # IH_OS_COUNT = auto()

#
# CPU Architecture Codes (supported by Linux)
#
# The following are exposed to uImage header.
# New IDs *MUST* be appended at the end of the list and *NEVER*
# inserted for backward compatibility.
#
class IHArch(IntEnum):
    IH_ARCH_INVALID        = 0    # Invalid CPU
    IH_ARCH_ALPHA = auto()            # Alpha
    IH_ARCH_ARM = auto()            # ARM
    IH_ARCH_I386 = auto()            # Intel x86
    IH_ARCH_IA64 = auto()            # IA64
    IH_ARCH_MIPS = auto()            # MIPS
    IH_ARCH_MIPS64 = auto()            # MIPS     64 Bit
    IH_ARCH_PPC = auto()            # PowerPC
    IH_ARCH_S390 = auto()            # IBM S390
    IH_ARCH_SH = auto()            # SuperH
    IH_ARCH_SPARC = auto()            # Sparc
    IH_ARCH_SPARC64 = auto()        # Sparc 64 Bit
    IH_ARCH_M68K = auto()            # M68K
    IH_ARCH_NIOS = auto()            # Nios-32
    IH_ARCH_MICROBLAZE = auto()        # MicroBlaze
    IH_ARCH_NIOS2 = auto()            # Nios-II
    IH_ARCH_BLACKFIN = auto()        # Blackfin
    IH_ARCH_AVR32 = auto()            # AVR32
    IH_ARCH_ST200 = auto()            # STMicroelectronics ST200
    IH_ARCH_SANDBOX = auto()        # Sandbox architecture (test only)
    IH_ARCH_NDS32 = auto()            # ANDES Technology - NDS32
    IH_ARCH_OPENRISC = auto()        # OpenRISC 1000
    IH_ARCH_ARM64 = auto()            # ARM64
    IH_ARCH_ARC = auto()            # Synopsys DesignWare ARC
    IH_ARCH_X86_64 = auto()            # AMD x86_64 Intel and Via
    IH_ARCH_XTENSA = auto()            # Xtensa
    IH_ARCH_RISCV = auto()            # RISC-V
    # IH_ARCH_COUNT = auto()

#
# Image Types
#
# "Standalone Programs" are directly runnable in the environment
#      provided by U-Boot; it is expected that (if they behave
#      well) you can continue to work in U-Boot after return from
#      the Standalone Program.
# "OS Kernel Images" are usually images of some Embedded OS which
#      will take over control completely. Usually these programs
#      will install their own set of exception handlers, device
#      drivers, set up the MMU, etc. - this means, that you cannot
#      expect to re-enter U-Boot except by resetting the CPU.
# "RAMDisk Images" are more or less just data blocks, and their
#      parameters (address, size) are passed to an OS kernel that is
#      being started.
# "Multi-File Images" contain several images, typically an OS
#      (Linux) kernel image and one or more data images like
#      RAMDisks. This construct is useful for instance when you want
#      to boot over the network using BOOTP etc., where the boot
#      server provides just a single image file, but you want to get
#      for instance an OS kernel and a RAMDisk image.
#
#      "Multi-File Images" start with a list of image sizes, each
#      image size (in bytes) specified by an "c_uint32" in network
#      byte order. This list is terminated by an "(c_uint32)0".
#      Immediately after the terminating 0 follow the images, one by
#      one, all aligned on "c_uint32" boundaries (size rounded up to
#      a multiple of 4 bytes - except for the last file).
#
# "Firmware Images" are binary images containing firmware (like
#      U-Boot or FPGA images) which usually will be programmed to
#      flash memory.
#
# "Script files" are command sequences that will be executed by
#      U-Boot's command interpreter; this feature is especially
#      useful when you configure U-Boot to use a real shell (hush)
#      as command interpreter (=> Shell Scripts).
#
# The following are exposed to uImage header.
# New IDs *MUST* be appended at the end of the list and *NEVER*
# inserted for backward compatibility.
#
class IHImageType(IntEnum):
    IH_TYPE_INVALID        = 0    # Invalid Image
    IH_TYPE_STANDALONE = auto()        # Standalone Program
    IH_TYPE_KERNEL = auto()            # OS Kernel Image
    IH_TYPE_RAMDISK = auto()        # RAMDisk Image
    IH_TYPE_MULTI = auto()            # Multi-File Image
    IH_TYPE_FIRMWARE = auto()        # Firmware Image
    IH_TYPE_SCRIPT = auto()            # Script file
    IH_TYPE_FILESYSTEM = auto()        # Filesystem Image (any type)
    IH_TYPE_FLATDT = auto()            # Binary Flat Device Tree Blob
    IH_TYPE_KWBIMAGE = auto()        # Kirkwood Boot Image
    IH_TYPE_IMXIMAGE = auto()        # Freescale IMXBoot Image
    IH_TYPE_UBLIMAGE = auto()        # Davinci UBL Image
    IH_TYPE_OMAPIMAGE = auto()        # TI OMAP Config Header Image
    IH_TYPE_AISIMAGE = auto()        # TI Davinci AIS Image
    # OS Kernel Image can run from any load address
    IH_TYPE_KERNEL_NOLOAD = auto()
    IH_TYPE_PBLIMAGE = auto()        # Freescale PBL Boot Image
    IH_TYPE_MXSIMAGE = auto()        # Freescale MXSBoot Image
    IH_TYPE_GPIMAGE = auto()        # TI Keystone GPHeader Image
    IH_TYPE_ATMELIMAGE = auto()        # ATMEL ROM bootable Image
    IH_TYPE_SOCFPGAIMAGE = auto()        # Altera SOCFPGA CV/AV Preloader
    IH_TYPE_X86_SETUP = auto()        # x86 setup.bin Image
    IH_TYPE_LPC32XXIMAGE = auto()        # x86 setup.bin Image
    IH_TYPE_LOADABLE = auto()        # A list of typeless images
    IH_TYPE_RKIMAGE = auto()        # Rockchip Boot Image
    IH_TYPE_RKSD = auto()            # Rockchip SD card
    IH_TYPE_RKSPI = auto()            # Rockchip SPI image
    IH_TYPE_ZYNQIMAGE = auto()        # Xilinx Zynq Boot Image
    IH_TYPE_ZYNQMPIMAGE = auto()        # Xilinx ZynqMP Boot Image
    IH_TYPE_ZYNQMPBIF = auto()        # Xilinx ZynqMP Boot Image (bif)
    IH_TYPE_FPGA = auto()            # FPGA Image
    IH_TYPE_VYBRIDIMAGE = auto()    # VYBRID .vyb Image
    IH_TYPE_TEE = auto()            # Trusted Execution Environment OS Image
    IH_TYPE_FIRMWARE_IVT = auto()        # Firmware Image with HABv4 IVT
    IH_TYPE_PMMC = auto()            # TI Power Management Micro-Controller Firmware
    IH_TYPE_STM32IMAGE = auto()        # STMicroelectronics STM32 Image
    IH_TYPE_SOCFPGAIMAGE_V1 = auto()    # Altera SOCFPGA A10 Preloader
    IH_TYPE_MTKIMAGE = auto()        # MediaTek BootROM loadable Image
    IH_TYPE_IMX8MIMAGE = auto()        # Freescale IMX8MBoot Image
    IH_TYPE_IMX8IMAGE = auto()        # Freescale IMX8Boot Image
    IH_TYPE_COPRO = auto()            # Coprocessor Image for remoteproc
    IH_TYPE_SUNXI_EGON = auto()        # Allwinner eGON Boot Image
    IH_TYPE_SUNXI_TOC0 = auto()        # Allwinner TOC0 Boot Image
    IH_TYPE_FDT_LEGACY = auto()        # Binary Flat Device Tree Blob    in a Legacy Image
    IH_TYPE_RENESAS_SPKG = auto()        # Renesas SPKG image
    # IH_TYPE_COUNT = auto()            # Number of image types

#
# Compression Types
#
# The following are exposed to uImage header.
# New IDs *MUST* be appended at the end of the list and *NEVER*
# inserted for backward compatibility.
#
class IHCompression(IntEnum):
    IH_COMP_NONE        = 0    #  No     Compression Used
    IH_COMP_GZIP = auto()            # gzip     Compression Used
    IH_COMP_BZIP2 = auto()            # bzip2 Compression Used
    IH_COMP_LZMA = auto()            # lzma  Compression Used
    IH_COMP_LZO = auto()            # lzo   Compression Used
    IH_COMP_LZ4 = auto()            # lz4   Compression Used
    IH_COMP_ZSTD = auto()            # zstd   Compression Used
    # IH_COMP_COUNT = auto()


LZ4F_MAGIC = 0x184D2204	# LZ4 Magic Number
IH_MAGIC = 0x27051956	# Image Magic Number
IH_NMLEN = 32	# Image Name Length


def ROUND(a, b):
    return (((a) + (b) - 1) & ~((b) - 1))


#
# Legacy format image header,
# all data in network byte order (aka natural aka bigendian).
#
class LegacyUImageHeader(ctypes.BigEndianStructure):
    _fields_ = [
        ("ih_magic", c_uint32),    # Image Header Magic Number
        ("ih_hcrc", c_uint32),    # Image Header CRC Checksum
        ("ih_time", c_uint32),    # Image Creation Timestamp
        ("ih_size", c_uint32),    # Image Data Size
        ("ih_load", c_uint32),    # Data     Load  Address
        ("ih_ep", c_uint32),        # Entry Point Address
        ("ih_dcrc", c_uint32),    # Image Data CRC Checksum
        ("ih_os", c_uint8),        # Operating System
        ("ih_arch", c_uint8),    # CPU architecture
        ("ih_type", c_uint8),    # Image Type
        ("ih_comp", c_uint8),    # Compression Type
        ("ih_name", c_uint8*IH_NMLEN)    # Image Name
    ]


class IntEnumArgOptions:
    """
    Generate a list of string options from an int enum class with a simple
    way to lookup the
    """
    def __init__(self, enum_class, prefix_str, invalid_suffix_list=None, ignore_list=None):
        self.prefix_str = prefix_str
        self.enum_class = enum_class
        if invalid_suffix_list is None:
            self._invalid_list = []
        else:
            # handle case of a single string for usability
            if isinstance(invalid_suffix_list, str):
                invalid_suffix_list = [invalid_suffix_list]
            self._invalid_list = [prefix_str + i for i in invalid_suffix_list]
        if ignore_list is not None:
            self._invalid_list += ignore_list

        # get all of the fieldnames of the enum class that are considered
        # valid options
        self._valid_enum_field_list = [i for i in dir(enum_class) \
                            if i.startswith(prefix_str) and \
                                 not (i.startswith("__") and i.endswith("__"))
                                 and i not in self._invalid_list]
        # make a mapping instead of a list so that mixed case names can
        # still be identified and associated when only provided a lowercase value
        self.lookup_mapping = {}
        upper_list = []
        lower_list = []
        for enum_field in self._valid_enum_field_list:
            without_prefix = enum_field.replace(prefix_str, "")
            field_value = getattr(self.enum_class, enum_field)
            upper_list.append((without_prefix, field_value))
            lower_list.append((without_prefix.lower(), field_value))

        # split into adding all upper options then all lower options so that
        # fields that wouldn't normally sort that way
        # (like fields that start with numbers) are still grouped correctly
        for k, v in upper_list:
            self.lookup_mapping[k] = v

        for k, v in lower_list:
            self.lookup_mapping[k] = v

        # all of the options that can be looked up
        self.option_strings = []
        self.generate_option_strings()

    def generate_option_strings(self):
        self.option_strings = [i for i in self.lookup_mapping.keys()]
        # self.option_strings.sort()

    def get_value_from_string(self, str_opt):
        return self.lookup_mapping[str_opt]


def batch(it, sz):
    length = len(it)
    for i in range(0, length, sz):
        yield it[i:i+sz]


class CustomFormatter(argparse.HelpFormatter):
    """Custom formatter for setting argparse formatter_class. Identical to the
    default formatter, except that very long option strings are split into two
    lines.
    """


    def _choice_format(self, action, choice_strs):
        if sum(len(s) for s in choice_strs) < self._width - (len(choice_strs) - 1) * 2:
            choices_block = ','.join(choice_strs)
        else:
            # really large lists of choices
            choices_block = ','.join(choice_strs)

        return "{%s}" % choices_block

    def _format_action_invocation(self, action):
        """
        This overriding function is just mean to limit the number of times
        each args_string is printed and print one arg option per line

        """
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar

        parts = []
        if action.nargs != 0:
            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            default = action.dest.upper()
            args_string = self._format_args(action, default)
            # join together the related option strings
            parts.append(", ".join(action.option_strings))
            # this is a hack to bypass asserts that are done in _format_usage.
            if action.choices is not None:
                # decompose the existing choice format
                choice_strs = [i for i in args_string.rstrip("}").lstrip("{").split(",")]
                parts.append(self._choice_format(action, choice_strs))
            else:
                parts.append(args_string)
        else:
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            parts.extend(action.option_strings)

        if sum(len(s) for s in parts) < self._width - (len(parts) - 1) * 2:
            return ', '.join(parts)
        else:
            return ',\n  '.join(parts)


def handle_compression(data, compression_type):
    if compression_type == IHCompression.IH_COMP_NONE:
        return data

    raise NotImplementedError("Compression type is not yet implemented")


def gen_uimage_header(data, entrypoint=0, load_address=0,
                      compression=IHCompression.IH_COMP_NONE,
                      operating_system=IHOS.IH_OS_LINUX,
                      arch=IHArch.IH_ARCH_X86_64,
                      image_type=IHImageType.IH_TYPE_KERNEL,
                      timestamp=0,
                      image_name=""
                     ):
    header = LegacyUImageHeader()
    header.ih_magic = IH_MAGIC
    header.ih_ep = entrypoint
    header.ih_load = load_address

    header.ih_comp = compress_opts.get_value_from_string(compression)
    compressed_data = handle_compression(data, header.ih_comp)

    header.ih_dcrc = zlib.crc32(compressed_data)
    header.ih_size = len(compressed_data)
    header.ih_os = os_opts.get_value_from_string(operating_system)
    header.ih_arch = arch_opts.get_value_from_string(arch)
    header.ih_type = image_type_opts.get_value_from_string(image_type)
    header.ih_time = timestamp
    if isinstance(image_name, str):
        encoded_name = image_name.encode()
    else:
        encoded_name = image_name
    for i, s in enumerate(encoded_name[:sizeof(header.ih_name)]):
        header.ih_name[i] = s

    header.ih_hcrc = zlib.crc32(bytes(header))

    log.debug("ih_magic %#x", header.ih_magic)
    log.debug("ih_hcrc %#x", header.ih_hcrc)
    log.debug("ih_time %#x", header.ih_time)
    log.debug("ih_size %#x", header.ih_size)
    log.debug("ih_load %#x", header.ih_load)
    log.debug("ih_ep %#x", header.ih_ep)
    log.debug("ih_dcrc %#x", header.ih_dcrc)
    log.debug("ih_os %#x", header.ih_os)
    log.debug("ih_arch %#x", header.ih_arch)
    log.debug("ih_type %#x", header.ih_type)
    log.debug("ih_comp %#x", header.ih_comp)
    log.debug("ih_name %s", str(bytes(header.ih_name)))

    return bytes(header) + compressed_data


if __name__ == "__main__":
    compress_opts = IntEnumArgOptions(IHCompression, "IH_COMP_")
    image_type_opts = IntEnumArgOptions(IHImageType, "IH_TYPE_", ["INVALID"])
    arch_opts = IntEnumArgOptions(IHArch, "IH_ARCH_", ["INVALID"])
    os_opts = IntEnumArgOptions(IHOS, "IH_OS_", ["INVALID"])

    parser = argparse.ArgumentParser(formatter_class=CustomFormatter)
    parser.add_argument("filepath", help="Path to file to wrap",
                        type=os.path.expanduser)
    parser.add_argument("-l", "--load-address",
                        help="address to load image at",
                        type=partial(int, base=0), default=0)
    parser.add_argument("-e", "--entrypoint",
                        help="address to set instruction pointer to",
                        type=partial(int, base=0), default=0)
    parser.add_argument("-s", "--operating-system",
                        choices=os_opts.option_strings,
                        default="LINUX")
    parser.add_argument("-a", "--architecture",
                        choices=arch_opts.option_strings,
                        default="X86_64")
    parser.add_argument("-i", "--image-type",
                        choices=image_type_opts.option_strings,
                        default="KERNEL")
    parser.add_argument("-c", "--compression",
                        choices=compress_opts.option_strings,
                        default="NONE")
    parser.add_argument("-t", "--timestamp", help="timestamp", type=int, default=0)
    parser.add_argument("-n", "--image-name", default="")
    parser.add_argument("-d", "--dry-run", action="store_true", default=False)
    parser.add_argument("--debug", action="store_true", default=False)
    parser.add_argument("-o", "--output", help="path to output to")
    args = parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)
        log.debug(args)

    with open(args.filepath, "rb") as f:
        contents = f.read()


    uimage_data = gen_uimage_header(contents,
                                    entrypoint=args.entrypoint,
                                    load_address=args.load_address,
                                    compression=args.compression,
                                    operating_system=args.operating_system,
                                    arch=args.architecture,
                                    image_type=args.image_type,
                                    timestamp=args.timestamp,
                                    image_name=args.image_name)

    if args.output and not args.dry_run:
        with open(args.output, "wb") as f:
            f.write(uimage_data)


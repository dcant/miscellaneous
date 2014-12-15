#! /usr/bin/python
import sys, os, subprocess, getopt
from os.path import basename

PCI_DEV_CAP_REG = 0xA4
PCI_DEV_CTRL_REG = 0xA8
PCI_DEV_CAP_EXT_TAG_MASK = 0x20
PCI_DEV_CTRL_EXT_TAG_MASK = 0x100

dev_ids = {}
flag = "Set"

def usage():
    '''Print usage information for the program'''
    argv0 = basename(sys.argv[0])
    print """
Usage:
------

     %(argv0)s [options] DEVICE1 DEVICE2 ....

where DEVICE1, DEVICE2 etc, are specified via PCI "domain:bus:slot.func" syntax
or "bus:slot.func" syntax. For devices bound to Linux kernel drivers, they may
also be referred to by Linux interface name e.g. eth0, eth1, em0, em1, etc.

Options:
    --help, --usage:
        Display usage information and quit

    -s --set:
        Set the following pci device

    -u --Unset:
		Unset the following pci device

Examples:
---------
To set pci 0a:00.0
        %(argv0)s -s 0a:00.0
        %(argv0)s --set 0a:00.0

To unset 0000:01:00.0
        %(argv0)s -u 0000:01:00.0
        %(argv0)s --unset 0000:01:00.0

To set 0000:02:00.0 and 0000:02:00.1
        %(argv0)s -s 02:00.0 02:00.1

    """ % locals() # replace items from local variables

def parse_args():
	global flag
	global dev_ids
	if len(sys.argv) <= 1:
		usage()
		sys.exit(0)
	try:
		opts, dev_ids = getopt.getopt(sys.argv[1:], "su", ["help", "usage", "set", "unset"])
	except getopt.GetoptError, error:
		print str(err)
		print "Run '%s --usage' for further information" % sys.argv[0]
		sys.exit(1)
	
	for opt, arg in opts:
		if opt == "--help" or opt == "--usage":
			usage()
			sys.exit(0)
		if opt == "-s" or opt == "--set":
			flag = "Set"
		if opt == "-u" or opt == "--unset":
			flag = "Unset"

def check_output(args, stderr=None):
	'''Run a command and capture its output'''
	return subprocess.Popen(args, stdout=subprocess.PIPE,
			stderr=stderr).communicate()[0]

def set_pci():
	if len(dev_ids) == 0:
		print "Error: No devices specified."
		print "Run '%s --usage' for further information" % sys.argv[0]
		sys.exit(1)
	param_cap = '''%x.L'''%(PCI_DEV_CAP_REG)
	for k in range(len(dev_ids)):
		val = check_output(["setpci", "-s", dev_ids[k], param_cap])
		if (not (int(val, 16) & PCI_DEV_CAP_EXT_TAG_MASK)):
			print dev_ids[k], "Not supported"
			continue
		if (int(val, 16) & PCI_DEV_CTRL_EXT_TAG_MASK):
			continue
		param_ctrl = '''%x.L'''%(PCI_DEV_CTRL_REG)
		val = check_output(["setpci", "-s", dev_ids[k], param_ctrl])
		if flag == "Set":
			val = int(val, 16) | PCI_DEV_CTRL_EXT_TAG_MASK
		else:
			val = int(val, 16) & ~PCI_DEV_CTRL_EXT_TAG_MASK
		param_ctrl = '''%x.L=%x'''%(PCI_DEV_CTRL_REG, val)
		check_output(["setpci", "-s", dev_ids[k], param_ctrl])

def main():
	parse_args()
	set_pci()

if __name__ == "__main__":
	main()
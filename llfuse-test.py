import sys, logging
import llfuse

mountpoint = 'llfuse-test'

class Operations(llfuse.Operations):
    def __init__(self):
        super().__init__()

    def opendir(self, inode):
        print("Opendir got inode", inode)
        if inode == llfuse.ROOT_INODE:
            print("  Root inode!")
        return 0

    def readdir(self, fh, off):
        print("Readdir got args", fh, off)
        return iter([])

    def releasedir(self, fh):
        print("Releasedir got handler", fh)

if __name__ == '__main__':
    print("Mounting to directory", mountpoint)

    fuse_options = set(llfuse.default_options)
    fuse_options.discard('nonempty') # necessary for osxfuse
    fuse_options.add('fsname=llfuse-test')
    # fuse_options.add('debug')
    # fuse_options.discard('default_permissions')
    # fuse_options.add('defer_permissions')

    ops = Operations()
    llfuse.init(ops, mountpoint, fuse_options)
    try:
        llfuse.main(workers=1)
    except:
        llfuse.close()
        raise
    llfuse.close()
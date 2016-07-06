import sys, logging, errno, stat, os, time
import llfuse

mountpoint = 'llfuse-test'

log = logging.getLogger() # get root Logger

class Operations(llfuse.Operations):
    def __init__(self):
        super().__init__()
        log.info('init')
        self.gid = os.getgid()
        self.uid = os.getuid()
        self.access_root = stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH # read+execute
        self.access = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH #read-only
        self.root_entry = self.construct_entry(llfuse.ROOT_INODE, stat.S_IFDIR | self.access_root, 1, int(time.time() * 1e9))

    def construct_entry(self, inode, mode, size, time):
        entry = llfuse.EntryAttributes()
        entry.st_ino = inode
        entry.st_mode = mode
        # entry.st_nlink = 1
        entry.st_size = size

        entry.st_uid = self.uid
        entry.st_gid = self.gid

        # entry.st_blocks = 1
        entry.st_atime_ns = time
        entry.st_mtime_ns = time
        entry.st_ctime_ns = time

        return entry

    def getattr(self, inode, ctx):
        log.info('getattr %i' % inode)
        assert inode == llfuse.ROOT_INODE
        # if inode == llfuse.ROOT_INODE:
        #     raise llfuse.FUSEError(errno.ENOENT)
        return self.root_entry

    def opendir(self, inode, ctx):
        log.info('opendir %i' % inode)
        # if inode != llfuse.ROOT_INODE:
        #     raise llfuse.FUSEError(errno.ENOENT)
        return inode

    def lookup(self, parent_inode, name, ctx=None):
        log.info('lookup %i: %s' % (parent_inode, name))
        # raise llfuse.FUSEError(errno.ENOENT)
        # if parent_inode != llfuse.ROOT_INODE or name != self.hello_name:
        #     raise llfuse.FUSEError(errno.ENOENT)
        # return self.getattr(self.hello_inode)
        if name == '.':
            inode = parent_inode
        elif name == '..':
            inode = llfuse.ROOT_INODE
        else:
            raise llfuse.FUSEError(errno.ENOENT)
        return self.getattr(inode)

    def readdir(self, fh, off):
        log.info('readdir %i/%i' % (fh, off))
        # raise llfuse.FUSEError(errno.ENOENT)
        if False:
            yield (0,0,0)
        #return iter([])

    def statfs(self, ctx):
        sfs = llfuse.StatvfsData()

        sfs.f_bsize = 512
        sfs.f_frsize = 512

        size = 0
        sfs.f_blocks = size // sfs.f_frsize
        sfs.f_bfree = 0 #max(size // sfs.f_frsize, 1024)
        sfs.f_bavail = sfs.f_bfree

        inodes = 1 #self.get_row('SELECT COUNT(id) FROM inodes')[0]
        sfs.f_files = inodes
        sfs.f_ffree = 0 #max(inodes, 100)
        sfs.f_favail = sfs.f_ffree

        return sfs

def init_logging():
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(threadName)s: '
                                  '[%(name)s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)

if __name__ == '__main__':
    init_logging()
    print("Mounting to directory", mountpoint)

    name = 'llfuse-test'
    fuse_options = set(llfuse.default_options)
    fuse_options.discard('nonempty') # necessary for osxfuse
    fuse_options.add('fsname=%s' % name)
    fuse_options.add('volname=%s' % name)
    # fuse_options.add('debug')
    # fuse_options.discard('default_permissions')
    # fuse_options.add('defer_permissions')

    llfuse.init(Operations(), mountpoint, fuse_options)
    try:
        llfuse.main(workers=1)
    except:
        llfuse.close()
        raise
    llfuse.close()
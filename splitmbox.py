import mailbox
import plac
import logging
logging.basicConfig(
    format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)


def main(mbox_file, output_dir):
    mbox = mailbox.UnixMailbox(open(mbox_file))
    counter = 0
    while True:
        msg = mbox.next()
        if not msg:
            break
        output_fname = '{0}/{1}.mbox'.format(output_dir, counter)
        with open(output_fname, 'w') as out:
            for hdr in msg.headers:
                out.write(hdr)
            out.write('\n')
            for bln in msg.fp.readlines():
                out.write(bln)
        logging.info('Saved {0}'.format(output_fname))
        counter += 1


if __name__ == '__main__':
    plac.call(main)

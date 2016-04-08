import math

from PIL import Image
from PIL import ImageChops


class ImageDiff(object):
    """"""
    def rmsdiff_2011(self, im1, im2):
        "Calculate the root-mean-square difference between two images"
        diff = ImageChops.difference(im1, im2)
        h = diff.histogram()
        sq = (value * (idx ** 2) for idx, value in enumerate(h))
        sum_of_squares = sum(sq)
        rms = math.sqrt(sum_of_squares / float(im1.size[0] * im1.size[1]))
        return rms


    def images_identical(self, path1, path2):
        im1 = Image.open(path1)
        im2 = Image.open(path2)
        return ImageChops.difference(im1, im2).getbbox() is None


    def image_diff(self, im1, im2, outpath, diffcolor):
        rmsdiff = self.rmsdiff_2011(im1, im2)

        pix1 = im1.load()
        pix2 = im2.load()

        if im1.mode != im2.mode:
            raise TestError('Different pixel modes between im1 and im2')
        if im1.size != im2.size:
            raise TestError('Different dimensions between im1 (%r) and im2 (%r)' % (im1.size, im2.size))

        mode = im1.mode

        if mode == '1':
            value = 255
        elif mode == 'L':
            value = 255
        elif mode == 'RGB':
            value = diffcolor
        elif mode == 'RGBA':
            value = diffcolor + (255,)
        elif mode == 'P':
            raise NotImplementedError('TODO: look up nearest palette color')
        else:
            raise NotImplementedError('Unexpected PNG mode')

        width, height = im1.size

        for y in xrange(height):
            for x in xrange(width):
                if pix1[x, y] != pix2[x, y]:
                    pix2[x, y] = value
        im2.save(outpath)

        return (rmsdiff, width, height)

    def validate(self, url, storage, suts, stub, color=(0,255,0)):
        stack = storage.get()
        stub_img = stack[stub.name][url][0]
        for sut in suts:
            sut_img = stack[sut.name][url][0]
            self.image_diff(stub_img, sut_img,
                            '/tmp/'+url.replace(":", "").replace("/", "")+'_'+sut.name+'.png',
                            color)

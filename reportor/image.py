import os
import json
import math
import time
import codecs
import collections

import Image
import ImageDraw
import validator.error


def reset_differences(differences, vertical_offsets):
    """
        >>> import json
        >>> import reportor.image
        >>> differences = json.load(open('results/full_IE_sut.json'))
        >>> res = reportor.image.reset_differences(differences)
        >>> import math
        >>> for d in res:
        ...     if d[5] == 'unmatch':
        ...         for k, v in d[-1].items():
        ...             if k == 'text':
        ...                 continue
        ...             if math.fabs(v) > 15:
        ...                 print(d[-1])
        ...                 break
    """
    return_results = list(differences)
    for _index, each in enumerate(return_results):
        _tmp = list(each)
        for top, offset in vertical_offsets:
            if offset < 0 and each[5] in ['miss', 'unmatch']:
                if each[0] >= top:
                    _tmp[0] -= offset
                elif each[5] == 'unmatch' and each[-1]['height'] == offset:
                    _tmp[0] -= offset
            if offset > 0 and each[5] == 'extra' and each[0] >= top:
                _tmp[0] += offset
            if each[0] >= top and each[5] == 'unmatch':
                _tmp[-1]['top'] -= offset
        return_results[_index] = _tmp
    return return_results


def scale_image(image1, image2):
    image1_width, image1_height = image1.size
    image2_width, image2_height = image2.size
    if image1_width == image2_width:
        return
    #scale to the same width
    if image2_width > image1_width:
        if image2_width%image1_width == 0:
            scale = float(image1_width)/float(image2_width)
            image2 = image2.resize((image1_width, int(image2_height*scale)))
    elif image2_width < image1_width:
        if image1_width%image2_width == 0:
            scale = float(image2_width)/float(image1_width)
            image1 = image1.resize((image2_width, int(image1_height*scale)))


def compose_image(sutShot, stubShot, vertical_offsets):
    sut_width, sut_height = sutShot.size
    stub_width, stub_height = stubShot.size
    sut_crop_paste, stub_crop_paste, full_height = \
        get_crop_paste(vertical_offsets, sut_height, sut_width, stub_height, stub_width)
    result_image = Image.new('RGBA', (sut_width+stub_width, full_height))
    for crop, paste in sut_crop_paste:
        result_image.paste(sutShot.crop(crop), paste)
    for crop, paste in stub_crop_paste:
        result_image.paste(stubShot.crop(crop), paste)
    return result_image


def get_crop_paste(offsets, sut_height, sut_width, stub_height, stub_width):
    """
        >>> import json
        >>> import reportor.image
        >>> differences = json.load(open('/tmp/http10.0.0.1195000mismatch_Galaxy_S4.json'))
        >>> offsets = reportor.image.get_vertical_offsets(differences)
        >>> sut_cp, stub_cp, full_height = reportor.image.get_crop_paste(offsets, 5000, 360, 5000, 360)
        >>> for c, p in stub_cp:
        ...     print(c,p)
    """
    sut_last_top = 0
    stub_last_top = 0
    sut_history_offset = 0
    stub_history_offset = 0
    sut_cp = []
    stub_cp = []
    for top, offset in offsets:
        if offset < 0:
            stub_cp.append(((0, stub_last_top, stub_width, top),
                            (sut_width, stub_last_top-stub_history_offset)))
            stub_last_top = top
            stub_history_offset += offset
        else:
            bottom = top - (offset + sut_history_offset + stub_history_offset)
            paste_y = sut_last_top + sut_history_offset
            sut_cp.append(((0, sut_last_top, sut_width, bottom), (0, paste_y)))
            sut_history_offset += offset
            sut_last_top = bottom
    sut_cp.append(((0, sut_last_top, sut_width, sut_height),
                   (0, sut_last_top+sut_history_offset)))
    stub_cp.append(((0, stub_last_top, stub_width, stub_height),
                    (sut_width, stub_last_top-stub_history_offset)))
    full_height = sut_height + sut_history_offset
    return sut_cp, stub_cp, full_height


class Reportor(object):

    def __init__(self, ignore_scrollbar=False, horizontal_tolerance=10,
                    vertical_tolerance=10):
        self.ignore_scrollbar = ignore_scrollbar
        self.horizontal_tolerance = horizontal_tolerance
        self.vertical_tolerance = vertical_tolerance

    def get_vertical_offsets(self, differences):
        """
            >>> import json
            >>> import reportor.image
            >>> differences = json.load(open('results/full_IE_sut.json'))
            >>> for offset in reportor.image.get_vertical_offsets(differences):
            ...     print(str(offset))
        """
        offsets = []
        history_offset = 0
        for _index, diff in enumerate(differences):
            if diff[5] == 'unmatch':
                if (math.fabs(diff[-1]['height']) > self.vertical_tolerance or
                    math.fabs(diff[-1]['left']) > self.horizontal_tolerance or
                    math.fabs(diff[-1]['width']) > self.horizontal_tolerance):
                    continue
                offset = diff[-1]['top'] - history_offset
                if diff[-1]['top'] == 0 or \
                    math.fabs(offset) <= self.vertical_tolerance:
                    continue
                top = diff[0] - diff[4]['marginTop']
                # check if the top line cut any element
                for _d in differences:
                    if _d == diff or _d[5] == 'extra':
                        continue
                    _mt = _d[4]['marginTop']
                    _mb = _d[4]['marginBottom']
                    if (_d[0] - _mt) < top < (_d[0] + _d[2] + _mb):
                        if (_d[0] < (diff[0] + diff[2]) <= (_d[0] + _d[2]) and
                            _d[1] <= diff[1] < (_d[1] + _d[3]) and
                            _d[1] < (diff[1] + diff[3]) <= (_d[1] + _d[3])):
                            continue
                        break
                else:
                    history_offset += offset
                    offsets.append((top, offset))
        return offsets

    def markelements(self, img, results):
        rate = 0
        drawer = ImageDraw.Draw(img)
        body = results[-1]
        width_diff = self.horizontal_tolerance
        drawn_results = []
        if body[5] == 'unmatch' and body[-1]['name'] == 'BODY':
            width_diff = body[-1]['width']
            if not self.ignore_scrollbar:
                width = body[1]+body[3]
                height = body[0]+body[2]
                if width_diff < 0:
                    rectangle = (width, body[0], width-width_diff, height)
                    drawer.rectangle(rectangle, fill='green', outline='green')
                elif width_diff > 0:
                    rectangle = (width-width_diff, body[0], width, height)
                    drawer.rectangle(rectangle, fill='blue', outline='blue')
            width_diff = math.fabs(width_diff)
        for each in results:
            top, left, height, width = each[0], each[1], each[2], each[3]
            if height == 0 or width == 0:
                continue
            bottom, right = top+height, left+width
            if each[5] == 'extra':
                drawer.rectangle((left, top, right, bottom), outline='green')
                drawn_results.append(each)
            elif each[5] == 'miss':
                drawer.rectangle((left, top, right, bottom), outline='blue')
                drawn_results.append(each)
            elif each[5] == 'unmatch':
                if each[2] > 500:
                    continue
                for key, value in each[-1].items():
                    if key in ['width', 'left']:
                        if math.fabs(value) > max(self.horizontal_tolerance, width_diff):
                            break
                    elif key in ['top', 'height']:
                        if math.fabs(value) > self.vertical_tolerance:
                            break
                else:
                    continue
                drawer.rectangle((left, top, right, bottom), outline='red')
                drawn_results.append(each)
        return drawn_results

    def vertical_split(self, differences, context_height=20):
        """
            >>> import json
            >>> import reportor.image
            >>> differences = json.load(open('/tmp/http10.0.0.1195000mismatch_Galaxy_S4.json'))
            >>> for (y1, y2) in reportor.image.vertical_split(differences).items():
            ...     print(y1, y2)
        """
        if len(differences) > 0:
            y1 = differences[0][0] - differences[0][4]['marginTop']
            y2 = differences[0][0] + differences[0][2] + differences[0][4]['marginBottom']
        res = []
        for _index, diff in enumerate(differences):
            if diff[2] > 400 or diff[2] == 0:
                    continue
            if diff[0] > y2 + 100:
                if (y1-context_height, y2+context_height) not in res:
                    res.append((y1-context_height, y2+context_height))
                y1 = diff[0] - diff[4]['marginTop']
                y2 = diff[0] + diff[2] + diff[4]['marginBottom']
            if diff[0] - diff[4]['marginTop'] < y1:
                y1 = diff[0] - diff[4]['marginTop']
            if diff[0] + diff[2] + diff[4]['marginBottom'] > y2:
                y2 = diff[0] + diff[2] + diff[4]['marginBottom']
        if (y1-context_height, y2+context_height) not in res:
            res.append((y1-context_height, y2+context_height))
        return res

    def report(self, differences, storage, sut_name, stub_name, url):
        #select differences
        limit_diffs = []
        for diff in differences:
            #ignore no sence record
            if diff[0] + diff[1] + diff[2] + diff[3] == 0:
                continue
            limit_diffs.append(diff)
        differences = limit_diffs
        if len(differences) == 0:
            return

        stack = storage.get()
        sutShot = stack[sut_name][url]['image']
        stubShot = stack[stub_name][url]['image']
        scale_image(sutShot, stubShot)

        #paste sut and stub with gaps
        vertical_offsets = self.get_vertical_offsets(differences)
        updated_differences = reset_differences(differences, vertical_offsets)
        full_image = compose_image(sutShot, stubShot, vertical_offsets)
        drawn_differences = self.markelements(full_image, updated_differences)
        if len(drawn_differences) == 0:
            return

        url = url[0]
        index = len(url)
        try:
            index = url.index('?')
        except ValueError:
            pass
        url = url[:index]
        url += "_"+time.ctime().replace(" ", "_")
        url = url.replace(":", "_").replace("/", "")
        ftp_root = "reports/"

        #text report
        drawn_json_file = ftp_root+url+'_'+sut_name+'_drawn.json'
        with codecs.open(drawn_json_file, 'w', 'utf-8') as fp:
            json.dump(drawn_differences, fp, ensure_ascii=False, indent=4)

        #full image report
        img_file = ftp_root+url+'_'+sut_name+'.png'
        full_image.save(img_file)

        #image pieces of differences
        pieces_dir = ftp_root+url+'_'+sut_name
        if not os.path.exists(pieces_dir):
            os.mkdir(pieces_dir)
        full_width = sutShot.size[0] + stubShot.size[0]
        for (y1, y2) in self.vertical_split(updated_differences):
            piece = full_image.crop((0, y1, full_width, y2))
            piece.save(pieces_dir + '/image_piece_%s.png'%str((0, y1)))

        host_ip = "10.0.0.119" #TODO set to the jenkins server ip address

        drawn_json_link = 'ftp://%s/'%host_ip + drawn_json_file[drawn_json_file.index("reports/")+8:]
        image_link = 'ftp://%s/'%host_ip + img_file[img_file.index("reports/")+8:]
        pieces_link = 'ftp://%s/'%host_ip + pieces_dir[pieces_dir.index("reports/")+8:]
        raise validator.error.TestError("%d differences found!"
                                        "\nDraw differences %s"
                                        "\nFull Image %s"
                                        "\nDifference Image Pieces %s"
                                        %(len(drawn_differences),
                                          drawn_json_link,
                                          image_link,
                                          pieces_link))

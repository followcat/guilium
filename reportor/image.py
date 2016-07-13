import os
import json
import math
import time
import collections

import Image
import ImageDraw
import validator.error


def reset_differences(differences):
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
    count_offsets = count_offset(differences)
    return_results = list(differences)
    for _index, each in enumerate(return_results):
        _tmp = list(each)
        for top, offset in count_offsets:
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

def markelements(img, results, ignore=5):
    rate = 0
    drawer = ImageDraw.Draw(img)
    body = results[-1]
    width_diff = ignore
    is_draw = False
    if body[5] == 'unmatch' and body[-1]['name'] == 'BODY':
        width_diff = body[-1]['width']
        width = body[1]+body[3]
        if width_diff < 0:
            rectangle = (width, body[0], width-width_diff, body[0]+body[2])
            drawer.rectangle(rectangle, fill='green', outline='green')
            is_draw = True
        elif width_diff > 0:
            rectangle = (width-width_diff, body[0], width, body[0]+body[2])
            drawer.rectangle(rectangle, fill='blue', outline='blue')
            is_draw = True
    for each in results:
        top, left, height, width = each[0], each[1], each[2], each[3]
        if height == 0 or width == 0:
            continue
        bottom, right = top+height, left+width
        if each[5] == 'extra':
            drawer.rectangle((left, top, right, bottom), outline='green')
            is_draw = True
        elif each[5] == 'miss':
            drawer.rectangle((left, top, right, bottom), outline='blue')
            is_draw = True
        elif each[5] == 'unmatch':
            for key, value in each[-1].items():
                if key in ['width', 'left']:
                    if math.fabs(value) >= max(ignore, math.fabs(width_diff)):
                        break
                elif key in ['top', 'height']:
                    if math.fabs(value) >= ignore:
                        break
            else:
                continue
            if each[2] > 500:
                continue
            drawer.rectangle((left, top, right, bottom), outline='red')
            is_draw = True
        return is_draw

def report(differences, storage, sut_name, stub_name, url):
    stack = storage.get()
    sutShot = stack[sut_name][url]['image']
    stubShot = stack[stub_name][url]['image']
    sut_width, sut_height = sutShot.size
    stub_width, stub_height = stubShot.size
    #scale to the same width
    if stub_width > sut_width:
        scale = float(sut_width)/float(stub_width)
        stubShot = stubShot.resize((sut_width, int(stub_height*scale)))
        stub_width, stub_height = stubShot.size
    elif stub_width < sut_width:
        scale = float(stub_width)/float(sut_width)
        sutShot = sutShot.resize((stub_width, int(sut_height*scale)))
        sut_width, sut_height = sutShot.size
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
    #text report
    url = url[0]
    index = len(url)
    try:
        index = url.index('?')
    except ValueError:
        pass
    url = url[:index]
    url += "_"+time.ctime().replace(" ", "_")
    url = url.replace(":", "").replace("/", "")
    ftp_root = "reports/"
    json_file = ftp_root+url+'_'+sut_name+'.json'
    with open(json_file, 'w') as fp:
        json.dump(differences, fp)
    #paste sut and stub with gaps
    count_offsets = count_offset(differences)
    sut_crop_paste, stub_crop_paste, full_height = \
        get_crop_paste(count_offsets, sut_height, sut_width, stub_height, stub_width)
    result_image = Image.new('RGBA', (sut_width+stub_width, full_height))
    for crop, paste in sut_crop_paste:
        result_image.paste(sutShot.crop(crop), paste)
    for crop, paste in stub_crop_paste:
        result_image.paste(stubShot.crop(crop), paste)
    update_differences = reset_differences(differences)
    is_draw_diff = markelements(result_image, update_differences)
    if not is_draw_diff:
        return
    img_file = ftp_root+url+'_'+sut_name+'.png'
    result_image.save(img_file)

    #image pieces
    pieces_dir = ftp_root+url+'_'+sut_name
    if not os.path.exists(pieces_dir):
        os.mkdir(pieces_dir)
    ch = 20
    for (y1, y2) in get_offset(update_differences):
        piece = result_image.crop((0, y1-ch, sut_width+stub_width, y2+ch))
        piece.save(pieces_dir + '/image_piece_%s.png'%str((0, y1)))

    host_ip = "10.0.0.119" #TODO set to the jenkins server ip address
    json_link = 'ftp://%s/'%host_ip + json_file[json_file.index("reports/")+8:]
    image_link = 'ftp://%s/'%host_ip + img_file[img_file.index("reports/")+8:]
    pieces_link = 'ftp://%s/'%host_ip + pieces_dir[pieces_dir.index("reports/")+8:]
    raise validator.error.TestError("%d differences found in "
                "positions %s... "
                "\nSee differences %s"
                "\nFull Image %s"
                "\nDifference Image Pieces %s"
                %(len(differences),
                  str((differences[0][0], differences[0][1])),
                  json_link,
                  image_link,
                  pieces_link))

def get_crop_paste(offsets, sut_height, sut_width, stub_height, stub_width):
    """
        >>> import json
        >>> import reportor.image
        >>> differences = json.load(open('/tmp/http10.0.0.1195000mismatch_Galaxy_S4.json'))
        >>> offsets = reportor.image.count_offset(differences)
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


def get_offset(differences):
    """
        >>> import json
        >>> import reportor.image
        >>> differences = json.load(open('/tmp/http10.0.0.1195000mismatch_Galaxy_S4.json'))
        >>> for (y1, y2) in reportor.image.get_offset(differences).items():
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
            if (y1, y2) not in res:
                res.append((y1, y2))
            y1 = diff[0] - diff[4]['marginTop']
            y2 = diff[0] + diff[2] + diff[4]['marginBottom']
        if diff[0] - diff[4]['marginTop'] < y1:
            y1 = diff[0] - diff[4]['marginTop']
        if diff[0] + diff[2] + diff[4]['marginBottom'] > y2:
            y2 = diff[0] + diff[2] + diff[4]['marginBottom']
    if (y1, y2) not in res:
        res.append((y1, y2))
    return res

def count_offset(differences):
    """
        >>> import json
        >>> import reportor.image
        >>> differences = json.load(open('results/full_IE_sut.json'))
        >>> for offset in reportor.image.count_offset(differences):
        ...     print(str(offset))
    """
    offsets = []
    history_offset = 0
    for _index, diff in enumerate(differences):
        if diff[5] == 'unmatch':
            for _key in ['left', 'height', 'width']:
                if math.fabs(diff[-1][_key]) > 5:
                    break
            else:
                offset = diff[-1]['top'] - history_offset
                if diff[-1]['top'] == 0 or offset == 0:
                    continue
                top = diff[0] - diff[4]['marginTop']
                # check if the top line cut any element
                for _d in differences:
                    if _d == diff or _d[5] == 'extra':
                        continue
                    if (_d[0] - _d[4]['marginTop']) < (diff[0] - diff[4]['marginTop']) < (_d[0] + _d[2] + _d[4]['marginBottom']):
                        if  _d[0] < (diff[0] + diff[2]) <= (_d[0] + _d[2]) and \
                            _d[1] <= diff[1] < (_d[1] + _d[3]) and \
                            _d[1] < (diff[1] + diff[3]) <= (_d[1] + _d[3]):
                            continue
                        break
                else:
                    history_offset += offset
                    offsets.append((top, offset))
    return offsets

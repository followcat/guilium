import os
import json
import collections

import Image
import ImageDraw
import validator.error


def reset_differences(differences):
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
        return_results[_index] = _tmp
    return return_results

def markelements(img, results):
    drawer = ImageDraw.Draw(img)
    for each in results:
        top, left, height, width = each[0], each[1], each[2], each[3]
        #height += each[4]
        bottom, right = top+height, left+width
        if each[5] == 'extra':
            drawer.rectangle((left, top, right, bottom), outline='green')
        elif each[5] == 'miss':
            drawer.rectangle((left, top, right, bottom), outline='blue')
        elif each[5] == 'unmatch':
            if each[2] > 500:
                continue
            drawer.rectangle((left, top, right, bottom), outline='red')

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
    #limit differences with 1 page
    limit_diffs = []
    for diff in differences:
        if diff[0] + diff[2] > sut_height:
            continue
        if diff[0] + diff[1] + diff[2] + diff[3] == 0:
            continue
        limit_diffs.append(diff)
    differences = limit_diffs
    if len(differences) == 0:
        return
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
    markelements(result_image, update_differences)
    img_file = '/tmp/'+url.replace(":", "").replace("/", "")+'_'+sut_name+'.png'
    result_image.save(img_file)

    #image pieces
    pieces_dir = '/tmp/'+url.replace(":", "").replace("/", "")+'_'+sut_name
    if not os.path.exists(pieces_dir):
        os.mkdir(pieces_dir)
    ch = 20
    for (y1, y2) in get_offset(update_differences):
        piece = result_image.crop((0, y1-ch, sut_width+stub_width, y2+ch))
        piece.save(pieces_dir + '/image_piece_%s.png'%str((0, y1)))

    #text report
    json_file = '/tmp/'+url.replace(":", "").replace("/", "")+'_'+sut_name+'.json'
    with open(json_file, 'w') as fp:
        json.dump(differences, fp)
    json_link = 'file://' + json_file
    image_link = 'file://' + img_file
    raise validator.error.TestError("%d differences found in "
                "positions %s... "
                "\nSee differences %s"
                "\nFull Image %s"
                "\nDifference Image Pieces %s"
                %(len(differences),
                  str((differences[0][0], differences[0][1])),
                  json_link,
                  image_link,
                  'file://' + pieces_dir))

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
        y1 = differences[0][0]
        y2 = differences[0][0] + differences[0][2] + differences[0][4]
    res = []
    for _index, diff in enumerate(differences):
        if diff[2] > 400 or diff[2] == 0:
                continue
        if diff[0] > y2 + 100:
            if (y1, y2) not in res:
                res.append((y1, y2))
            y1 = diff[0]
            y2 = diff[0] + diff[2] + diff[4]
        if diff[0] < y1:
            y1 = diff[0]
        if diff[0] + diff[2] + diff[4] > y2:
            y2 = diff[0] + diff[2] + diff[4]
    if (y1, y2) not in res:
        res.append((y1, y2))
    return res

def count_offset(differences):
    """
        >>> import json
        >>> import reportor.image
        >>> differences = json.load(open('/tmp/http10.0.0.1195000mismatch_Galaxy_S4.json'))
        >>> for offset in reportor.image.count_offset(differences):
        ...     print(offset)
    """
    offsets = []
    history_offset = 0
    if len(differences) > 0:
        y1 = differences[0][0]
        y2 = differences[0][0] + differences[0][2] + differences[0][4]
    for _index, diff in enumerate(differences):
        if diff[5] == 'unmatch':
            for _key in ['left', 'height', 'width']:
                if diff[-1][_key] != 0:
                    break
            else:
                offset = diff[-1]['top'] - history_offset
                history_offset += offset
                if offset != 0:
                    offsets.append((diff[0], offset))
    return offsets

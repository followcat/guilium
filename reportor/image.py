import json

import Image
import ImageDraw
import validator.error


def markelements(img, results):
    drawer = ImageDraw.Draw(img)
    for each in results:
        top, left, height, width = each[0], each[1], each[2], each[3]
        button, right = top+height, left+width
        if each[4]:
            drawer.rectangle((left, top, right, button), outline='green')
        else:
            drawer.rectangle((left, top, right, button), outline='red')

def report(differences, storage, sut_name, stub_name, url):
    stack = storage.get()
    sutShot = stack[sut_name][url]['image']
    markelements(sutShot, differences)
    stubShot = stack[stub_name][url]['image']

    sut_width, sut_height = sutShot.size
    stub_width, stub_height = stubShot.size
    if stub_width > sut_width:
        scale = float(sut_width)/float(stub_width)
        stubShot = stubShot.resize((sut_width, int(stub_height*scale)))
        stub_width, stub_height = stubShot.size
    elif stub_width < sut_width:
        scale = float(stub_width)/float(sut_width)
        sutShot = sutShot.resize((stub_width, int(sut_height*scale)))
        sut_width, sut_height = sutShot.size
    result_image = Image.new('RGBA', (sut_width+stub_width,
                                      max(sut_height, stub_height)))
    result_image.paste(sutShot, (0, 0))
    result_image.paste(stubShot, (sut_width, 0))
    img_file = '/tmp/'+url.replace(":", "").replace("/", "")+'_'+sut_name+'.png'
    result_image.save(img_file)
    if len(differences) == 0:
        return
    init_y1 = differences[0][0]
    init_y2 = differences[0][0] + differences[0][2]
    for _index, diff in enumerate(differences):
        if diff[0] < init_y1 or diff[2] > 400 or diff[2] == 0:
            continue
        if diff[0] < init_y1:
            init_y1 = diff[0]
        if diff[0] > init_y2 +100:
            img_piece = result_image.crop((0, init_y1-20,
                            result_image.size[0], init_y2+20))
            img_piece.save('/tmp/diff/image_piece_%s.png'
                            %str((0, init_y1)))
            init_y1 = diff[0]
        if diff[0] + diff[2] > init_y2:
            init_y2 = diff[0] + diff[2]
    img_piece = result_image.crop((0, init_y1-20,
                    result_image.size[0], init_y2+20))
    img_piece.save('/tmp/diff/image_piece_%s.png'%str((0, init_y1)))

    if len(differences) > 0:
        json_file = '/tmp/'+url.replace(":", "").replace("/", "")+'_'+sut_name+'.json'
        with open(json_file, 'w') as fp:
            json.dump(differences, fp)
        json_link = 'file://' + json_file
        image_link = 'file://' + img_file
        raise validator.error.TestError("%d differences found in "
                    "positions %s... "
                    "\nSee %s"
                    "\n %s"%(len(differences), differences[0][0], json_link, image_link))

import os

from PIL import Image


def get_img_size(file_name: str):
    im = Image.open(file_name)
    return im.size


types = {"带电芯充电宝": "core", "不带电芯充电宝": "coreless"}


template = """
            <object>
                <name>{}</name>
                <pose>Frontal</pose>
                <truncated>0</truncated>
                <difficult>0</difficult>
                <bndbox>
                    <xmin>{}</xmin>
                    <ymin>{}</ymin>
                    <xmax>{}</xmax>
                    <ymax>{}</ymax>
                </bndbox>
            </object>
"""


def parse_to_xml(image_root, annotation_root, img_id):
    txt_path = annotation_root + os.sep + img_id + ".txt"
    img_path = image_root + os.sep + img_id + ".jpg"

    objects = []

    filename = img_id
    # read txt
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            t, x1, y1, x2, y2 = line.split(" ")[1:6]

            t = types.get(t, "unknow")
            objects.append({"t": t, "x1": x1, "x2": x2, "y1": y1, "y2": y2})

    img_size = get_img_size(img_path)
    size_w, size_h = img_size[0], img_size[1]

    unknow = True

    object_str = ""

    for o in objects:
        x1 = o["x1"]
        x2 = o["x2"]
        y1 = o["y1"]
        y2 = o["y2"]

        if o["t"] != "unknow":
            unknow = False
            object_str += template.format(o["t"], x1, y1, x2, y2)
    if unknow:
        return None
    content = f"""
        <annotation>
            <folder>ml</folder>
            <filename>{filename}.jpg</filename>
            <source>
                <database>imgs</database>
                <annotation>imgs_anno</annotation>
                <image>flickr</image>
                <flickrid>{filename}.jpg</flickrid>
            </source>
            <owner>
                <flickrid>buaa</flickrid>
                <name>soft</name>
            </owner>
            <size>
                <width>{size_w}</width>
                <height>{size_h}</height>
                <depth>3</depth>
            </size>
            <segmented>0</segmented>
            {object_str}
        </annotation>
        """
    return content

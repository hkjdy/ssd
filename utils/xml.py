import os
import shutil

from PIL import Image


def get_img_size(file_name: str):
    im = Image.open(file_name)
    return im.size


types = {"带电芯充电宝": "core", "不带电芯充电宝": "coreless"}


objects = """
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


def init_xmls(image_path, anno_path, out_put):
    if not os.path.exists(out_put):
        os.makedirs(out_put)
    result = {}
    filenames = os.listdir(anno_path)
    for filename in filenames:
        if not filename.endswith(".txt"):
            continue

        filename = filename[:-4]
        anno_file = anno_path + os.sep + filename + ".txt"
        img_file = image_path + os.sep + filename + ".jpg"

        with open(anno_file, "r", encoding="UTF-8") as f:
            for line in f:
                line = line.rstrip()
                t, x1, y1, x2, y2 = line.split(" ")[1:6]

                if filename not in result:
                    result[filename] = {}
                if "objects" not in result[filename]:
                    result[filename]["objects"] = []

                t = types.get(t, "unknow")

                result[filename]["objects"].append(
                    {"t": t, "x1": x1, "x2": x2, "y1": y1, "y2": y2}
                )

        img_size = get_img_size(img_file)
        size_w, size_h = img_size[0], img_size[1]

        if filename not in result:
            result[filename] = {}

        result[filename].update({"w": size_w, "h": size_h})

    for key, value in result.items():
        img_id = key[-5:]
        img_name = f"{key}.jpg"
        height = value["h"]
        width = value["w"]

        object_str = ""
        unknow = True
        for o in value["objects"]:
            x1 = o["x1"]
            x2 = o["x2"]
            y1 = o["y1"]
            y2 = o["y2"]

            if o["t"] != "unknow":
                unknow = False
                object_str += objects.format(o["t"], x1, y1, x2, y2)
        if unknow:
            continue
        content = f"""
            <annotation>
                <folder>ml</folder>
                <filename>{img_name}</filename>
                <source>
                    <database>imgs</database>
                    <annotation>imgs_anno</annotation>
                    <image>flickr</image>
                    <flickrid>{img_name}</flickrid>
                </source>
                <owner>
                    <flickrid>buaa</flickrid>
                    <name>soft</name>
                </owner>
                <size>
                    <width>{width}</width>
                    <height>{height}</height>
                    <depth>3</depth>
                </size>
                <segmented>0</segmented>
                {object_str}
            </annotation>
            """
        with open(f"{out_put}/{img_name[:-4]}.xml", "w") as o:
            o.write(content)
            o.close()


def clear_xmls(path):
    if os.path.exists(path):
        shutil.rmtree(path)

from ..core.bbox_parser import bbox_parser
from xmltodict import parse
import xml.etree.ElementTree as ET


def read_xml(path, mapping=None, kwargs={}) -> None:

    # parse xml file
    tree = ET.parse("PATH_TO_XML")
    root = tree.getroot()  # get root object

    height = int(root.find("size")[0].text)
    width = int(root.find("size")[1].text)
    channels = int(root.find("size")[2].text)

    with open("XML_PATH") as file:
        file_data = file.read()  # read file contents

        # parse data using package
        dict_data = parse(file_data)
        print("Not Implemented")
        pass

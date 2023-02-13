from ..core.bbox_parser import BboxParser
from pandas import DataFrame, json_normalize
import json
from os import PathLike


def get_bbox_type(df) -> str:
    bbox_types = [('x_center', 'y_center', 'width', 'height'),
                  ('x_max', 'y_max', 'x_min', 'y_min'),
                  ('x_min', 'y_min', 'width', 'height')]
    for bbox_type, cols in enumerate(bbox_types):
        if all(col in df.columns for col in cols):
            return ['cwh', 'tlbr', 'tlwh'][bbox_type]
    return None


def read_manifest(path: str | PathLike, format='auto') -> BboxParser:
    '''
    Read bounding boxes from a manifest file using pandas.read_csv.

    Parameters
    ----------
    path : str | os.PathLike
        Path to csv file
    format : str
        Format of the manifest file. Can be one of the following: 'auto', 'coco', 'pascal'
    '''

    mapping = {
        'top': 'y_min',
        'left': 'x_min',
        'right': 'x_max',
        'bottom': 'y_max',
        'width': 'width',
        'height': 'height',
        'class': 'class_name',
        'confidence': 'confidence',
        'image_width': 'image_width',
        'image_height': 'image_height',
        'image_channels': 'image_channel',
        'file_path': 'file_path'
    }

    with open(path, 'r') as f:

        data = DataFrame()
        for line in f:
            json_obj = json.loads(line)

            # Get the image file path
            file_path = json_obj['source-ref']

            # Get the image information
            img = json_obj['crh-label-test5']['image_size'][0]
            image_width, image_height, image_channel = img.values()

            # Get the bboxes mapping of the classes
            class_map = json_obj['crh-label-test5-metadata']['class-map']
            class_map = {int(k): v for k, v in class_map.items()}

            # Get the bboxes annotations
            annotations = json_obj['crh-label-test5']['annotations']
            bboxes = json_normalize(annotations)

            # Add the image information to the bboxes
            bboxes['image_width'] = image_width
            bboxes['image_height'] = image_height
            bboxes['image_channel'] = image_channel
            bboxes['file_path'] = file_path
            bboxes['class_name'] = bboxes['class_id'].map(class_map)
            bboxes.drop(columns=['class_id'], inplace=True)

            data = data.append(bboxes, ignore_index=True)

    data.rename(columns=mapping, inplace=True)

    return BboxParser(data, 'tlwh')

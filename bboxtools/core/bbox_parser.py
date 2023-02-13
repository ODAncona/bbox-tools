from pandas.core.frame import DataFrame
from bboxtools.core.bbox import BBox, TLBR_BBox, TLWH_BBox, CWH_BBox
from bboxtools.io.writer_coco import to_coco
from bboxtools.io.writer_yolo import to_yolo
from bboxtools.io.writer_pascal_voc import to_pascal_voc
from os import PathLike

FORMAT = ['voc', 'coco', 'yolo', 'sagemaker']
TYPES = ['tlbr', 'tlwh', 'cwh']


class BboxParser():
    """
    Bounding box parser class
    
    Parameters
    ----------
    data : pandas.DataFrame
        Dataframe containing bounding boxes. Could contains some of the following columns:
            -'class_name'
            -'file_path'
            -'x_min',s
            -'y_min',
            -'x_max',
            -'y_max',
            -'x_center', 
            -'y_center',
            -'width',
            -'height'
            -'confidence'
            -'image_height'
            -'image_width'
            -'image_channels'
    bbox_type : str
        Type of bounding box. Can be one of the following: 'tlbr', 'tlwh', 'cwh'
    """

    data: DataFrame = None
    bbox_type: str = None

    def __init__(self, data: DataFrame, bbox_type) -> None:
        self.data = data
        self.bbox_type = bbox_type

    def create_bbox(self, bbox_type: str, **kwargs) -> BBox:
        '''
        Create bounding box object from a dictionary of parameters

        Parameters
        ----------
        bbox_type : str
            Type of bounding box. Can be one of the following: 'tlbr', 'tlwh', 'cwh'
        **kwargs : dict
            Dictionary of parameters for bounding box
        '''
        if bbox_type == 'tlbr':
            return TLBR_BBox(**kwargs)
        if bbox_type == 'tlwh':
            return TLWH_BBox(**kwargs)
        if bbox_type == 'cwh':
            return CWH_BBox(**kwargs)
        return None

    def export(self, output_path: str | PathLike, format: str) -> None:
        '''
        Export bounding boxes to a popular file format
        
        Parameters
        ----------
        output_path : str | os.PathLike
            Path to output file
        format : str
            Format of output file. Can be one of the following: 'voc', 'coco', 'yolo', 'sagemaker'
        type : str
            Type of bounding box. Can be one of the following: 'tlbr', 'tlwh', 'cwh'
        '''
        assert self.bbox_type is not None

        # Conversion function map (output_format, input_bbox_type)
        # For each format should have three functions to convert from TLBR, TLWH, CWH
        format_map = {
            ('voc', 'tlwh'): TLBR_BBox.from_TLWH,
            ('voc', 'cwh'): TLBR_BBox.from_CWH,
            ('voc', 'tlbr'): True,
            ('coco', 'tlbr'): TLWH_BBox.from_TLBR,
            ('coco', 'cwh'): TLWH_BBox.from_CWH,
            ('coco', 'tlwh'): True,
            ('yolo', 'tlbr'): CWH_BBox.from_TLBR,
            ('yolo', 'tlwh'): CWH_BBox.from_TLWH,
            ('yolo', 'cwh'): True,
        }

        # Get conversion function
        convert_func = format_map.get((format.lower(), self.bbox_type))

        if convert_func is None:
            raise ValueError(f"Invalid export format: {format}")

        # Transform data to bounding boxes
        bboxes = self.data.apply(
            lambda x: self.create_bbox(self.bbox_type, **x.to_dict()), axis=1)

        # Serialize bounding boxes
        bboxes = bboxes.apply(lambda x: convert_func(x).to_dict()
                              if convert_func != True else x.to_dict())

        # Save to file
        if format == 'coco':
            #to_coco(bboxes, output_path)
            pass
        if format == 'voc':
            #to_pascal_voc(bboxes, output_path)
            pass
        if format == 'yolo':
            #to_yolo(bboxes, output_path)
            pass

    def to_csv(self, output_path: str | PathLike, type) -> None:
        '''
        Export bounding boxes to a csv file
        
        Parameters
        ----------
        output_path : str | os.PathLike
            Path to output file
        type : str
            Type of bounding box. Can be one of the following: 'tlbr', 'tlwh', 'cwh'
        '''
        assert self.bbox_type is not None
        if type not in TYPES:
            raise ValueError(f"Invalid bbox type: {type}")

        # Conversion function map (output_type, input_bbox_type)
        # Each type should have two functions to convert from TLBR, TLWH, CWH
        type_map = {
            ('tlbr', 'tlwh'): TLBR_BBox.from_TLWH,
            ('tlbr', 'cwh'): TLBR_BBox.from_CWH,
            ('tlwh', 'tlbr'): TLWH_BBox.from_TLBR,
            ('tlwh', 'cwh'): TLWH_BBox.from_CWH,
            ('cwh', 'tlbr'): CWH_BBox.from_TLBR,
            ('cwh', 'tlwh'): CWH_BBox.from_TLWH,
        }

        if type == self.bbox_type:
            # No conversion needed
            self.data.to_csv(output_path, index=False)
            return

        # Get conversion function
        convert_func = type_map.get((type, self.bbox_type))

        if convert_func is None:
            raise ValueError(f"Invalid bbox type: {type}")

        # Transform data to bounding boxes
        bboxes = self.data.drop(
            columns=['image_width', 'image_height', 'image_channel'],
            errors='ignore').apply(
                lambda x: self.create_bbox(self.bbox_type, **x.to_dict()),
                axis=1)

        # Serialize bounding boxes
        bboxes = bboxes.apply(lambda x: convert_func(x).to_dict())

        # Save to file
        DataFrame.from_records(bboxes).to_csv(output_path, index=False)

    def __str__(self) -> str:
        return self.data.to_string()

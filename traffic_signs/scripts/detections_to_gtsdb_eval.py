#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author: Boyuan Deng <bryanhsudeng@gmail.com>

from __future__ import print_function

doppia_root_dir = "../../../doppia"


import os, os.path
import sys

sys.path.append(os.path.join(doppia_root_dir, "tools", "objects_detection"))
sys.path.append(os.path.join(doppia_root_dir, "tools", "data_sequence"))
sys.path.append(os.path.join(doppia_root_dir, "tools", "helpers"))
 
from detections_pb2 import Detections, Detection
from data_sequence import DataSequence

from optparse import OptionParser


def open_data_sequence(data_filepath):
        
    assert os.path.exists(data_filepath)
    
    the_data_sequence = DataSequence(data_filepath, Detections)
    
    def data_sequence_reader(data_sequence):    
        while True:
            data = data_sequence.read()
            if data is None:
                raise StopIteration
            else:
                yield data
    
    return data_sequence_reader(the_data_sequence)    
    

def parse_arguments():
        
    parser = OptionParser()
    parser.description = \
        "This program takes a detections.data_sequence created by ./objects_detection and converts it into the GTSDB evaluation format"

    parser.add_option("-i", "--input", dest="input_path",
                       metavar="FILE", type="string",
                       help="path to the .data_sequence file")

    parser.add_option("-o", "--output", dest="output_path",
                       metavar="FILE", type="string",
                       help="path to the GTSDB result file you want to create")
                                                  
    (options, args) = parser.parse_args()
    #print (options, args)

    if options.input_path:
        if not os.path.exists(options.input_path):
            parser.error("Could not find the input file")
    else:
        parser.error("'input' option is required to run this program")

    return options 


def create_gtsdb_detections(detections_sequence, output_path):
    """
    """
    
    for detections in detections_sequence:
        # trick to restore the ".ppm" file extension
        image_name = os.path.splitext(detections.image_name)[0] + ".ppm"
        text_file = open(output_path, "a") # append to the file
            
        for detection in detections.detections:
            # never care about the detection name --deng #
            if detection.object_class != Detection.Pedestrian:
                continue
            
            if False and detection.score < 0:
                # we skip negative scores
                continue
            
            box = detection.bounding_box
            min_x, min_y = box.min_corner.x, box.min_corner.y
            max_x, max_y = box.max_corner.x, box.max_corner.y

            # data is [x,y,w,h, score]
            detection_data = []            
            detection_data += [min_x, min_y]
            detection_data += [max_x, max_y]
            detection_line = image_name + ";" + ";".join([str(x) for x in detection_data]) + "\n"
            text_file.write(detection_line)
            
        text_file.close()
        
    return

def detections_to_gtsdb(input_path, output_path):
    
    # get the input file
    #input_file = open(options.input_path, "r")
    detections_sequence = open_data_sequence(input_path)
    create_gtsdb_detections(detections_sequence, output_path)
    print("Created file ", output_path)
    
    return

def main():
    
    options = parse_arguments()    
    detections_to_gtsdb(options.input_path, options.output_path)
    return


if __name__ == "__main__":
        
    # Import Psyco if available
    try:
        import psyco
        psyco.full()
    except ImportError:
        #print("(psyco not found)")
        pass
    else:
        print("(using psyco)")
      
    main()







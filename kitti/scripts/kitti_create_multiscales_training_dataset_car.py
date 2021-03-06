#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Boyuan Deng <bryanhsudeng@gmail.com>

"""
This program parses the KITTI dataset and creates
the data for training a multiscales model
"""

from __future__ import print_function

import sys
#sys.path.append("..")
#sys.path.append("../data_sequence")
#sys.path.append("../helpers")

#from detections_pb2 import Box
#from data_sequence import DataSequence

import os, os.path, glob
from optparse import OptionParser
from multiprocessing import Pool, Lock, cpu_count
import itertools
import cv2

import matplotlib
matplotlib.use("Qt4Agg") # force matplotlib to display interactive plots

import math, pylab

class Point2d:
    """
    Helper class to define Box
    """
    def __init__(self, x,y):
        self.x = x
        self.y = y
        return

class Box:
    """
    This class replaces from detections_pb2 import Box
    since it does not support negative coordinates for the boxes
    """

    def __init__(self):
        self.min_corner = Point2d(0,0)
        self.max_corner = Point2d(0,0)
        return

    def copy(self):
        b = Box()
        b.min_corner = self.min_corner
        b.max_corner = self.max_corner
        return b

    def width(self):
        return self.max_corner.x - self.min_corner.x

    def height(self):
        return self.max_corner.y - self.min_corner.y


def annotations_to_filenames_and_boxes(data_path, category):
    """
    We expect the data_path to be
    <path to KITTI root>/training

    will return an generator that yields (file_path, boxes) tuples
    boxes is a list with instances of Box
    """

    assert os.path.split(data_path)[-1] == "training"
    annotations_path_pattern = os.path.join(data_path, 'label_2/*.txt')

    for file_path in glob.iglob(annotations_path_pattern):
        f = open(file_path)
        boxes = []

        image_path = os.path.join(
            data_path, 'image_2',
            os.path.split(file_path)[-1].replace(".txt", ".png")
            )

        for line in f:
            if line.startswith(category):
                bbox = line.split()[4:8]
                box = Box()
                box.min_corner.x = float(bbox[0])
                box.min_corner.y = float(bbox[1])
                box.max_corner.x = float(bbox[2])
                box.max_corner.y = float(bbox[3])

                boxes.append(box)

        #if not boxes:
            #raise "Failed to find a bounding box inside %s" % file_path
        #if not image_path:
            #raise "Failed to find the image path inside %s" % file_path

        yield (image_path, boxes)

    return


def print_kitti_training_statistics(data_path, category):
    # dataset statistics
    """
    Small helper function.
    """
    assert os.path.split(data_path)[-1] == "training"
    annotations_path_pattern = os.path.join(data_path, 'label_2/*.txt')

    # trick: impossible default values
    min_width = 1000.0
    min_height = 1000.0
    max_width = 0
    max_height = 0
    min_ratio = 100
    max_ratio = 0.01

    for file_path in glob.iglob(annotations_path_pattern):
        f = open(file_path)
        boxes = []

        image_path = os.path.join(
            data_path, 'image_2',
            os.path.split(file_path)[-1].replace(".txt", ".png")
            )

        for line in f:
            if line.startswith(category):
                bbox = line.split()[4:8]
                box = Box()
                box.min_corner.x = float(bbox[0])
                box.min_corner.y = float(bbox[1])
                box.max_corner.x = float(bbox[2])
                box.max_corner.y = float(bbox[3])

                width = box.max_corner.x - box.min_corner.x
                height = box.max_corner.y - box.min_corner.y
                ratio = height/float(width)

                min_width = min(min_width, width)
                min_height = min(min_height, height)
                max_width = max(max_width, width)
                max_height = max(max_height, height)

                min_ratio = min(min_ratio, ratio)
                max_ratio = max(max_ratio, ratio)

    print("min_width ==", min_width)
    print("min_height ==", min_height)
    print("max_width ==", max_width)
    print("max_height ==", max_height)
    print("max_ratio ==", max_ratio)
    print("min_ratio ==", min_ratio)

    return


def parse_arguments():

    parser = OptionParser()
    parser.description = \
        "This program takes the KITTI dataset and " \
        "creates a new training dataset for multiscale objects detection"

    parser.add_option("-i", "--input", dest="input_path",
                       metavar="PATH", type="string",
                       help="path to the KITTI dataset training folder")

    parser.add_option("-o", "--output", dest="output_path",
                       metavar="DIRECTORY", type="string",
                       help="path to a non existing directory where the new training dataset will be created")

    parser.add_option("-c", "--category", dest="object_category",
                       metavar="CATEGORY", type="string",
                       help="category of objects")

    (options, args) = parser.parse_args()
    #print (options, args)

    if options.input_path:
        if not os.path.exists(options.input_path):
            parser.error("Could not find the input file")
        else:
            # we normalize the path
            options.input_path = os.path.normpath(options.input_path)
    else:
        parser.error("'input' option is required to run this program")

    if options.output_path:
        if os.path.exists(options.output_path):
            parser.error("output_path should point to a non existing directory")
    else:
        parser.error("'output' option is required to run this program")

    if options.object_category:
        if options.object_category not in ['Car', 'Pedestrian', 'Cyclist']:
            parser.error("Unknown category, or this category needs no evaluation")
    else:
        parser.error("you must pick one category of objects")

    return options


def plot_cumulative_boxes_scale(annotations, dataset_name):
    # TODO: different object_height for categories, this function seems unused.
    # model_height = 128

    # object_height = 48
    boxes_scales = []

    for filename, boxes in annotations:
        for box in boxes:
            height = box.max_corner.y - box.min_corner.y
            scale = height / float(object_height)
            boxes_scales.append(scale)


    boxes_log_scales = [math.log(x)/math.log(2) for x in boxes_scales]
    min_log_scale = int(round(min(boxes_log_scales)))
    max_log_scale = int(round(max(boxes_log_scales)))

    if True:
        print("min/max scale in dataset %s == %.4f/%.4f" \
              % (dataset_name, min(boxes_scales), max(boxes_scales)))

    num_boxes_per_scale = pylab.zeros((max_log_scale - min_log_scale)+1)
    log_scales_range = range(min_log_scale, max_log_scale+1)
    for index, log_scale in enumerate(log_scales_range):
        num_boxes_per_scale[index] = len([x for x in boxes_log_scales if round(x) >= log_scale])


    if False:
        # create a new figure
        pylab.figure()
        pylab.gcf().set_facecolor("w") # set white background

        #scales_cumsum = pylab.cumsum(boxes_scales)
        #pylab.plot(scales_cumsum)
        pylab.hist(#boxes_scales,
                   boxes_log_scales,
                   bins=10,
                   #cumulative= True,
                   normed=True,
                   histtype = "stepfilled")
        pylab.title("Cumulative histogram of the annotated windows scales\n Dataset: " + dataset_name)
        pylab.xlabel("Annotated window scale octave")
        pylab.ylabel("Percent of annotated windows")


    # create a new figure
    pylab.figure()
    pylab.gcf().set_facecolor("w") # set white background

    pylab.plot(log_scales_range, num_boxes_per_scale)
    pylab.xlabel("Annotated window scale octave")
    pylab.ylabel("Number of annotated windows")
    pylab.title("Number of annotated windows per scale octave\n Dataset: " + dataset_name)

    pylab.grid(True)
    pylab.xticks(log_scales_range)
    #pylab.yticks(yticks)
    pylab.xlim([log_scales_range[0] - 0.5,  log_scales_range[-1] + 0.5])

    return


def adjust_box_ratio(box, model_width, model_height):

    box_height = box.max_corner.y - box.min_corner.y
    box_width = box_height*(model_width/model_height)
    box_x_center = (box.max_corner.x + box.min_corner.x) / 2
    box.min_corner.x = box_x_center - box_width/2
    box.max_corner.x = box_x_center + box_width/2
    return box


def adjust_box_border(box, top_bottom_border, left_right_border):

    assert top_bottom_border > 0
    assert left_right_border > 0
    box = box.copy() # to be sure we are not messing the data
    box.min_corner.x -= left_right_border
    box.min_corner.y -= top_bottom_border
    box.max_corner.x += left_right_border
    box.max_corner.y += top_bottom_border

    # image boxes only make sense with integer values
    box.min_corner.x = int(round(box.min_corner.x))
    box.min_corner.y = int(round(box.min_corner.y))
    box.max_corner.x = int(round(box.max_corner.x))
    box.max_corner.y = int(round(box.max_corner.y))

    return box


def resized_image(image, desired_width, desired_height):
    """
    Resizes an image, applies adequate filter, and then subsample/upsample the image
    """

    input_height, input_width, _ = image.shape
    resized_shape = (desired_height, desired_width)

    will_do_shrinking = (resized_shape[0] < image.shape[0]) or (resized_shape[1] < image.shape[1])

    if will_do_shrinking:
        height_ratio = resized_shape[0] / float(image.shape[0])
        width_ratio = resized_shape[1] / float(image.shape[1])
        resizing_ratio = min(height_ratio, width_ratio)

        #print("resized_shape ==", resized_shape)
        #print("image.shape ==",  image.shape)
        #assert resizing_ratio > 0
        assert resizing_ratio < 1
        # Following OpenCv and Vincent De Smet suggestions for the
        # kernel size and sigma values
        kernel_size = int(5/(2*resizing_ratio))
        sigma = 0.5 / resizing_ratio
        kernel = cv2.getGaussianKernel(kernel_size, sigma)
        image_to_resize = cv2.filter2D(image, cv2.CV_8UC3, kernel)
        interpolation_type = cv2.INTER_AREA
    else:
        # doing streching
        image_to_resize = image
        #interpolation_type = cv2.INTER_LINEAR
        interpolation_type = cv2.INTER_CUBIC
        #interpolation_type = cv2.INTER_LANCZOS4

    resized_image = cv2.resize(image_to_resize,
                           (desired_width, desired_height), # destination size (width, height)
                           None,
                           0, 0, interpolation_type)

    return resized_image


failures_count = 0

def compute_resized_positive_example(input_image, input_image_path,
                                     box, box_scale, model_octave,
                                     cropping_border, model_width, model_height):
    """
    The input box is expected to be a tight box around the pedestrian
    """

    assert input_image != None
    assert type(model_width) is int
    assert type(model_height) is int
    assert type(cropping_border) is int

    image_height, image_width, image_depth = input_image.shape

    # adjust the ratio, add the border --

    # adjusting the ratio is a bad idea, pedestrians look "fat"
    # instead, we adjust the left/right border
    #box = adjust_box_ratio(box, model_width, model_height)

    example_width = model_width+(2*cropping_border)
    example_height = model_height+(2*cropping_border)

    model_scale = 2**model_octave
    box_relative_scale = box_scale/model_scale

    input_box_width, input_box_height = box.width(), box.height()

    # XXX: adjust_ratio
    adjust_ratio = True

    if adjust_ratio:
        desired_input_box_height = example_height * box_relative_scale

        # TODO: different object_width for categories
        object_width = 90
        box_width_scale = input_box_width / float(object_width)
        box_width_relative_scale = box_width_scale/model_scale
        desired_input_box_width = example_width * box_width_relative_scale
    else:
        desired_input_box_width = example_width * box_relative_scale
        desired_input_box_height = example_height * box_relative_scale



    top_bottom_border = (desired_input_box_height - input_box_height)/2.0
    left_right_border = (desired_input_box_width - input_box_width)/2.0

    desired_input_box_shape = (desired_input_box_height, desired_input_box_width)

    if (left_right_border <= 0) or False:
        print("model width, height ==", (model_width, model_height))
        print("example_width ==", example_width)
        print("box_scale ==", box_scale)
        print("model_scale ==", model_scale)
        print("box_relative_scale ==", box_relative_scale)
        print("desired_input_box_width ==", desired_input_box_width)
        print("input_box_width ==", input_box_width)
        print("input_box_height ==", input_box_height)
        print("input_box ratio ==", input_box_height/float(input_box_width))
        p1 = (int(box.min_corner.x), int(box.min_corner.y))
        p2 = (int(box.max_corner.x), int(box.max_corner.y))
        print("input_box min_corner, max_corner == ", p1, ",", p2)
        color = (255, 10, 50)
        failure_image = input_image.copy()
        cv2.rectangle(failure_image, p1, p2, color)
        global failures_count
        failure_filename = "failure_case_%i_%s" % (failures_count, os.path.basename(input_image_path))
        cv2.imwrite(failure_filename, failure_image)
        print("Created %s skipping one bounding_box in picture %s" % (failure_filename, input_image_path))
        failures_count += 1
        return None # indicate that something went wrong


    box = adjust_box_border(box, top_bottom_border, left_right_border)
    # the box now has the desired_input_box_width and _height

    box_shape = (box.height(), box.width())
    #print(box_shape, "=?=", desired_input_box_shape)
    assert abs(box_shape[0] - desired_input_box_shape[0]) <= 1.0
    assert abs(box_shape[1] - desired_input_box_shape[1]) <= 1.0


    # crop the box --
    # which part of the box is outside the image ?
    left_border = int(max(0, 0 - box.min_corner.x))
    top_border = int(max(0, 0 - box.min_corner.y))
    right_border = int(max(0, box.max_corner.x - image_width))
    bottom_border = int(max(0, box.max_corner.y - image_height))

    # define the part of the box that is inside the image
    inner_box = box.copy()
    inner_box.min_corner.x = max(0, box.min_corner.x)
    inner_box.min_corner.y = max(0, box.min_corner.y)
    inner_box.max_corner.x = min(box.max_corner.x, image_width)
    inner_box.max_corner.y = min(box.max_corner.y, image_height)

    # crop
    cropped_image = input_image[inner_box.min_corner.y:inner_box.max_corner.y,
                                inner_box.min_corner.x:inner_box.max_corner.x,
                               :]
    # extrapolate --

    #border_type = cv2.BORDER_CONSTANT
    border_type = cv2.BORDER_REPLICATE
    #border_type = cv2.BORDER_WRAP
    #border_type = cv2.BORDER_REFLECT
    #border_type = cv2.BORDER_REFLECT_101
    cropped_image = cv2.copyMakeBorder(cropped_image,
                                       top_border, bottom_border,
                                       left_border, right_border,
                                       border_type)


    #print(cropped_image.shape[:2], "=?=", box_shape)
    assert cropped_image.shape[:2] == box_shape


    # rescale the box so it fits the desired dimensions --
    resized_positive_example = resized_image(cropped_image, example_width, example_height)
    assert resized_positive_example.shape == (example_height, example_width, image_depth)

    return resized_positive_example


def plot_dataset_annotations_sizes(data_path):

    # check thet data path is either Train or Test inside INRIAPerson
    inria_person_path, subfolder_name = os.path.split(data_path)
    assert os.path.isdir(data_path)
    assert os.path.basename(inria_person_path) == "INRIAPerson"
    assert subfolder_name in ["Train", "Test"]

    def plot_annotations(inria_path, subfolder_name):
        data_folder = os.path.join(inria_person_path,  subfolder_name)
        assert os.path.isdir(data_folder)
        t_annotations = list(annotations_to_filenames_and_boxes(data_folder))
        plot_cumulative_boxes_scale(t_annotations, data_folder)

    show_train_data = True
    if show_train_data:
        plot_annotations(inria_person_path,  "Train")

    show_test_data = True
    if show_test_data:
        plot_annotations(inria_person_path,  "Test")
        pass

    if show_train_data or show_test_data:
        pylab.show()

    return


def save_positive_example(example, positives_path, box_counter, is_bigger, create_flipped):

    if example == None:
        # something went wrong, skipping
        print("[WARNING] Skipping example %i since it turns out to be empty" % box_counter)
        return

    extension = ".png"
    if not is_bigger:
        extension = ".upscaled" + extension
    else:
        # by default everything is expected to be downscaled
        pass
    filename_base = "sample_%i" % box_counter
    example_path = os.path.join(positives_path,
                                filename_base + extension)
    cv2.imwrite(example_path, example)

    if create_flipped:
        flip_code = 1 # flip around the vertical axis
        example_flipped = cv2.flip(example, flip_code)
        example_flipped_path = \
                os.path.join(positives_path,
                             filename_base + "_mirror" + extension)
        cv2.imwrite(example_flipped_path, example_flipped)
        #print("Created :", example_path, "(and its mirror)")
    else:
        #print("Created :", example_path)
        pass

    return



print_counter = 0

def create_positives_process_annotation_box(box_counter, annotation_box, positives_path,
                                            model_width, model_height, cropping_border, octave):

    image_path, box = annotation_box
    # TODO: different object_height for categories
    object_height = 50 # the expected height of the traffic sign inside the detection box

    # when create_blurred is true, will create
    # blurry scaled up images (ignoring the scales constraints)
    #create_blurred = False
    create_blurred = True

    create_flipped = True

    height = box.max_corner.y - box.min_corner.y
    scale = height / float(object_height)
    box_octave = round(math.log(scale)/math.log(2))

    is_bigger = (box_octave >= octave)
    if is_bigger or create_blurred:
        #print("Reading :", image_path)
        input_image = cv2.imread(image_path)

        example = compute_resized_positive_example(
                input_image, image_path, box, scale, octave,
                cropping_border, model_width, model_height)

        save_positive_example(example, positives_path, box_counter, is_bigger, create_flipped)

        print(".", end="")
        global print_counter
        print_counter += 1 # no need to be thread safe
        if print_counter % 10:
            sys.stdout.flush()
    else:
        # we skip this sample
        pass


    #if create_blurred:
    #    print("These examples include blurry, upscaled, images")

    return
# end of "def create_positives_process_annotation_box"


class Lambda:

    def __init__(self, f, args_tuple):
        self.args_tuple = args_tuple
        self.f = f
        return

    def __call__(self, args):
        #print("Lambda.__call__ with args", args)
        return self.f(*(args + self.args_tuple))


def create_positives(model_width, model_height,
                     cropping_border, octave,
                     annotations,
                     output_path):
    """
    Create the positives examples
    """

    # we expand all the anotations in the a long list of
    # (filename, box)
    # each box represent an object
    annotation_boxes = itertools.chain.from_iterable(
                [itertools.product([x[0]], x[1]) for x in annotations])

    # create the output folder
    positives_path = os.path.join(output_path, "positives_octave_%.1f" % octave)
    if os.path.exists(positives_path):
        raise RuntimeError(positives_path + " should not exist")

    os.mkdir(positives_path)
    print("Created folder", positives_path)

    data = list(enumerate(annotation_boxes))
    #print("data[:10] ==", data[:10])
    g = Lambda(create_positives_process_annotation_box,
                   (positives_path, model_width, model_height, cropping_border, octave))

    #use_multithreads = True
    use_multithreads = False
    if use_multithreads:
        # multithreaded processing of the files
        num_processes = cpu_count() + 1
        pool = Pool(processes = num_processes)
        #g = lambda z: f(z[0], z[1])
        chunk_size = len(data) / num_processes
        pool.map(g, data, chunk_size)

    else:
        for d in data:
            g(d)


    # end of "for each annotation file"
    print()
    print("Created the positives examples for octave %.1f" % (octave) )
    #if create_flipped:
    #    print("For octave %.1f created %i positive examples (and its mirror)" % (octave, ns.sample_counter) )
    #else:
    #    print("For octave %.1f created %i positive examples" % (octave, ns.sample_counter) )

    #if create_blurred:
    #    print("These examples include blurry, upscaled, images")

    return
# end of "def create_positives"


def create_negatives_process_file(negatives_counter, file_path, model_width, model_height, negatives_path):
    negative_image = cv2.imread(file_path)

    model_to_negative_factor = 1.5 # negative images are 1.5 bigger than the model
    minimum_image_shape = (model_height*model_to_negative_factor, model_width*model_to_negative_factor)

    # <= because the C++ code has some weird +1's
    if (negative_image.shape[1] <= minimum_image_shape[1]) or  \
        (negative_image.shape[0] <= minimum_image_shape[0]):
        # must resize the image
        negative_filename = "negative_sample_%i.resized.png" % negatives_counter

        # width / height
        image_ratio = float(negative_image.shape[1]) / negative_image.shape[0]
        if (negative_image.shape[1] <= minimum_image_shape[1]):
            resized_size = (int(minimum_image_shape[1]),
                            int(minimum_image_shape[1]/image_ratio))

        if (negative_image.shape[0] <= minimum_image_shape[0]):
            resized_size = (int(minimum_image_shape[0]*image_ratio),
                            int(minimum_image_shape[0]))

        resized_shape = (resized_size[1], resized_size[0], negative_image.shape[2])
        assert resized_shape[0] >= minimum_image_shape[0]
        assert resized_shape[1] >= minimum_image_shape[1]

        negative_image_resized = resized_image(negative_image, resized_size[0], resized_size[1])
        negative_image = negative_image_resized
    else:
        # we can just copy
        negative_filename = "negative_sample_%i.png" % negatives_counter

    image_output_path = os.path.join(negatives_path, negative_filename)
    cv2.imwrite(image_output_path, negative_image)
    print(".", end="")
    global print_counter
    print_counter += 1 # no need to be thread safe
    if print_counter % 10:
        sys.stdout.flush()
    return
# end of "create_negatives_process_file"


def create_negatives(model_width, model_height, octave,
                     data_path, output_path):

    # create the output folder
    negatives_path = os.path.join(output_path, "negatives_octave_%.1f" % octave)
    if os.path.exists(negatives_path):
        raise RuntimeError(negatives_path + " should not exist")

    os.mkdir(negatives_path)
    print("Created folder", negatives_path)

    negatives_path_pattern = os.path.join(data_path, "neg/*.*")
    files_paths = list(glob.iglob(negatives_path_pattern))

    g = Lambda(create_negatives_process_file, (model_width, model_height, negatives_path))

    #use_multithreads = True
    use_multithreads = False
    if use_multithreads:
        # multithreaded processing of the files
        num_processes = cpu_count() + 1
        pool = Pool(processes = num_processes)
        chunk_size = len(files_paths) / num_processes
        pool.map(g, enumerate(files_paths))
        #parallel_map(process_file, files_paths, cpu_count() + 1)
    else:
        for counter, file_path in enumerate(files_paths):
            g((counter, file_path))

    print()

    resized_path_pattern = os.path.join(negatives_path, "*.resized.png")
    num_resized = len(list(glob.iglob(resized_path_pattern)))
    print("For octave %.1f created %i negatives images (%i are resized)"
            % (octave, len(files_paths), num_resized))

    return
# end of "def create_negatives"


def create_positives_and_negatives(data_path, output_path, annotations,
                                   model_width, model_height, cropping_border,
                                   octave):

    model_width, model_height = int(model_width*(2**octave)), int(model_height*(2**octave))
    octave_cropping_border = int(cropping_border*(2**octave))

    # make sure model size is pair, so we have a well defined center
    if (model_width % 2) == 1: model_width += 1
    if (model_height % 2) == 1: model_height += 1

    print("At octave %.1f, model (width, height) == %s and cropping_border == %i" %
            (octave, str((model_width, model_height)), octave_cropping_border))

    create_positives(model_width, model_height,
                     octave_cropping_border, octave,
                     annotations,
                     output_path)

    create_negatives(model_width, model_height, octave,
                     data_path, output_path)
    return
# end of "def create_positives_and_negatives"


def create_multiscales_training_dataset(data_path, output_path, category):


    # check that data path is KITTI's training path
    assert os.path.split(data_path)[-1] == "training"

    annotations = list(annotations_to_filenames_and_boxes(data_path, category))

    # define the scales we care about
    min_scale, max_scale = 1, 1 # this is the scales range used for KITTI
    delta_octave = 1.0
    #delta_octave = 0.5

    # TODO: different model size for categories
    model_width, model_height = 104, 58

    cropping_border = 10 # how many pixels around the model box to define a test image ?

    if False:
        # just for testing
        cropping_border = 20 # how many pixels around the model box to define a test image ?
        min_scale, max_scale = 4, 4

    min_octave = int(round(math.log(min_scale)/math.log(2)))
    max_octave = int(round(math.log(max_scale)/math.log(2)))
    octaves = list(pylab.frange(min_octave, max_octave, delta_octave))
    octaves.reverse() # for debugging, it is easier to look at big pictures first

    if os.path.exists(output_path):
        raise RuntimeError(output_path + " should not exist")
    else:
        os.mkdir(output_path)
        print("Created folder", output_path)

    print("Will create data for octaves", octaves)

    for octave in octaves:
        create_positives_and_negatives(data_path, output_path, annotations,
                                       model_width, model_height, cropping_border,
                                       octave)
    # end of "for each octave"

    return
# end of "def create_multiscales_training_dataset"



def main():
    options = parse_arguments()

    if False:
    #if True:
        print_kitti_training_statistics(options.input_path, options.object_category)
    else:
        create_multiscales_training_dataset(options.input_path, options.output_path, options.object_category)

    print("End of game, have a nice day!")
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

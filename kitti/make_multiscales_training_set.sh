### first set this ###
KITTI_DATASET_ROOT_DIR=/home/deng/datasets/KITTI
NEGATIVES_PATH=/home/deng/datasets/negatives


KITTI_TRAIN_SET_DIR=${KITTI_DATASET_ROOT_DIR}/training
KITTI_NEGATIVES_DIR=${KITTI_DATASET_ROOT_DIR}/training/neg
KITTI_MULTISCALES_TRAIN_SET_DIR=${KITTI_DATASET_ROOT_DIR}/Train_multiscales


if [ -d $KITTI_MULTISCALES_TRAIN_SET_DIR ]
then
    rm -r $KITTI_MULTISCALES_TRAIN_SET_DIR
    mkdir $KITTI_MULTISCALES_TRAIN_SET_DIR
else
    mkdir $KITTI_MULTISCALES_TRAIN_SET_DIR
fi

if [ -d $KITTI_NEGATIVES_DIR ]
then
    rm -r $KITTI_NEGATIVES_DIR
fi

# model size/ object size (width, height)
# Car 104 58 / 90 50
# Pedestrian  70 126 / 60 108
# Cyclist 22 38 / 18 32

python scripts/generate_negative_samples.py -i ${NEGATIVES_PATH} -o ${KITTI_NEGATIVES_DIR} --target_size "90,50" --sample_ratio 1.8 -n 2000
python scripts/kitti_create_multiscales_training_dataset_car.py -i $KITTI_TRAIN_SET_DIR -o ${KITTI_MULTISCALES_TRAIN_SET_DIR}/Car -c 'Car'
rm -r $KITTI_NEGATIVES_DIR
python scripts/generate_negative_samples.py -i ${NEGATIVES_PATH} -o ${KITTI_NEGATIVES_DIR} --target_size "60,108" --sample_ratio 0.55 -n 2000
python scripts/kitti_create_multiscales_training_dataset_pedestrian.py -i $KITTI_TRAIN_SET_DIR -o ${KITTI_MULTISCALES_TRAIN_SET_DIR}/Pedestrian -c 'Pedestrian'
rm -r $KITTI_NEGATIVES_DIR
python scripts/generate_negative_samples.py -i ${NEGATIVES_PATH} -o ${KITTI_NEGATIVES_DIR} --target_size "80,100" --sample_ratio 0.57 -n 2000
python scripts/kitti_create_multiscales_training_dataset_cyclist.py -i $KITTI_TRAIN_SET_DIR -o ${KITTI_MULTISCALES_TRAIN_SET_DIR}/Cyclist -c 'Cyclist'


# [Car]
# min_width == 23.22
# min_height == 15.37
# max_width == 402.31
# max_height == 193.1
# max_ratio == 0.96795985331
# min_ratio == 0.344980868782

# [Pederstrian]
# min_width == 30.71
# min_height == 59.9
# max_width == 98.33
# max_height == 164.92
# max_ratio == 1.95050472159
# min_ratio == 1.67720939693

# [Cyclist]
# min_width == 12.38
# min_height == 29.98
# max_width == 25.01
# max_height == 37.51
# max_ratio == 2.42164781906
# min_ratio == 1.49980007997

# ratio = height/width

### first set this ###
GTSDB_DATASET_ROOT_DIR=/home/deng/datasets/GTSDB
NEGATIVES_PATH=/home/deng/datasets/negatives


GTSDB_TRAIN_SET_DIR=${GTSDB_DATASET_ROOT_DIR}/TrainIJCNN2013
GTSDB_MULTISCALES_TRAIN_SET_DIR=${GTSDB_DATASET_ROOT_DIR}/Train_multiscales

### do the following at the first time ###
### add negatives samples to TrainIJCNN2013/neg ###
# python scripts/generate_negative_samples.py -i $NEGATIVES_PATH -o ${GTSDB_TRAIN_SET_DIR}/neg --target_size "48,48" --sample_ratio 1.0

if [ -d $GTSDB_MULTISCALES_TRAIN_SET_DIR ]
then
    rm -r $GTSDB_MULTISCALES_TRAIN_SET_DIR
    mkdir $GTSDB_MULTISCALES_TRAIN_SET_DIR
else
    mkdir $GTSDB_MULTISCALES_TRAIN_SET_DIR
fi

python scripts/gtsdb_create_multiscales_training_dataset.py -i $GTSDB_TRAIN_SET_DIR -o ${GTSDB_MULTISCALES_TRAIN_SET_DIR}/Prohibitive -c 'Prohibitive'
python scripts/gtsdb_create_multiscales_training_dataset.py -i $GTSDB_TRAIN_SET_DIR -o ${GTSDB_MULTISCALES_TRAIN_SET_DIR}/Mandatory -c 'Mandatory'
python scripts/gtsdb_create_multiscales_training_dataset.py -i $GTSDB_TRAIN_SET_DIR -o ${GTSDB_MULTISCALES_TRAIN_SET_DIR}/Danger -c 'Danger'

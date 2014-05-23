DOPPIA_ROOT_DIR="../../doppia"

python ${DOPPIA_ROOT_DIR}/tools/objects_detection/create_multiscales_model.py \
-i train_confs_and_models/2014_05_22_78514_Danger_trained_model_octave_-2.proto.bin \
-i train_confs_and_models/2014_05_22_78739_Danger_trained_model_octave_-1.proto.bin \
-i train_confs_and_models/2014_05_22_79407_Danger_trained_model_octave_0.proto.bin \
-i train_confs_and_models/2014_05_22_83254_Danger_trained_model_octave_1.proto.bin \
-o Danger_trained_model_multiscales.proto.bin

python ${DOPPIA_ROOT_DIR}/tools/objects_detection/create_multiscales_model.py \
-i train_confs_and_models/2014_05_22_68903_Mandatory_trained_model_octave_-2.proto.bin \
-i train_confs_and_models/2014_05_22_69233_Mandatory_trained_model_octave_-1.proto.bin \
-i train_confs_and_models/2014_05_22_70002_Mandatory_trained_model_octave_0.proto.bin \
-i train_confs_and_models/2014_05_22_74158_Mandatory_trained_model_octave_1.proto.bin \
-o Mandatory_trained_model_multiscales.proto.bin

python ${DOPPIA_ROOT_DIR}/tools/objects_detection/create_multiscales_model.py \
-i train_confs_and_models/2014_05_22_59492_Prohibitive_trained_model_octave_-2.proto.bin \
-i train_confs_and_models/2014_05_22_59685_Prohibitive_trained_model_octave_-1.proto.bin \
-i train_confs_and_models/2014_05_22_60342_Prohibitive_trained_model_octave_0.proto.bin \
-i train_confs_and_models/2014_05_22_64363_Prohibitive_trained_model_octave_1.proto.bin \
-o Prohibitive_trained_model_multiscales.proto.bin

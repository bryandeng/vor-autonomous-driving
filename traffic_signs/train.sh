cd train_confs_and_models
DOPPIA_ROOT_DIR="../../../doppia"

# prohibitive
${DOPPIA_ROOT_DIR}/src/applications/boosted_learning/boosted_learning -c prohibitive/prohibitive_octave_-2.ini
${DOPPIA_ROOT_DIR}/src/applications/boosted_learning/boosted_learning -c prohibitive/prohibitive_octave_-1.ini
${DOPPIA_ROOT_DIR}/src/applications/boosted_learning/boosted_learning -c prohibitive/prohibitive_octave_0.ini
${DOPPIA_ROOT_DIR}/src/applications/boosted_learning/boosted_learning -c prohibitive/prohibitive_octave_1.ini

# mandatory
${DOPPIA_ROOT_DIR}/src/applications/boosted_learning/boosted_learning -c mandatory/mandatory_octave_-2.ini
${DOPPIA_ROOT_DIR}/src/applications/boosted_learning/boosted_learning -c mandatory/mandatory_octave_-1.ini
${DOPPIA_ROOT_DIR}/src/applications/boosted_learning/boosted_learning -c mandatory/mandatory_octave_0.ini
${DOPPIA_ROOT_DIR}/src/applications/boosted_learning/boosted_learning -c mandatory/mandatory_octave_1.ini

# danger
${DOPPIA_ROOT_DIR}/src/applications/boosted_learning/boosted_learning -c danger/danger_octave_-2.ini
${DOPPIA_ROOT_DIR}/src/applications/boosted_learning/boosted_learning -c danger/danger_octave_-1.ini
${DOPPIA_ROOT_DIR}/src/applications/boosted_learning/boosted_learning -c danger/danger_octave_0.ini
${DOPPIA_ROOT_DIR}/src/applications/boosted_learning/boosted_learning -c danger/danger_octave_1.ini

import numpy as np
import pandas as pd
import os
import json

def charge_raw_data(datum: np.ndarray, input_window_size: int, target_window_size: int, hop_size: int):
    """
    convert audio signals of each subject into 3D matrices to be fed
    later to an LSTM model
    """

    # calculate the total window size thorugh input and target winodw sizes
    window_size = input_window_size + target_window_size

    # get number of rows of 16000hz signals 
    n_rows = datum.shape[0]
    x_signals = datum
    print(n_rows)


    # initialize segments to empty list as this will store our
    # segmented signals 
    # subject_names = []
    input_segments = []
    target_segments = []
    
    # this segments our signals into overlapping segments
    for i in range(0, (n_rows - window_size) + hop_size, hop_size):
        # # last segment would have start x: 464000 - end x: 512000
        # # and because 512000 plus our hop size of 16000 = 528000 
        # # already exceeding 521216 this then terminates the loop
        # i += hop_size
        # start = i
        # end = i + window_size
        start = i
        end = min((i + window_size), n_rows)
        # print(f'start x: {start} - end x: {end}')

        # extract segment from calculated start and end
        # indeces, which will be a (window_size, n_f matrix)
        segment = x_signals[start:end, :]
        
        if segment.shape[0] < window_size:
            print(f'last segment shape {segment.shape}')

            # we grab the last day close, high, open, low prices, and volume, and
            # volume weighted values
            last_sample = segment[-1, :]
            n_repeats = window_size - segment.shape[0]
            print(f"n padding to be added: {n_repeats}") 

            # we create the features for the missing days by replicating
            # the feature values of the last day in the segment
            # resulting in a (window_size - segment.shape[0], n_features)
            # matrix
            last_samples = np.repeat([last_sample], repeats=n_repeats)            
            

            # we use the newly created copy of the last day to fill in
            # the empty spots
            segment = np.concat((segment, last_samples), axis=0)

        # split the segment into the input and target segments
        input_segment = segment[:input_window_size, :]
        target_segment = segment[input_window_size:, :]
        # print(input_segment.shape)
        # print(target_segment.shape)

        # append input_segment and target_segment into their
        # respective input and target segments lists
        input_segments.append(input_segment)
        target_segments.append(target_segment)


    # because x_window_list and y_window_list when converted to a numpy array will
    # be of dimensions (m, 6) and (m, 4) respectively we need to first and foremost
    # reshpae x_window_list into a 3D matrix such that it is able to be taken in
    # by an LSTM layer, m being the number of examples, 640 being the number of time steps
    # and 1 being the number of features which will be just our raw audio signals.    
    inputs = np.array(input_segments)
    print(inputs.shape)

    targets = np.array(target_segments)
    print(targets.shape)

    return inputs, targets
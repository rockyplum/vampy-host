#!/usr/bin/env python

#   Python Vamp Host
#   Copyright (c) 2008-2015 Queen Mary, University of London
#
#   Permission is hereby granted, free of charge, to any person
#   obtaining a copy of this software and associated documentation
#   files (the "Software"), to deal in the Software without
#   restriction, including without limitation the rights to use, copy,
#   modify, merge, publish, distribute, sublicense, and/or sell copies
#   of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be
#   included in all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
#   CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
#   CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#   WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#   Except as contained in this notice, the names of the Centre for
#   Digital Music and Queen Mary, University of London shall not be
#   used in advertising or otherwise to promote the sale, use or other
#   dealings in this Software without prior written authorization.

'''A high-level interface to the vampyhost extension module, for quickly and easily running Vamp audio analysis plugins on audio files and buffers.'''

import vampyhost
import vamp.load
import vamp.process
import vamp.frames

import numpy as np

def get_feature_step_time(sample_rate, step_size, output_desc):
    if output_desc["sampleType"] == vampyhost.ONE_SAMPLE_PER_STEP:
        return vampyhost.frame_to_realtime(step_size, sample_rate)
    elif output_desc["sampleType"] == vampyhost.FIXED_SAMPLE_RATE:
        return vampyhost.RealTime('seconds', 1.0 / output_desc["sampleRate"])
    else:
        return 1

def timestamp_features(sample_rate, step_size, output_desc, features):
    n = -1
    if output_desc["sampleType"] == vampyhost.ONE_SAMPLE_PER_STEP:
        for f in features:
            n = n + 1
            t = vampyhost.frame_to_realtime(n * step_size, sample_rate)
            f["timestamp"] = t
            yield f
    elif output_desc["sampleType"] == vampyhost.FIXED_SAMPLE_RATE:
        output_rate = output_desc["sampleRate"]
        for f in features:
            if "has_timestamp" in f:
                n = int(f["timestamp"].to_float() * output_rate + 0.5)
            else:
                n = n + 1
            f["timestamp"] = vampyhost.RealTime('seconds', float(n) / output_rate)
            yield f
    else:
        for f in features:
            yield f

def fill_timestamps(results, sample_rate, step_size, output_desc):

    output = output_desc["identifier"]
    
    selected = [ r[output] for r in results ]

    stamped = timestamp_features(sample_rate, step_size, output_desc, selected)

    for s in stamped:
        yield s

def deduce_shape(output_desc):
    if output_desc["hasDuration"]:
        return "list"
    if output_desc["sampleType"] == vampyhost.VARIABLE_SAMPLE_RATE:
        return "list"
    if not output_desc["hasFixedBinCount"]:
        return "list"
    if output_desc["binCount"] == 0:
        return "list"
    if output_desc["binCount"] == 1:
        return "vector"
    return "matrix"


def reshape(results, sample_rate, step_size, output_desc, shape):

    output = output_desc["identifier"]
    out_step = get_feature_step_time(sample_rate, step_size, output_desc)

    if shape == "vector":
        rv = ( out_step,
               np.array([r[output]["values"][0] for r in results], np.float32) )
    elif shape == "matrix":
        #!!! todo: check that each feature has the right number of bins?
        outseq = [r[output]["values"] for r in results]
        rv = ( out_step, np.array(outseq, np.float32) )
    else:
        rv = list(fill_timestamps(results, sample_rate, step_size, output_desc))

    return rv

        
def collect(data, sample_rate, key, output = "", parameters = {}):
    """Process audio data with a Vamp plugin, and make the results from a
    single plugin output available as a single structure.

    The provided data should be a 1- or 2-dimensional list or NumPy
    array of floats. If it is 2-dimensional, the first dimension is
    taken to be the channel count.

    The returned results will be those calculated by the plugin with
    the given key and returned through its output with the given
    output identifier. If the requested output is the empty string,
    the first output provided by the plugin will be used.

    If the parameters dict is non-empty, the plugin will be configured
    by setting its parameters according to the (string) key and
    (float) value data found in the dict.

    The results are returned in a dictionary which will always contain
    exactly one element, whose key is one of the strings "vector",
    "matrix", or "list". Which one is used depends on the structure of
    features set out in the output descriptor for the requested plugin
    output:

    * If the plugin output emits single-valued features at a fixed
      sample-rate, then the "vector" element will be used. It will
      contain a tuple of step time (the time in seconds between
      consecutive feature values) and a one-dimensional NumPy array of
      feature values. An example of such a feature might be a loudness
      curve against time.

    * If the plugin output emits multiple-valued features, with an
      equal number of bins per feature, at a fixed sample-rate, then
      the "matrix" element will be used. It will contain a tuple of
      step time (the time in seconds between consecutive feature
      values) and a two-dimensional NumPy array of feature values. An
      example of such a feature might be a spectrogram.

    * Otherwise, the "list" element will be used, and will contain a
      list of features, where each feature is represented as a
      dictionary containing a timestamp (always) and a duration
      (optionally), a label (string), and a 1-dimensional array of
      float values.

    If you would prefer to obtain features as they are calculated
    (where the plugin supports this) and with the format in which the
    plugin returns them, via an asynchronous generator function, use
    vamp.process() instead.

    """

    plugin, step_size, block_size = vamp.load.load_and_configure(data, sample_rate, key, parameters)

    if output == "":
        output_desc = plugin.get_output(0)
        output = output_desc["identifier"]
    else:
        output_desc = plugin.get_output(output)

    ff = vamp.frames.frames_from_array(data, step_size, block_size)

    results = vamp.process.process_with_initialised_plugin(ff, sample_rate, step_size, plugin, [output])

    shape = deduce_shape(output_desc)
    rv = reshape(results, sample_rate, step_size, output_desc, shape)

    plugin.unload()
    return { shape : rv }

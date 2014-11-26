
import vampyhost as vh
import numpy as np

testPluginKey = "vamp-test-plugin:vamp-test-plugin"

rate = 44100

def test_load_unload():
    plug = vh.loadPlugin(testPluginKey, rate)
    plug.unload()
    try:
        plug.unload() # should throw but not crash
        assert(False)
    except AttributeError:
        pass

def test_get_set_parameter():
    plug = vh.loadPlugin(testPluginKey, rate)
    value = plug.getParameterValue("produce_output")
    assert(value == 1.0)
    plug.setParameterValue("produce_output", 0.0)
    value = plug.getParameterValue("produce_output")
    assert(value == 0.0)
    
def test_process_without_initialise():
    plug = vh.loadPlugin(testPluginKey, rate)
    try:
        plug.process([[1,2,3,4]], vh.RealTime(0, 0))
        assert False
    except StandardError:
        pass

def test_process_input_format():
    plug = vh.loadPlugin(testPluginKey, rate)
    plug.initialise(2, 4, 4) # channels, stepsize, blocksize
    result = plug.process([[1,2,3,4],[5,6,7,8]], vh.RealTime(0, 0))
    result = plug.process([np.array([1,2,3,4]),np.array([5,6,7,8])], vh.RealTime(0, 0))
    result = plug.process(np.array([[1,2,3,4],[5,6,7,8]]), vh.RealTime(0, 0))
    try:
        # Wrong number of channels
        result = plug.process(np.array([[1,2,3,4]]), vh.RealTime(0, 0))
        assert False
    except TypeError:
        pass
    try:
        # Wrong number of samples per channel
        result = plug.process(np.array([[1,2,3],[4,5,6]]), vh.RealTime(0, 0))
        assert False
    except TypeError:
        pass
    try:
        # Differing numbers of samples per channel
        result = plug.process(np.array([[1,2,3,4],[5,6,7]]), vh.RealTime(0, 0))
        assert False
    except TypeError:
        pass



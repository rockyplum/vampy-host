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

'''Load and use Vamp plugins for audio feature analysis. This module
is a high-level interface wrapper around a native-code extension, for
quickly and easily running Vamp analysis plugins on buffers of audio
data. For low-level plugin loading and manipulation, refer to the
vamp.vampyhost namespace which contains the native-code extension.
'''

import vampyhost

from vamp.load import list_plugins, get_outputs_of, get_category_of
from vamp.process import process_audio, process_frames, process_audio_multiple_outputs, process_frames_multiple_outputs
from vamp.collect import collect


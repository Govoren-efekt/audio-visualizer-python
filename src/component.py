'''
    Base classes for components to import.
'''
from PyQt5 import uic, QtCore, QtWidgets
import os


class Component(QtCore.QObject):
    '''
        A class for components to inherit. Read comments for documentation
        on making a valid component. All subclasses must implement this signal:
            modified = QtCore.pyqtSignal(int, bool)
    '''

    def __init__(self, moduleIndex, compPos, core):
        super().__init__()
        self.currentPreset = None
        self.canceled = False
        self.moduleIndex = moduleIndex
        self.compPos = compPos
        self.core = core

    def __str__(self):
        return self.__doc__

    def version(self):
        '''
            Change this number to identify new versions of a component
        '''
        return 1

    def properties(self):
        '''
            Return a list of properties to signify if your component is
            non-animated ('static'), returns sound ('audio'), or has
            encountered an error in configuration ('error').
        '''
        return []

    def error(self):
        '''
            Return a string containing an error message, or None for a default.
        '''
        return

    def cancel(self):
        '''
            Stop any lengthy process in response to this variable
        '''
        self.canceled = True

    def reset(self):
        self.canceled = False

    def update(self):
        '''
            Read your widget values from self.page, then call super().update()
        '''
        self.parent.drawPreview()
        saveValueStore = self.savePreset()
        saveValueStore['preset'] = self.currentPreset
        self.modified.emit(self.compPos, saveValueStore)

    def loadPreset(self, presetDict, presetName):
        '''
            Subclasses take (presetDict, presetName=None) as args.
            Must use super().loadPreset(presetDict, presetName) first,
            then update self.page widgets using the preset dict.
        '''
        self.currentPreset = presetName \
            if presetName is not None else presetDict['preset']

    def preFrameRender(self, **kwargs):
        '''
            Triggered only before a video is exported (video_thread.py)
                self.worker = the video thread worker
                self.completeAudioArray = a list of audio samples
                self.sampleSize = number of audio samples per video frame
                self.progressBarUpdate = signal to set progress bar number
                self.progressBarSetText = signal to set progress bar text
            Use the latter two signals to update the MainWindow if needed
            for a long initialization procedure (i.e., for a visualizer)
        '''
        for key, value in kwargs.items():
            setattr(self, key, value)

    def command(self, arg):
        '''
            Configure a component using argument from the commandline.
            Use super().command(arg) at the end of a subclass's method,
            if no arguments are found in that method first
        '''
        if arg.startswith('preset='):
            _, preset = arg.split('=', 1)
            path = os.path.join(self.core.getPresetDir(self), preset)
            if not os.path.exists(path):
                print('Couldn\'t locate preset "%s"' % preset)
                quit(1)
            else:
                print('Opening "%s" preset on layer %s' % (
                    preset, self.compPos)
                )
                self.core.openPreset(path, self.compPos, preset)
        else:
            print(
                self.__doc__, 'Usage:\n'
                'Open a preset for this component:\n'
                '    "preset=Preset Name"')
            self.commandHelp()
            quit(0)

    def commandHelp(self):
        '''Print help text for this Component's commandline arguments'''

    def loadUi(self, filename):
        return uic.loadUi(os.path.join(self.core.componentsPath, filename))

    '''
    ### Reference methods for creating a new component
    ### (Inherit from this class and define these)

    def widget(self, parent):
        self.parent = parent
        page = self.loadUi('example.ui')
        # --- connect widget signals here ---
        self.page = page
        return page

    def previewRender(self, previewWorker):
        width = int(previewWorker.core.settings.value('outputWidth'))
        height = int(previewWorker.core.settings.value('outputHeight'))
        from frame import BlankFrame
        image = BlankFrame(width, height)
        return image

    def frameRender(self, layerNo, frameNo):
        audioArrayIndex = frameNo * self.sampleSize
        width = int(self.worker.core.settings.value('outputWidth'))
        height = int(self.worker.core.settings.value('outputHeight'))
        from frame import BlankFrame
        image = BlankFrame(width, height)
        return image

    def audio(self):
        \'''
            Return audio to mix into master as a tuple with two elements:
            The first element can be:
                - A string (path to audio file),
                - Or an object that returns audio data through a pipe
            The second element must be a dictionary of ffmpeg filters/options
            to apply to the input stream. See the filter docs for ideas:
            https://ffmpeg.org/ffmpeg-filters.html
        \'''

    @classmethod
    def names(cls):
        \'''
            Alternative names for renaming a component between project files.
        \'''
        return []
    '''


class BadComponentInit(Exception):
    def __init__(self, arg, name):
        string = '''################################
Mandatory argument "%s" not specified
  in %s instance initialization
###################################'''
        print(string % (arg, name))
        quit()

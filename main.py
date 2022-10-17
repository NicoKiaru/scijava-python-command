import imagej

from scyjava import jimport
from jpype import JImplements, JOverride
from jpype.types import JString, JBoolean, JDouble, JInt

from scijava_python_command import ScijavaCommand, ScijavaInput, ScijavaOutput


if __name__ == '__main__':
    print('main executed')



    # Let's create a command from Python, because this is convenient for testing

    print('ok')

    pass


# Example of registering a Scijava Command via the @ScijavaCommand decorator
print('hum')

ij = imagej.init(['net.imagej:imagej:2.9.0', 'ch.epfl.biop:pyimagej-scijava-command:0.1.4'])
@ScijavaCommand(context=ij.context(),  # ij context needed
                name='pyCommand.HelloCommand')
class HelloCommand:

    @ScijavaInput(label='Name :', description='Please enter your name')
    def name(self, value: JString):
        pass

    @ScijavaInput
    def familiar(self, value: JBoolean):
        pass

    def run(self):
        if (self._familiar):
            self._greetings = 'Hi ' + str(self._name) + '!'
        else:
            self._greetings = 'Hello my dear ' + str(self._name) + '.'
        print(self._greetings)

    @ScijavaOutput
    def greetings(self) -> JString:
        pass

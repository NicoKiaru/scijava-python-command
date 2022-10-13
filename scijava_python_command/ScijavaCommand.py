from scyjava import jimport
from jpype.types import JObject, JClass

PyCommandBuilder = jimport('org.scijava.command.PyCommandBuilder')

# Decorator that registers a python CLASS containing a method named "run" as a Scijava Command
#
# This uses PyCommandBuilder which is in the java repo ch.epfl.biop:pyimagej-scijava-command
# PyCommandBuilder allows to build a Command fully programmatically without using any
# java annotation as java annotations are needed for 'easy' Scijava Commands definition
# but these are not completely supported in JPype:
# cf https://github.com/jpype-project/jpype/issues/940
#
# Example of registering a Scijava Command via the @ScijavaCommand decorator:
# ------------------------------------------
# @ScijavaCommand(context = ij.context(), # ij context needed
#                 name = 'pyCommand.HelloCommand', # name of this command, mind potential naming conflicts!
#                 inputs = {'name': JString, 'familiar': JBoolean}, # input name, input Java class, as dictionary
#                 outputs = {'greetings': JString}) # output name, output Java class, as dictionary
# class MyPyCommand:
#     def run(self):
#         if (self.familiar):
#             self.greetings = 'Hi ' + str(self.name) + '!'
#         else:
#             self.greetings = 'Hello my dear ' + str(self.name) + '.'
#         print(self.greetings)
# ------------------------------------------
#
# Note: this way of defining a command is probably not ideal if this has to be used from the python side also
#
# Because it's a preliminary work, this decorator prints a lot of stuff in the process
#
# TODO: functools ??

def ScijavaCommand(**kwargs):
    print("- Registering scijava command " + kwargs['name'])

    def registerCommand(func):
        # This class will be registered as a SciJava Command
        builder = PyCommandBuilder()  # Java PyCommandBuilder

        # The name of the command - to avoid name conflicts, consider a 'virtual' class name with its package
        builder = builder.name(kwargs['name'])

        # Register all inputs
        print('- Inputs')
        for name, javaClass in kwargs['inputs'].items():
            print('\t', name, ' : ', javaClass)
            builder = builder.input(name, javaClass)
            setattr(func, name, None)  # declares empty input field
        print('Inputs registered')

        # Register all outputs
        print('- Outputs')
        for name, javaClass in kwargs['outputs'].items():
            print('\t', name, ' : ', javaClass)
            builder = builder.output(name, javaClass)
            setattr(func, name, None)  # declares empty output field
        print('Outputs registered')

        # Wraps the run function - takes kwargs as input, returns outputs
        def wrapped_run(inner_kwargs):
            inner_object = func()
            # Settings inputs...
            # print(inner_kwargs)
            for name, javaClass in kwargs['inputs'].items():
                # print(name)
                # print(str(inner_kwargs[name]))
                setattr(inner_object, name, inner_kwargs[name])  # sets inputs
            # Inputs set.
            # print('Running scijava command: ' + kwargs['name'])
            inner_object.run()
            # print(kwargs['name'] + ' command execution done.')
            # print('Fetching outputs...')
            outputs = {}
            for name, javaClass in kwargs['outputs'].items():
                outputs[name] = getattr(inner_object, name)  # gets outputs
            # print('Outputs set.')
            return JObject(outputs, JClass('java.util.Map'))  # Returns output as a java HashMap

        # Sets the function in PyCommandBuilder:
        # Function<Map<String, Object>, Map<String, Object>> command
        builder = builder.function(wrapped_run)

        # Effectively registers this command to the ij context
        builder.create(kwargs['context'])
        return func

    return registerCommand

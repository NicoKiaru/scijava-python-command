import threading
import ipywidgets as widgets
from IPython.display import display
from scyjava import jimport
from jpype import JImplements, JOverride
from jpype.types import JString, JBoolean, JDouble, JInt

PyPreprocessor = jimport('org.scijava.processor.PyPreprocessor')
Consumer = jimport('java.util.function.Consumer')
Supplier = jimport('java.util.function.Supplier')


def enable_jupyter_ui():
    PyPreprocessor.register(IPyWidgetCommandPreprocessorSupplier())
    print('Scijava jupyter ui enabled')


@JImplements(Consumer)
class IPyWidgetCommandPreprocessor(object):

    @JOverride
    def accept(self, module):
        inputs = module.getInputs()
        all_widgets = dict()
        for input_key in inputs.keySet():
            if not module.isInputResolved(input_key):
                current_widget = get_jupyter_widget(module, input_key)
                if current_widget is not None:
                    all_widgets[input_key] = current_widget
                else:
                    # maybe log something or put a warning
                    pass

        if len(all_widgets) != 0:
            list_of_widgets = [x.get_widget() for key, x in all_widgets.items()]

            # Creates an OK button, and its associated event
            user_has_clicked = threading.Event()
            ok_button = widgets.Button(description='OK')
            ok_button.on_click(lambda _: user_has_clicked.set())
            list_of_widgets.append(ok_button)
            display(widgets.VBox(list_of_widgets))

            # Wait for button click
            user_has_clicked.wait()

            # the user has clicked
            # retrieve contents of all widgets:
            for key, w in all_widgets.items():
                module.setInput(key, w.get_value())
                module.resolveInput(key)

@JImplements(Supplier)
class IPyWidgetCommandPreprocessorSupplier(object):
    @JOverride
    def get(self):
        return IPyWidgetCommandPreprocessor()


booleanClasses = ['class java.lang.Boolean', 'boolean']
intClasses = ['class java.lang.Integer', 'int']
floatClasses = ['class java.lang.Double', 'class java.lang.Float', 'double', 'float']


def get_jupyter_widget(module, input_key):
    if str(module.getInfo().getInput(input_key).getType()) == 'class java.lang.String':
        return JupyterTextWidget(module, input_key)

    if str(module.getInfo().getInput(input_key).getType()) in booleanClasses:
        return JupyterToggleWidget(module, input_key)

    if str(module.getInfo().getInput(input_key).getType()) in intClasses:
        return JupyterIntWidget(module, input_key)

    if str(module.getInfo().getInput(input_key).getType()) in floatClasses:
        return JupyterFloatWidget(module, input_key)

    print(str(module.getInfo().getInput(input_key).getType()) + " unsupported widget")

    return None


class JupyterInputWidget:
    def __init__(self, module, input_key):
        pass

    def get_widget(self):
        return self.widget

    def get_value(self):
        return None


class JupyterTextWidget(JupyterInputWidget):
    def __init__(self, module, input_key):
        self.widget = widgets.Text(
            value=str(module.getInput(input_key)),
            placeholder='Type something',
            description=str(input_key),
            disabled=False
        )

    def get_value(self):
        return JString(self.widget.value)


class JupyterToggleWidget(JupyterInputWidget):
    def __init__(self, module, input_key):
        self.widget = widgets.Checkbox(
            value=bool(module.getInput(input_key)),
            description=str(input_key),
            disabled=False,
            indent=False
        )

    def get_value(self):
        return JBoolean(self.widget.value)


class JupyterIntWidget(JupyterInputWidget):
    def __init__(self, module, input_key):

        min_value = module.getInfo().getInput(input_key).getMinimumValue()
        max_value = module.getInfo().getInput(input_key).getMaximumValue()
        step_size = module.getInfo().getInput(input_key).getStepSize()

        if (min_value is not None) and (max_value is not None):
            if step_size is None:
                step_size = 1
            else:
                step_size = step_size.intValue()

            self.widget = widgets.IntText(
                value=int(module.getInput(input_key)),
                min=int(min_value),
                max=int(max_value),
                step=int(step_size),
                description=str(input_key),
                disabled=False
            )
        else:
            self.widget = widgets.BoundedIntText(
                value=int(module.getInput(input_key)),
                description=str(input_key),
                disabled=False
            )

    def get_value(self):
        return JInt(self.widget.value)


class JupyterFloatWidget(JupyterInputWidget):
    def __init__(self, module, input_key):

        min_value = module.getInfo().getInput(input_key).getMinimumValue()
        max_value = module.getInfo().getInput(input_key).getMaximumValue()
        step_size = module.getInfo().getInput(input_key).getStepSize()

        if (min_value is not None) and (max_value is not None):
            if step_size is None:
                step_size = 1
            else:
                step_size = step_size.intValue()

            self.widget = widgets.FloatText(
                value=float(module.getInput(input_key)),
                min=float(min_value),
                max=float(max_value),
                step=float(step_size),
                description=str(input_key),
                disabled=False
            )
        else:
            self.widget = widgets.BoundedFloatText(
                value=float(module.getInput(input_key)),
                description=str(input_key),
                disabled=False
            )

    def get_value(self):
        return JDouble(self.widget.value)  # TODO : fix casting


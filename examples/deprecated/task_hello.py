#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from qmt.tasks import Task, SweepManager

sweep = SweepManager.create_empty_sweep()  # our dask sweep manager


class HelloTask(Task):
    def __init__(self):
        super().__init__()  # required init

    @staticmethod
    def _solve_instance(inputs, options):  # required task solver function
        print("Hello World")


hi = HelloTask()  # create a new task
sweep.run(hi).result()  # run through dask and resolve future.result()
hi.run_daskless()  # can also run locally


class HelloOptionTask(Task):
    def __init__(self, language_options):
        super().__init__(options=language_options)

    @staticmethod
    def _solve_instance(inputs, options):
        greetings = {"English": "Hello", "Spanish": "Hola"}
        print(greetings[options["language"]] + " World")


hola = HelloOptionTask({"language": "Spanish"})
sweep.run(hola).result()


class NameTask(Task):
    def __init__(self, name_options):
        super().__init__(options=name_options)

    @staticmethod
    def _solve_instance(inputs, options):
        return options["name"]


class HelloDependentTask(Task):
    def __init__(self, name_task, language_options):
        super().__init__(task_list=[name_task], options=language_options)

    @staticmethod
    def _solve_instance(inputs, options):
        name = inputs[0]
        greetings = {"English": "Hello", "Spanish": "Hola"}
        print(greetings[options["language"]] + " " + name)


name = NameTask({"name": "John"})
hola = HelloDependentTask(name, {"language": "Spanish"})
sweep.run(hola).result()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from qmt.tasks import Task, SweepManager, SweepTag


class HelloSweepTask(Task):

    def __init__(self, language_options):
        super().__init__(options=language_options)

    @staticmethod
    def _solve_instance(inputs, options):
        greetings = {'English': 'Hello', 'Spanish': 'Hola'}
        print(greetings[options['language']] + ' World')


print('Run a sweep over the languages:')
lang_tag = SweepTag('language tag description')
sweep = [{lang_tag: 'English'}, {lang_tag: 'Spanish'}]
lm = SweepManager(sweep)
bilingual = HelloSweepTask({'language': lang_tag})

lm.run(bilingual).result()


class NameTask(Task):

    def __init__(self, name_options):
        super().__init__(options=name_options)

    @staticmethod
    def _solve_instance(inputs, options):
        return options['name']


class HelloDependentTask(Task):

    def __init__(self, name_task, language_options):
        super().__init__(task_list=[name_task], options=language_options)

    @staticmethod
    def _solve_instance(inputs, options):
        greetings = {'English': 'Hello', 'Spanish': 'Hola'}
        name = inputs[0]
        print(greetings[options['language']] + ' ' + name)


print('Chaining a NameTask and a sweep of HelloDependingTask:')
name = NameTask({'name': 'John'})
lm = SweepManager(sweep)
bilingual = HelloDependentTask(name, {'language': lang_tag})

lm.run(bilingual).result()

print('We can build arbitrary sweeps:')
name_tag = SweepTag('name tag description')
lang_tag = SweepTag('language tag description')
name = NameTask({'name': name_tag})
greet = HelloDependentTask(name, {'language': lang_tag})
sweeps = [{name_tag: 'John', lang_tag: 'English'},
          {name_tag: 'Jose', lang_tag: 'Spanish'}]
tm = SweepManager(sweeps)

tm.run(greet).result()

print('Or cartesian products:')
# need new NameTask, 'greet' consumed the previous
name = NameTask({'name': name_tag})
greet = HelloDependentTask(name, {'language': lang_tag})
values = {name_tag: ['John', 'Jose'], lang_tag: ['English', 'Spanish']}
cartesian = SweepManager.construct_cartesian_product(values)

cartesian.run(greet).result()

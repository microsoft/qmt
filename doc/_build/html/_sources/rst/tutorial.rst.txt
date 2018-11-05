Tutorial
========

Geometry Sweep
--------------

This example showcases geometry building. It is directly executable as `examples/geometry_sweep.py`.

The FreeCAD template document required by this example is located at
`examples/geometry_sweep_showcase.fcstd`.
It contains sketches with FreeCAD-internal names, which are visible when selecting an object
(not to be confused with the human-readable labels in the model tree view).

.. literalinclude:: ../../examples/geometry_sweep.py
    :language: python
    :start-after: """Example geometry sweeping."""
    :end-before: # Set up geometry task

First we use the internal names to generate :py:mod:`qmt.data.geometry.Part3DData` objects.

.. literalinclude:: ../../examples/geometry_sweep.py
    :language: python
    :start-after: # Set up geometry task
    :end-before: # Parameters

Then we package these 3D parts into a build order list and feed them, along with other parameters
to a :py:mod:`qmt.tasks.geometry.build_3d_geometry` task.
The :code:`py2env` path must correspond to a callable Python 2 interpreter.

.. literalinclude:: ../../examples/geometry_sweep.py
    :language: python
    :start-after: # Parameters
    :end-before: # Create a local temporary

The result should contain three instances of the built geometry. They differ in the length of
the 'Parametrised Block', which was set up to correspond to the parameter :code:`d1` in the template document.

Finally we write these documents to a temporary directory for visual inspection, along with STEP exports of all objects.

.. literalinclude:: ../../examples/geometry_sweep.py
    :language: python
    :start-after: # Create a local temporary


Hello World Task
----------------

| This example shows how to greet the world with self written QMT tasks.
| The fundamentals for :code:`Task` objects are explained in :py:mod:`qmt.tasks.task`.
| For a directly executable example of the following snippets, check out `examples/task_hello.py`.

.. literalinclude:: ../../examples/task_hello.py
    :language: python
    :start-after: # -*- coding: utf-8 -*-
    :end-before: class HelloTask(Task):

| The above is common setup code. Below we define our task class.

.. literalinclude:: ../../examples/task_hello.py
    :language: python
    :start-after: sweep = SweepManager.create_empty_sweep()
    :end-before: class HelloOptionTask(Task):

| We can use dicts to pass options.

.. literalinclude:: ../../examples/task_hello.py
    :language: python
    :start-after: hi.run_daskless()
    :end-before: class NameTask(Task):

| And tasks can depend on each other.

.. literalinclude:: ../../examples/task_hello.py
    :language: python
    :start-after: sweep.run(hola).result()

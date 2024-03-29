{{ badge.pypi }}

{{ badge.github_workflow() }}

{{ badge.readthedocs }}

==============================
mscxyz - The MuseScore Manager
==============================

Manipulate the XML based ``.mscz`` and ``.mscx`` files of the notation software
`MuseScore <https://musescore.org>`_.

Features
========

* Batch processing of ``.msc[zx]`` files in nested folder structures
* Rename ``.msc[zx]`` files based on meta tags
* Set, read and synchronized meta tags
* Set style properties
* Can handle MuseScore 2, 3 and 4 files
* Command line interface
* Python API

Installation
============

.. code:: Shell

    pipx install mscxyz


How to ...
==========

... specify the MuseScore files to work on?
-------------------------------------------

To find out which files are selected by the script, the ``-L, --list-files``
option can be used. The ``--list-files`` option lists as the name suggests
only the file paths and doesn’t touch the specified *MuseScore* files:

::

    musescore-manager --list-files

Without an option the script lists all MuseScore files in the current directory
in a recursive way (``musescore-manager`` = ``musescore-manager .``).
You can pass multiple file paths to the script:

::

    musescore-manager -L score1.mscz score2.mscz score3.mscz

or multiple directories:

::

    musescore-manager -L folder1 folder2 folder3

or use the path expansion of your shell:

::

    musescore-manager -L *.mscz


To apply glob patterns on the file paths, the ``--glob`` option can be used.

::

    musescore-manager -L --glob "*/folder/*.mscz"

To selection only *mscz* oder *mscx* files use the options ``--mscz`` or ``--mscx``.
Don’t mix the options ``--mscz`` and ``--mscx`` with the option ``--glob``.

The python package ``mscxyz`` exports a function named ``list_path`` which can
be used to list the paths of MuseScore files. This allows you to list score
paths in a nested folder structure in a similar way to the command line.
This folder structure is used for the following example:

::

    cd /home/xyz/scores
    find . | sort

    .
    ./level1
    ./level1/level2
    ./level1/level2/score2.mscz
    ./level1/level2/level3
    ./level1/level2/level3/score3.mscz
    ./level1/score1.mscz
    ./score0.mscz

.. code-block:: Python

    from mscxyz import list_path, Score

    score_paths = []
    for score_path in list_path(path="/home/xyz/scores", extension="mscz"):
        score = Score(score_path)
        assert score.path.exists()
        assert score.extension == "mscz"
        score_paths.append(str(score_path))

    assert len(score_paths) == 4

    assert "level1/level2/level3/score3.mscz" in score_paths[3]
    assert "level1/level2/score2.mscz" in score_paths[2]
    assert "level1/score1.mscz" in score_paths[1]
    assert "score0.mscz" in score_paths[0]

... export files to different files types?
------------------------------------------

On the command line use the option ``--export`` to export the scores to
different file types. The exported file has the same path, only the file
extension is different. Further information about the supported file formats
can be found at the MuseScore website:
`Version 2 <https://musescore.org/en/handbook/2/file-formats>`_,
`Version 3 <https://musescore.org/en/handbook/3/file-export>`_ and
`Version 4 <https://musescore.org/en/handbook/4/file-export>`_
The MuseScore binay must be installed and the script must know the location of t
his binary.

::

    musescore-manager --export pdf
    musescore-manager --export png

.. code-block:: Python

    score = Score('score.mscz')
    score.export.to_extension("musicxml")


... change the styling of a score?
----------------------------------

Set a single style by its style name ``--style``:

::

    musescore-manager --style staffDistance 7.5 score.mscz


To set mulitple styles at once specify the option ``--style`` multiple times:

::

    musescore-manager --style staffUpperBorder 5.5 --style staffLowerBorder 5.5 score.mscz

... change the font faces of a score?
-------------------------------------

Some options change mutliple font related xml elements at once:

::

    musescore-manager --text-font Alegreya score.mscz
    musescore-manager --title-font "Alegreya Sans" score.mscz
    musescore-manager --musical-symbol-font Leland score.mscz
    musescore-manager --musical-text-font "Leland Text" score.mscz


Set all font faces (using a for loop, not available in MuseScore 2):

.. code-block:: Python

    score = Score('score.mscz')
    assert score.style.get("defaultFontFace") == "FreeSerif"

    for element in score.style.styles:
        if "FontFace" in element.tag:
            element.text = "Alegreya"
    score.save()

    new_score: Score = score.reload()
    assert new_score.style.get("defaultFontFace") == "Alegreya"

Set all text font faces (using the method ``score.style.set_text_font_faces(font_face)``,
not available in MuseScore 2):

.. code-block:: Python

    score = Score('score.mscz')
    assert score.style.get("defaultFontFace") == "FreeSerif"

    response = score.style.set_text_font_faces("Alegreya")

    assert response == [
        ...
        ("harpPedalTextDiagramFontFace", "Edwin", "Alegreya"),
        ("longInstrumentFontFace", "FreeSerif", "Alegreya"),
        ...
    ]

    score.save()

    new_score: Score = score.reload()
    assert new_score.style.get("defaultFontFace") == "Alegreya"


... enable autocomplete support?
--------------------------------

Use one of the following autocomplete files ...

* `bash <https://github.com/Josef-Friedrich/mscxyz/blob/main/autocomplete.bash>`_
* `zsh <https://github.com/Josef-Friedrich/mscxyz/blob/main/autocomplete.zsh>`_
* `tcsh <https://github.com/Josef-Friedrich/mscxyz/blob/main/autocomplete.tcsh>`_

... or generate the autocomplete files by yourself?
---------------------------------------------------

::

    musescore-manager --print-completion bash > autocomplete.bash
    musescore-manager --print-completion zsh > autocomplete.zsh
    musescore-manager --print-completion tcsh > autocomplete.tcsh

... rename many files at once?
------------------------------

Fields
^^^^^^

{{ cli('musescore-manager --list-fields') }}

Functions
^^^^^^^^^

{{ cli('tmep-doc --functions-rst') }}

{{ cli('tmep-doc --introduction-rst') }}

The following example assumes that the folder ``/home/xyz/messy-leadsheets``
contains the following three MuseScore files: ``folsom prison blues.mscz``,
``Johnny Cash - I Walk the Line.mscz``, ``Jackson (Cash).mscz``
The files are named arbitrarily without any recognizable pattern, but they have a
title in the first vertical frame (VBox).

{% raw %}

The files should be moved to a target directory (``--target /home/xyz/tidy-leadsheets``) and
the file names should not contain any spaces (``--no-whitespace``).
The title should be used as the file name (``--rename '$vbox_title'``).
The individual files should be stored in subdirectories named after the first
letter of the title (``--rename '%lower{%shorten{$vbox_title,1}}/...'``)

::

    musescore-manager --rename '%lower{%shorten{$vbox_title,1}}/$vbox_title' \
        --target /home/xyz/tidy-leadsheets \
        --no-whitespace \
        /home/xyz/messy-leadsheets


{% endraw %}

After executing the above command on the command line, ``find /home/xyz/tidy-leadsheets``
should show the following output:

::

    i/I-Walk-the-Line.mscz
    j/Jackson.mscz
    f/Folsom-Prison-Blues.mscz

... use the Python API?
-----------------------

Please visit the `API documentation <https://mscxyz.readthedocs.io>`_ on readthedocs.

Instantiate a ``Score`` object:

.. code-block:: Python

    from mscxyz import Score
    score = Score('score.mscz')
    assert score.path.exists()
    assert score.filename == "score.mscz"
    assert score.basename == "score"
    assert score.extension == "mscz"
    assert score.version == 4.20
    assert score.version_major == 4

Examine the most important attribute of a ``Score`` object: ``xml_root``.
It is the root element of the XML document in which MuseScore stores all information
about a score.
It’s best to take a look at the `lxml API <https://lxml.de/api.html>`_ documentation
to see what you can do with this element. So much can be revealed:
lots of interesting things.

.. code-block:: Python

    score = Score('score.mscz')

    def print_elements(element: _Element, level: int) -> None:
        for sub_element in element:
            print(f"{'    ' * level}<{sub_element.tag}>")
            print_elements(sub_element, level + 1)

    print_elements(score.xml_root, 0)

The output of the code example is very long, so here is a shortened version:

::

    <programVersion>
    <programRevision>
    <LastEID>
    <Score>
        <Division>
        <showInvisible>
        <showUnprintable>
        <showFrames>
        <showMargins>
        <open>
        <metaTag>
        ...

... edit the meta data of a score file?
---------------------------------------

metatag
^^^^^^^

XML structure of a meta tag:

.. code-block:: xml

    <metaTag name="tag"></metaTag>

All meta tags:

- ``arranger``
- ``audioComUrl`` (new in v4)
- ``composer``
- ``copyright``
- ``creationDate``
- ``lyricist``
- ``movementNumber``
- ``movementTitle``
- ``mscVersion``
- ``platform``
- ``poet`` (not in v4)
- ``source``
- ``sourceRevisionId``
- ``subtitle``
- ``translator``
- ``workNumber``
- ``workTitle``

vbox
^^^^

XML structure of a vbox tag:

.. code-block:: xml

    <VBox>
        <Text>
        <style>title</style>
        <text>Some title text</text>
        </Text>

All vbox tags:

- ``title`` (v2,3: ``Title``)
- ``subtitle`` (v2,3: ``Subtitle``)
- ``composer`` (v2,3: ``Composer``)
- ``lyricist`` (v2,3: ``Lyricist``)

This command line tool bundles some meta data informations:

Combined meta data fields:
^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``title`` (1. ``vbox_title`` 2. ``metatag_work_title``)
- ``subtitle`` (1. ``vbox_subtitle`` 2. ``metatag_subtitle`` 3. ``metatag_movement_title``)
- ``composer`` (1. ``vbox_composer`` 2. ``metatag_composer``)
- ``lyricist`` (1. ``vbox_lyricist`` 2. ``metatag_lyricist``)

Set the meta tag ``composer``:

.. code-block:: xml

    <museScore version="4.20">
        <Score>
            <metaTag name="composer">Composer</metaTag>

.. code-block:: Python

    score = Score('score.mscz')
    assert score.meta.meta_tag.composer == "Composer"

    score.meta.meta_tag.composer  = "Mozart"
    score.save()

    new_score: Score = score.reload()
    assert new_score.meta.meta_tag.composer == "Mozart"

.. code-block:: xml

    <museScore version="4.20">
        <Score>
            <metaTag name="composer">Mozart</metaTag>

CLI Usage
=========

{{ cli('musescore-manager --help') | literal }}

Configuration file
==================

``/etc/mscxyz.ini``

.. code-block:: ini

    [general]
    executable = /usr/bin/mscore3
    colorize = True

    [rename]
    format = '$title ($composer)'

Other MuseScore related projects
================================

* https://github.com/johentsch/ms3

Development
===========

Test
----

::

    make test


Publish a new version
---------------------

::

    git tag 1.1.1
    git push --tags
    make publish


Package documentation
---------------------

The package documentation is hosted on
`readthedocs <http://mscxyz.readthedocs.io>`_.

Generate the package documentation:

::

    make docs

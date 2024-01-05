{{ badge.pypi }}

{{ badge.github_workflow() }}

{{ badge.readthedocs }}

======
mscxyz
======

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

    pip install mscxyz

Usage
=====

{{ cli('mscx-manager help --rst all') }}

API Usage
=========

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

List score paths in a nested folder structure:

::

    cd /home/xyz/scores
    find . | sort

::

    .
    ./level1
    ./level1/level2
    ./level1/level2/score2.mscz
    ./level1/level2/level3
    ./level1/level2/level3/score3.mscz
    ./level1/score1.mscz
    ./score0.mscz

.. code-block:: Python

    from mscxyz import list_score_paths, Score

    score_paths = list_score_paths(path="/home/xyz/scores", extension="mscz")
    for score_path in score_paths:
        score = Score(score_path)
        assert score.path.exists()
        assert score.extension == "mscz"
        
    assert len(score_paths) == 4

    assert "level1/level2/level3/score3.mscz" in score_paths[0] 
    assert "level1/level2/score2.mscz" in score_paths[1] 
    assert "level1/score1.mscz" in score_paths[2] 
    assert "score0.mscz" in score_paths[3] 

``meta``
--------

Set the meta tag ``composer``:

.. code-block:: xml

    <museScore version="4.20">
        <Score>
            <metaTag name="composer">Composer</metaTag>

.. code-block:: Python

    score = Score('score.mscz')
    assert score.meta.interface.metatag_composer == "Composer"

    score.meta.interface.metatag_composer = "Mozart"
    score.save()

    new_score: Score = score.reload()
    assert new_score.meta.interface.metatag_composer == "Mozart"

.. code-block:: xml

    <museScore version="4.20">
        <Score>
            <metaTag name="composer">Mozart</metaTag>

``style``
---------

Set all font faces (using a for loop, not available in MuseScore 2):

.. code-block:: Python

    score = Score('score.mscz')
    assert score.style.get_value("defaultFontFace") == "FreeSerif"
    
    for element in score.style.styles:
        if "FontFace" in element.tag:
            element.text = "Alegreya"
    score.save()

    new_score: Score = score.reload()
    assert new_score.style.get_value("defaultFontFace") == "Alegreya"


.. code-block:: Python

Set all font faces (using the method ``score.style.set_all_font_faces(font_face)``, 
not available in MuseScore 2):

.. code-block:: Python

    score = Score('score.mscz')
    assert score.style.get_value("defaultFontFace") == "FreeSerif"

    response = score.style.set_all_font_faces("Alegreya")

    assert response == [
        ("lyricsOddFontFace", "FreeSerif", "Alegreya"),
        ("lyricsEvenFontFace", "FreeSerif", "Alegreya"),
        ("hairpinFontFace", "FreeSerif", "Alegreya"),
        ("pedalFontFace", "FreeSerif", "Alegreya"),
        ("chordSymbolAFontFace", "FreeSerif", "Alegreya"),
        ("chordSymbolBFontFace", "FreeSerif", "Alegreya"),
        ("romanNumeralFontFace", "Campania", "Alegreya"),
        ("nashvilleNumberFontFace", "FreeSerif", "Alegreya"),
        ("voltaFontFace", "FreeSerif", "Alegreya"),
        ("ottavaFontFace", "FreeSerif", "Alegreya"),
        ("tupletFontFace", "FreeSerif", "Alegreya"),
        ("defaultFontFace", "FreeSerif", "Alegreya"),
        ("titleFontFace", "FreeSerif", "Alegreya"),
        ("subTitleFontFace", "FreeSerif", "Alegreya"),
        ("composerFontFace", "FreeSerif", "Alegreya"),
        ("lyricistFontFace", "FreeSerif", "Alegreya"),
        ("fingeringFontFace", "FreeSerif", "Alegreya"),
        ("lhGuitarFingeringFontFace", "FreeSerif", "Alegreya"),
        ("rhGuitarFingeringFontFace", "FreeSerif", "Alegreya"),
        ("stringNumberFontFace", "FreeSerif", "Alegreya"),
        ("harpPedalDiagramFontFace", "Edwin", "Alegreya"),
        ("harpPedalTextDiagramFontFace", "Edwin", "Alegreya"),
        ("longInstrumentFontFace", "FreeSerif", "Alegreya"),
        ("shortInstrumentFontFace", "FreeSerif", "Alegreya"),
        ("partInstrumentFontFace", "FreeSerif", "Alegreya"),
        ("dynamicsFontFace", "FreeSerif", "Alegreya"),
        ("expressionFontFace", "FreeSerif", "Alegreya"),
        ("tempoFontFace", "FreeSerif", "Alegreya"),
        ("tempoChangeFontFace", "Edwin", "Alegreya"),
        ("metronomeFontFace", "FreeSerif", "Alegreya"),
        ("measureNumberFontFace", "FreeSerif", "Alegreya"),
        ("mmRestRangeFontFace", "Edwin", "Alegreya"),
        ("translatorFontFace", "FreeSerif", "Alegreya"),
        ("systemFontFace", "FreeSerif", "Alegreya"),
        ("staffFontFace", "FreeSerif", "Alegreya"),
        ("rehearsalMarkFontFace", "FreeSerif", "Alegreya"),
        ("repeatLeftFontFace", "FreeSerif", "Alegreya"),
        ("repeatRightFontFace", "FreeSerif", "Alegreya"),
        ("frameFontFace", "FreeSerif", "Alegreya"),
        ("textLineFontFace", "FreeSerif", "Alegreya"),
        ("systemTextLineFontFace", "Edwin", "Alegreya"),
        ("glissandoFontFace", "FreeSerif", "Alegreya"),
        ("bendFontFace", "FreeSerif", "Alegreya"),
        ("headerFontFace", "FreeSerif", "Alegreya"),
        ("footerFontFace", "FreeSerif", "Alegreya"),
        ("instrumentChangeFontFace", "FreeSerif", "Alegreya"),
        ("stickingFontFace", "FreeSerif", "Alegreya"),
        ("figuredBassFontFace", "MScoreBC", "Alegreya"),
        ("user1FontFace", "FreeSerif", "Alegreya"),
        ("user2FontFace", "FreeSerif", "Alegreya"),
        ("user3FontFace", "FreeSerif", "Alegreya"),
        ("user4FontFace", "FreeSerif", "Alegreya"),
        ("user5FontFace", "FreeSerif", "Alegreya"),
        ("user6FontFace", "FreeSerif", "Alegreya"),
        ("user7FontFace", "FreeSerif", "Alegreya"),
        ("user8FontFace", "FreeSerif", "Alegreya"),
        ("user9FontFace", "FreeSerif", "Alegreya"),
        ("user10FontFace", "FreeSerif", "Alegreya"),
        ("user11FontFace", "FreeSerif", "Alegreya"),
        ("user12FontFace", "FreeSerif", "Alegreya"),
        ("letRingFontFace", "FreeSerif", "Alegreya"),
        ("palmMuteFontFace", "FreeSerif", "Alegreya"),
    ]
    score.save()

    new_score: Score = score.reload()
    assert new_score.style.get_value("defaultFontFace") == "Alegreya"

Configuration file
==================

``/etc/mscxyz.ini``

.. code-block:: ini

    [general]
    executable = /usr/bin/mscore3
    colorize = True

    [rename]
    format = '$combined_title ($combined_composer)'

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

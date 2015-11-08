Maya Tools repository
=======================

sceneSearch
------------
Search dag nodes within a Maya scene. UI filters results based on text input and updates treeView field. Used Model-View design pattern.

tbLoadSaveWeights
------------
Import and export Maya skinCluster weights to a .xml format. UI automatically fills fields based on skinCluster selection from a pulldown menu of available skinClusters in the scene. Additional option to export .xml using minidom instead of cElementTree for a more readable format.

Using tools
------------
The easiest way to get started is to use the following helper function and change the source to your downloaded python file.

```python
import sys
import os
 
def psource(module):
    file = os.path.basename( module )
    dir = os.path.dirname( module )
    toks = file.split( '.' )
    modname = toks[0]

    if( os.path.exists( dir ) ):
        paths = sys.path
        pathfound = 0
        for path in paths:
            if(dir == path):
                pathfound = 1
        if not pathfound:
            sys.path.append( dir )
 
    exec ('import ' + modname) in globals()
    exec( 'reload( ' + modname + ' )' ) in globals()
    return modname

psource( 'c:/Users/Tom/PycharmProjects/tbLoadSaveWeights/tbLoadSaveWeights_UI.py' )
tbLoadSaveWeights_UI.tbLoadSaveWeights_UI()
```

tbRibbon - written in 2013
------------
Launches a PySide UI from a Designer UI file and creates a Maya ribbon limb. Options for naming, number of joints, width, length ratio and additional fk controls. Centered control to place and addtional fk controls or nodes to constrain under a limb or spine setup.

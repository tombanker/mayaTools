Maya Tools repository
=======================

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

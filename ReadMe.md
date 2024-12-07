# ReadMe

Code:

[https://people.eecs.berkeley.edu/~jrs/stellar/](https://people.eecs.berkeley.edu/~jrs/stellar/)

Updates:

- updated the `makefile` use clang instead of cc for Mac using [Claude](https://claude.ai/new)
- update `meshconvert.py` so it can convert between `node/ele` and `tet` format
- add `tet_viewer_ps.py` use polyscope to view tetrahedron


Test: 


```
python3 meshconvert.py house2.node house2.tet #convert
python3 tet_viewer_ps.py house2.tet
```


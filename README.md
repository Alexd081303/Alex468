# Alex468
+-------------------+          REST/HTTP          +-------------------+
|                   |  POST /process              |                   |
|   Web API         | --------------------------> |   Worker Service  |
|   (Flask/Python)  |                             |   (Python/Node)   |
|                   | <-------------------------- |                   |
|                   |        JSON Result          |                   |
+-------------------+                             +-------------------+
        |                                                   |
        |                                                   |
     Client                                            Internal
   (Browser)                                           Processing

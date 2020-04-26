# cmpe273-assignment2

This scantron application supports for test subject details submission and scantron submission. It calculates score by comparing subject answer keys with scantron answers and update scores.
It supports below main functionalities

* Scantron submission
* Format validation
* Save scantron file on server for future references
* Score calculation against answer keys
* Score reporting

All the above features will be handled via a set of REST APIs. The application will persist data into a local SQLite DB.

# APIs

## Create a test

_Request_

> POST http://localhost:5000/api/tests



## Upload a scantron

_Request_

> POST http://localhost:5000/api/tests/1/scantrons


```
# HTTP Request Body
JSON_SCANTRON_FILE 
```

_Response_



## Check all scantron submissions

_Request_

> GET http://localhost:5000/api/tests/1


_Response_




![](scantron-100.jpg)




# Meetings notes

## Meeting 1.
* **DATE:** 13.2.2020
* **ASSISTANTS:** Marta Cortes Orduna

### Minutes
* Deliverable review
* The DL 2 is this week!

### Action points
* Sell the idea!
* Update Concepts and Relations to match what has been described
* Functions don't have to be described in Concepts and Relations
* The TA will check if we have to describe two additional API uses


### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*

## Meeting 2.
* **DATE:** 24.2.2020
* **ASSISTANTS:** Ivan Sanchez Milara

### Minutes
*Summary of what was discussed during the meeting*
* Documentation review
* DB limiations could be considered (e.g. notifications)
* The code will change later and it can be used for DL4

### Action points
*List here the actions points discussed with assistants*
* The first table doesn't have a name in Wiki: add it
* Add instructions how to run the tests
* Who created the event should be in the database to allow editing it
* Remove Oranigazations ID "unique requirement" (it's PK)
* Look at limitations (e.g. notifications can be 0 or 1)
* Check that the deleted element has been deleted
* Associate users to organizations that don't exist (relations)
* Follow events that don't exist (relations)


### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*

## Meeting 3.
* **DATE:** 20.3.2020
* **ASSISTANTS:** Ivan Sanchez Milara

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*


### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*

## Meeting 4.
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*
* Add events the users are following to the table
* Remove Following from the state diagram and connect to the User
* We can use the Events resource with filtering, e.g. events=/api/events?user={user_id} and events_by_user=/api/users/{user_id}/events
* The same is true for associations
* Link relations should be the same as the arrow names in the diagram
* Change varchars to string
* Datetime doesn’t exist in JSON?
* Edit user doesn’t need to have location header

### Action points
*List here the actions points discussed with assistants*
* Add the entry point to the state diagram
* Remove Following from the state diagram and connect to the User
* Link relations should be the same as the arrow names in the diagram
* Change varchars to string
* Give the url of the created resource (location header)
* Put the profile to e.g. Get Event (the documentation URL as a control profile or addition to the content type)
* Using namespaces is recommended
* Have 404 status code in edit
* Organizations should have get
* All arrows in the state diagram should be implemented in Apiary
* Edit should not return 201 but 204

### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*

## Midterm meeting
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*


### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*

## Final meeting
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*


### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*


# DB sync

this module is a custom python script that saves a rasa conversation in a sqlite table named "conversations".

Here is an example of filled table.
![Alt text](assets/Screenshot%202023-04-12%20at%2016.23.57.png)

Fields are:
- id, id of the entry
- sender_id, name of the sender
- user_text, user input
- system_text, system response. In case of multiple utterances, the text is concatenated with .
- start_timestamp, user input time
- end_timestamp, last element with a timestamp before next user input
- \* slots a column for each slot is automatically added when tracking a user

## features

- ``` ActionDBSync ``` is a action that once called syncs the tracker dictionary to the db file. It syncs the whole conversation once called. Call explicitly in a rasa story with a custom action `action_db_sync`
- ```RetrieveDBSync``` is an action that once called retrieves the `requested_slot` from the rasa form and tries to get the data from the existing tracked history of the user.
-  ```RetrieveDBSyncAll``` is an action that once called retrieves all possible slots for the existing user and tries to fill all available slots.
-  ```RetrieveDBSyncSymptoms``` is an action that once called retrieves only the slot `symptoms` for the existing user if the slot is present.

All actions have to be called explicitly by either a rasa story of some other mechanism like automatic slot mapping
## usage

to use

```
from db.actions_db_tracker import ActionDBSync, RetrieveDBSync, RetrieveDBSyncAll , RetrieveDBSyncSymptoms
```

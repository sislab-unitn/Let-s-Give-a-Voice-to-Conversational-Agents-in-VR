try:
    from db.db_utils import DBUtils
except ImportError:
    from db_utils import DBUtils
import json


class DBTracker:
    def __init__(self, db_file: str) -> None:
        # connection
        self.conn = DBUtils.create_connection(db_file)
        # create table if not exist
        DBUtils.create_table(
            "conversations",
            [
                "id INTEGER PRIMARY KEY AUTOINCREMENT",
                "sender_id TEXT NOT NULL",
                "user_text TEXT NOT NULL",
                "system_text TEXT NOT NULL",
                "start_timestamp INTEGER NOT NULL",
                "end_timestamp INTEGER NOT NULL",
                "user_message_id TEXT NOT NULL"
            ],
            self.conn,
        )
        columns = DBUtils.get_table_fields("conversations", self.conn)
        self.slots = [ l[1] for l in columns if l[1] not in ['id','sender_id','user_text','system_text','start_timestamp','end_timestamp','user_message_id']]
    def __del__(self) -> None:
        self.conn.close()
    
    def add_slots_to_table(self, tracker: dict, blacklist:list[str] = ['requested_slot','session_started_metadata','results_data']) -> None:
        """Add slots to the conversations table"""
        fields = DBUtils.get_table_fields("conversations", self.conn)
        if fields:
            fields = [f[1] for f in fields]
        for slot_name, slot_value in tracker["slots"].items():
            if slot_name not in fields and slot_name not in blacklist:
                DBUtils.update_table("conversations", [f"{slot_name} TEXT"], self.conn)
                self.slots.append(slot_name)
    def track_conversation_from_index(self, tracker: dict, idx: int = 0, blacklist:list[str] = ['requested_slot','session_started_metadata','results_data'] ) -> None:
        """Track conversation from a given starting index"""
        sender_id = tracker["sender_id"]
        # prevent unbound exceptions
        user_text = ""
        system_text = ""
        start_timestamp = ""
        end_timestamp = ""
        user_message_id = ""
        unique_slots_idx = dict()
        for item in tracker["events"][idx:]:
            if item["event"] == "user":
                # if there is a user message, insert the previous message
                if 'user_text' in locals():
                    DBUtils.insert_row(
                        "conversations",
                        ["sender_id", "user_text", "system_text", "start_timestamp", "end_timestamp", "user_message_id", *unique_slots_idx.keys()],
                        [sender_id, user_text, system_text, start_timestamp, end_timestamp, user_message_id, *unique_slots_idx.values()],
                        self.conn,
                    )
                system_text = ""
                end_timestamp  = ""
                unique_slots_idx = dict()
                user_text = item["text"]
                user_message_id = item["message_id"]
                start_timestamp = item["timestamp"]
            elif item["event"] == "bot":
                system_text += item["text"] + ". "
                end_timestamp = item["timestamp"]
            elif item["event"] == "slot" and item["name"] not in blacklist:
                unique_slots_idx[item["name"]] = item["value"]
        # flush the last turn
        DBUtils.insert_row(
                        "conversations",
                        ["sender_id", "user_text", "system_text", "start_timestamp", "end_timestamp", "user_message_id", *unique_slots_idx.keys()],
                        [sender_id, user_text, system_text, start_timestamp, end_timestamp, user_message_id, *unique_slots_idx.values()],
                        self.conn,
                    )
    def track_whole_conversation(self, tracker: dict) -> None:
        """tracks the whole conversation"""
        self.add_slots_to_table(tracker)
        self.track_conversation_from_index(tracker,0)
        
    def track_from_latest_message(self, message_id:str, tracker: dict) -> None:
        """Track conversation from the latest message that has been tracked"""
        # get the index of the latest message
        idxes = [
            i for i, elem in enumerate(tracker["events"]) if elem["event"] == "user" and elem["message_id"] == message_id
        ]
        if idxes:
            # get the index of the next message
            idx = idxes[-1]+1
            # check if there are any user messages after the latest message
            sliced_events = tracker["events"][idx:]
            usr_idx = [
                i for i, elem in enumerate(sliced_events) if elem["event"] == "user"
            ]
            if usr_idx:
                # track the conversation from the next message
                self.track_conversation_from_index(tracker, idx+usr_idx[0])
    
    def track_user(self, tracker: dict) -> None:
        """Track user's conversation and slot values"""
        sender_id = tracker["sender_id"]
        # get the current conversation
        conversation = self.get_conversation(sender_id)
        # if there is no conversation, track the whole conversation
        if not conversation:
            print("no conversation")
            self.track_whole_conversation(tracker)
        else:
            print("conversation exists")
            latest_messages_idx = [i for i, elem in enumerate(conversation) if elem[-1]!= None ]
            if latest_messages_idx:
                latest_message_idx = latest_messages_idx[-1]
                latest_message_id = conversation[latest_message_idx][-1]
                self.track_from_latest_message(latest_message_id, tracker)
                
    
    def get_conversation(self, sender_id: str) -> list[tuple]:
        """Get conversation history of a user"""
        fields = ["sender_id", "user_text", "system_text", "start_timestamp", "end_timestamp", "user_message_id"]
        table = "conversations"
        condition = "sender_id=?"
        start_timestamp = "start_timestamp"
        query = f'SELECT {",".join(fields)} FROM {table} WHERE {condition} ORDER BY {start_timestamp} ASC'
        return DBUtils.return_query(query, [sender_id], self.conn)
    def get_slots(self, sender_id: str) -> dict:
        """Get slot values of a user"""
        fields = self.slots
        print (fields)
        table = "conversations"
        condition = "sender_id=?"
        start_timestamp = "start_timestamp"
        query = f'SELECT {",".join(fields)} FROM {table} WHERE {condition} ORDER BY {start_timestamp} ASC'
        tuples = DBUtils.return_query(query, [sender_id], self.conn)
        result = dict()
        for tup in tuples:
            for i, slot in enumerate(fields):
                if tup[i] != None:
                    result[slot] = tup[i]
        return result
    @staticmethod
    def tracker_to_dict(tracker) -> dict:
        """Converts a tracker to a dictionary"""
        tracker_dict = dict()
        for attr in tracker.__dict__:
            tracker_dict[attr] = tracker.__dict__[attr]
        return tracker_dict
if __name__ == "__main__":
    import sys
    # with open(sys.argv[1]) as f:
    #     tracker = json.load(f)
    # from pprint import pprint

    # pprint(tracker)
    # for k in tracker.keys():
    #     print(k)

    db_tracker = DBTracker("test.sqlite3")
    # db_tracker.track_user(tracker)

    # a = db_tracker.get_conversation("s")
    # print(len(a))
    # print(a)
    # a = db_tracker.get_conversation("a")
    # print(a)
    # a = db_tracker.get_conversation("l")
    # print(db_tracker.slots)
    b = db_tracker.get_slots("18d4256d96a1417fb6cac957e6744d4b")
    print(b)
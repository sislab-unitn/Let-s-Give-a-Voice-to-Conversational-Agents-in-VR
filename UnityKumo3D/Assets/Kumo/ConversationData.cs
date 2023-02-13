using UnityEngine;
using System.Collections;
using System.Collections.Generic;
[System.Serializable]

public class Slots{
    public string name;
    public string value;
}
public class ConversationData
{
    public string sender;
    public string audio;
    public string message;
    public string response;
    public string slots;

    public static ConversationData CreateFromJSON(string jsonString)
    {
        return JsonUtility.FromJson<ConversationData>(jsonString);
    }
}
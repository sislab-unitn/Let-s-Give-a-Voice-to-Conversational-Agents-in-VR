using UnityEngine;

[System.Serializable]
public class ConversationData
{
    public string sender;
    public string audio;
    public string message;
    public string response;
    public string tracker;

    public static ConversationData CreateFromJSON(string jsonString)
    {
        return JsonUtility.FromJson<ConversationData>(jsonString);
    }

    // Given JSON input:
    // {"name":"Dr Charles","lives":3,"health":0.8}
    // this example will return a ConversationData object with
    // name == "Dr Charles", lives == 3, and health == 0.8f.
}
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;
using UnityEngine.UI;
using System.IO;
using UnityEditor;
public class ServerConnection : MonoBehaviour
{
    
    string url;
    
    #region Editor Exposed Variables
    
    /// <summary>
    /// The host to post the audio file to
    /// </summary>
    [Tooltip("The host to post the audio file to")]
    public string host;

    /// <summary>
    /// The port to post the audio file to
    /// </summary>
    [Tooltip("The port to post the audio file to")]
    public string port;
        /// <summary>
    /// The path to post the audio file to
    /// </summary>
    [Tooltip("The path to post the audio file to")]
    public string path;
        /// <summary>
    /// Use SSL or not
    /// </summary>
    [Tooltip("Use SSL or not")]
    public bool ssl;
    /// <summary>
    /// The name of the inputfile to upload
    /// </summary>
    [Tooltip("The name of the inputfile to upload")]
    public string inputFileName;
    /// <summary>
    /// The name of the outputfile to save
    /// </summary>
    [Tooltip("The name of the outputfile to save")]
    public string outputFileName;
    /// <summary>
    /// Set a Button to enable sending the audio file
    /// </summary>
    ///[Tooltip("Set a Button to enable sending the audio file")]
    public Button SendButton;
    #endregion
    public UnityEvent requestDone = new UnityEvent();

    // Start is called before the first frame update
    void Start()
    {
        url = (ssl?"https://":"http://")+host+":"+port;
        UnityWebRequest request = UnityWebRequest.Get(url);
        request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success) {
            Debug.Log(request.error);
        }else {
            Debug.Log("Connection Successful!");
        }
        url =  Path.Combine(url, path);
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    public void sendAudio(){
        StartCoroutine(postRequestAudio());
    }
    IEnumerator postRequestAudio()
    {
        byte [] fileContent= File.ReadAllBytes("Assets/Kumo/"+inputFileName+".wav");
        string content = System.Convert.ToBase64String(fileContent);
        // log the result
        //Debug.Log("here");
        // create a request with json
        string json = "{\"sender\":\"Unity\",\"audio\": \""+content+"\"}";
        UnityWebRequest request = UnityWebRequest.Put(url,json);
        request.SetRequestHeader("Content-Type", "application/json");
        yield return request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success) {
            Debug.Log(request.error);
        }
        else {
            Debug.Log("Upload complete!");
            // save the result as binary
            // parse back the result
            ConversationData data = (ConversationData) JsonUtility.FromJson(request.downloadHandler.text, typeof(ConversationData));
            File.WriteAllBytes("Assets/Kumo/"+outputFileName+".wav", System.Convert.FromBase64String(data.audio));
            Debug.Log("Response Saved Succesfully!");
            // refresh the asset database to show the new file
            AssetDatabase.Refresh();
            // send event to play the audio
            requestDone.Invoke();
        }
    }

}

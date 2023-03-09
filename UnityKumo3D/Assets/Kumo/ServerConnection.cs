using UnityEngine;
using UnityEngine.Networking;
public class ServerConnection : MonoBehaviour
{
    #region Editor Exposed Variables

    /// <summary>
    /// The host to post the data file to
    /// </summary>
    [Tooltip("The host to post the data file to")]
    public string host;
    /// <summary>
    /// The port to post the data file to
    /// </summary>
    [Tooltip("The port to post the data file to")]
    public string port;
    /// <summary>
    /// The path to post the data file to
    /// </summary>
    [Tooltip("The path to post the data file to")]
    public string path;
    /// <summary>
    /// The sender id for rasa to use
    /// </summary>
    [Tooltip("The sender id for rasa to use")]
    public string sender_id;
    /// <summary>
    /// Use SSL or not
    /// </summary>
    [Tooltip("Use SSL or not")]
    public bool ssl;

    #endregion
    /// <summary>
    /// The complete url to post the data file to
    /// </summary>
    private string url;
    void Start()
    {
        this.url = (this.ssl ? "https://" : "http://") + this.host + ((this.port != "") ? ":" + this.port : "");
        // do a get request to the server to check if it is up
        UnityWebRequest request = UnityWebRequest.Get(this.url);
        request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.error);
        }
        else
        {
            Debug.Log("Connection Successful!");
        }
        this.url = this.url + "/" + this.path + "?sender=" + this.sender_id;
    }

    void Update()
    {
        
    }
    void RequestServer()
    {
        // do a post request to the server
        UnityWebRequest request = UnityWebRequest.Get(this.url);
        request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.error);
        }
        else
        {
            Debug.Log("Request Successful!");
        }
    }
}

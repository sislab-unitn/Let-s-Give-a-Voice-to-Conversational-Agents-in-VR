using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.Events;
using System.Collections;

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
    /// UnityEvent that is invoked when the request is started
    /// </summary>
    public UnityEvent requestStarted = new UnityEvent();
    /// <summary>
    /// UnityEvent that is invoked when the request is done
    /// </summary>
    public UnityEvent requestDone = new UnityEvent();
    /// <summary>
    /// The complete url to post the data file to
    /// </summary>
    protected string url;
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
    IEnumerator RequestServer()
    {
        // do a post request to the server
        UnityWebRequest request = UnityWebRequest.Get(this.url);
        yield return request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.error);
        }
        else
        {
            Debug.Log("Request Successful!");
        }
        yield return null;
    }
}

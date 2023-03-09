using System.Collections;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;
using UnityEngine.UI;
public class ServerConnectionStreamSynthesis : MonoBehaviour
{
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
    /// output audio sample rate
    /// <summary>
    [Tooltip("output audio sample rate")]
    public int outputSampleRate;
    /// <summary>
    /// Set a Button to enable sending the audio file
    /// </summary>
    [Tooltip("Set a Button to enable sending the audio file")]
    public Button sendButton;
    /// <summary>
    /// Set the outputsource
    /// <summary>
    [Tooltip("audiosource from where to play the response")]
    public AudioSource outputSource;
    /// <summary>
    /// Text to synthetise
    /// <summary>
    [Tooltip("Text to synthetise")]
    public string textToSynthetise;
    /// <summary>
    /// Length of the pause for pause detection
    /// <summary>
    [Tooltip("Length of the pause for pause detection")]
    public int pauseLength = 100;
    #endregion
    public UnityEvent audioChanged = new UnityEvent();
    private string url;
    void Start()
    {
        this.url = (this.ssl ? "https://" : "http://") + this.host + ((this.port != "") ? ":" + this.port : "");
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
        this.url = this.url + "/" + this.path;
        this.sendButton.onClick.AddListener(SendRequest);
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    public void SendRequest()
    {
        this.sendButton.interactable = false;
        StartCoroutine(GetStreamAndPlay());
    }



    IEnumerator GetStreamAndPlay()
    {
        string encoded = System.Uri.EscapeUriString(this.textToSynthetise);
        encoded = this.url + "?text=" + encoded;
        UnityWebRequest request = new UnityWebRequest(encoded, "GET");
        // the download handler is a custom one that automatically plays the audio in streaming mode
        StreamingPCMDownloadHandler downloader = new StreamingPCMDownloadHandler(this.outputSource, this.outputSampleRate,1, pauseLength : this.pauseLength);
        request.downloadHandler = downloader;
        request.SetRequestHeader("Content-Type", "audio/wav");
        yield return request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.error);
        }
        else
        {
        }
        while (this.outputSource.isPlaying)
        {
            yield return null;
        }
        this.sendButton.interactable = true;
        yield return null;
    }
    // This comes from SoundWav module


}

using System.Collections;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;
using UnityEngine.UI;
/// <summary>
/// This class is used to connect to a server and send a request to get a stream of audio data
/// </summary>
public class ServerConnectionStream : MonoBehaviour
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
    /// The sender id for rasa to use
    /// </summary>
    [Tooltip("The sender id for rasa to use")]
    public string sender_id;
    /// <summary>
    /// Use SSL or not
    /// </summary>
    [Tooltip("Use SSL or not")]
    public bool ssl;
    /// <summary>
    /// input audio sample rate
    /// <summary>
    [Tooltip("input audio sample rate")]
    public int inputSampleRate;
    /// <summary>
    /// output audio sample rate
    /// <summary>
    [Tooltip("output audio sample rate")]
    public int outputSampleRate;
    /// <summary>
    /// Set a Button to enable sending the audio file
    /// </summary>
    [Tooltip("Set a Button to enable sending the audio file")]
    public Button SendButton;
    /// <summary>
    /// Set the outputsource
    /// <summary>
    [Tooltip("audiosource from where to play the response")]
    public AudioSource outputSource;
    #endregion
    /// <summary>
    /// UnityEvent that is invoked when the request is started
    /// </summary>
    public UnityEvent requestStarted = new UnityEvent();
    /// <summary>
    /// UnityEvent that is invoked when the request is done
    /// </summary>
    public UnityEvent requestDone = new UnityEvent();
    private string url;
    // recorded clip
    private AudioClip clip;
    private bool isRecording = false;
    private int maxRecordingTime = 300;
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
        this.url = this.url + "/" + this.path + "?sender=" + this.sender_id;
    }

    // Update is called once per frame
    void Update()
    {

    }
    public void buttonClicked()
    {
        if (!this.isRecording)
        {
            StartRecording();
        }
        else
        {
            StopRecording();
            SendAndPlay();
        }
    }
    public void StartRecording()
    {
        this.clip = Microphone.Start(Microphone.devices[0], true, this.maxRecordingTime, this.inputSampleRate);
        this.isRecording = true;
    }
    public void StopRecording()
    {
        var position = Microphone.GetPosition(Microphone.devices[0]);
        Microphone.End(Microphone.devices[0]);
        this.isRecording = false;
        this.clip = Audio.trimAudioClip(this.clip, position);

    }
    public void SendAndPlay()
    {
        requestStarted.Invoke();
        StartCoroutine(PostStreamAndPlay());
    }


    IEnumerator PostStreamAndPlay()
    {
        byte[] fileContent = Audio.ConvertWav(this.clip);
        UnityWebRequest request = new UnityWebRequest(this.url, "POST");
        UploadHandler uploader = new UploadHandlerRaw(fileContent);
        // the download handler is a custom one that automatically plays the audio in streaming mode
        StreamingPCMDownloadHandler downloader = new StreamingPCMDownloadHandler(this.outputSource, this.outputSampleRate,1);
        request.uploadHandler = uploader;
        request.downloadHandler = downloader;
        request.SetRequestHeader("Content-Type", "audio/wav");
        request.chunkedTransfer = true;
        yield return request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.error);
        }
        else
        {
            requestDone.Invoke();
        }
        yield return null;
    }
    // This comes from SoundWav module


}
